"""计算器模块"""
from typing import Dict, List
from models import Instruction, Allocation, CalculationResult
from constants import MIN_NUMBER, MAX_NUMBER


class Calculator:
    """计算器"""

    def __init__(self, animal_mapping: dict):
        """
        初始化计算器

        Args:
            animal_mapping: 动物号码映射 {动物名: [号码列表]}
        """
        self.animal_mapping = animal_mapping
        # 构建反向映射 {号码: 动物名}
        self.number_to_animal = {}
        for animal, numbers in animal_mapping.items():
            for num in numbers:
                self.number_to_animal[num] = animal

    def calculate(self, instructions: List[Instruction],
                  initial_amounts: Dict[int, int] = None) -> CalculationResult:
        """
        计算指令结果

        Args:
            instructions: 指令列表
            initial_amounts: 初始金额 {号码: 金额整数}，默认全0

        Returns:
            计算结果
        """
        if initial_amounts is None:
            initial_amounts = {i: 0 for i in range(MIN_NUMBER, MAX_NUMBER + 1)}

        # 复制初始金额
        number_amounts = initial_amounts.copy()

        # 存储所有分配和来源
        allocations = []
        sources = {i: [] for i in range(MIN_NUMBER, MAX_NUMBER + 1)}

        for instruction in instructions:
            # 根据目标类型进行分配
            if instruction.target_type == 'number':
                # 直接号码分配
                for target in instruction.targets:
                    num = int(target)
                    number_amounts[num] += instruction.amount_integer

                    allocation = Allocation(
                        number=num,
                        animal=self.number_to_animal.get(num, ''),
                        amount_integer=instruction.amount_integer,
                        instruction_id=instruction.id
                    )
                    allocations.append(allocation)
                    sources[num].append(instruction.original_text)

            elif instruction.target_type == 'animal':
                # 动物分配（各号）
                for animal in instruction.targets:
                    numbers = self.animal_mapping.get(animal, [])
                    for num in numbers:
                        number_amounts[num] += instruction.amount_integer

                        allocation = Allocation(
                            number=num,
                            animal=animal,
                            amount_integer=instruction.amount_integer,
                            instruction_id=instruction.id
                        )
                        allocations.append(allocation)
                        sources[num].append(instruction.original_text)

        # 计算总数和非零数量
        total_amount = sum(number_amounts.values())
        non_zero_count = sum(1 for amount in number_amounts.values() if amount > 0)

        result = CalculationResult(
            number_amounts=number_amounts,
            total_amount=total_amount,
            non_zero_count=non_zero_count,
            allocations=allocations,
            sources=sources
        )

        return result
