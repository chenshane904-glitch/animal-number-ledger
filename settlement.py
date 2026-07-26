# -*- coding: utf-8 -*-
"""
每日结算模块
"""

from datetime import datetime
from typing import Dict, List
from models import Allocation
from constants import AMOUNT_MULTIPLIER


class Settlement:
    """每日结算"""

    # 赔率
    ODDS = 47

    def __init__(self, database):
        """
        初始化结算模块

        Args:
            database: 数据库实例
        """
        self.db = database

    def calculate_settlement(self, winning_number: int, ledger_date: str) -> Dict:
        """
        计算每日结算

        Args:
            winning_number: 中奖号码（1-49）
            ledger_date: 账本日期（YYYY-MM-DD格式）

        Returns:
            结算结果字典
        """
        # 1. 获取当天的活跃账本
        ledger = self.db.get_active_ledger(ledger_date)

        if not ledger:
            return {
                'error': f'未找到日期 {ledger_date} 的账本',
                'winning_number': winning_number,
                'ledger_date': ledger_date
            }

        # 2. 获取当天所有已确认的分配记录
        all_allocations = []
        for batch in ledger.batches:
            all_allocations.extend(batch.allocations)

        if not all_allocations:
            return {
                'error': f'当天没有任何下注记录',
                'winning_number': winning_number,
                'ledger_date': ledger_date
            }

        # 3. 统计每个号码的累计下注金额
        number_amounts = {}
        for alloc in all_allocations:
            if alloc.number not in number_amounts:
                number_amounts[alloc.number] = 0
            number_amounts[alloc.number] += alloc.amount_integer

        # 4. 计算中奖号码的累计金额
        winning_amount = number_amounts.get(winning_number, 0)

        # 5. 计算应赔金额 = 中奖号码金额 × 赔率
        payout_amount = winning_amount * self.ODDS

        # 6. 计算今日总下注
        total_bet = sum(number_amounts.values())

        # 7. 计算今日盈亏 = 总下注 - 应赔金额
        profit_loss = total_bet - payout_amount

        # 8. 构建结算结果
        result = {
            'winning_number': winning_number,
            'ledger_date': ledger_date,
            'winning_amount': winning_amount,
            'winning_amount_display': f'{winning_amount / AMOUNT_MULTIPLIER:.2f}',
            'odds': self.ODDS,
            'payout_amount': payout_amount,
            'payout_amount_display': f'{payout_amount / AMOUNT_MULTIPLIER:.2f}',
            'total_bet': total_bet,
            'total_bet_display': f'{total_bet / AMOUNT_MULTIPLIER:.2f}',
            'profit_loss': profit_loss,
            'profit_loss_display': f'{profit_loss / AMOUNT_MULTIPLIER:.2f}',
            'total_records': len(all_allocations),
            'number_with_bet': len([a for a in number_amounts.values() if a > 0])
        }

        return result

    def save_settlement(self, settlement_result: Dict) -> int:
        """
        保存结算记录到数据库

        Args:
            settlement_result: 结算结果字典

        Returns:
            结算记录ID
        """
        # TODO: 需要在database.py中添加保存结算记录的方法
        # 暂时返回0
        return 0

    def get_settlement_history(self, limit: int = 30) -> List[Dict]:
        """
        获取结算历史记录

        Args:
            limit: 返回记录数量限制

        Returns:
            结算历史列表
        """
        # TODO: 需要在database.py中添加查询结算历史的方法
        # 暂时返回空列表
        return []
