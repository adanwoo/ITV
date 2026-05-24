# src/alias_matcher.py
# 别名匹配模块，支持正则表达式

import re
from pathlib import Path
from typing import Dict, Optional, Union

from src.config import ALIAS_FILE, ENABLE_ALIAS

class AliasMatcher:
    def __init__(self, alias_file: Path = ALIAS_FILE):
        self.alias_file = alias_file
        self.mappings: Dict[Union[str, re.Pattern], str] = {}  # alias -> standard
        self._load()

    def _load(self):
        if not self.alias_file.exists():
            print(f"⚠️ 别名文件不存在: {self.alias_file}")
            return
        with open(self.alias_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                parts = line.split(',')
                if len(parts) < 2:
                    print(f"⚠️ 别名文件第 {line_num} 行格式错误，跳过: {line}")
                    continue
                standard = parts[0].strip()
                aliases = parts[1:]
                for alias in aliases:
                    alias = alias.strip()
                    if not alias:
                        continue
                    if alias.startswith('re:'):
                        pattern_str = alias[3:].strip()
                        try:
                            pattern = re.compile(pattern_str, re.IGNORECASE)
                            self.mappings[pattern] = standard
                        except re.error as e:
                            print(f"⚠️ 别名文件第 {line_num} 行正则错误: {e}")
                    else:
                        self.mappings[alias.lower()] = standard
        print(f"✅ 已加载 {len(self.mappings)} 条别名规则")

    def match(self, channel_name: str) -> Optional[str]:
        """返回标准化名称，若无匹配则返回 None"""
        if not channel_name:
            return None
        name_lower = channel_name.lower()
        # 优先匹配普通字符串（子串包含）
        for alias, standard in self.mappings.items():
            if isinstance(alias, str):
                if alias in name_lower:
                    return standard
        # 再匹配正则表达式
        for pattern, standard in self.mappings.items():
            if isinstance(pattern, re.Pattern):
                if pattern.search(channel_name):
                    return standard
        return None

    def normalize(self, channel_name: str) -> str:
        """标准化频道名，若无匹配则返回原名称"""
        mapped = self.match(channel_name)
        return mapped if mapped is not None else channel_name

_matcher = None

def get_alias_matcher() -> AliasMatcher:
    global _matcher
    if _matcher is None and ENABLE_ALIAS:
        _matcher = AliasMatcher()
    return _matcher
