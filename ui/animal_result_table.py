# -*- coding: utf-8 -*-
"""
平特模式结果表格组件 - 显示12生肖
"""

import tkinter as tk
from constants import AMOUNT_MULTIPLIER


class AnimalResultTable(tk.Frame):
    """平特模式结果表格 - 12生肖"""

    def __init__(self, parent, odds: float):
        super().__init__(parent, bg="#FFFFFF")

        self.odds = odds
        self.animals = ["鼠", "牛", "虎", "兔", "龙", "蛇", "马", "羊", "猴", "鸡", "狗", "猪"]
        self.animal_amounts = {animal: 0 for animal in self.animals}
        self.total_amount = 0
        self.row_height = 32  # 行高

        # 列宽配置（百分比）
        self.col_widths = {
            'animal': 0.16,   # 16%
            'amount': 0.24,   # 24%
            'odds': 0.15,     # 15%
            'payout': 0.225,  # 22.5%
            'profit': 0.225   # 22.5%
        }

        self._build_table()

    def _build_table(self):
        """构建表格"""
        # 表头Frame
        header_frame = tk.Frame(self, bg="#1A237E", height=36)
        header_frame.pack(fill='x', side='top')
        header_frame.pack_propagate(False)

        # 表头Canvas
        self.header_canvas = tk.Canvas(
            header_frame,
            bg="#1A237E",
            height=36,
            highlightthickness=0
        )
        self.header_canvas.pack(fill='both', expand=True)

        # 数据区域
        data_container = tk.Frame(self, bg="#FFFFFF")
        data_container.pack(fill='both', expand=True, side='top')

        # 滚动条
        scrollbar = tk.Scrollbar(data_container, orient='vertical')
        scrollbar.pack(side='right', fill='y')

        # 数据Canvas
        self.data_canvas = tk.Canvas(
            data_container,
            bg="#FFFFFF",
            yscrollcommand=scrollbar.set,
            highlightthickness=0
        )
        self.data_canvas.pack(side='left', fill='both', expand=True)

        scrollbar.config(command=self.data_canvas.yview)

        # 绑定事件
        self.data_canvas.bind('<Configure>', self._on_resize)
        self.data_canvas.bind_all('<MouseWheel>', self._on_mousewheel)

        # 绘制表头
        self.after(100, self._draw_header)

    def _on_mousewheel(self, event):
        """鼠标滚轮事件"""
        delta = -1 if event.delta > 0 else 1
        self.data_canvas.yview_scroll(delta, "units")

    def _on_resize(self, event):
        """窗口大小改变时重绘"""
        self.redraw()

    def _draw_header(self):
        """绘制表头"""
        self.header_canvas.delete("all")

        width = self.header_canvas.winfo_width()
        if width <= 1:
            width = 600

        # 计算列位置
        col_x = self._calculate_column_x(width)
        col_w = self._calculate_column_width(width)

        # 绘制表头文字
        headers = [
            ('animal', "生肖"),
            ('amount', "金额"),
            ('odds', "赔率"),
            ('payout', "赔付"),
            ('profit', "盈利")
        ]

        for col_key, text in headers:
            x = col_x[col_key] + col_w[col_key] / 2
            self.header_canvas.create_text(
                x, 18,
                text=text,
                fill="#FFFFFF",
                font=("Microsoft YaHei", 12, "bold")
            )

    def _calculate_column_x(self, width):
        """计算列起始位置"""
        x = {}
        current_x = 0
        for key in ['animal', 'amount', 'odds', 'payout', 'profit']:
            x[key] = current_x
            current_x += width * self.col_widths[key]
        return x

    def _calculate_column_width(self, width):
        """计算列宽度"""
        return {key: width * w for key, w in self.col_widths.items()}

    def update_data(self, animal_amounts: dict, total_amount: int):
        """
        更新表格数据

        Args:
            animal_amounts: {生肖: 金额整数}
            total_amount: 总金额整数
        """
        self.animal_amounts = animal_amounts
        self.total_amount = total_amount
        self.redraw()

    def redraw(self):
        """重绘数据区"""
        self.data_canvas.delete("all")

        width = self.data_canvas.winfo_width()
        if width <= 1:
            width = 600

        # 计算列位置和宽度
        col_x = self._calculate_column_x(width)
        col_w = self._calculate_column_width(width)

        # 绘制12个生肖行
        y = 0
        for i, animal in enumerate(self.animals):
            # 背景色交替
            bg_color = "#FAFAFA" if i % 2 == 0 else "#FFFFFF"

            # 绘制背景
            self.data_canvas.create_rectangle(
                0, y, width, y + self.row_height,
                fill=bg_color,
                outline=""
            )

            # 获取数据
            amount_int = self.animal_amounts.get(animal, 0)
            amount = amount_int / AMOUNT_MULTIPLIER
            payout = int(amount_int * self.odds) / AMOUNT_MULTIPLIER
            profit = (int(amount_int * self.odds) - self.total_amount) / AMOUNT_MULTIPLIER

            # 生肖名（居中）
            self.data_canvas.create_text(
                col_x['animal'] + col_w['animal'] / 2,
                y + self.row_height / 2,
                text=animal,
                fill="#333333",
                font=("Microsoft YaHei", 11, "bold")
            )

            # 金额（右对齐）
            amount_color = "#0066CC" if amount_int > 0 else "#999999"
            self.data_canvas.create_text(
                col_x['amount'] + col_w['amount'] - 10,
                y + self.row_height / 2,
                text=f"{amount:,.2f}" if amount_int > 0 else "--",
                fill=amount_color,
                font=("Consolas", 11),
                anchor='e'
            )

            # 赔率（居中）
            self.data_canvas.create_text(
                col_x['odds'] + col_w['odds'] / 2,
                y + self.row_height / 2,
                text=f"{self.odds:.2f}",
                fill="#666666",
                font=("Consolas", 10)
            )

            # 赔付（右对齐）
            if amount_int > 0:
                self.data_canvas.create_text(
                    col_x['payout'] + col_w['payout'] - 10,
                    y + self.row_height / 2,
                    text=f"{payout:,.2f}",
                    fill="#00AA00",
                    font=("Consolas", 11),
                    anchor='e'
                )

            # 盈利（右对齐，根据正负显示颜色）
            if amount_int > 0:
                profit_color = "#DD0000" if profit >= 0 else "#006600"
                profit_text = f"+{profit:,.2f}" if profit >= 0 else f"{profit:,.2f}"
                self.data_canvas.create_text(
                    col_x['profit'] + col_w['profit'] - 10,
                    y + self.row_height / 2,
                    text=profit_text,
                    fill=profit_color,
                    font=("Consolas", 11, "bold"),
                    anchor='e'
                )

            y += self.row_height

        # 更新滚动区域
        self.data_canvas.config(scrollregion=(0, 0, width, y))

    def clear(self):
        """清空表格数据"""
        self.animal_amounts = {animal: 0 for animal in self.animals}
        self.total_amount = 0
        self.redraw()
