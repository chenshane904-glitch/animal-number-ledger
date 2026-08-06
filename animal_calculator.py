# -*- coding: utf-8 -*-
"""
平特模式计算器
独立于号码模式，不修改原有calculator.py
"""

from typing import Dict, List
from models import Instruction
from constants import AMOUNT_MULTIPLIER
import json


class AnimalCalculationResult:
    """平特模式计算结果"""
    def __init__(self):
        self.animal_amounts: Dict[str, int] = {}  # {生肖: 金额整数}
        self.total_amount: int = 0  # 总金额（整数）
        self.non_zero_count: int = 0  # 非零生肖数量
        self.max_animal: str = ""  # 最高下注生肖
        self.max_amount: int = 0  # 最高金额


class AnimalCalculator:
    """平特模式计算器"""

    def __init__(self, config: dict):
        """
        初始化平特计算器

        Args:
            config: 玩法配置字典
        """
        self.config = config
        self.animals = config.get('animals', [])
        self.odds = config.get('odds', 1.0)

        # 初始化所有生肖金额为0
        self.animal_amounts = {animal: 0 for animal in self.animals}

    def calculate(self, instructions: List[Instruction], current_totals: Dict[str, int]) -> AnimalCalculationResult:
        """
        计算平特模式结果

        Args:
            instructions: 指令列表
            current_totals: 当前生肖累计 {生肖: 金额整数}

        Returns:
            AnimalCalculationResult: 计算结果
        """
        result = AnimalCalculationResult()

        # 从current_totals初始化（如果是生肖字典）
        for animal in self.animals:
            result.animal_amounts[animal] = current_totals.get(animal, 0)

        # 处理每条指令
        for inst in instructions:
            if inst.target_type == 'animal':
                # 平特模式：直接累加生肖金额
                for target in inst.targets:
                    if target in self.animals:
                        result.animal_amounts[target] += inst.amount_integer

        # 计算统计信息
        result.total_amount = sum(result.animal_amounts.values())
        result.non_zero_count = sum(1 for amount in result.animal_amounts.values() if amount > 0)

        # 找到最高下注生肖
        if result.non_zero_count > 0:
            max_animal = max(result.animal_amounts.items(), key=lambda x: x[1])
            result.max_animal = max_animal[0]
            result.max_amount = max_animal[1]

        return result

    def calculate_payout(self, amount: int) -> int:
        """
        计算赔付金额

        Args:
            amount: 下注金额（整数，已乘以AMOUNT_MULTIPLIER）

        Returns:
            int: 赔付金额（整数）
        """
        # 赔付 = 金额 × 赔率
        return int(amount * self.odds)

    def calculate_profit(self, payout: int, total_bet: int) -> int:
        """
        计算盈利

        Args:
            payout: 赔付金额（整数）
            total_bet: 今日总下注（整数）

        Returns:
            int: 盈利（整数，可能为负）
        """
        # 盈利 = 赔付 - 今日总下注
        return payout - total_bet
