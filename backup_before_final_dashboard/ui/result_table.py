"""结果表格组件 - 使用Canvas绘制完整表格"""
import tkinter as tk
from tkinter import ttk
from constants import MIN_NUMBER, MAX_NUMBER, AMOUNT_MULTIPLIER


class ResultTable(ttk.Frame):
    """结果表格 - 专业数据展示"""

    def __init__(self, parent):
        super().__init__(parent)

        self.current_totals = {}
        self.total_bet = 0
        self.row_height = 31  # 固定行高

        # 列宽配置（百分比）
        self.col_widths = {
            'number': 0.14,   # 14%
            'amount': 0.23,   # 23%
            'payout': 0.29,   # 29%
            'profit': 0.34    # 34%
        }

        self._build_table()

    def _build_table(self):
        """构建表格"""
        # 创建容器
        container = tk.Frame(self, bg="#FFFFFF")
        container.pack(fill='both', expand=True)

        # 表头Frame（固定在顶部）
        header_frame = tk.Frame(container, bg="#003366", height=35)
        header_frame.pack(fill='x', side='top')
        header_frame.pack_propagate(False)

        # 创建表头Canvas
        self.header_canvas = tk.Canvas(
            header_frame,
            bg="#003366",
            highlightthickness=0,
            height=35
        )
        self.header_canvas.pack(fill='both', expand=True)

        # 数据区域容器
        data_container = tk.Frame(container, bg="#FFFFFF")
        data_container.pack(fill='both', expand=True, side='top')

        # 创建数据Canvas（可滚动）
        self.data_canvas = tk.Canvas(
            data_container,
            bg="#FFFFFF",
            highlightthickness=0
        )
        self.data_canvas.pack(side='left', fill='both', expand=True)

        # 创建滚动条
        scrollbar = tk.Scrollbar(
            data_container,
            orient='vertical',
            command=self.data_canvas.yview
        )
        scrollbar.pack(side='right', fill='y')

        self.data_canvas.configure(yscrollcommand=scrollbar.set)

        # 绑定鼠标滚轮
        self.data_canvas.bind('<MouseWheel>', self._on_mousewheel)

        # 绑定resize事件以重绘表头
        self.header_canvas.bind('<Configure>', self._on_resize)

        print("Canvas表格已创建")

    def _on_mousewheel(self, event):
        """鼠标滚轮事件"""
        delta = -1 if event.delta > 0 else 1
        self.data_canvas.yview_scroll(delta, "units")

    def _on_resize(self, event):
        """窗口大小改变时重绘表头"""
        self._draw_header()

    def _draw_header(self):
        """绘制表头"""
        self.header_canvas.delete("all")

        width = self.header_canvas.winfo_width()
        if width <= 1:
            width = 550  # 默认宽度

        # 计算列位置
        col_x = {
            'number': 0,
            'amount': width * self.col_widths['number'],
            'payout': width * (self.col_widths['number'] + self.col_widths['amount']),
            'profit': width * (self.col_widths['number'] + self.col_widths['amount'] + self.col_widths['payout'])
        }

        col_w = {
            'number': width * self.col_widths['number'],
            'amount': width * self.col_widths['amount'],
            'payout': width * self.col_widths['payout'],
            'profit': width * self.col_widths['profit']
        }

        # 绘制表头文字
        self.header_canvas.create_text(
            col_x['number'] + col_w['number'] / 2, 17,
            text="号码",
            fill="#FFFFFF",
            font=("Microsoft YaHei", 12, "bold")
        )

        self.header_canvas.create_text(
            col_x['amount'] + col_w['amount'] - 10, 17,
            text="金额",
            fill="#FFFFFF",
            font=("Microsoft YaHei", 12, "bold"),
            anchor='e'
        )

        self.header_canvas.create_text(
            col_x['payout'] + col_w['payout'] - 10, 17,
            text="赔付（金额×47）",
            fill="#FFFFFF",
            font=("Microsoft YaHei", 12, "bold"),
            anchor='e'
        )

        self.header_canvas.create_text(
            col_x['profit'] + col_w['profit'] - 10, 17,
            text="盈利（总下注－赔付）",
            fill="#FFFFFF",
            font=("Microsoft YaHei", 12, "bold"),
            anchor='e'
        )

    def update_data(self, totals, total_bet_int):
        """
        更新表格数据

        参数:
            totals: {号码: 金额整数} 字典
            total_bet_int: 总下注金额整数
        """
        self.current_totals = totals
        self.total_bet = total_bet_int / AMOUNT_MULTIPLIER

        # 清空现有数据
        self.data_canvas.delete("all")

        # 排序：金额从大到小，金额相同按号码从小到大
        sorted_numbers = []
        for num in range(MIN_NUMBER, MAX_NUMBER + 1):
            amount_int = totals.get(num, 0)
            sorted_numbers.append((num, amount_int))

        sorted_numbers.sort(key=lambda x: (-x[1], x[0]))

        # 获取Canvas宽度
        width = self.data_canvas.winfo_width()
        if width <= 1:
            width = 550

        # 计算列位置
        col_x = {
            'number': 0,
            'amount': width * self.col_widths['number'],
            'payout': width * (self.col_widths['number'] + self.col_widths['amount']),
            'profit': width * (self.col_widths['number'] + self.col_widths['amount'] + self.col_widths['payout'])
        }

        col_w = {
            'number': width * self.col_widths['number'],
            'amount': width * self.col_widths['amount'],
            'payout': width * self.col_widths['payout'],
            'profit': width * self.col_widths['profit']
        }

        # 绘制每一行
        for idx, (num, amount_int) in enumerate(sorted_numbers):
            rank = idx + 1
            y1 = idx * self.row_height
            y2 = y1 + self.row_height
            y_center = y1 + self.row_height // 2

            amount = amount_int / AMOUNT_MULTIPLIER
            payout = amount * 47
            profit = self.total_bet - payout

            # 根据排名确定背景和文字颜色
            if rank <= 10:
                bg_color = "#FFE0E0"  # 浅红
                num_color = "#B71C1C"  # 深红
            elif rank <= 20:
                bg_color = "#DDEEFF"  # 浅蓝
                num_color = "#0D47A1"  # 深蓝
            elif rank <= 30:
                bg_color = "#FFF0D5"  # 浅橙
                num_color = "#E65100"  # 深橙
            elif rank <= 40:
                bg_color = "#E1F5E5"  # 浅绿
                num_color = "#1B5E20"  # 深绿
            else:
                bg_color = "#F0F0F0"  # 浅灰
                num_color = "#616161"  # 深灰

            # 绘制横向长方条背景
            self.data_canvas.create_rectangle(
                0, y1, width, y2,
                fill=bg_color,
                outline=""
            )

            # 绘制分隔线
            if idx > 0:
                self.data_canvas.create_line(
                    0, y1, width, y1,
                    fill="#E0E0E0",
                    width=1
                )

            # 绘制号码（居中，使用排名颜色，加粗）
            self.data_canvas.create_text(
                col_x['number'] + col_w['number'] / 2, y_center,
                text=f"{num:02d}",
                fill=num_color,
                font=("Microsoft YaHei", 13, "bold")
            )

            # 绘制金额（右对齐，深黑色）
            self.data_canvas.create_text(
                col_x['amount'] + col_w['amount'] - 10, y_center,
                text=f"{amount:,.2f}",
                fill="#111111",
                font=("Arial", 12),
                anchor='e'
            )

            # 绘制赔付（右对齐，深黑色）
            self.data_canvas.create_text(
                col_x['payout'] + col_w['payout'] - 10, y_center,
                text=f"{payout:,.2f}",
                fill="#111111",
                font=("Arial", 12),
                anchor='e'
            )

            # 绘制盈利（右对齐，根据正负显示颜色）
            if profit >= 0:
                profit_text = f"+{profit:,.2f}"
                profit_color = "#1B5E20"  # 深绿
            else:
                profit_text = f"{profit:,.2f}"
                profit_color = "#B71C1C"  # 深红

            self.data_canvas.create_text(
                col_x['profit'] + col_w['profit'] - 10, y_center,
                text=profit_text,
                fill=profit_color,
                font=("Arial", 12, "bold"),
                anchor='e'
            )

        # 设置滚动区域
        total_height = len(sorted_numbers) * self.row_height
        self.data_canvas.configure(scrollregion=(0, 0, width, total_height))

        # 绘制表头
        self._draw_header()

        print(f"已绘制 {len(sorted_numbers)} 行横向长方条")
        print("前10行排名颜色：")
        for idx, (num, amount_int) in enumerate(sorted_numbers[:10]):
            rank = idx + 1
            amount = amount_int / AMOUNT_MULTIPLIER
            if rank <= 10:
                color_name = "浅红背景+深红号码"
            elif rank <= 20:
                color_name = "浅蓝背景+深蓝号码"
            elif rank <= 30:
                color_name = "浅橙背景+深橙号码"
            elif rank <= 40:
                color_name = "浅绿背景+深绿号码"
            else:
                color_name = "浅灰背景+深灰号码"
            print(f"  第{rank:02d}名 | {num:02d}号 | {amount:>10,.2f} | {color_name}")

    def clear(self):
        """清空表格"""
        self.data_canvas.delete("all")
        self.current_totals = {}
        self.total_bet = 0

    def scroll_to_top(self):
        """滚动到顶部"""
        self.data_canvas.yview_moveto(0)



