"""
在 main_window.py 的 _save_input_history 方法前添加平特一肖刷新方法
"""

# 读取文件
with open('ui/main_window.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 找到 _save_input_history 方法的位置
insert_line = None
for i, line in enumerate(lines):
    if '    def _save_input_history' in line:
        insert_line = i
        break

if insert_line is None:
    print("ERROR: 找不到 _save_input_history 方法")
    exit(1)

print(f"找到插入位置: 行 {insert_line + 1}")

# 新增的两个方法
new_methods = '''    def _refresh_flat_zodiac_display(self, summary: dict):
        """刷新右侧12生肖表格显示"""
        from constants import AMOUNT_MULTIPLIER

        zodiac_amounts = summary['zodiac_amounts']
        total_bet = summary['total_bet']

        # 更新表格
        self.result_table.update_data(zodiac_amounts, total_bet)

        print(f"[DEBUG] 右侧表格已更新:")
        for zodiac, amount in zodiac_amounts.items():
            if amount > 0:
                print(f"  {zodiac}: {amount / AMOUNT_MULTIPLIER:.2f}")

    def _refresh_flat_zodiac_stats(self, summary: dict):
        """刷新顶部统计显示"""
        from constants import AMOUNT_MULTIPLIER

        total_bet = summary['total_bet']
        non_zero_count = summary['non_zero_count']
        max_zodiac = summary['max_zodiac']
        max_amount = summary['max_amount']

        # 更新顶部统计标签
        self.total_label.configure(text=f"{total_bet / AMOUNT_MULTIPLIER:,.2f}")
        self.count_label.configure(text=f"{non_zero_count}")
        self.max_num_label.configure(text=max_zodiac)
        self.max_amount_label.configure(text=f"{max_amount / AMOUNT_MULTIPLIER:,.2f}")

        print(f"[DEBUG] 顶部统计已更新:")
        print(f"  今日总下注: {total_bet / AMOUNT_MULTIPLIER:.2f}")
        print(f"  非零生肖: {non_zero_count}")
        print(f"  最高下注生肖: {max_zodiac}")
        print(f"  最高金额: {max_amount / AMOUNT_MULTIPLIER:.2f}")

'''

# 插入新方法
new_lines = lines[:insert_line] + [new_methods] + lines[insert_line:]

# 写回文件
with open('ui/main_window.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print(f"添加完成！在第 {insert_line + 1} 行前插入了刷新方法")
