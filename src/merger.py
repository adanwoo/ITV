# src/merger.py
# 频道合并模块：按标准化名称合并多源，排序后只保留最优源

from collections import defaultdict
from src.config import MAX_SOURCES_PER_CHANNEL

def normalize_channel_name(name: str) -> str:
    """标准化频道名（用于合并，去除清晰度等噪声）"""
    import re
    name = re.sub(r'\s*(?:1080[pi]|720[pi]|4K|8K|HD|高清|超清|标清|流畅|付费)\s*', '', name, flags=re.IGNORECASE)
    name = re.sub(r'[（(][^）)]*[）)]', '', name)
    name = re.sub(r'[^\w\u4e00-\u9fa5\-]', '', name)  # 保留连字符
    return name.strip()

def merge_channels_by_name(valid_channels: list) -> list:
    """按标准化名称合并，每个频道保留最多 MAX_SOURCES_PER_CHANNEL 个源，按优先级排序"""
    groups = defaultdict(list)
    for ch in valid_channels:
        norm_name = normalize_channel_name(ch["name"])
        groups[norm_name].append(ch)
    
    merged = []
    for norm_name, ch_list in groups.items():
        # 排序：优先 H.264，然后延迟低
        def sort_key(ch):
            codec = ch.get("video_codec", "")
            codec_priority = 0 if codec == "h264" else 1 if codec == "hevc" else 2
            latency = ch.get("latency", 9999)
            return (codec_priority, latency)
        ch_list.sort(key=sort_key)
        top = ch_list[:MAX_SOURCES_PER_CHANNEL]
        # 使用第一个频道的元数据作为模板
        primary = top[0]
        merged_ch = {
            "name": primary["name"],   # 标准化名称
            "urls": [c["url"] for c in top],
            "url": primary["url"],
            "latency": primary["latency"],
            "video_codec": primary["video_codec"],
            "group_title": primary.get("group_title", ""),
            "id": primary.get("tvg_id", ""),
            "logo": primary.get("tvg_logo", ""),
            "ip_info": primary.get("ip_info")
        }
        merged.append(merged_ch)
    
    print(f"🔄 频道合并完成：{len(valid_channels)} 个源 -> {len(merged)} 个频道（每个频道最多 {MAX_SOURCES_PER_CHANNEL} 个源）")
    return merged
