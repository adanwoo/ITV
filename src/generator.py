# src/generator.py
# 输出生成：M3U 和 TXT 格式（使用标准化后的频道名）

from pathlib import Path
from src.config import OUTPUT_DIR, M3U_FILE, TXT_FILE

def clean_channel_name(name: str) -> str:
    """去除残留的清晰度标签（以防万一）"""
    import re
    name = re.sub(r'\s*(?:1080[pi]|720[pi]|4K|8K|HD|高清|超清|标清|流畅|付费|备\d*)\s*', '', name, flags=re.IGNORECASE)
    name = re.sub(r'[（(][^）)]*[）)]', '', name)
    name = re.sub(r'\s+', ' ', name).strip()
    return name

def generate_m3u(classified: dict, output_path: Path):
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for category, channels in classified.items():
            if not channels:
                continue
            f.write(f"\n# 分类: {category}\n")
            for ch in channels:
                url = ch["urls"][0] if "urls" in ch and ch["urls"] else ch["url"]
                clean_name = clean_channel_name(ch["name"])
                extinf = f'#EXTINF:-1'
                if ch.get("id"):
                    extinf += f' tvg-id="{ch["id"]}"'
                if ch.get("logo"):
                    extinf += f' tvg-logo="{ch["logo"]}"'
                if category:
                    extinf += f' group-title="{category}"'
                extinf += f',{clean_name}\n'
                f.write(extinf)
                f.write(f"{url}\n")

def generate_txt(classified: dict, output_path: Path):
    with open(output_path, "w", encoding="utf-8") as f:
        for category, channels in classified.items():
            if not channels:
                continue
            f.write(f"\n# {category}\n")
            for ch in channels:
                url = ch["urls"][0] if "urls" in ch and ch["urls"] else ch["url"]
                f.write(f"{url}\n")

def generate_outputs(classified: dict):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    m3u_path = OUTPUT_DIR / M3U_FILE
    txt_path = OUTPUT_DIR / TXT_FILE
    generate_m3u(classified, m3u_path)
    generate_txt(classified, txt_path)
    print(f"📄 输出已生成：\n  - {m3u_path}\n  - {txt_path}")
