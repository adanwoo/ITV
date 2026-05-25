# src/alias_matcher.py
# 别名匹配模块：支持逗号或冒号分隔，仅精确匹配和正则匹配

import re
from pathlib import Path
from typing import Dict, Optional

from src.config import ALIAS_FILE, ENABLE_ALIAS

class AliasMatcher:
    def __init__(self, alias_file: Path = ALIAS_FILE):
        self.alias_file = alias_file
        self.exact_mappings: Dict[str, str] = {}
        self.regex_mappings: Dict[re.Pattern, str] = {}
        self._load()

    def _parse_line(self, line: str) -> tuple:
        """解析一行，返回 (标准名, [别名列表])，支持逗号和冒号分隔"""
        line = line.strip()
        # 优先按逗号分割
        if ',' in line:
            parts = [p.strip() for p in line.split(',')]
            if len(parts) >= 2:
                return parts[0], parts[1:]
        # 如果没有逗号，尝试冒号（兼容旧格式）
        if ':' in line and not line.startswith('re:'):
            parts = [p.strip() for p in line.split(':', 1)]
            if len(parts) == 2:
                print(f"⚠️ 行使用冒号分隔，建议改用逗号: {line}")
                return parts[0], [parts[1]]
        return None, []

    def _load(self):
        if not self.alias_file.exists():
            print(f"⚠️ 别名文件不存在: {self.alias_file}")
            return
        with open(self.alias_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                standard, aliases = self._parse_line(line)
                if not standard:
                    print(f"⚠️ 别名文件第 {line_num} 行格式错误，跳过: {line}")
                    continue
                for alias in aliases:
                    alias = alias.strip()
                    if not alias:
                        continue
                    if alias.startswith('re:'):
                        pattern_str = alias[3:].strip()
                        try:
                            pattern = re.compile(pattern_str, re.IGNORECASE)
                            self.regex_mappings[pattern] = standard
                        except re.error as e:
                            print(f"⚠️ 别名文件第 {line_num} 行正则错误: {e}")
                    else:
                        self.exact_mappings[alias.lower()] = standard
        print(f"✅ 已加载别名规则：精确 {len(self.exact_mappings)}，正则 {len(self.regex_mappings)}")

    def match(self, channel_name: str) -> Optional[str]:
        if not channel_name:
            return None
        name_lower = channel_name.lower()
        # 精确匹配
        if name_lower in self.exact_mappings:
            return self.exact_mappings[name_lower]
        # 正则匹配
        for pattern, standard in self.regex_mappings.items():
            if pattern.search(channel_name):
                return standard
        return None

    def normalize(self, channel_name: str) -> str:
        mapped = self.match(channel_name)
        return mapped if mapped is not None else channel_name

_matcher = None

def get_alias_matcher() -> AliasMatcher:
    global _matcher
    if _matcher is None and ENABLE_ALIAS:
        _matcher = AliasMatcher()
    return _matcher
