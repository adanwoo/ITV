# src/classifier.py
# 智能分类模块：央视、卫视、地方、港澳台

from src.config import CCTV_ORDER

# 港澳台关键词（宽泛覆盖）
HK_MACAU_TAIWAN_KEYWORDS = [
    "港", "澳", "台", "香港", "澳门", "台湾", "翡翠", "明珠", "凤凰", "tvb", "无线",
    "rthk", "hoy", "viu", "tvbs", "东森", "民视", "台视", "华视", "中视", "三立",
    "纬来", "靖天", "星空", "澳视", "澳门卫视", "香港卫视", "凤凰卫视", "TVB"
]

def classify_channel(channel: dict) -> str:
    name = channel.get("name", "")
    name_lower = name.lower()
    group = channel.get("group_title", "").lower()
    
    # 1. 央视
    if any(kw in name_lower for kw in ["cctv", "央视", "中央电视", "中央-", "中央台", "cntv"]):
        return "央视"
    
    # 2. 港澳台（优先级高于卫视和地方）
    for kw in HK_MACAU_TAIWAN_KEYWORDS:
        if kw.lower() in name_lower or kw.lower() in group:
            return "港澳台"
    
    # 3. 卫视
    if "卫视" in name:
        return "卫视"
    
    # 4. 地方（省、市、常见后缀）
    provinces = [
        "北京", "天津", "上海", "重庆", "河北", "山西", "辽宁", "吉林", "黑龙江",
        "江苏", "浙江", "安徽", "福建", "江西", "山东", "河南", "湖北", "湖南",
        "广东", "海南", "四川", "贵州", "云南", "陕西", "甘肃", "青海", "台湾",
        "内蒙古", "广西", "西藏", "宁夏", "新疆", "香港", "澳门"
    ]
    for prov in provinces:
        if prov in name:
            return "地方"
    if any(kw in name for kw in ["电视台", "综合频道", "公共频道", "生活频道", "新闻综合"]):
        return "地方"
    
    return "其他"

def classify_and_filter(channels: list) -> dict:
    """只保留央视、卫视、地方、港澳台四类"""
    result = {"央视": [], "卫视": [], "地方": [], "港澳台": []}
    other_count = 0
    for ch in channels:
        cat = classify_channel(ch)
        if cat in result:
            result[cat].append(ch)
        else:
            other_count += 1
    
    # 央视频道按顺序排序
    if result["央视"]:
        def ctv_key(ch):
            name = ch["name"]
            for idx, std in enumerate(CCTV_ORDER):
                if std.lower() == name.lower() or name.lower().startswith(std.lower()):
                    return idx
            return len(CCTV_ORDER)
        result["央视"].sort(key=ctv_key)
    
    # 其他分类按名称排序
    for cat in ["卫视", "地方", "港澳台"]:
        if result[cat]:
            result[cat].sort(key=lambda x: x["name"])
    
    print("📊 分类统计（央视/卫视/地方/港澳台）：")
    for cat, lst in result.items():
        if lst:
            print(f"  {cat}: {len(lst)} 个频道")
    print(f"  （其他分类被过滤: {other_count} 个频道）")
    return result
