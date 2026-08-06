"""
重写 animal_result_table.py 的 redraw 方法
"""

# 读取文件
with open('ui/animal_result_table.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 定义新的 redraw 方法
new_redraw = '''    def redraw(self):
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
                fill=bg_color, outline=""
            )

            # 获取金额（元）
            amount = self.animal_amounts.get(animal, 0)
            payout = amount * self.odds
            profit = self.total_amount - payout

            # 生肖名（居中）
            self.data_canvas.create_text(
                col_x['animal'] + col_w['animal'] / 2,
                y + self.row_height / 2,
                text=animal,
                fill="#333333",
                font=("Microsoft YaHei", 11, "bold")
            )

            # 金额（右对齐）
            amount_color = "#0066CC" if amount > 0 else "#999999"
            self.data_canvas.create_text(
                col_x['amount'] + col_w['amount'] - 10,
                y + self.row_height / 2,
                text=format_amount(amount) if amount > 0 else "--",
                fill=amount_color,
                font=("Consolas", 11),
                anchor='e'
            )

            # 赔率（居中）
            self.data_canvas.create_text(
                col_x['odds'] + col_w['odds'] / 2,
                y + self.row_height / 2,
                text=format_amount(self.odds),
                fill="#666666",
                font=("Consolas", 10)
            )

            # 赔付（右对齐）
            if amount > 0:
                self.data_canvas.create_text(
                    col_x['payout'] + col_w['payout'] - 10,
                    y + self.row_height / 2,
                    text=format_amount(payout),
                    fill="#00AA00",
                    font=("Consolas", 11),
                    anchor='e'
                )

            # 盈利（右对齐，根据正负显示颜色）
            if amount > 0:
                profit_color = "#DD0000" if profit >= 0 else "#006600"
                profit_text = f"+{format_amount(profit)}" if profit >= 0 else format_amount(profit)
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
        self.data_canvas.config(scrollregion=(0, 0, width, y))'''

# 找到 redraw 方法的开始和结束
import re
pattern = r'    def redraw\(self\):.*?(?=\n    def |\n\nclass |\Z)'
match = re.search(pattern, content, re.DOTALL)

if match:
    new_content = content[:match.start()] + new_redraw + content[match.end():]

    with open('ui/animal_result_table.py', 'w', encoding='utf-8') as f:
        f.write(new_content)

    print("redraw 方法已更新")
else:
    print("未找到 redraw 方法")
