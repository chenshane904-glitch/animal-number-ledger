# -*- coding: utf-8 -*-
"""
输入历史记录窗口 - 精简显示+详情折叠
"""

import customtkinter as ctk
from datetime import datetime, timedelta
from typing import List, Dict
from format_utils import format_amount


class HistoryWindow(ctk.CTkToplevel):
    """输入历史记录窗口"""

    def __init__(self, parent, db, current_ledger, current_mode):
        super().__init__(parent)

        self.db = db
        self.current_ledger = current_ledger
        self.current_mode = current_mode

        # 窗口设置
        from play_mode import PlayMode
        mode_name = "号码模式" if current_mode == PlayMode.NUMBER else "平特一肖模式"
        self.title(f"历史记录 - {mode_name}")
        self.geometry("800x650")

        # 计算本周起始日期
        today = datetime.now().date()
        self.week_start = today - timedelta(days=today.weekday())

        self._build_ui()
        self._load_history()

    def _build_ui(self):
        """构建UI"""
        from play_mode import PlayMode

        # 顶部信息栏
        header = ctk.CTkFrame(self, fg_color="#2B2B2B", height=50)
        header.pack(fill='x')
        header.pack_propagate(False)

        mode_name = "号码模式" if self.current_mode == PlayMode.NUMBER else "平特一肖模式"

        ctk.CTkLabel(
            header,
            text=f"● {mode_name}",
            font=("Microsoft YaHei", 14, "bold"),
            text_color="#FFFFFF"
        ).pack(side='left', padx=15)

        if self.current_ledger:
            ctk.CTkLabel(
                header,
                text=f"账本 {self.current_ledger.ledger_date}",
                font=("Arial", 11),
                text_color="#AAAAAA"
            ).pack(side='left', padx=5)

        # 滚动区域
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="#F0F0F0")
        self.scroll_frame.pack(fill='both', expand=True, padx=0, pady=0)

        # 底部按钮
        bottom = ctk.CTkFrame(self, fg_color="#2B2B2B", height=45)
        bottom.pack(fill='x')
        bottom.pack_propagate(False)

        ctk.CTkButton(
            bottom,
            text="刷新",
            command=self._load_history,
            width=80,
            height=30,
            fg_color="#555555",
            hover_color="#666666"
        ).pack(side='left', padx=10, pady=8)

        ctk.CTkButton(
            bottom,
            text="关闭",
            command=self.destroy,
            width=80,
            height=30,
            fg_color="#555555",
            hover_color="#666666"
        ).pack(side='right', padx=10, pady=8)

    def _load_history(self):
        """加载历史记录"""
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        from play_mode import PlayMode
        week_start_str = self.week_start.strftime('%Y-%m-%d')

        if self.current_mode == PlayMode.NUMBER:
            records = self._load_number_history(week_start_str)
            mode_name = "号码模式"
        else:
            records = self._load_flat_zodiac_history(week_start_str)
            mode_name = "平特一肖模式"

        if not records:
            ctk.CTkLabel(
                self.scroll_frame,
                text=f"{mode_name}：本周暂无输入记录",
                font=("Microsoft YaHei", 13),
                text_color="#999999"
            ).pack(pady=80)
            return

        # 按日期分组
        grouped = {}
        for record in records:
            date = record['record_date']
            if date not in grouped:
                grouped[date] = []
            grouped[date].append(record)

        # 按日期倒序显示
        for date in sorted(grouped.keys(), reverse=True):
            self._render_date_group(date, grouped[date])

    def _load_number_history(self, week_start_str: str) -> List[Dict]:
        """加载号码模式历史"""
        return self.db.get_input_history_by_week(week_start_str, play_mode='number')

    def _load_flat_zodiac_history(self, week_start_str: str) -> List[Dict]:
        """加载平特一肖历史"""
        try:
            cursor = self.db.conn.cursor()
            cursor.execute("""
                SELECT b.id, b.ledger_id, b.raw_input, b.entry_total, b.status, b.created_at
                FROM flat_zodiac_batches b
                WHERE b.ledger_id = ? AND DATE(b.created_at) >= ?
                ORDER BY b.created_at DESC
            """, (self.current_ledger.id, week_start_str))

            batches = cursor.fetchall()
            records = []

            for batch in batches:
                cursor.execute("""
                    SELECT zodiac, amount, odds, payout
                    FROM flat_zodiac_items
                    WHERE batch_id = ?
                    ORDER BY id
                """, (batch[0],))

                items = cursor.fetchall()
                created_at = datetime.fromisoformat(batch[5]) if isinstance(batch[5], str) else batch[5]

                records.append({
                    'id': batch[0],
                    'ledger_id': batch[1],
                    'batch_id': batch[0],
                    'record_date': created_at.strftime('%Y-%m-%d'),
                    'created_at': batch[5],
                    'raw_input': batch[2],
                    'entry_total': batch[3],
                    'status': batch[4],
                    'items': [{'zodiac': i[0], 'amount': i[1], 'odds': i[2], 'payout': i[3]} for i in items]
                })

            return records
        except Exception as e:
            print(f"[ERROR] 加载平特一肖历史失败: {e}")
            return []

    def _render_date_group(self, date: str, records: List[Dict]):
        """渲染日期分组"""
        from play_mode import PlayMode

        # 日期标题
        date_obj = datetime.strptime(date, '%Y-%m-%d')
        weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        weekday = weekdays[date_obj.weekday()]

        date_bar = ctk.CTkFrame(self.scroll_frame, fg_color="#DDDDDD", height=32)
        date_bar.pack(fill='x', pady=(10, 5), padx=0)
        date_bar.pack_propagate(False)

        ctk.CTkLabel(
            date_bar,
            text=f"{date_obj.strftime('%Y/%m/%d')} {weekday}",
            font=("Microsoft YaHei", 12, "bold"),
            text_color="#444444"
        ).pack(side='left', padx=15, pady=0)

        # 渲染记录
        for record in records:
            if self.current_mode == PlayMode.NUMBER:
                NumberRecordCard(self.scroll_frame, record)
            else:
                FlatZodiacRecordCard(self.scroll_frame, record)

    def _parse_datetime(self, dt_str):
        """解析日期时间"""
        if isinstance(dt_str, str):
            try:
                return datetime.fromisoformat(dt_str)
            except:
                try:
                    return datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
                except:
                    return datetime.now()
        return dt_str if isinstance(dt_str, datetime) else datetime.now()


class NumberRecordCard:
    """号码模式记录卡片"""

    def __init__(self, parent, record: Dict):
        self.record = record
        self.expanded = False

        # 卡片容器
        self.card = ctk.CTkFrame(parent, fg_color="#FFFFFF", corner_radius=6)
        self.card.pack(fill='x', pady=4, padx=12)

        self._build_ui()

    def _build_ui(self):
        """构建UI"""
        # 内容区
        content = ctk.CTkFrame(self.card, fg_color="transparent")
        content.pack(fill='both', expand=True, padx=12, pady=10)

        # 第一行：时间 + 模式 + 状态
        created_at = self._parse_datetime(self.record['created_at'])
        time_str = created_at.strftime('%H:%M:%S')

        is_active = self.record.get('status') == 'active'
        status_text = "有效" if is_active else "已撤销"
        status_color = "#00AA00" if is_active else "#CC0000"

        line1 = ctk.CTkFrame(content, fg_color="transparent")
        line1.pack(fill='x', pady=(0, 6))

        ctk.CTkLabel(
            line1,
            text=time_str,
            font=("Consolas", 11),
            text_color="#888888"
        ).pack(side='left')

        ctk.CTkLabel(
            line1,
            text="  号码模式  ",
            font=("Microsoft YaHei", 10),
            text_color="#666666"
        ).pack(side='left')

        ctk.CTkLabel(
            line1,
            text=status_text,
            font=("Microsoft YaHei", 10, "bold"),
            text_color=status_color
        ).pack(side='left')

        # 第二行：原始输入（大字体）
        raw_input = self.record.get('raw_input', '无')
        ctk.CTkLabel(
            content,
            text=raw_input,
            font=("Microsoft YaHei", 13, "bold"),
            text_color="#111111",
            anchor='w'
        ).pack(fill='x', pady=(0, 8))

        # 第三行：汇总信息（大字体）
        entry_total = self.record.get('entry_total', 0)
        expanded_items = self.record.get('expanded_items', [])
        count = len([i for i in expanded_items if i.get('amount', 0) > 0])

        summary = ctk.CTkFrame(content, fg_color="transparent")
        summary.pack(fill='x', pady=(0, 8))

        ctk.CTkLabel(
            summary,
            text=f"本次金额：",
            font=("Microsoft YaHei", 11),
            text_color="#666666"
        ).pack(side='left')

        ctk.CTkLabel(
            summary,
            text=format_amount(entry_total),
            font=("Microsoft YaHei", 13, "bold"),
            text_color="#0066CC"
        ).pack(side='left', padx=(2, 15))

        ctk.CTkLabel(
            summary,
            text=f"涉及号码：",
            font=("Microsoft YaHei", 11),
            text_color="#666666"
        ).pack(side='left')

        ctk.CTkLabel(
            summary,
            text=f"{count}个",
            font=("Microsoft YaHei", 11, "bold"),
            text_color="#333333"
        ).pack(side='left')

        # 详情区（折叠）
        self.detail_frame = ctk.CTkFrame(content, fg_color="#F8F8F8", corner_radius=4)

        # 查看详情按钮
        if expanded_items and count > 0:
            self.toggle_btn = ctk.CTkButton(
                content,
                text="▼ 查看展开详情",
                command=self._toggle_detail,
                width=120,
                height=28,
                fg_color="#E0E0E0",
                hover_color="#D0D0D0",
                text_color="#555555",
                font=("Microsoft YaHei", 10)
            )
            self.toggle_btn.pack(anchor='w', pady=(0, 0))

    def _toggle_detail(self):
        """切换详情显示"""
        if self.expanded:
            # 收起
            self.detail_frame.pack_forget()
            self.toggle_btn.configure(text="▼ 查看展开详情")
            self.expanded = False
        else:
            # 展开
            self._render_detail()
            self.detail_frame.pack(fill='x', pady=(8, 8), before=self.toggle_btn)
            self.toggle_btn.configure(text="▲ 收起详情")
            self.expanded = True

    def _render_detail(self):
        """渲染详情"""
        # 清空
        for widget in self.detail_frame.winfo_children():
            widget.destroy()

        expanded_items = self.record.get('expanded_items', [])
        if not expanded_items:
            return

        detail_content = ctk.CTkFrame(self.detail_frame, fg_color="transparent")
        detail_content.pack(fill='both', padx=10, pady=8)

        ctk.CTkLabel(
            detail_content,
            text="展开号码明细：",
            font=("Microsoft YaHei", 10, "bold"),
            text_color="#555555",
            anchor='w'
        ).pack(fill='x', pady=(0, 5))

        # 按金额分组
        amount_groups = {}
        for item in expanded_items:
            amt = item.get('amount', 0)
            if amt > 0:
                if amt not in amount_groups:
                    amount_groups[amt] = []
                amount_groups[amt].append(item.get('number', '??'))

        # 显示每组
        for amt in sorted(amount_groups.keys(), reverse=True):
            numbers = sorted(amount_groups[amt])

            group_frame = ctk.CTkFrame(detail_content, fg_color="transparent")
            group_frame.pack(fill='x', pady=2)

            # 金额标签
            ctk.CTkLabel(
                group_frame,
                text=f"× {format_amount(amt)}：",
                font=("Microsoft YaHei", 10, "bold"),
                text_color="#0066CC",
                width=80,
                anchor='e'
            ).pack(side='left')

            # 号码列表
            nums_text = "  ".join(numbers)
            ctk.CTkLabel(
                group_frame,
                text=nums_text,
                font=("Consolas", 10),
                text_color="#333333",
                anchor='w',
                wraplength=600,
                justify='left'
            ).pack(side='left', padx=(5, 0), fill='x', expand=True)

    def _parse_datetime(self, dt_str):
        """解析日期时间"""
        if isinstance(dt_str, str):
            try:
                return datetime.fromisoformat(dt_str)
            except:
                try:
                    return datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
                except:
                    return datetime.now()
        return dt_str if isinstance(dt_str, datetime) else datetime.now()


class FlatZodiacRecordCard:
    """平特一肖记录卡片"""

    def __init__(self, parent, record: Dict):
        self.record = record

        # 卡片容器
        self.card = ctk.CTkFrame(parent, fg_color="#FFFFFF", corner_radius=6)
        self.card.pack(fill='x', pady=4, padx=12)

        self._build_ui()

    def _build_ui(self):
        """构建UI"""
        # 内容区
        content = ctk.CTkFrame(self.card, fg_color="transparent")
        content.pack(fill='both', expand=True, padx=12, pady=10)

        # 第一行：时间 + 模式 + 状态
        created_at = self._parse_datetime(self.record['created_at'])
        time_str = created_at.strftime('%H:%M:%S')

        is_active = self.record.get('status') == 'active'
        status_text = "有效" if is_active else "已撤销"
        status_color = "#00AA00" if is_active else "#CC0000"

        line1 = ctk.CTkFrame(content, fg_color="transparent")
        line1.pack(fill='x', pady=(0, 6))

        ctk.CTkLabel(
            line1,
            text=time_str,
            font=("Consolas", 11),
            text_color="#888888"
        ).pack(side='left')

        ctk.CTkLabel(
            line1,
            text="  平特一肖  ",
            font=("Microsoft YaHei", 10),
            text_color="#666666"
        ).pack(side='left')

        ctk.CTkLabel(
            line1,
            text=status_text,
            font=("Microsoft YaHei", 10, "bold"),
            text_color=status_color
        ).pack(side='left')

        # 第二行：原始输入（大字体）
        raw_input = self.record.get('raw_input', '无')
        ctk.CTkLabel(
            content,
            text=raw_input,
            font=("Microsoft YaHei", 13, "bold"),
            text_color="#111111",
            anchor='w'
        ).pack(fill='x', pady=(0, 8))

        # 第三行：生肖明细（清晰显示）
        items = self.record.get('items', [])
        if items:
            detail_frame = ctk.CTkFrame(content, fg_color="#F8F8F8", corner_radius=4)
            detail_frame.pack(fill='x', pady=(0, 8))

            detail_content = ctk.CTkFrame(detail_frame, fg_color="transparent")
            detail_content.pack(fill='x', padx=10, pady=6)

            ctk.CTkLabel(
                detail_content,
                text="生肖明细：",
                font=("Microsoft YaHei", 10),
                text_color="#666666",
                anchor='w'
            ).pack(fill='x', pady=(0, 4))

            # 每个生肖单独一行
            for item in items:
                item_line = ctk.CTkFrame(detail_content, fg_color="transparent")
                item_line.pack(fill='x', pady=1)

                ctk.CTkLabel(
                    item_line,
                    text=f"{item['zodiac']}：",
                    font=("Microsoft YaHei", 11, "bold"),
                    text_color="#333333",
                    width=50,
                    anchor='e'
                ).pack(side='left')

                ctk.CTkLabel(
                    item_line,
                    text=format_amount(item['amount']),
                    font=("Microsoft YaHei", 11),
                    text_color="#0066CC",
                    anchor='w'
                ).pack(side='left', padx=(5, 0))

        # 第四行：汇总信息（大字体）
        entry_total = self.record.get('entry_total', 0)
        count = len(items)

        summary = ctk.CTkFrame(content, fg_color="transparent")
        summary.pack(fill='x')

        ctk.CTkLabel(
            summary,
            text=f"本次金额：",
            font=("Microsoft YaHei", 11),
            text_color="#666666"
        ).pack(side='left')

        ctk.CTkLabel(
            summary,
            text=format_amount(entry_total),
            font=("Microsoft YaHei", 13, "bold"),
            text_color="#0066CC"
        ).pack(side='left', padx=(2, 15))

        ctk.CTkLabel(
            summary,
            text=f"涉及生肖：",
            font=("Microsoft YaHei", 11),
            text_color="#666666"
        ).pack(side='left')

        ctk.CTkLabel(
            summary,
            text=f"{count}个",
            font=("Microsoft YaHei", 11, "bold"),
            text_color="#333333"
        ).pack(side='left')

    def _parse_datetime(self, dt_str):
        """解析日期时间"""
        if isinstance(dt_str, str):
            try:
                return datetime.fromisoformat(dt_str)
            except:
                try:
                    return datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
                except:
                    return datetime.now()
        return dt_str if isinstance(dt_str, datetime) else datetime.now()
