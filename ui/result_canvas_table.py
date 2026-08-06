"""统一Canvas表格组件 - 最终定型版"""
import tkinter as tk
from tkinter import ttk
from constants import MIN_NUMBER, MAX_NUMBER, AMOUNT_MULTIPLIER


class ResultCanvasTable(tk.Frame):
    """结果表格 - 使用Canvas统一绘制"""

    def __init__(self, parent):
        super().__init__(parent, bg="#FFFFFF")

        self.rows = []
        self.total_amount = 0
        self.row_height = 28  # 固定行高

        # 列宽配置（百分比）
        self.col_widths = {
            'number': 0.14,   # 14%
            'amount': 0.26,   # 26%
            'payout': 0.30,   # 30%
            'profit': 0.30    # 30%
        }

        self._build_table()

    def _build_table(self):
        """构建表格"""
        # 表头Frame（固定在顶部）
        header_frame = tk.Frame(self, bg="#1A237E", height=36)
        header_frame.pack(fill='x', side='top')
        header_frame.pack_propagate(False)

        # 创建表头Canvas
        self.header_canvas = tk.Canvas(
            header_frame,
            bg="#1A237E",
            highlightthickness=0,
            height=36
        )
        self.header_canvas.pack(fill='both', expand=True)

        # 数据区域容器
        data_container = tk.Frame(self, bg="#FFFFFF")
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

        # 绑定事件
        self.data_canvas.bind('<MouseWheel>', self._on_mousewheel)
        self.header_canvas.bind('<Configure>', self._on_resize)
        self.data_canvas.bind('<Configure>', self._on_resize)

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
        self.header_canvas.create_text(
            col_x['number'] + col_w['number'] / 2, 18,
            text="号码",
            fill="#FFFFFF",
            font=("Microsoft YaHei", 12, "bold")
        )

        self.header_canvas.create_text(
            col_x['amount'] + col_w['amount'] - 10, 18,
            text="金额",
            fill="#FFFFFF",
            font=("Microsoft YaHei", 12, "bold"),
            anchor='e'
        )

        self.header_canvas.create_text(
            col_x['payout'] + col_w['payout'] - 10, 18,
            text="赔付（金额×47）",
            fill="#FFFFFF",
            font=("Microsoft YaHei", 12, "bold"),
            anchor='e'
        )

        self.header_canvas.create_text(
            col_x['profit'] + col_w['profit'] - 10, 18,
            text="盈利（总下注－赔付）",
            fill="#FFFFFF",
            font=("Microsoft YaHei", 12, "bold"),
            anchor='e'
        )

    def _calculate_column_x(self, width):
        """计算列X坐标"""
        return {
            'number': 0,
            'amount': width * self.col_widths['number'],
            'payout': width * (self.col_widths['number'] + self.col_widths['amount']),
            'profit': width * (self.col_widths['number'] + self.col_widths['amount'] + self.col_widths['payout'])
        }

    def _calculate_column_width(self, width):
        """计算列宽度"""
        return {
            'number': width * self.col_widths['number'],
            'amount': width * self.col_widths['amount'],
            'payout': width * self.col_widths['payout'],
            'profit': width * self.col_widths['profit']
        }

    def set_rows(self, rows, total_amount):
        """
        设置表格数据

        参数:
            rows: 已排序的行数据列表，每行包含 {number, amount, payout, profit}
            total_amount: 总下注金额
        """
        self.rows = rows
        self.total_amount = total_amount
        self.redraw()

    def redraw(self):
        """重新绘制表格"""
        # 清空现有数据
        self.data_canvas.delete("all")

        if not self.rows:
            return

        # 获取Canvas宽度
        width = self.data_canvas.winfo_width()
        if width <= 1:
            width = 600

        # 计算列位置
        col_x = self._calculate_column_x(width)
        col_w = self._calculate_column_width(width)

        # 绘制每一行
        for idx, row in enumerate(self.rows):
            rank = idx + 1
            y1 = idx * self.row_height
            y2 = y1 + self.row_height
            y_center = y1 + self.row_height // 2

            # 数据断言 - 确保数据一致性
            assert row['payout'] == row['amount'] * 47, f"赔付计算错误: {row['payout']} != {row['amount']} * 47"
            assert abs(row['profit'] - (self.total_amount - row['payout'])) < 0.01, \
                f"盈利计算错误: {row['profit']} != {self.total_amount} - {row['payout']}"

            # 根据排名确定背景和号码颜色
            if rank <= 10:
                bg_color = "#FFE5E5"  # 浅红
                num_color = "#C62828"  # 深红
            elif rank <= 20:
                bg_color = "#E5F1FF"  # 浅蓝
                num_color = "#1565C0"  # 深蓝
            elif rank <= 30:
                bg_color = "#FFF1D8"  # 浅橙
                num_color = "#EF6C00"  # 深橙
            elif rank <= 40:
                bg_color = "#E7F7E9"  # 浅绿
                num_color = "#2E7D32"  # 深绿
            else:
                bg_color = "#F2F2F2"  # 浅灰
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
                text=f"{row['number']:02d}",
                fill=num_color,
                font=("Microsoft YaHei", 13, "bold")
            )

            # 绘制金额（右对齐，深色）
            self.data_canvas.create_text(
                col_x['amount'] + col_w['amount'] - 10, y_center,
                text=f"{row['amount']:,.2f}",
                fill="#212121",
                font=("Arial", 12),
                anchor='e'
            )

            # 绘制赔付（右对齐，深色）
            self.data_canvas.create_text(
                col_x['payout'] + col_w['payout'] - 10, y_center,
                text=f"{row['payout']:,.2f}",
                fill="#212121",
                font=("Arial", 12),
                anchor='e'
            )

            # 绘制盈利（右对齐，根据正负显示颜色）
            if row['profit'] >= 0:
                profit_text = f"+{row['profit']:,.2f}"
                profit_color = "#2E7D32"  # 深绿
            else:
                profit_text = f"{row['profit']:,.2f}"
                profit_color = "#C62828"  # 深红

            self.data_canvas.create_text(
                col_x['profit'] + col_w['profit'] - 10, y_center,
                text=profit_text,
                fill=profit_color,
                font=("Arial", 12, "bold"),
                anchor='e'
            )

        # 设置滚动区域
        total_height = len(self.rows) * self.row_height
        self.data_canvas.configure(scrollregion=(0, 0, width, total_height))

        # 绘制表头
        self._draw_header()

    def clear(self):
        """清空表格"""
        self.rows = []
        self.total_amount = 0
        self.data_canvas.delete("all")

    def scroll_to_top(self):
        """滚动到顶部"""
        self.data_canvas.yview_moveto(0)
