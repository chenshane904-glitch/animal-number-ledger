# -*- coding: utf-8 -*-
"""
输入历史记录窗口
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog
from datetime import datetime, timedelta
from typing import List, Dict
import csv
from constants import AMOUNT_MULTIPLIER


class HistoryWindow(ctk.CTkToplevel):
    """输入历史记录窗口"""

    def __init__(self, parent, db, current_ledger):
        super().__init__(parent)

        self.db = db
        self.current_ledger = current_ledger

        # 调试输出
        import os
        print(f"[HISTORY WINDOW] 数据库路径: {os.path.abspath(db.db_path)}")
        print(f"[HISTORY WINDOW] 当前账本ID: {current_ledger.id if current_ledger else 'None'}")
        print(f"[HISTORY WINDOW] 当前账本日期: {current_ledger.ledger_date if current_ledger else 'None'}")

        # 窗口设置
        self.title("输入历史记录")
        self.geometry("900x700")

        # 计算当前周起止日期
        today = datetime.now()
        self.week_start = self._get_week_start(today)
        week_end = self.week_start + timedelta(days=6)

        # 设置UI
        self._setup_ui()

        # 加载历史记录
        self._load_history()

    def _get_week_start(self, date: datetime) -> datetime:
        """获取指定日期所在周的周一"""
        # weekday(): 0=周一, 6=周日
        days_since_monday = date.weekday()
        week_start = date - timedelta(days=days_since_monday)
        return week_start.replace(hour=0, minute=0, second=0, microsecond=0)

    def _setup_ui(self):
        """设置UI"""
        # 顶部信息栏
        header_frame = ctk.CTkFrame(self)
        header_frame.pack(fill='x', padx=10, pady=10)

        ctk.CTkLabel(
            header_frame,
            text="输入历史记录",
            font=("Arial", 16, "bold")
        ).pack(side='left', padx=10)

        # 周信息
        week_end = self.week_start + timedelta(days=6)
        week_str = f"{self.week_start.strftime('%Y-%m-%d')} 至 {week_end.strftime('%Y-%m-%d')}"
        ctk.CTkLabel(
            header_frame,
            text=f"本周：{week_str}",
            font=("Arial", 12)
        ).pack(side='left', padx=20)

        # 账本信息
        if self.current_ledger:
            ctk.CTkLabel(
                header_frame,
                text=f"账本：{self.current_ledger.ledger_date}",
                font=("Arial", 12)
            ).pack(side='left', padx=10)

        # 中间：滚动区域
        self.scroll_frame = ctk.CTkScrollableFrame(self)
        self.scroll_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # 底部按钮栏
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(fill='x', padx=10, pady=10)

        ctk.CTkButton(
            button_frame,
            text="刷新",
            command=self._load_history,
            width=100,
            height=32
        ).pack(side='left', padx=5)

        ctk.CTkButton(
            button_frame,
            text="导出本周记录",
            command=self._export_csv,
            width=120,
            height=32
        ).pack(side='left', padx=5)

        ctk.CTkButton(
            button_frame,
            text="关闭",
            command=self.destroy,
            width=100,
            height=32
        ).pack(side='right', padx=5)

    def _load_history(self):
        """加载历史记录"""
        # 清空现有内容
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        # 获取本周历史记录
        week_start_str = self.week_start.strftime('%Y-%m-%d')

        print(f"[HISTORY QUERY] 查询周起始: {week_start_str}")
        print(f"[HISTORY QUERY] week_start对象: {self.week_start}")
        print(f"[HISTORY QUERY] 当前账本ID: {self.current_ledger.id if self.current_ledger else 'None'}")

        # 直接测试SQL
        import sqlite3
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT week_start, COUNT(*) FROM input_history GROUP BY week_start")
        print(f"[HISTORY QUERY] 数据库中的week_start值:")
        for row in cursor.fetchall():
            print(f"  week_start='{row[0]}', count={row[1]}")

        records = self.db.get_input_history_by_week(week_start_str)

        print(f"[HISTORY QUERY] 返回记录数: {len(records)}")
        if len(records) > 0:
            print(f"[HISTORY QUERY] 第一条: {records[0]['raw_input']}")
        else:
            print(f"[HISTORY QUERY] 查询SQL: WHERE week_start = '{week_start_str}'")

        if not records:
            ctk.CTkLabel(
                self.scroll_frame,
                text="本周暂无输入记录",
                font=("Arial", 14),
                text_color="#999999"
            ).pack(pady=50)
            return

        # 按日期分组
        grouped = {}
        for record in records:
            date = record['record_date']
            if date not in grouped:
                grouped[date] = []
            grouped[date].append(record)

        # 按日期倒序显示
        sorted_dates = sorted(grouped.keys(), reverse=True)

        for date in sorted_dates:
            # 日期标题 - 简洁样式
            date_obj = datetime.strptime(date, '%Y-%m-%d')
            weekday_names = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
            weekday = weekday_names[date_obj.weekday()]

            date_header = ctk.CTkFrame(self.scroll_frame, fg_color="#F5F5F5", corner_radius=0)
            date_header.pack(fill='x', pady=(5, 0))

            ctk.CTkLabel(
                date_header,
                text=f"{date}  {weekday}",
                font=("Arial", 12, "bold"),
                text_color="#333333",
                anchor='w'
            ).pack(side='left', padx=15, pady=8)

            # 当天的记录
            for record in grouped[date]:
                self._create_record_item(record)

    def _create_record_item(self, record: Dict):
        """创建单条记录项 - 连续流水式"""
        from constants import AMOUNT_MULTIPLIER

        # 内容容器 - 白色背景
        content_frame = ctk.CTkFrame(self.scroll_frame, fg_color="#FFFFFF", corner_radius=0)
        content_frame.pack(fill='x', padx=15, pady=8)

        # 解析时间
        created_at_str = record['created_at']
        if isinstance(created_at_str, str):
            try:
                created_at = datetime.fromisoformat(created_at_str)
            except:
                try:
                    created_at = datetime.strptime(created_at_str, '%Y-%m-%d %H:%M:%S')
                except:
                    created_at = datetime.now()
        else:
            created_at = datetime.now()

        time_str = created_at.strftime('%Y/%m/%d %H:%M:%S')

        # 第一行：时间（撤销状态标记）
        time_color = "#666666"
        time_display = time_str
        if record.get('status') == 'undone':
            time_display = f"{time_str} [已撤销]"
            time_color = "#FF0000"

        ctk.CTkLabel(
            content_frame,
            text=time_display,
            font=("Arial", 11),
            text_color=time_color,
            anchor='w'
        ).pack(fill='x', pady=(0, 3))

        # 第二行：原始输入
        ctk.CTkLabel(
            content_frame,
            text=record['raw_input'],
            font=("Arial", 12, "bold"),
            text_color="#333333",
            anchor='w'
        ).pack(fill='x', pady=(0, 3))

        # 第三行：展开号码
        expanded_items = record.get('expanded_items', [])
        if expanded_items:
            # 格式化号码列表
            number_parts = []
            amounts_set = set()

            for item in expanded_items[:20]:  # 最多显示20个
                number_parts.append(item['number'])
                amounts_set.add(item['amount'])

            numbers_text = "、".join(number_parts)
            if len(expanded_items) > 20:
                numbers_text += f" 等{len(expanded_items)}个"

            # 如果所有金额相同，添加"各XX"
            if len(amounts_set) == 1:
                amount = list(amounts_set)[0]
                numbers_text += f" 各{amount:.0f}"

            ctk.CTkLabel(
                content_frame,
                text=numbers_text,
                font=("Arial", 11),
                text_color="#666666",
                anchor='w',
                wraplength=850
            ).pack(fill='x', pady=(0, 3))

        # 第四行：本次总和
        entry_total = record['entry_total'] / AMOUNT_MULTIPLIER
        total_text = f"【本次总和：{entry_total:.2f}】"

        ctk.CTkLabel(
            content_frame,
            text=total_text,
            font=("Arial", 11, "bold"),
            text_color="#0066CC",
            anchor='w'
        ).pack(fill='x')

        # 分隔线
        separator = ctk.CTkFrame(self.scroll_frame, fg_color="#E0E0E0", height=1)
        separator.pack(fill='x', pady=0)

    def _show_detail(self, record: Dict):
        """显示记录详情"""
        detail_window = ctk.CTkToplevel(self)
        detail_window.title("记录详情")
        detail_window.geometry("600x500")

        # 详情内容
        detail_frame = ctk.CTkScrollableFrame(detail_window)
        detail_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # 基本信息
        ctk.CTkLabel(
            detail_frame,
            text=f"时间：{record['created_at']}",
            font=("Arial", 12),
            anchor='w'
        ).pack(fill='x', pady=2)

        ctk.CTkLabel(
            detail_frame,
            text=f"状态：{record['status']}",
            font=("Arial", 12),
            anchor='w'
        ).pack(fill='x', pady=2)

        ctk.CTkLabel(
            detail_frame,
            text=f"\n原始输入：",
            font=("Arial", 12, "bold"),
            anchor='w'
        ).pack(fill='x', pady=5)

        ctk.CTkLabel(
            detail_frame,
            text=record['raw_input'],
            font=("Arial", 11),
            anchor='w',
            wraplength=550
        ).pack(fill='x', padx=10)

        ctk.CTkLabel(
            detail_frame,
            text=f"\n解析结果：",
            font=("Arial", 12, "bold"),
            anchor='w'
        ).pack(fill='x', pady=5)

        ctk.CTkLabel(
            detail_frame,
            text=record['parsed_summary'],
            font=("Arial", 11),
            anchor='w',
            wraplength=550
        ).pack(fill='x', padx=10)

        # 展开号码
        ctk.CTkLabel(
            detail_frame,
            text=f"\n展开号码及金额：",
            font=("Arial", 12, "bold"),
            anchor='w'
        ).pack(fill='x', pady=5)

        items = record['expanded_items']
        if items:
            for item in items[:20]:  # 最多显示20个
                number = item['number']
                amount = item['amount']
                ctk.CTkLabel(
                    detail_frame,
                    text=f"  {number}: {amount:.2f}",
                    font=("Arial", 11),
                    anchor='w'
                ).pack(fill='x', padx=10)

            if len(items) > 20:
                ctk.CTkLabel(
                    detail_frame,
                    text=f"  ... 共{len(items)}个号码",
                    font=("Arial", 11),
                    text_color="#999999",
                    anchor='w'
                ).pack(fill='x', padx=10)

        # 汇总
        entry_total = record['entry_total'] / AMOUNT_MULTIPLIER
        daily_total = record['daily_total_after'] / AMOUNT_MULTIPLIER

        ctk.CTkLabel(
            detail_frame,
            text=f"\n本次总金额：{entry_total:,.2f}",
            font=("Arial", 12, "bold"),
            anchor='w'
        ).pack(fill='x', pady=5)

        ctk.CTkLabel(
            detail_frame,
            text=f"操作后今日累计：{daily_total:,.2f}",
            font=("Arial", 12, "bold"),
            anchor='w'
        ).pack(fill='x', pady=2)

        # 关闭按钮
        ctk.CTkButton(
            detail_window,
            text="关闭",
            command=detail_window.destroy,
            width=100,
            height=32
        ).pack(pady=10)

    def _export_csv(self):
        """导出本周记录为CSV"""
        week_start_str = self.week_start.strftime('%Y-%m-%d')
        week_end = self.week_start + timedelta(days=6)
        week_end_str = week_end.strftime('%Y-%m-%d')

        # 获取记录
        records = self.db.get_input_history_by_week(week_start_str)

        if not records:
            messagebox.showinfo("提示", "本周暂无记录可导出")
            return

        # 选择保存路径
        filename = f"澳门版_下注历史_{week_start_str}至{week_end_str}.csv"
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV文件", "*.csv")],
            initialfile=filename
        )

        if not filepath:
            return

        try:
            with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)

                # 表头
                writer.writerow([
                    '日期', '时间', '账本编号', '原始输入', '解析结果',
                    '展开号码数', '本次金额', '今日累计', '状态'
                ])

                # 数据行
                for record in records:
                    date = record['record_date']
                    time = datetime.fromisoformat(record['created_at']).strftime('%H:%M:%S')
                    ledger_id = record['ledger_id']
                    raw_input = record['raw_input']
                    parsed = record['parsed_summary']
                    item_count = len(record['expanded_items'])
                    entry_total = record['entry_total'] / AMOUNT_MULTIPLIER
                    daily_total = record['daily_total_after'] / AMOUNT_MULTIPLIER
                    status = '已撤销' if record['status'] == 'undone' else '有效'

                    writer.writerow([
                        date, time, ledger_id, raw_input, parsed,
                        item_count, f"{entry_total:.2f}", f"{daily_total:.2f}", status
                    ])

            messagebox.showinfo("成功", f"已导出 {len(records)} 条记录到：\n{filepath}")

        except Exception as e:
            messagebox.showerror("错误", f"导出失败：{e}")
