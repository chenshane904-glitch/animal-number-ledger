# -*- coding: utf-8 -*-
"""
玩法模式定义
"""

from enum import Enum


class PlayMode(Enum):
    """玩法模式枚举"""
    NUMBER = "number"  # 号码模式（原有模式，包含生肖、波色等）
    FLAT_ZODIAC = "flat_zodiac"  # 平特一肖模式（新增模式，不展开号码）

    def __str__(self):
        return self.value

    @classmethod
    def from_string(cls, mode_str: str):
        """从字符串转换为枚举"""
        for mode in cls:
            if mode.value == mode_str:
                return mode
        return cls.NUMBER  # 默认返回号码模式


# 玩法模式显示名称
PLAY_MODE_NAMES = {
    PlayMode.NUMBER: "号码模式",
    PlayMode.FLAT_ZODIAC: "平特模式"
}
