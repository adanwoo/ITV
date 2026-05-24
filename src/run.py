#!/usr/bin/env python3
import asyncio
import sys
import os
import time
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import (
    IPTV_SOURCES, ENABLE_REGION_FILTER, PREFERRED_LOCATION, PREFERRED_ISP,
    ENABLE_IP_RESOLVE, ENABLE_DEMO_FILTER, ENABLE_ALIAS, ENABLE_BLACKLIST,
    DATABASE_ENABLE, CACHE_EXPIRY_SECONDS, DATABASE_TABLE
)
from src.fetcher import fetch_all_sources
from src.parser import parse_and_dedupe
from src.speed_tester import test_channels_concurrent
from src.ffmpeg_validator import validate_batch, cleanup as ffmpeg_cleanup
from src.generator import generate_outputs_from_demo, generate_excluded_output
from src.merger import merge_channels_by_name, fix_cctv_mismatch
from src.ip_resolver import get_resolver, matches_region
from src.blacklist_filter import get_blacklist_filter
from src.demo_filter import filter_and_order_by_demo
from src.alias_matcher import get_alias_matcher
from src.database import get_db_cache, channel_key

async def init_ip_resolver():
    if not ENABLE_IP_RESOLVE:
        print("⚙️ IP解析未启用")
        return
    resolver = get_resolver()
    if resolver.is_available:
        print("✅ IP解析器已就绪")
    else:
        print("⚠️ IP解析器不可用，将跳过地域筛选")

def filter_by_region(channels):
    if not ENABLE_REGION_FILTER:
        return channels
    preferred_locations = [loc.strip() for loc in PREFERRED_LOCATION.split(",") if loc.strip()]
    preferred_isps = [isp.strip() for isp in PREFERRED_ISP.split(",") if isp.strip()]
    if not preferred_locations and not preferred_isps:
        return channels
    print(f"🎯 地域筛选: 地域={preferred_locations}, 运营商={preferred_isps}")
    resolver = get_resolver()
    if not resolver.is_available:
        print("⚠️ IP解析器不可用，跳过地域筛选")
        return channels
    filtered = []
    for ch in channels:
        ip_info = ch.get("ip_info")
        if ip_info and matches_region(ip_info, preferred_locations, preferred_isps):
            filtered.append(ch)
    print(f"  筛选结果: {len(filtered)}/{len(channels)} 个频道通过地域筛选")
    return filtered

async def save_speed_cache(db, channels):
    """将测速通过的每个源保存到数据库缓存"""
    for ch in channels:
        key = channel_key(ch["name"], ch["url"])
        await db.set_speed_result(key, ch)
    print(f"💾 已保存 {len(channels)} 个频道源到数据库缓存")

async def main():
    print("🚀 IPTV智能整理平台启动")
    print(f"📡 配置：超时={os.getenv('TIMEOUT','10')}s, 并发={os.getenv('MAX_WORKERS','10')}, ffmpeg={os.getenv('FFMPEG_ENABLE','true')}")
    print(f"📋 增强过滤: demo={ENABLE_DEMO_FILTER}, alias={ENABLE_ALIAS}, blacklist={ENABLE_BLACKLIST}")

    await init_ip_resolver()
    if os.getenv("FFMPEG_ENABLE", "true").lower() == "true":
        from src.ffmpeg_validator import check_ffprobe
        await check_ffprobe()

    db = await get_db_cache()

    # 始终执行完整采集（拉取源），但测速会复用数据库缓存
    print("\n📥 执行完整采集流程...")
    raw_contents = await fetch_all_sources(IPTV_SOURCES)
    channels_dict = parse_and_dedupe(raw_contents)
    if not channels_dict:
        print("❌ 未获取到任何频道，请检查网络或源地址")
        return 1

    print(f"📊 原始频道数（去重后）: {len(channels_dict)}")

    # 测速（内部会优先使用数据库缓存）
    valid_channels = await test_channels_concurrent(channels_dict)
    print(f"📊 通过HTTP测速的频道数: {len(valid_channels)}")

    valid_channels = await validate_batch(valid_channels)
    print(f"📊 通过ffmpeg深度验证的频道数: {len(valid_channels)}")

    # 保存测速结果到数据库（供下次使用）
    if DATABASE_ENABLE:
        await save_speed_cache(db, valid_channels)
        await db.set_last_update_time()

    # 合并相同频道名
    merged_channels = merge_channels_by_name(valid_channels)
    print(f"📊 合并后的频道数: {len(merged_channels)}")

    # 修复 CCTV-1 与 CCTV-17 错位问题
    merged_channels = fix_cctv_mismatch(merged_channels)
    print(f"📊 修复央视错位后频道数: {len(merged_channels)}")

    # 黑名单过滤
    if ENABLE_BLACKLIST:
        blacklist_filter = get_blacklist_filter()
        before = len(merged_channels)
        merged_channels = blacklist_filter.filter_channels(merged_channels)
        print(f"📊 黑名单过滤后: {len(merged_channels)} (减少 {before - len(merged_channels)})")

    # Demo 筛选和排序（同时获得匹配和未匹配的频道）
    if ENABLE_DEMO_FILTER:
        before = len(merged_channels)
        ordered_channels, excluded_channels = filter_and_order_by_demo(merged_channels)
        print(f"📊 Demo筛选后: {len(ordered_channels)} (匹配), 剔除 {len(excluded_channels)} 个频道")
        if not ordered_channels:
            print("❌ Demo 筛选后无频道，尝试不筛选")
            ordered_channels = merged_channels
            excluded_channels = []
        # 输出被剔除的频道
        if excluded_channels:
            generate_excluded_output(excluded_channels)
    else:
        ordered_channels = merged_channels

    # 地域筛选
    ordered_channels = filter_by_region(ordered_channels)
    if not ordered_channels:
        print("❌ 过滤后无有效频道")
        return 1

    # 输出：直接使用 demo 顺序
    generate_outputs_from_demo(ordered_channels)

    total = len(ordered_channels)
    print(f"🎉 完成！有效频道总数: {total}")
    ffmpeg_cleanup()
    await db.close()
    return 0

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
