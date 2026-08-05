"""香港版主窗口 - 标签页布局"""
import json
from datetime import datetime
from pathlib import Path
import customtkinter as ctk
from tkinter import messagebox, filedialog
from typing import Optional, Dict
from database import Database, DatabaseError
from daily_rollover import DailyRollover
from parser import InstructionParser, ParserError
from calculator import Calculator
from backup import BackupManager, BackupError
from constants import MIN_NUMBER, MAX_NUMBER, AMOUNT_MULTIPLIER
from ui.history_window import HistoryWindow
from ui.mapping_window import MappingWindow


class MainWindowHK(ctk.CTk):
    """香港版主窗口 - 标签页设计"""

    # 生肖emoji映射
    ANIMAL_EMOJI = {
        "马": "🐴", "蛇": "🐍", "龙": "🐲", "兔": "🐰",
        "虎": "🐯", "牛": "🐮", "鼠": "🐭", "猪": "🐷",
        "狗": "🐶", "鸡": "🐔", "猴": "🐵", "羊": "🐑"
    }

    # 香港版配色方案
    COLOR_PRIMARY = "#00796B"      # 深青色
    COLOR_SECONDARY = "#4DB6AC"    # 浅青色
    COLOR_ACCENT = "#FF6F00"       # 橙色
    COLOR_BG = "#E0F2F1"           # 淡青色背景
    COLOR_SUCCESS = "#43A047"      # 绿色
    COLOR_WARNING = "#FFA726"      # 橙色
    COLOR_DANGER = "#E53935"       # 红色

    def __init__(self, db: Database, rollover: DailyRollover, app_data_dir: Path):
        super().__init__()

        self.db = db
        self.rollover = rollover
        self.app_data_dir = app_data_dir
        self.backup_manager = BackupManager(db)

        # 当前账本
        self.current_ledger = None
        self.current_totals = {}
        self.current_sources = {}

        # 生肖卡片引用
        self.animal_cards = {}

        # 设置窗口
        self.title("香港")
        self.geometry("1400x900")

        # 设置外观
        ctk.set_appearance_mode("light")

        # 初始化界面
        self._setup_ui()

        # 启动时先结算跨日遗留账本，再加载今天账本
        startup_settlements = self.rollover.initialize()

        # 加载当前账本
        self._load_current_ledger()

        if startup_settlements:
            _, ledger_date, total = startup_settlements[-1]
            self._set_last_settlement(ledger_date, total)
            settlement_lines = [
                f"{date}：{amount / AMOUNT_MULTIPLIER:.2f}"
                for _, date, amount in startup_settlements
            ]
            self.after(
                200,
                lambda: messagebox.showinfo(
                    "启动结算完成",
                    "已自动结算跨日账本：\n\n" + '\n'.join(settlement_lines)
                )
            )
        else:
            self._load_last_settlement_display()

        # 启动定时检查跨日
        self._schedule_rollover_check()
    def _setup_ui(self):
        """设置界面"""
        # ===== 顶部标题栏 =====
        header_frame = ctk.CTkFrame(self, height=70, fg_color=self.COLOR_PRIMARY)
        header_frame.pack(fill='x', padx=0, pady=0)
        header_frame.pack_propagate(False)

        # 左侧标题
        title_container = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_container.pack(side='left', padx=20, pady=10)

        title_label = ctk.CTkLabel(
            title_container,
            text="香港",
            font=("Microsoft YaHei UI", 28, "bold"),
            text_color="white"
        )
        title_label.pack(anchor='w')

        version_label = ctk.CTkLabel(
            title_container,
            text="v1.0",
            font=("Arial", 11),
            text_color=self.COLOR_BG
        )
        version_label.pack(anchor='w')

        # 右侧信息
        info_container = ctk.CTkFrame(header_frame, fg_color="transparent")
        info_container.pack(side='right', padx=20)

        self.date_label = ctk.CTkLabel(
            info_container,
            text="",
            font=("Arial", 13, "bold"),
            text_color="white"
        )
        self.date_label.pack(anchor='e')

        self.ledger_label = ctk.CTkLabel(
            info_container,
            text="",
            font=("Arial", 11),
            text_color=self.COLOR_BG
        )
        self.ledger_label.pack(anchor='e', pady=(3, 0))

        self.settlement_info_label = ctk.CTkLabel(
            info_container,
            text="",
            font=("Arial", 10),
            text_color=self.COLOR_BG
        )
        self.settlement_info_label.pack(anchor='e', pady=(3, 0))

        # ===== 标签页容器 =====
        self.tabview = ctk.CTkTabview(self, height=750)
        self.tabview.pack(fill='both', expand=True, padx=10, pady=10)

        # 创建5个标签页
        self.tab_input = self.tabview.add("📝 输入")
        self.tab_stats = self.tabview.add("📊 统计")
        self.tab_settlement = self.tabview.add("🏆 结算")
        self.tab_history = self.tabview.add("📋 历史")
        self.tab_settings = self.tabview.add("⚙️ 设置")

        # 设置默认标签页
        self.tabview.set("📝 输入")

        # 初始化各个标签页
        self._setup_input_tab()
        self._setup_stats_tab()
        self._setup_settlement_tab()
        self._setup_history_tab()
        self._setup_settings_tab()

        # ===== 底部状态栏 =====
        footer_frame = ctk.CTkFrame(self, height=60, fg_color="#F5F5F5")
        footer_frame.pack(fill='x', padx=0, pady=0)
        footer_frame.pack_propagate(False)

        self.status_label = ctk.CTkLabel(
            footer_frame,
            text="系统就绪",
            font=("Microsoft YaHei UI", 11),
            text_color="#666666"
        )
        self.status_label.pack(side='left', padx=20, pady=20)

        self.total_display_label = ctk.CTkLabel(
            footer_frame,
            text="今日总额: ￥0.00",
            font=("Microsoft YaHei UI", 14, "bold"),
            text_color=self.COLOR_PRIMARY
        )
        self.total_display_label.pack(side='right', padx=20, pady=20)
    def _setup_input_tab(self):
        """设置输入标签页"""
        # 标题
        title_label = ctk.CTkLabel(
            self.tab_input,
            text="输入投注指令",
            font=("Microsoft YaHei UI", 18, "bold"),
            text_color=self.COLOR_PRIMARY
        )
        title_label.pack(pady=(20, 10), padx=20, anchor='w')

        # 输入框
        self.input_text = ctk.CTkTextbox(
            self.tab_input,
            height=200,
            font=("Consolas", 13),
            border_width=2,
            border_color=self.COLOR_SECONDARY
        )
        self.input_text.pack(fill='x', pady=(0, 15), padx=20)
        self.input_text.bind('<KeyRelease>', lambda e: self._on_input_change())

        # 按钮组
        button_frame = ctk.CTkFrame(self.tab_input, fg_color="transparent")
        button_frame.pack(fill='x', padx=20, pady=(0, 15))

        self.calculate_btn = ctk.CTkButton(
            button_frame,
            text="✅ 确认追加",
            command=self._confirm_add,
            state='disabled',
            font=("Microsoft YaHei UI", 14, "bold"),
            height=45,
            fg_color=self.COLOR_SUCCESS,
            hover_color="#388E3C"
        )
        self.calculate_btn.pack(side='left', padx=(0, 10))

        self.clear_input_btn = ctk.CTkButton(
            button_frame,
            text="🗑️ 清空",
            command=self._clear_input,
            font=("Microsoft YaHei UI", 13),
            height=45,
            fg_color="#757575",
            hover_color="#616161"
        )
        self.clear_input_btn.pack(side='left', padx=5)

        self.undo_btn = ctk.CTkButton(
            button_frame,
            text="↩️ 撤销",
            command=self._undo_last,
            font=("Microsoft YaHei UI", 13),
            height=45,
            fg_color=self.COLOR_WARNING,
            hover_color="#FB8C00"
        )
        self.undo_btn.pack(side='left', padx=5)

        # 预览区域
        preview_title = ctk.CTkLabel(
            self.tab_input,
            text="实时预览",
            font=("Microsoft YaHei UI", 14, "bold"),
            text_color=self.COLOR_PRIMARY
        )
        preview_title.pack(pady=(10, 5), padx=20, anchor='w')

        self.preview_text = ctk.CTkTextbox(
            self.tab_input,
            height=250,
            font=("Consolas", 11),
            state='disabled'
        )
        self.preview_text.pack(fill='both', expand=True, pady=(0, 20), padx=20)

    def _setup_stats_tab(self):
        """设置统计标签页"""
        # 标题
        title_label = ctk.CTkLabel(
            self.tab_stats,
            text="生肖投注统计",
            font=("Microsoft YaHei UI", 18, "bold"),
            text_color=self.COLOR_PRIMARY
        )
        title_label.pack(pady=(20, 10), padx=20, anchor='w')

        # 卡片容器（滚动）
        self.stats_scroll = ctk.CTkScrollableFrame(
            self.tab_stats,
            fg_color="transparent"
        )
        self.stats_scroll.pack(fill='both', expand=True, padx=20, pady=(0, 20))

    def _setup_settlement_tab(self):
        """设置结算标签页"""
        # 标题
        title_label = ctk.CTkLabel(
            self.tab_settlement,
            text="开奖结算",
            font=("Microsoft YaHei UI", 18, "bold"),
            text_color=self.COLOR_PRIMARY
        )
        title_label.pack(pady=(20, 10), padx=20, anchor='w')

        # 结算按钮
        settlement_btn = ctk.CTkButton(
            self.tab_settlement,
            text="🏆 打开结算窗口",
            command=self._open_settlement,
            font=("Microsoft YaHei UI", 16, "bold"),
            height=60,
            fg_color=self.COLOR_ACCENT,
            hover_color="#F57C00"
        )
        settlement_btn.pack(pady=30, padx=20)

        # 结算说明
        info_label = ctk.CTkLabel(
            self.tab_settlement,
            text="点击按钮打开结算窗口，输入开奖号码计算盈亏\n赔率：47倍",
            font=("Microsoft YaHei UI", 13),
            text_color="#666666",
            justify='center'
        )
        info_label.pack(pady=10)

    def _setup_history_tab(self):
        """设置历史标签页"""
        # 标题
        title_label = ctk.CTkLabel(
            self.tab_history,
            text="历史记录",
            font=("Microsoft YaHei UI", 18, "bold"),
            text_color=self.COLOR_PRIMARY
        )
        title_label.pack(pady=(20, 10), padx=20, anchor='w')

        # 历史按钮
        history_btn = ctk.CTkButton(
            self.tab_history,
            text="📋 打开历史记录",
            command=self._open_history,
            font=("Microsoft YaHei UI", 16, "bold"),
            height=60,
            fg_color=self.COLOR_SECONDARY,
            hover_color="#26A69A"
        )
        history_btn.pack(pady=30, padx=20)

    def _setup_settings_tab(self):
        """设置设置标签页"""
        # 标题
        title_label = ctk.CTkLabel(
            self.tab_settings,
            text="系统设置",
            font=("Microsoft YaHei UI", 18, "bold"),
            text_color=self.COLOR_PRIMARY
        )
        title_label.pack(pady=(20, 10), padx=20, anchor='w')

        # 按钮容器
        buttons_container = ctk.CTkFrame(self.tab_settings, fg_color="transparent")
        buttons_container.pack(fill='both', expand=True, padx=20, pady=20)

        # 生肖号码表
        mapping_btn = ctk.CTkButton(
            buttons_container,
            text="🔢 生肖号码映射表",
            command=self._open_mapping,
            font=("Microsoft YaHei UI", 14),
            height=50
        )
        mapping_btn.pack(pady=10, fill='x')

        # 导出备份
        export_btn = ctk.CTkButton(
            buttons_container,
            text="💾 导出数据备份",
            command=self._export_backup,
            font=("Microsoft YaHei UI", 14),
            height=50
        )
        export_btn.pack(pady=10, fill='x')

        # 恢复备份
        import_btn = ctk.CTkButton(
            buttons_container,
            text="📥 恢复数据备份",
            command=self._import_backup,
            font=("Microsoft YaHei UI", 14),
            height=50
        )
        import_btn.pack(pady=10, fill='x')

        # 结算清空
        clear_btn = ctk.CTkButton(
            buttons_container,
            text="💰 结算并清空今日",
            command=self._clear_today,
            font=("Microsoft YaHei UI", 14),
            height=50,
            fg_color=self.COLOR_DANGER,
            hover_color="#C62828"
        )
        clear_btn.pack(pady=10, fill='x')

        # 系统自检
        test_btn = ctk.CTkButton(
            buttons_container,
            text="🔧 运行系统自检",
            command=self._run_selftest,
            font=("Microsoft YaHei UI", 14),
            height=50
        )
        test_btn.pack(pady=10, fill='x')
    def _load_current_ledger(self):
        """加载当前账本"""
        current_date = self.rollover.get_current_date_str()
        self.current_ledger = self.db.get_or_create_active_ledger(current_date)
        self._update_display()

    def _set_last_settlement(self, ledger_date: str, total_integer: int):
        """更新最近一次结算金额显示"""
        self.settlement_info_label.configure(
            text=f"上次结算 ({ledger_date}): ￥{total_integer / AMOUNT_MULTIPLIER:.2f}"
        )

    def _load_last_settlement_display(self):
        """从历史账本加载最近一次结算金额"""
        for ledger in self.db.get_all_ledgers():
            if ledger.status == 'archived' and ledger.settled_total_integer is not None:
                self._set_last_settlement(
                    ledger.ledger_date,
                    ledger.settled_total_integer
                )
                return
        self.settlement_info_label.configure(text="上次结算: --")

    def _update_display(self):
        """更新显示"""
        # 更新顶部信息
        self.date_label.configure(text=f"📅 {self.current_ledger.ledger_date}")
        self.ledger_label.configure(text=f"账本 #{self.current_ledger.sequence_number}")

        # 获取当前累计
        self.current_totals = self.db.get_ledger_totals(self.current_ledger.id)
        self.current_sources = self.db.get_ledger_sources(self.current_ledger.id)

        # 获取动物映射
        animal_mapping = self.db.get_animal_mapping()

        # 计算每个动物的总金额
        animal_totals = {}
        for animal, numbers in animal_mapping.items():
            total = sum(self.current_totals.get(num, 0) for num in numbers)
            animal_totals[animal] = total

        # 找出最大金额
        max_amount = max(animal_totals.values()) if animal_totals else 0

        # 排序：金额从大到小
        sorted_animals = sorted(
            animal_totals.items(),
            key=lambda x: (-x[1], x[0])
        )

        # 清空统计页卡片
        for widget in self.stats_scroll.winfo_children():
            widget.destroy()
        self.animal_cards.clear()

        # 创建卡片
        total_amount = 0
        for animal, amount_int in sorted_animals:
            amount = amount_int / AMOUNT_MULTIPLIER
            is_max = amount_int > 0 and amount_int == max_amount

            numbers = animal_mapping.get(animal, [])
            card = self._create_animal_card(animal, numbers, amount, is_max)
            self.animal_cards[animal] = card

            total_amount += amount_int

        # 更新底部总额显示
        self.total_display_label.configure(
            text=f"今日总额: ￥{total_amount / AMOUNT_MULTIPLIER:.2f}"
        )

        # 更新状态
        non_zero_count = sum(1 for a in animal_totals.values() if a > 0)
        self.status_label.configure(
            text=f"涉及生肖: {non_zero_count}/12"
        )

    def _create_animal_card(self, animal: str, numbers: list, amount: float,
                           is_max: bool = False) -> ctk.CTkFrame:
        """创建生肖卡片"""
        # 卡片框架
        if is_max:
            card = ctk.CTkFrame(
                self.stats_scroll,
                fg_color="#FFEBEE",
                border_width=3,
                border_color=self.COLOR_DANGER,
                corner_radius=12
            )
        else:
            card = ctk.CTkFrame(
                self.stats_scroll,
                fg_color="white",
                border_width=1,
                border_color="#E0E0E0",
                corner_radius=12
            )

        card.pack(fill='x', pady=8, padx=10)

        # 内容容器
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill='x', padx=20, pady=15)

        # 左侧：动物信息
        left_frame = ctk.CTkFrame(content, fg_color="transparent")
        left_frame.pack(side='left', fill='both', expand=True)

        # 动物名称
        emoji = self.ANIMAL_EMOJI.get(animal, "🎯")
        animal_label = ctk.CTkLabel(
            left_frame,
            text=f"{emoji} {animal}",
            font=("Microsoft YaHei UI", 20, "bold"),
            text_color=self.COLOR_DANGER if is_max else self.COLOR_PRIMARY
        )
        animal_label.pack(anchor='w')

        # 号码列表
        numbers_text = ", ".join([f"{n:02d}" for n in sorted(numbers)])
        numbers_label = ctk.CTkLabel(
            left_frame,
            text=f"号码: {numbers_text}",
            font=("Consolas", 12),
            text_color="#757575"
        )
        numbers_label.pack(anchor='w', pady=(5, 0))

        # 右侧：金额
        amount_frame = ctk.CTkFrame(content, fg_color="transparent")
        amount_frame.pack(side='right', padx=20)

        amount_label = ctk.CTkLabel(
            amount_frame,
            text=f"￥{amount:.2f}",
            font=("Arial", 26, "bold"),
            text_color=self.COLOR_DANGER if is_max else self.COLOR_SUCCESS
        )
        amount_label.pack()

        if is_max and amount > 0:
            max_badge = ctk.CTkLabel(
                amount_frame,
                text="⭐ 最高",
                font=("Microsoft YaHei UI", 13, "bold"),
                text_color=self.COLOR_DANGER
            )
            max_badge.pack(pady=(5, 0))

        # 点击显示详情
        card.bind('<Button-1>', lambda e: self._show_animal_details(animal))
        animal_label.bind('<Button-1>', lambda e: self._show_animal_details(animal))
        numbers_label.bind('<Button-1>', lambda e: self._show_animal_details(animal))
        amount_label.bind('<Button-1>', lambda e: self._show_animal_details(animal))

        return card

    def _on_input_change(self):
        """输入变化时的处理"""
        input_text = self.input_text.get("1.0", "end-1c").strip()

        if not input_text:
            self.calculate_btn.configure(state='disabled')
            self._clear_preview()
            return

        # 解析预览
        try:
            animal_mapping = self.db.get_animal_mapping()
            parser = InstructionParser(animal_mapping)
            instructions = parser.parse_input(input_text)

            # 显示解析预览
            preview_lines = []
            for inst in instructions:
                if inst.target_type == 'number':
                    targets_str = ', '.join(inst.targets)
                else:
                    targets_str = ', '.join(inst.targets) + ' (各号)'

                amount = inst.amount_integer / AMOUNT_MULTIPLIER
                line = f"第{inst.source_line}行: {targets_str} → ￥{amount:.2f}"

                if inst.warning:
                    line += f" ⚠️ {inst.warning}"

                preview_lines.append(line)

            self.preview_text.configure(state='normal')
            self.preview_text.delete("1.0", "end")
            self.preview_text.insert("1.0", '\n'.join(preview_lines))
            self.preview_text.configure(state='disabled')

            # 启用确认按钮
            self.calculate_btn.configure(state='normal')

        except ParserError as e:
            # 显示错误
            self.preview_text.configure(state='normal')
            self.preview_text.delete("1.0", "end")
            self.preview_text.insert("1.0", f"❌ 解析错误：\n{str(e)}")
            self.preview_text.configure(state='disabled')
            self.calculate_btn.configure(state='disabled')

    def _clear_preview(self):
        """清空预览"""
        self.preview_text.configure(state='normal')
        self.preview_text.delete("1.0", "end")
        self.preview_text.configure(state='disabled')
    def _confirm_add(self):
        """确认追加"""
        input_text = self.input_text.get("1.0", "end-1c").strip()

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
                    f"已结算{self.rollover.last_settled_ledger_date}账本\n"
                    f"总账总金额：{self.rollover.last_settlement_total / AMOUNT_MULTIPLIER:.2f}\n\n"
                    f"已新建{new_date}账本"
                )
                self._load_current_ledger()

            # 解析
            animal_mapping = self.db.get_animal_mapping()
            parser = InstructionParser(animal_mapping)
            instructions = parser.parse_input(input_text)

            # 计算
            calculator = Calculator(animal_mapping)
            result = calculator.calculate(instructions, self.current_totals)

            # 保存批次
            from models import Batch
            batch = Batch(
                raw_input=input_text,
                total_before=sum(self.current_totals.values()),
                total_after=result.total_amount,
                mapping_snapshot=json.dumps(animal_mapping, ensure_ascii=False),
                instructions=instructions
            )

            self.db.add_batch_with_allocations(
                self.current_ledger.id,
                batch,
                animal_mapping
            )

            # 清空输入
            self.input_text.delete("1.0", "end")
            self.calculate_btn.configure(state='disabled')
            self._clear_preview()

            # 刷新显示
            self._update_display()

            # 自动切换到统计页
            self.tabview.set("📊 统计")

            messagebox.showinfo("成功", "✅ 已追加到账本")

        except ParserError as e:
            messagebox.showerror("解析错误", f"❌ 输入格式有误：\n{str(e)}")
        except Exception as e:
            messagebox.showerror("错误", f"❌ 追加失败：\n{str(e)}")

    def _clear_input(self):
        """清空输入"""
        self.input_text.delete("1.0", "end")
        self.calculate_btn.configure(state='disabled')
        self._clear_preview()

    def _undo_last(self):
        """撤销最近一次"""
        last_batch_id = self.db.get_last_batch_id(self.current_ledger.id)
        if not last_batch_id:
            messagebox.showinfo("提示", "当前账本没有记录")
            return

        if messagebox.askyesno("确认", "确定要撤销最近一次追加吗？"):
            try:
                self.db.delete_batch(last_batch_id)
                self._update_display()
                messagebox.showinfo("成功", "✅ 已撤销")
            except DatabaseError as e:
                messagebox.showerror("错误", f"❌ 撤销失败：{str(e)}")

    def _clear_today(self):
        """清空今日累计"""
        if messagebox.askyesno(
            "确认结算",
            "确定要结算当前账本并清空今日累计吗？\n"
            "结算结果会保存在历史记录中。"
        ):
            try:
                # 归档当前账本并创建新账本
                settled_date = self.current_ledger.ledger_date
                settled_total = self.db.archive_ledger(self.current_ledger.id)
                self.rollover.last_settled_ledger_date = settled_date
                self.rollover.last_settlement_total = settled_total
                self._set_last_settlement(settled_date, settled_total)
                self._load_current_ledger()
                messagebox.showinfo(
                    "结算完成",
                    f"✅ 本次总账总金额：￥{settled_total / AMOUNT_MULTIPLIER:.2f}\n"
                    "已开启新的今日账本"
                )
            except DatabaseError as e:
                messagebox.showerror("错误", f"❌ 清空失败：{str(e)}")

    def _show_animal_details(self, animal: str):
        """显示生肖详情"""
        animal_mapping = self.db.get_animal_mapping()
        numbers = animal_mapping.get(animal, [])

        # 收集该生肖所有号码的来源
        details = []
        total = 0
        for num in numbers:
            amount_int = self.current_totals.get(num, 0)
            if amount_int > 0:
                amount = amount_int / AMOUNT_MULTIPLIER
                sources = self.current_sources.get(num, [])
                details.append(f"号码 {num:02d}: ￥{amount:.2f}")
                if sources:
                    for src in sources:
                        details.append(f"  • {src}")
                total += amount_int

        if not details:
            messagebox.showinfo(
                f"{self.ANIMAL_EMOJI.get(animal, '')} {animal}",
                f"号码: {', '.join([str(n) for n in numbers])}\n\n暂无投注记录"
            )
        else:
            messagebox.showinfo(
                f"{self.ANIMAL_EMOJI.get(animal, '')} {animal}",
                f"号码: {', '.join([str(n) for n in numbers])}\n"
                f"总金额: ￥{total / AMOUNT_MULTIPLIER:.2f}\n\n"
                + '\n'.join(details)
            )

    def _open_history(self):
        """打开历史记录"""
        HistoryWindow(self, self.db, self.backup_manager, self.current_ledger.id)

    def _open_mapping(self):
        """打开生肖号码表设置"""
        MappingWindow(self, self.db, self._update_display)

    def _open_settlement(self):
        """打开开奖结算窗口"""
        from settlement import Settlement
        from ui.settlement_window import SettlementWindow

        settlement = Settlement(self.db)
        SettlementWindow(self, self.db, settlement)

    def _export_backup(self):
        """导出备份"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile=f"backup_hk_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

        if file_path:
            try:
                self.backup_manager.export_to_json(file_path)
                messagebox.showinfo("成功", f"✅ 已导出备份到：\n{file_path}")
            except BackupError as e:
                messagebox.showerror("错误", f"❌ 导出失败：{str(e)}")

    def _import_backup(self):
        """恢复备份"""
        if not messagebox.askyesno("警告", "恢复备份将清空当前所有数据！\n请确认已备份当前数据。\n\n是否继续？"):
            return

        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if file_path:
            try:
                safety_path = self.app_data_dir / (
                    f"pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                )
                self.backup_manager.export_to_json(str(safety_path))
                self.backup_manager.import_from_json(file_path)
                settlements = self.rollover.initialize()
                self._load_current_ledger()
                if settlements:
                    _, ledger_date, total = settlements[-1]
                    self._set_last_settlement(ledger_date, total)
                else:
                    self._load_last_settlement_display()
                messagebox.showinfo(
                    "成功",
                    "✅ 备份恢复成功！\n\n"
                    f"恢复前安全备份已保存到：\n{safety_path}"
                )
            except (BackupError, DatabaseError) as e:
                messagebox.showerror("错误", f"❌ 恢复失败：{str(e)}")

    def _run_selftest(self):
        """运行自检"""
        from tests.test_runner import run_safe_tests
        result = run_safe_tests()
        messagebox.showinfo("自检结果", result)

    def _schedule_rollover_check(self):
        """定时检查跨日"""
        # 每分钟检查一次
        rolled_over, new_date = self.rollover.check_and_rollover(self.current_ledger.id)
        if rolled_over:
            self._set_last_settlement(
                self.rollover.last_settled_ledger_date,
                self.rollover.last_settlement_total
            )
            messagebox.showinfo(
                "跨日结算",
                f"已结算{self.rollover.last_settled_ledger_date}账本\n"
                f"总账总金额：{self.rollover.last_settlement_total / AMOUNT_MULTIPLIER:.2f}\n\n"
                f"已新建{new_date}账本"
            )
            self._load_current_ledger()

        # 60秒后再次检查
        self.after(60000, self._schedule_rollover_check)