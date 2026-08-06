"""
替换 main_window.py 中的 _confirm_add 方法为独立闭环版本
"""

# 读取文件
with open('ui/main_window.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 找到 _confirm_add 方法的开始和结束
start_line = None
end_line = None
indent_count = None

for i, line in enumerate(lines):
    if '    def _confirm_add(self):' in line:
        start_line = i
        indent_count = len(line) - len(line.lstrip())
        continue

    if start_line is not None and line.strip() and not line.startswith(' ' * (indent_count + 4)):
        # 找到下一个相同缩进级别的内容（下一个方法）
        if line.startswith(' ' * indent_count) and 'def ' in line:
            end_line = i
            break

if start_line is None:
    print("ERROR: 找不到 _confirm_add 方法")
    exit(1)

if end_line is None:
    # 如果没找到下一个方法，查找文件末尾
    end_line = len(lines)

print(f"找到 _confirm_add 方法: 行 {start_line+1} 到 {end_line}")

# 新的方法内容
new_method = '''    def _confirm_add(self):
        """确认追加 - 独立闭环版本"""
        print("\\n" + "="*60)
        print("[ENTER] confirm_add()")
        print("="*60)

        input_text = self.input_text.get("1.0", "end-1c").strip()

        print(f"[1] 原始输入: {input_text}")
        print(f"[2] 当前模式: {self.current_mode}")
        print(f"[3] 当前账本ID: {self.current_ledger.id}")
        print(f"[4] 数据库路径: {self.db.db_path}")

        try:
            # 检查跨日
            rolled_over, new_date = self.rollover.check_and_rollover(self.current_ledger.id)
            if rolled_over:
                self._set_last_settlement(
                    self.rollover.last_settled_ledger_date,
                    self.rollover.last_settlement_total
                )
                messagebox.showinfo(
                    "跨日结算",
                    f"已结算{self.rollover.last_settled_ledger_date}账本\\n"
                    f"总账总金额：{self.rollover.last_settlement_total / AMOUNT_MULTIPLIER:.2f}\\n\\n"
                    f"已新建{new_date}账本"
                )
                self._load_current_ledger()

            # 模式分支
            from play_mode import PlayMode

            if self.current_mode == PlayMode.FLAT_ZODIAC:
                print(f"[5] 进入平特一肖独立流程")
                self._confirm_add_flat_zodiac(input_text)
            else:
                print(f"[5] 进入号码模式流程")
                self._confirm_add_number_mode(input_text)

        except Exception as e:
            import traceback
            print("\\n" + "="*60)
            print("追加失败 - 完整错误堆栈:")
            print("="*60)
            traceback.print_exc()
            print("="*60 + "\\n")
            messagebox.showerror("错误", f"追加失败：{str(e)}")

    def _confirm_add_flat_zodiac(self, input_text: str):
        """平特一肖独立追加流程"""
        from flat_zodiac_service import FlatZodiacService

        # 创建服务
        service = FlatZodiacService(self.db.conn)

        # 解析输入
        print(f"[6] 解析输入...")
        entries = service.parse_input(input_text)
        print(f"[7] 解析成功: {len(entries)} 条记录")
        for e in entries:
            print(f"    {e.zodiac} = {e.amount:.2f}")

        # 计算本次总额
        entry_total = sum(e.amount for e in entries)
        print(f"[8] 本次总额: {entry_total:.2f}")

        # 写入数据库（事务）
        print(f"[9] 写入数据库...")
        batch_id = service.add_batch(self.current_ledger.id, input_text, entries)
        print(f"[10] 数据库提交成功，批次ID: {batch_id}")
        print(f"[11] 写入items数量: {len(entries)}")

        # 重新查询
        print(f"[12] 重新查询汇总...")
        summary = service.get_summary(self.current_ledger.id)
        print(f"[13] 查询成功:")
        print(f"     总下注: {summary['total_bet'] / AMOUNT_MULTIPLIER:.2f}")
        for zodiac in ['虎', '龙', '鼠', '牛', '兔', '蛇', '马', '羊', '猴', '鸡', '狗', '猪']:
            if summary['zodiac_amounts'].get(zodiac, 0) > 0:
                print(f"     {zodiac}累计: {summary['zodiac_amounts'][zodiac] / AMOUNT_MULTIPLIER:.2f}")

        # 刷新右侧12生肖表
        print(f"[14] 刷新右侧12生肖表...")
        self._refresh_flat_zodiac_display(summary)
        print(f"[15] 右侧刷新完成")

        # 刷新顶部统计
        print(f"[16] 刷新顶部统计...")
        self._refresh_flat_zodiac_stats(summary)
        print(f"[17] 顶部统计刷新完成")

        # 清空输入
        self.input_text.delete("1.0", "end")
        self._clear_preview()
        self._clear_calc()

        # 最后才显示成功
        print(f"[18] 显示追加成功消息")
        messagebox.showinfo("成功", "已追加到账本")

        print("="*60)
        print("[DONE] 平特一肖追加完成")
        print("="*60 + "\\n")

    def _confirm_add_number_mode(self, input_text: str):
        """号码模式原有追加流程（完全保持不变）"""
        from play_mode import PlayMode
        from calculator_factory import CalculatorFactory
        from models import Batch

        animal_mapping = self.db.get_animal_mapping()

        # 号码模式：使用原有解析器
        parser = InstructionParser(animal_mapping)
        instructions = parser.parse_input(input_text)

        # 号码模式：使用原有计算器
        calculator = CalculatorFactory.get_calculator(PlayMode.NUMBER, animal_mapping)
        result = calculator.calculate(instructions, self.current_totals)

        # 保存批次
        batch = Batch(
            raw_input=input_text,
            total_before=sum(self.current_totals.values()),
            total_after=result.total_amount,
            mapping_snapshot=json.dumps(animal_mapping, ensure_ascii=False),
            instructions=instructions
        )

        batch_id = self.db.add_batch_with_allocations(
            self.current_ledger.id,
            batch,
            animal_mapping
        )

        # 保存输入历史
        self._save_input_history(
            batch_id,
            input_text,
            instructions,
            result,
            animal_mapping,
            'number'
        )

        # 清空输入
        self.input_text.delete("1.0", "end")
        self._clear_preview()
        self._clear_calc()

        # 刷新显示
        self._update_display()

        # 显示成功
        messagebox.showinfo("成功", "已追加到账本")

'''

# 替换方法
new_lines = lines[:start_line] + [new_method + '\n'] + lines[end_line:]

# 写回文件
with open('ui/main_window.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print(f"替换完成！")
print(f"原方法: {end_line - start_line} 行")
print(f"新方法: {len(new_method.split(chr(10)))} 行")
