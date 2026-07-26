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
        try:
            ledger = self.db.get_or_create_active_ledger(ledger_date)
        except Exception as e:
            return {
                'error': f'无法获取日期 {ledger_date} 的账本: {str(e)}',
                'winning_number': winning_number,
                'ledger_date': ledger_date
            }

        if not ledger:
            return {
                'error': f'未找到日期 {ledger_date} 的账本',
                'winning_number': winning_number,
                'ledger_date': ledger_date
            }

        # 2. 使用get_ledger_totals获取每个号码的累计金额
        number_amounts = self.db.get_ledger_totals(ledger.id)

        if not number_amounts or all(amount == 0 for amount in number_amounts.values()):
            return {
                'error': f'当天没有任何下注记录',
                'winning_number': winning_number,
                'ledger_date': ledger_date,
                'winning_amount': 0,
                'winning_amount_display': '0.00',
                'odds': self.ODDS,
                'payout_amount': 0,
                'payout_amount_display': '0.00',
                'total_bet': 0,
                'total_bet_display': '0.00',
                'profit_loss': 0,
                'profit_loss_display': '0.00',
                'total_records': 0,
                'number_with_bet': 0
            }

        # 3. 计算中奖号码的累计金额
        winning_amount = number_amounts.get(winning_number, 0)

        # 4. 计算应赔金额 = 中奖号码金额 × 赔率
        payout_amount = winning_amount * self.ODDS

        # 5. 计算今日总下注
        total_bet = sum(number_amounts.values())

        # 6. 计算今日盈亏 = 总下注 - 应赔金额
        profit_loss = total_bet - payout_amount

        # 7. 统计涉及号码数量
        number_with_bet = sum(1 for amount in number_amounts.values() if amount > 0)

        # 8. 构建结算结果
        result = {
            'winning_number': winning_number,
            'ledger_date': ledger_date,
            'ledger_id': ledger.id,
            'winning_amount': winning_amount,
            'winning_amount_display': f'{winning_amount / AMOUNT_MULTIPLIER:.2f}',
            'odds': self.ODDS,
            'payout_amount': payout_amount,
            'payout_amount_display': f'{payout_amount / AMOUNT_MULTIPLIER:.2f}',
            'total_bet': total_bet,
            'total_bet_display': f'{total_bet / AMOUNT_MULTIPLIER:.2f}',
            'profit_loss': profit_loss,
            'profit_loss_display': f'{profit_loss / AMOUNT_MULTIPLIER:.2f}',
            'total_records': number_with_bet,  # 简化：使用涉及号码数
            'number_with_bet': number_with_bet
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
        if 'error' in settlement_result:
            raise ValueError(f"无法保存错误的结算结果: {settlement_result['error']}")

        return self.db.save_settlement(
            ledger_id=settlement_result['ledger_id'],
            settlement_date=settlement_result['ledger_date'],
            winning_number=settlement_result['winning_number'],
            winning_amount=settlement_result['winning_amount'],
            odds=settlement_result['odds'],
            payout_amount=settlement_result['payout_amount'],
            total_bet=settlement_result['total_bet'],
            profit_loss=settlement_result['profit_loss']
        )

    def get_settlement_history(self, limit: int = 30) -> List[Dict]:
        """
        获取结算历史记录

        Args:
            limit: 返回记录数量限制

        Returns:
            结算历史列表
        """
        return self.db.get_settlement_history(limit)
