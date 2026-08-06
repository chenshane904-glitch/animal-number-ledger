# -*- coding: utf-8 -*-
"""
平特一肖独立服务
完全独立的数据流程，不依赖号码模式
"""

import sqlite3
import re
from typing import List, Dict, Tuple, Optional
from constants import AMOUNT_MULTIPLIER


class FlatZodiacEntry:
    """平特一肖单条记录"""
    def __init__(self, zodiac: str, amount: float):
        self.zodiac = zodiac
        self.amount = amount  # 元（浮点数）
        self.amount_int = int(amount * AMOUNT_MULTIPLIER)  # 分（整数）


class FlatZodiacService:
    """平特一肖独立服务"""

    ZODIACS = ['鼠', '牛', '虎', '兔', '龙', '蛇', '马', '羊', '猴', '鸡', '狗', '猪']
    DEFAULT_ODDS = 1.0

    def __init__(self, db_conn: sqlite3.Connection):
        """
        初始化服务

        Args:
            db_conn: 数据库连接
        """
        self.conn = db_conn

    def parse_input(self, text: str) -> List[FlatZodiacEntry]:
        """
        解析平特一肖输入

        Args:
            text: 原始输入文本

        Returns:
            解析后的记录列表

        Raises:
            ValueError: 解析失败
        """
        from flat_zodiac_parser import FlatZodiacParser
        parser = FlatZodiacParser()
        return parser.parse(text)

    def add_batch(self, ledger_id: int, raw_input: str, entries: List[FlatZodiacEntry]) -> int:
        """
        添加一批平特一肖记录

        Args:
            ledger_id: 账本ID
            raw_input: 原始输入文本
            entries: 解析后的记录列表

        Returns:
            batch_id

        Raises:
            Exception: 数据库操作失败
        """
        cursor = self.conn.cursor()

        try:
            # 计算本次总额（元）
            entry_total = sum(e.amount for e in entries)

            # 插入批次
            cursor.execute("""
                INSERT INTO flat_zodiac_batches
                (ledger_id, raw_input, entry_total, status)
                VALUES (?, ?, ?, 'active')
            """, (ledger_id, raw_input, entry_total))

            batch_id = cursor.lastrowid

            # 插入明细
            for entry in entries:
                payout = entry.amount * self.DEFAULT_ODDS
                cursor.execute("""
                    INSERT INTO flat_zodiac_items
                    (batch_id, zodiac, amount, odds, payout)
                    VALUES (?, ?, ?, ?, ?)
                """, (batch_id, entry.zodiac, entry.amount, self.DEFAULT_ODDS, payout))

            # 提交事务
            self.conn.commit()

            return batch_id

        except Exception as e:
            self.conn.rollback()
            raise Exception(f"添加批次失败: {e}")

    def get_summary(self, ledger_id: int) -> Dict:
        """
        获取平特一肖汇总数据

        Args:
            ledger_id: 账本ID

        Returns:
            {
                'total_bet': 总下注（浮点数，元）,
                'non_zero_count': 非零生肖数量,
                'max_zodiac': 最高下注生肖,
                'max_amount': 最高金额（浮点数，元）,
                'zodiac_amounts': {生肖: 金额浮点数（元）}
            }
        """
        cursor = self.conn.cursor()

        # 查询所有活跃记录
        cursor.execute("""
            SELECT i.zodiac, SUM(i.amount) as total
            FROM flat_zodiac_items i
            JOIN flat_zodiac_batches b ON i.batch_id = b.id
            WHERE b.ledger_id = ? AND b.status = 'active'
            GROUP BY i.zodiac
        """, (ledger_id,))

        zodiac_amounts = {z: 0 for z in self.ZODIACS}
        for row in cursor.fetchall():
            zodiac_amounts[row[0]] = row[1]

        # 计算统计
        total_bet = sum(zodiac_amounts.values())
        non_zero_count = sum(1 for amt in zodiac_amounts.values() if amt > 0)

        max_zodiac = '--'
        max_amount = 0
        for zodiac, amount in zodiac_amounts.items():
            if amount > max_amount:
                max_amount = amount
                max_zodiac = zodiac

        return {
            'total_bet': total_bet,
            'non_zero_count': non_zero_count,
            'max_zodiac': max_zodiac,
            'max_amount': max_amount,
            'zodiac_amounts': zodiac_amounts
        }
