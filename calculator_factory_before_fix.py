# -*- coding: utf-8 -*-
"""
计算器工厂 - 根据玩法模式返回对应的计算器
"""

from play_mode import PlayMode
from calculator import Calculator
from animal_calculator import AnimalCalculator
from play_mode_config import load_play_mode_config


class CalculatorFactory:
    """计算器工厂"""

    @staticmethod
    def create_calculator(mode: PlayMode, animal_mapping: dict):
        """
        创建计算器实例

        Args:
            mode: 玩法模式
            animal_mapping: 动物映射表

        Returns:
            对应的计算器实例
        """
        if mode == PlayMode.NUMBER:
            # 号码模式：使用原有Calculator
            return Calculator(animal_mapping)
        elif mode == PlayMode.ANIMAL:
            # 平特模式：使用AnimalCalculator
            config = load_play_mode_config(mode)
            return AnimalCalculator(config)
        else:
            raise ValueError(f"不支持的玩法模式: {mode}")

    @staticmethod
    def get_calculator(mode: PlayMode, animal_mapping: dict):
        """
        获取计算器（别名，与create_calculator相同）

        Args:
            mode: 玩法模式
            animal_mapping: 动物映射表

        Returns:
            对应的计算器实例
        """
        return CalculatorFactory.create_calculator(mode, animal_mapping)
