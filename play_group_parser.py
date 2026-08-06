# -*- coding: utf-8 -*-
"""
组合玩法解析器 - 识别红单、蓝双、尾大等组合玩法
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from constants import MIN_NUMBER, MAX_NUMBER


class PlayGroupsLoader:
    """组合玩法配置加载器"""

    def __init__(self, config_path: str = "play_groups.json"):
        self.config_path = Path(config_path)
        self.play_groups: Dict[str, List[str]] = {}
        self._load_config()

    def _load_config(self):
        """加载配置文件"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"组合玩法配置文件不存在: {self.config_path}")

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.play_groups = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"组合玩法配置文件格式错误: {e}")

        # 验证配置
        self._validate_config()

    def _validate_config(self):
        """验证配置内容"""
        if not self.play_groups:
            raise ValueError("组合玩法配置为空")

        for play_name, numbers in self.play_groups.items():
            if not isinstance(numbers, list):
                raise ValueError(f"玩法 '{play_name}' 的号码必须是列表")

            if not numbers:
                raise ValueError(f"玩法 '{play_name}' 的号码列表为空")

            # 验证号码格式
            for num_str in numbers:
                try:
                    num = int(num_str)
                    if not (MIN_NUMBER <= num <= MAX_NUMBER):
                        raise ValueError(f"玩法 '{play_name}' 包含无效号码: {num_str}")
                except ValueError:
                    raise ValueError(f"玩法 '{play_name}' 包含无效号码格式: {num_str}")

    def get_play_names(self) -> List[str]:
        """获取所有玩法名称，按长度降序排列（最长优先）"""
        return sorted(self.play_groups.keys(), key=len, reverse=True)

    def get_numbers(self, play_name: str) -> Optional[List[str]]:
        """获取玩法对应的号码列表"""
        return self.play_groups.get(play_name)


class PlayGroupParser:
    """组合玩法解析器"""

    def __init__(self, play_groups_loader: PlayGroupsLoader):
        self.loader = play_groups_loader
        self.play_names = self.loader.get_play_names()

    def extract_play_groups(self, text: str) -> List[Tuple[str, int, int]]:
        """
        从文本中提取组合玩法

        返回: [(玩法名称, 起始位置, 结束位置), ...]
        按最长匹配优先原则
        """
        found_plays = []

        # 按玩法名称长度降序匹配（最长优先）
        for play_name in self.play_names:
            # 直接查找玩法名称
            start_pos = 0
            while True:
                pos = text.find(play_name, start_pos)
                if pos == -1:
                    break

                start = pos
                end = pos + len(play_name)

                # 检查是否与已找到的玩法重叠
                overlaps = False
                for _, existing_start, existing_end in found_plays:
                    if not (end <= existing_start or start >= existing_end):
                        overlaps = True
                        break

                if not overlaps:
                    found_plays.append((play_name, start, end))

                start_pos = pos + 1

        # 按位置排序
        found_plays.sort(key=lambda x: x[1])

        return found_plays

    def replace_play_groups_with_placeholder(self, text: str) -> Tuple[str, Dict[str, str]]:
        """
        将文本中的组合玩法替换为占位符

        返回: (替换后的文本, {占位符: 玩法名称})
        """
        found_plays = self.extract_play_groups(text)

        if not found_plays:
            return text, {}

        # 从后往前替换（避免位置偏移）
        result = text
        play_map = {}

        for idx, (play_name, start, end) in enumerate(reversed(found_plays)):
            placeholder = f"__PLAY_{len(found_plays) - idx - 1}__"
            result = result[:start] + placeholder + result[end:]
            play_map[placeholder] = play_name

        return result, play_map

    def expand_play_group(self, play_name: str) -> Optional[List[str]]:
        """展开组合玩法为号码列表"""
        return self.loader.get_numbers(play_name)


def test_play_group_parser():
    """测试组合玩法解析器"""
    print("=== 测试组合玩法解析器 ===\n")

    loader = PlayGroupsLoader()
    parser = PlayGroupParser(loader)

    # 测试1: 提取单个玩法
    text1 = "红单各50"
    plays1 = parser.extract_play_groups(text1)
    print(f"测试1: '{text1}'")
    print(f"  提取结果: {plays1}")
    if plays1:
        numbers = parser.expand_play_group(plays1[0][0])
        print(f"  展开号码: {numbers}")
        print(f"  号码数量: {len(numbers)}")

    # 测试2: 3尾（数字不应被误识别为普通号码）
    text2 = "3尾各50"
    plays2 = parser.extract_play_groups(text2)
    print(f"\n测试2: '{text2}'")
    print(f"  提取结果: {plays2}")
    if plays2:
        numbers = parser.expand_play_group(plays2[0][0])
        print(f"  展开号码: {numbers}")

    # 测试3: 最长匹配优先（红单 vs 单）
    text3 = "红单各20 单各10"
    plays3 = parser.extract_play_groups(text3)
    print(f"\n测试3: '{text3}'")
    print(f"  提取结果: {plays3}")

    # 测试4: 替换为占位符
    text4 = "红单各50 虎各20 蓝波各30"
    replaced, play_map = parser.replace_play_groups_with_placeholder(text4)
    print(f"\n测试4: '{text4}'")
    print(f"  替换后: '{replaced}'")
    print(f"  玩法映射: {play_map}")

    print("\n=== 测试完成 ===")


if __name__ == "__main__":
    test_play_group_parser()
