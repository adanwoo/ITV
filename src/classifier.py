# src/classifier.py
# 智能分类模块（基于标准化名称）

from src.config import CATEGORY_KEYWORDS, CCTV_ORDER

def classify_channel(channel: dict) -> str:
    """根据标准化频道名返回分类"""
    name = channel.get("name", "")
    group = channel.get("group_title", "")
    
    # 优先使用 group-title 匹配
    if group:
        for cat, keywords in CATEGORY_KEYWORDS.items():
            if cat == "其他":
                continue
            for kw in keywords:
                if kw.lower() in group.lower():
                    return cat
    
    # 其次匹配频道名
    for cat, keywords in CATEGORY_KEYWORDS.items():
        if cat == "其他":
            continue
        for kw in keywords:
            if kw.lower() in name.lower():
                return cat
    
    # 特殊规则：包含“卫视”但未匹配到上述分类的，归为卫视
    if "卫视" in name:
        return "卫视"
    
    return "其他"

def classify_all(channels: list) -> dict:
    """分类所有频道，返回 {分类: [频道字典, ...]}，并按照央视顺序排序"""
    classified = {cat: [] for cat in CATEGORY_KEYWORDS.keys()}
    for ch in channels:
        cat = classify_channel(ch)
        classified[cat].append(ch)
    
    # 央视频道内部排序
    if "央视" in classified:
        def ctv_key(ch):
            name = ch["name"]
            for idx, std in enumerate(CCTV_ORDER):
                if std.lower() == name.lower() or name.lower().startswith(std.lower()):
                    return idx
            return len(CCTV_ORDER)
        classified["央视"].sort(key=ctv_key)
    
    # 其他分类按名称排序
    for cat in classified:
        if cat != "央视":
            classified[cat].sort(key=lambda x: x["name"])
    
    # 输出统计
    print("📊 分类统计：")
    for cat, lst in classified.items():
        if lst:
            print(f"  {cat}: {len(lst)} 个频道")
    return classified
