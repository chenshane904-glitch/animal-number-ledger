"""每日归档模块"""
from datetime import datetime
from typing import Callable, List, Tuple
from database import Database


class DailyRollover:
    """每日归档管理器"""

    def __init__(self, db: Database, get_current_time: Callable[[], datetime] = None):
        """
        初始化归档管理器

        Args:
            db: 数据库实例
            get_current_time: 获取当前时间的函数（用于测试）
        """
        self.db = db
        self.get_current_time = get_current_time or datetime.now
        self.last_check_date = None
        self.last_settlement_total = None
        self.last_settled_ledger_date = None

    def get_current_date_str(self) -> str:
        """获取当前日期字符串"""
        return self.get_current_time().strftime('%Y-%m-%d')

    def initialize(self) -> List[Tuple[int, str, int]]:
        """启动时结算所有跨日遗留的活动账本。"""
        current_date = self.get_current_date_str()
        settlements = self.db.archive_stale_active_ledgers(current_date)
        self.last_check_date = current_date

        if settlements:
            _, ledger_date, total = settlements[-1]
            self.last_settled_ledger_date = ledger_date
            self.last_settlement_total = total

        return settlements

    def check_and_rollover(self, current_ledger_id: int) -> tuple[bool, str]:
        """
        检查是否需要归档并执行

        Args:
            current_ledger_id: 当前账本ID

        Returns:
            (是否发生了归档, 新日期)
        """
        current_date = self.get_current_date_str()

        # 首次检查
        if self.last_check_date is None:
            self.last_check_date = current_date
            return False, current_date

        # 日期未变化
        if current_date == self.last_check_date:
            return False, current_date

        # 日期变化，执行归档
        settled_ledger = self.db.get_ledger(current_ledger_id)
        total = self.db.archive_ledger(current_ledger_id)
        self.last_settlement_total = total
        self.last_settled_ledger_date = (
            settled_ledger.ledger_date if settled_ledger else self.last_check_date
        )
        self.last_check_date = current_date

        return True, current_date
