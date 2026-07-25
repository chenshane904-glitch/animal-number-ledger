"""数据模型"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime


class ParserError(Exception):
    """解析错误"""
    pass


@dataclass
class Instruction:
    """指令模型"""
    source_line: int
    original_text: str
    normalized_text: str
    target_type: str  # 'number' or 'animal'
    targets: List[str]  # 号码列表或动物列表
    amount_integer: int  # 金额（扩大100倍的整数）
    warning: Optional[str] = None
    id: Optional[int] = None
    batch_id: Optional[int] = None


@dataclass
class Allocation:
    """分配模型"""
    number: int
    animal: str
    amount_integer: int
    instruction_id: Optional[int] = None
    id: Optional[int] = None


@dataclass
class Batch:
    """批次模型"""
    raw_input: str
    total_before: int  # 追加前总数（整数）
    total_after: int  # 追加后总数（整数）
    mapping_snapshot: str  # JSON格式的动物映射快照
    created_at: Optional[datetime] = None
    id: Optional[int] = None
    ledger_id: Optional[int] = None
    instructions: List[Instruction] = field(default_factory=list)


@dataclass
class Ledger:
    """账本模型"""
    ledger_date: str  # YYYY-MM-DD格式
    sequence_number: int
    status: str  # 'active' or 'archived'
    created_at: Optional[datetime] = None
    archived_at: Optional[datetime] = None
    settled_total_integer: Optional[int] = None  # 归档结算时固化的总账金额
    id: Optional[int] = None
    batches: List[Batch] = field(default_factory=list)


@dataclass
class CalculationResult:
    """计算结果模型"""
    number_amounts: Dict[int, int]  # {号码: 金额整数}
    total_amount: int  # 总金额（整数）
    non_zero_count: int  # 非零号码数量
    allocations: List[Allocation]  # 所有分配记录
    sources: Dict[int, List[str]]  # {号码: [来源文本列表]}
