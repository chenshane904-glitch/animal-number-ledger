"""主窗口"""
import json
from datetime import datetime
from pathlib import Path
import customtkinter as ctk
from tkinter import messagebox, filedialog
from typing import Optional
from database import Database, DatabaseError
from daily_rollover import DailyRollover
from parser import InstructionParser, ParserError
from calculator import Calculator
from backup import BackupManager, BackupError
from constants import MIN_NUMBER, MAX_NUMBER, AMOUNT_MULTIPLIER
from ui.history_window import HistoryWindow
from ui.mapping_window import MappingWindow


class MainWindow(ctk.CTk):
    """主窗口"""

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

        # 设置窗口
        self.title("十二动物号码归纳器 v1.2.2")
        self.geometry("1200x800")

        # 初始化界面
        self._setup_ui()

        # 启动时先结算跨日遗留账本，再加载今天账本。
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
        # 顶部信息栏
        self.info_frame = ctk.CTkFrame(self)
        self.info_frame.pack(fill='x', padx=10, pady=5)

        self.date_label = ctk.CTkLabel(self.info_frame, text="", font=("Arial", 14, "bold"))
        self.date_label.pack(side='left', padx=10)

        self.ledger_label = ctk.CTkLabel(self.info_frame, text="", font=("Arial", 14))
        self.ledger_label.pack(side='left', padx=10)

        self.settlement_label = ctk.CTkLabel(
            self.info_frame,
            text="上次结算总账金额: --",
            font=("Arial", 14, "bold")
        )
        self.settlement_label.pack(side='right', padx=10)

        # 主容器（左侧28% 右侧72%）
        self.main_container = ctk.CTkFrame(self)
        self.main_container.pack(fill='both', expand=True, padx=10, pady=(5, 0))

        # 底部状态栏
        status_bar = ctk.CTkFrame(self, height=28, fg_color="#F0F0F0")
        status_bar.pack(fill='x', padx=10, pady=(0, 5))
        status_bar.pack_propagate(False)

        # 配置状态栏3列
        status_bar.grid_columnconfigure(0, weight=4)
        status_bar.grid_columnconfigure(1, weight=2)
        status_bar.grid_columnconfigure(2, weight=3)

        # 左侧提示
        ctk.CTkLabel(
            status_bar,
            text="提示：支持组合玩法、生肖、动物、号码混合输入，自动识别并累计。",
            font=("Arial", 9),
            text_color="#666666",
            anchor='w'
        ).grid(row=0, column=0, sticky='w', padx=10)

        # 中间状态
        ctk.CTkLabel(
            status_bar,
            text="状态：就绪",
            font=("Arial", 9),
            text_color="#666666",
            anchor='center'
        ).grid(row=0, column=1, sticky='ew')

        # 右侧说明
        ctk.CTkLabel(
            status_bar,
            text="赔付＝金额×47 | 盈利＝总下注－赔付 | v1.2.2 澳门版",
            font=("Arial", 9),
            text_color="#666666",
            anchor='e'
        ).grid(row=0, column=2, sticky='e', padx=10)


        # 配置grid布局权重：左侧窄 右侧宽
        self.main_container.grid_columnconfigure(0, weight=28, minsize=300)  # 左侧28%
        self.main_container.grid_columnconfigure(1, weight=72, minsize=800)  # 右侧72%，最小800px
        self.main_container.grid_rowconfigure(0, weight=1)

        # 左侧：操作区域
        self.left_frame = ctk.CTkFrame(self.main_container)
        self.left_frame.grid(row=0, column=0, sticky='nsew', padx=(0, 5))

        # 配置左侧区域的行权重
        self.left_frame.grid_rowconfigure(0, weight=42)  # 输入数据 42%
        self.left_frame.grid_rowconfigure(1, weight=23)  # 解析预览 23%
        self.left_frame.grid_rowconfigure(2, weight=20)  # 本次计算 20%
        self.left_frame.grid_rowconfigure(3, weight=15, minsize=120)  # 按钮区域 15%

        # === 1. 输入数据区域 (42%) ===
        input_container = ctk.CTkFrame(self.left_frame)
        input_container.grid(row=0, column=0, sticky='nsew', padx=5, pady=(5, 3))

        # 标题栏
        input_header = ctk.CTkFrame(input_container, height=28)
        input_header.pack(fill='x')
        input_header.pack_propagate(False)
        ctk.CTkLabel(input_header, text="输入数据（每行一笔）", font=("Arial", 11, "bold")).pack(side='left', padx=8, pady=4)
        ctk.CTkButton(input_header, text="清空", width=45, height=22, font=("Arial", 10),
                     command=self._clear_input, fg_color="#666666").pack(side='right', padx=8, pady=3)

        # 输入框
        self.input_text = ctk.CTkTextbox(input_container, font=("Consolas", 10))
        self.input_text.pack(fill='both', expand=True, padx=5, pady=(2, 5))
        self.input_text.bind('<KeyRelease>', lambda e: self._on_input_change())

        # === 2. 解析预览区域 (23%) ===
        preview_container = ctk.CTkFrame(self.left_frame)
        preview_container.grid(row=1, column=0, sticky='nsew', padx=5, pady=3)

        # 标题栏
        preview_header = ctk.CTkFrame(preview_container, height=28)
        preview_header.pack(fill='x')
        preview_header.pack_propagate(False)
        ctk.CTkLabel(preview_header, text="解析预览", font=("Arial", 11, "bold")).pack(side='left', padx=8, pady=4)
        ctk.CTkButton(preview_header, text="清空", width=45, height=22, font=("Arial", 10),
                     command=self._clear_preview, fg_color="#666666").pack(side='right', padx=8, pady=3)

        # 预览框
        self.preview_text = ctk.CTkTextbox(preview_container, font=("Consolas", 9))
        self.preview_text.pack(fill='both', expand=True, padx=5, pady=(2, 5))
        self.preview_text.configure(state='disabled')

        # === 3. 本次计算区域 (20%) ===
        calc_container = ctk.CTkFrame(self.left_frame)
        calc_container.grid(row=2, column=0, sticky='nsew', padx=5, pady=3)

        # 标题栏
        calc_header = ctk.CTkFrame(calc_container, height=28)
        calc_header.pack(fill='x')
        calc_header.pack_propagate(False)
        ctk.CTkLabel(calc_header, text="本次计算", font=("Arial", 11, "bold")).pack(side='left', padx=8, pady=4)
        ctk.CTkButton(calc_header, text="清空", width=45, height=22, font=("Arial", 10),
                     command=self._clear_calc, fg_color="#666666").pack(side='right', padx=8, pady=3)

        # 计算框
        self.calc_text = ctk.CTkTextbox(calc_container, font=("Consolas", 10, "bold"))
        self.calc_text.pack(fill='both', expand=True, padx=5, pady=(2, 5))
        self.calc_text.configure(state='disabled')

        # === 4. 按钮区域 (15%) ===
        button_container = ctk.CTkFrame(self.left_frame)
        button_container.grid(row=3, column=0, sticky='nsew', padx=5, pady=(3, 5))

        # 配置4列均分
        for i in range(4):
            button_container.grid_columnconfigure(i, weight=1)

        # 第一行按钮
        self.confirm_btn = ctk.CTkButton(
            button_container, text="确认追加", command=self._confirm_add,
            fg_color="#1E88E5", height=28, font=("Arial", 10), state='disabled'
        )
        self.confirm_btn.grid(row=0, column=0, sticky='ew', padx=2, pady=2)

        self.undo_btn = ctk.CTkButton(
            button_container, text="撤销最近一次", command=self._undo_last,
            fg_color="#1E88E5", height=28, font=("Arial", 10)
        )
        self.undo_btn.grid(row=0, column=1, sticky='ew', padx=2, pady=2)

        self.clear_input_btn = ctk.CTkButton(
            button_container, text="清空输入", command=self._clear_input,
            fg_color="#1E88E5", height=28, font=("Arial", 10)
        )
        self.clear_input_btn.grid(row=0, column=2, sticky='ew', padx=2, pady=2)

        self.clear_today_btn = ctk.CTkButton(
            button_container, text="结算并清空今日", command=self._clear_today,
            fg_color="#1E88E5", height=28, font=("Arial", 9)
        )
        self.clear_today_btn.grid(row=0, column=3, sticky='ew', padx=2, pady=2)

        # 第二行按钮
        self.history_btn = ctk.CTkButton(
            button_container, text="历史记录", command=self._open_history,
            fg_color="#1E88E5", height=28, font=("Arial", 10)
        )
        self.history_btn.grid(row=1, column=0, sticky='ew', padx=2, pady=2)

        self.settlement_btn = ctk.CTkButton(
            button_container, text="开奖结算", command=self._open_settlement,
            fg_color="#FF9800", height=28, font=("Arial", 10)
        )
        self.settlement_btn.grid(row=1, column=1, sticky='ew', padx=2, pady=2)

        self.mapping_btn = ctk.CTkButton(
            button_container, text="动物号码表", command=self._open_mapping,
            fg_color="#1E88E5", height=28, font=("Arial", 10)
        )
        self.mapping_btn.grid(row=1, column=2, sticky='ew', padx=2, pady=2)

        self.export_btn = ctk.CTkButton(
            button_container, text="导出备份", command=self._export_backup,
            fg_color="#1E88E5", height=28, font=("Arial", 10)
        )
        self.export_btn.grid(row=1, column=3, sticky='ew', padx=2, pady=2)

        # 第三行按钮
        self.import_btn = ctk.CTkButton(
            button_container, text="恢复备份", command=self._import_backup,
            fg_color="#1E88E5", height=28, font=("Arial", 10)
        )
        self.import_btn.grid(row=2, column=0, sticky='ew', padx=2, pady=2)

        self.test_btn = ctk.CTkButton(
            button_container, text="运行自检", command=self._run_selftest,
            fg_color="#1E88E5", height=28, font=("Arial", 10)
        )
        self.test_btn.grid(row=2, column=1, sticky='ew', padx=2, pady=2)

        help_btn = ctk.CTkButton(
            button_container, text="使用帮助", command=self._show_help,
            fg_color="#1E88E5", height=28, font=("Arial", 10)
        )
        help_btn.grid(row=2, column=2, sticky='ew', padx=2, pady=2)


        # 右侧：结果显示
        self.right_frame = ctk.CTkFrame(self.main_container)
        self.right_frame.grid(row=0, column=1, sticky='nsew', padx=(5, 0))

        # 顶部统计区域：四个统计栏横向排列
        stats_container = ctk.CTkFrame(self.right_frame, height=70)
        stats_container.pack(fill='x', padx=10, pady=(10, 5))
        stats_container.pack_propagate(False)

        # 配置4列均分
        for i in range(4):
            stats_container.grid_columnconfigure(i, weight=1)

        # 统计栏1：今日总下注（蓝色）
        stats1 = ctk.CTkFrame(stats_container)
        stats1.grid(row=0, column=0, sticky='nsew', padx=2, pady=5)
        ctk.CTkLabel(stats1, text="今日总下注", font=("Arial", 12)).pack(pady=(5, 0))
        self.total_label = ctk.CTkLabel(
            stats1,
            text="0.00",
            font=("Arial", 20, "bold"),
            text_color="#0066CC"
        )
        self.total_label.pack(pady=(0, 5))

        # 统计栏2：非零号码（绿色）
        stats2 = ctk.CTkFrame(stats_container)
        stats2.grid(row=0, column=1, sticky='nsew', padx=2, pady=5)
        ctk.CTkLabel(stats2, text="非零号码", font=("Arial", 12)).pack(pady=(5, 0))
        self.count_label = ctk.CTkLabel(
            stats2,
            text="0",
            font=("Arial", 20, "bold"),
            text_color="#00AA00"
        )
        self.count_label.pack(pady=(0, 5))

        # 统计栏3：最高下注号码（红色）
        stats3 = ctk.CTkFrame(stats_container)
        stats3.grid(row=0, column=2, sticky='nsew', padx=2, pady=5)
        ctk.CTkLabel(stats3, text="最高下注号码", font=("Arial", 12)).pack(pady=(5, 0))
        self.max_num_label = ctk.CTkLabel(
            stats3,
            text="--",
            font=("Arial", 20, "bold"),
            text_color="#DD0000"
        )
        self.max_num_label.pack(pady=(0, 5))

        # 统计栏4：最高金额（红色）
        stats4 = ctk.CTkFrame(stats_container)
        stats4.grid(row=0, column=3, sticky='nsew', padx=2, pady=5)
        ctk.CTkLabel(stats4, text="最高金额", font=("Arial", 12)).pack(pady=(5, 0))
        self.max_amount_label = ctk.CTkLabel(
            stats4,
            text="0.00",
            font=("Arial", 20, "bold"),
            text_color="#DD0000"
        )
        self.max_amount_label.pack(pady=(0, 5))

        # 表格区域
        table_frame = ctk.CTkFrame(self.right_frame)
        table_frame.pack(fill='both', expand=True, padx=10, pady=(5, 10))

        # 表头（固定在顶部，深蓝色背景）
        header_frame = ctk.CTkFrame(table_frame, fg_color="#003366", height=35)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)

        # 配置表头列宽
        header_frame.grid_columnconfigure(0, weight=15)  # 号码 15%
        header_frame.grid_columnconfigure(1, weight=25)  # 金额 25%
        header_frame.grid_columnconfigure(2, weight=28)  # 赔付 28%
        header_frame.grid_columnconfigure(3, weight=32)  # 盈利 32%

        # 表头标签
        ctk.CTkLabel(
            header_frame,
            text="号码",
            font=("Arial", 14, "bold"),
            text_color="white"
        ).grid(row=0, column=0, sticky='ew', padx=5)

        ctk.CTkLabel(
            header_frame,
            text="金额",
            font=("Arial", 14, "bold"),
            text_color="white"
        ).grid(row=0, column=1, sticky='e', padx=5)

        ctk.CTkLabel(
            header_frame,
            text="赔付（金额×47）",
            font=("Arial", 14, "bold"),
            text_color="white"
        ).grid(row=0, column=2, sticky='e', padx=5)

        ctk.CTkLabel(
            header_frame,
            text="盈利（总下注－赔付）",
            font=("Arial", 14, "bold"),
            text_color="white"
        ).grid(row=0, column=3, sticky='e', padx=5)

        # 表格内容区域（可滚动）
        self.results_scroll = ctk.CTkScrollableFrame(table_frame)
        self.results_scroll.pack(fill='both', expand=True)

        # 初始化存储
        self.number_labels = {}
        self.number_frames = {}

    def _load_current_ledger(self):
        """加载当前账本"""
        current_date = self.rollover.get_current_date_str()
        self.current_ledger = self.db.get_or_create_active_ledger(current_date)

        # 更新显示
        self._update_display()

    def _set_last_settlement(self, ledger_date: str, total_integer: int):
        """更新最近一次结算金额显示。"""
        self.settlement_label.configure(
            text=(
                f"上次结算 ({ledger_date}) 总账金额: "
                f"{total_integer / AMOUNT_MULTIPLIER:.2f}"
            )
        )

    def _load_last_settlement_display(self):
        """从历史账本加载最近一次结算金额。"""
        for ledger in self.db.get_all_ledgers():
            if ledger.status == 'archived' and ledger.settled_total_integer is not None:
                self._set_last_settlement(
                    ledger.ledger_date,
                    ledger.settled_total_integer
                )
                return
        self.settlement_label.configure(text="上次结算总账金额: --")

    def _update_display(self):
        """更新显示"""
        # 更新日期和账本信息
        self.date_label.configure(text=f"日期: {self.current_ledger.ledger_date}")
        self.ledger_label.configure(text=f"账本编号: {self.current_ledger.sequence_number}")

        # 获取当前累计
        self.current_totals = self.db.get_ledger_totals(self.current_ledger.id)
        self.current_sources = self.db.get_ledger_sources(self.current_ledger.id)

        # 找出最大金额（只考虑大于0的总数）
        max_amount_int = 0
        for amount_int in self.current_totals.values():
            if amount_int > max_amount_int:
                max_amount_int = amount_int

        # 更新号码显示（按金额排序）
        total = 0
        non_zero = 0

        # 创建排序列表：(号码, 金额整数)
        sorted_numbers = []
        for i in range(MIN_NUMBER, MAX_NUMBER + 1):
            amount_int = self.current_totals.get(i, 0)
            sorted_numbers.append((i, amount_int))

        # 排序：金额从大到小，金额相同按号码从小到大
        sorted_numbers.sort(key=lambda x: (-x[1], x[0]))

        # 清空当前显示
        for widget in self.results_scroll.winfo_children():
            widget.destroy()

        # 重新创建号码标签（按排序顺序）
        self.number_labels = {}
        self.number_frames = {}

        # 计算总下注（先遍历一遍）
        total = 0
        non_zero = 0
        for i in range(MIN_NUMBER, MAX_NUMBER + 1):
            amount_int = self.current_totals.get(i, 0)
            total += amount_int
            if amount_int > 0:
                non_zero += 1

        # 找出最大金额的号码
        max_num = None
        max_amount_int = 0
        for num, amount_int in sorted_numbers:
            if amount_int > max_amount_int:
                max_amount_int = amount_int
                max_num = num

        # 创建表格行
        for idx, (num, amount_int) in enumerate(sorted_numbers):
            amount = amount_int / AMOUNT_MULTIPLIER

            # 确定排名色条颜色
            rank = idx + 1
            if rank <= 10:
                rank_color = "#DD0000"  # 红色
            elif rank <= 20:
                rank_color = "#0066CC"  # 蓝色
            elif rank <= 30:
                rank_color = "#FF8800"  # 橙色
            elif rank <= 40:
                rank_color = "#00AA00"  # 绿色
            else:
                rank_color = "#888888"  # 灰色

            # 行容器（pack到scrollable frame中）
            row_frame = ctk.CTkFrame(self.results_scroll, height=32)
            row_frame.pack(fill='x', pady=1)
            row_frame.pack_propagate(False)

            # 配置列宽
            row_frame.grid_columnconfigure(0, weight=5, minsize=5)    # 色条
            row_frame.grid_columnconfigure(1, weight=10, minsize=40)  # 号码
            row_frame.grid_columnconfigure(2, weight=25)              # 金额
            row_frame.grid_columnconfigure(3, weight=28)              # 赔付
            row_frame.grid_columnconfigure(4, weight=32)              # 盈利

            # 排名色条
            color_bar = ctk.CTkFrame(row_frame, width=5, fg_color=rank_color)
            color_bar.grid(row=0, column=0, sticky='ns', padx=0)

            # 号码（居中）
            num_label = ctk.CTkLabel(
                row_frame,
                text=f"{num:02d}",
                font=("Arial", 13, "bold"),
                anchor='center'
            )
            num_label.grid(row=0, column=1, sticky='nsew', padx=3, pady=5)

            # 金额（右对齐）
            amount_label = ctk.CTkLabel(
                row_frame,
                text=f"{amount:,.2f}",
                font=("Arial", 13),
                anchor='e'
            )
            amount_label.grid(row=0, column=2, sticky='nsew', padx=5, pady=5)

            # 赔付（右对齐，占位）
            payout_label = ctk.CTkLabel(
                row_frame,
                text="--",
                font=("Arial", 13),
                anchor='e'
            )
            payout_label.grid(row=0, column=3, sticky='nsew', padx=5, pady=5)

            # 盈利（右对齐，占位）
            profit_label = ctk.CTkLabel(
                row_frame,
                text="--",
                font=("Arial", 13, "bold"),
                anchor='e'
            )
            profit_label.grid(row=0, column=4, sticky='nsew', padx=5, pady=5)

            # 点击显示来源
            row_frame.bind('<Button-1>', lambda e, n=num: self._show_sources(n))
            num_label.bind('<Button-1>', lambda e, n=num: self._show_sources(n))
            amount_label.bind('<Button-1>', lambda e, n=num: self._show_sources(n))
            payout_label.bind('<Button-1>', lambda e, n=num: self._show_sources(n))
            profit_label.bind('<Button-1>', lambda e, n=num: self._show_sources(n))

            # 保存引用
            self.number_labels[num] = {
                'amount': amount_label,
                'payout': payout_label,
                'profit': profit_label
            }
            self.number_frames[num] = row_frame

        # 更新统计
        self.total_label.configure(text=f"{total / AMOUNT_MULTIPLIER:,.2f}")
        self.count_label.configure(text=f"{non_zero}")

        # 更新最高下注号码和金额
        if max_num is not None:
            self.max_num_label.configure(text=f"{max_num:02d}")
            self.max_amount_label.configure(text=f"{max_amount_int / AMOUNT_MULTIPLIER:,.2f}")
        else:
            self.max_num_label.configure(text="--")
            self.max_amount_label.configure(text="0.00")

        # 实时风险预览：更新所有号码的赔付和盈利
        self._update_risk_preview(total)

    def _update_risk_preview(self, total_bet_int):
        """
        实时风险预览：计算并更新每个号码的风险数据

        参数:
            total_bet_int: 当天总下注金额（整数，已乘以AMOUNT_MULTIPLIER）
        """
        total_bet = total_bet_int / AMOUNT_MULTIPLIER

        for num in range(MIN_NUMBER, MAX_NUMBER + 1):
            if num not in self.number_labels:
                continue

            labels = self.number_labels[num]
            row_frame = self.number_frames[num]

            # 获取本号下注金额
            num_bet_int = self.current_totals.get(num, 0)
            num_bet = num_bet_int / AMOUNT_MULTIPLIER

            # 计算中奖赔付：本号下注 × 47
            payout = num_bet * 47

            # 计算预计利润：总下注 - 中奖赔付
            profit = total_bet - payout

            # 更新金额显示（已在创建时设置）
            labels['amount'].configure(text=f"{num_bet:,.2f}")

            # 更新赔付显示
            labels['payout'].configure(text=f"{payout:,.2f}")

            # 更新盈利显示，根据正负设置颜色
            if profit >= 0:
                profit_text = f"+{profit:,.2f}"
                profit_color = "#00AA00"  # 绿色
            else:
                profit_text = f"{profit:,.2f}"  # 负数自带减号
                profit_color = "#DD0000"  # 红色

            labels['profit'].configure(text=profit_text, text_color=profit_color)


    def _on_input_change(self):
        """输入变化时解析预览"""
        input_text = self.input_text.get("1.0", "end-1c").strip()

        if not input_text:
            self._clear_preview()
            self.confirm_btn.configure(state='disabled')
            return

        # 解析
        try:
            animal_mapping = self.db.get_animal_mapping()
            parser = InstructionParser(animal_mapping)
            instructions = parser.parse_input(input_text)

            # 显示解析预览
            preview_lines = []
            has_warning = False
            for inst in instructions:
                if inst.target_type == 'number':
                    targets_str = ', '.join(inst.targets)
                else:
                    targets_str = ', '.join(inst.targets) + ' (各号)'

                amount = inst.amount_integer / AMOUNT_MULTIPLIER
                line = f"第{inst.source_line}行: {targets_str} → {amount:.2f}"

                if inst.warning:
                    line += f" ⚠️ {inst.warning}"
                    has_warning = True

                preview_lines.append(line)

            self.preview_text.configure(state='normal')
            self.preview_text.delete("1.0", "end")
            self.preview_text.insert("1.0", '\n'.join(preview_lines))
            self.preview_text.configure(state='disabled')

            # 计算本次结果
            calculator = Calculator(animal_mapping)
            result = calculator.calculate(instructions, {i: 0 for i in range(MIN_NUMBER, MAX_NUMBER + 1)})

            calc_lines = []
            for i in range(MIN_NUMBER, MAX_NUMBER + 1):
                if result.number_amounts[i] > 0:
                    amount = result.number_amounts[i] / AMOUNT_MULTIPLIER
                    calc_lines.append(f"{i:02d}: {amount:.2f}")

            total = result.total_amount / AMOUNT_MULTIPLIER
            calc_lines.append(f"\n本次总数: {total:.2f}")
            calc_lines.append(f"涉及号码: {result.non_zero_count}")

            self.calc_text.configure(state='normal')
            self.calc_text.delete("1.0", "end")
            self.calc_text.insert("1.0", '\n'.join(calc_lines))
            self.calc_text.configure(state='disabled')

            # 启用确认按钮
            self.confirm_btn.configure(state='normal')

        except ParserError as e:
            # 显示错误
            self.preview_text.configure(state='normal')
            self.preview_text.delete("1.0", "end")
            self.preview_text.insert("1.0", f"❌ 解析错误：\n{str(e)}")
            self.preview_text.configure(state='disabled')

            self._clear_calc()
            self.confirm_btn.configure(state='disabled')

    def _clear_preview(self):
        """清空预览"""
        self.preview_text.configure(state='normal')
        self.preview_text.delete("1.0", "end")
        self.preview_text.configure(state='disabled')

    def _clear_calc(self):
        """清空计算"""
        self.calc_text.configure(state='normal')
        self.calc_text.delete("1.0", "end")
        self.calc_text.configure(state='disabled')

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
            self._clear_preview()
            self._clear_calc()

            # 刷新显示
            self._update_display()

            messagebox.showinfo("成功", "已追加到账本")

        except Exception as e:
            messagebox.showerror("错误", f"追加失败：{str(e)}")

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
                messagebox.showinfo("成功", "已撤销")
            except DatabaseError as e:
                messagebox.showerror("错误", f"撤销失败：{str(e)}")

    def _clear_input(self):
        """清空输入"""
        self.input_text.delete("1.0", "end")
        self._clear_preview()
        self._clear_calc()
        self.confirm_btn.configure(state='disabled')

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
                    f"本次总账总金额：{settled_total / AMOUNT_MULTIPLIER:.2f}\n"
                    "已开启新的今日账本"
                )
            except DatabaseError as e:
                messagebox.showerror("错误", f"清空失败：{str(e)}")

    def _show_sources(self, number: int):
        """显示号码来源"""
        sources = self.current_sources.get(number, [])
        if not sources:
            messagebox.showinfo("来源", f"号码 {number:02d} 暂无来源")
            return

        source_text = f"号码 {number:02d} 的来源：\n\n" + '\n'.join(f"• {s}" for s in sources)
        messagebox.showinfo("来源", source_text)

    def _open_history(self):
        """打开历史记录"""
        HistoryWindow(self, self.db, self.backup_manager, self.current_ledger.id)

    def _open_mapping(self):
        """打开动物号码表设置"""
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
            initialfile=f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

        if file_path:
            try:
                self.backup_manager.export_to_json(file_path)
                messagebox.showinfo("成功", f"已导出备份到：\n{file_path}")
            except BackupError as e:
                messagebox.showerror("错误", f"导出失败：{str(e)}")

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
                    "备份恢复成功！\n\n"
                    f"恢复前安全备份已保存到：\n{safety_path}"
                )
            except (BackupError, DatabaseError) as e:
                messagebox.showerror("错误", f"恢复失败：{str(e)}")

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

    def _show_help(self):
        """显示使用帮助"""
        help_text = """
【使用帮助】

1. 输入格式：
   - 单号码：01 100
   - 多号码：01 02 03 100
   - 范围：01-05 100
   - 动物：鼠 100
   - 生肖混合：鼠 牛 虎 100

2. 实时风险预览：
   - 每个号码显示：金额、赔付、盈利
   - 赔付 = 金额 × 47
   - 盈利 = 总下注 - 赔付
   - 绿色表示盈利，红色表示亏损

3. 快捷操作：
   - 确认追加：保存当前输入
   - 撤销：取消最近一次追加
   - 开奖结算：输入中奖号码并结算
   - 历史记录：查看往期账本

支持的动物：鼠牛虎兔龙蛇马羊猴鸡狗猪
        """
        messagebox.showinfo("使用帮助", help_text)
