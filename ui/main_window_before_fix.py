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
from ui.result_canvas_table import ResultCanvasTable


class MainWindow(ctk.CTk):
    """主窗口"""

    def __init__(self, db: Database, rollover: DailyRollover, app_data_dir: Path):
        super().__init__()

        self.db = db
        self.rollover = rollover
        self.app_data_dir = app_data_dir
        self.backup_manager = BackupManager(db)

        # 当前玩法模式（默认号码模式）
        from play_mode import PlayMode
        self.current_mode = PlayMode.NUMBER

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

        # 模式切换按钮（在结算信息右侧）
        mode_frame = ctk.CTkFrame(self.info_frame, fg_color="transparent")
        mode_frame.pack(side='right', padx=(0, 20))

        from play_mode import PlayMode, PLAY_MODE_NAMES

        self.mode_number_btn = ctk.CTkButton(
            mode_frame,
            text=PLAY_MODE_NAMES[PlayMode.NUMBER],
            width=90,
            height=32,
            fg_color="#1E88E5",
            command=lambda: self._switch_mode(PlayMode.NUMBER)
        )
        self.mode_number_btn.pack(side='left', padx=2)

        self.mode_animal_btn = ctk.CTkButton(
            mode_frame,
            text=PLAY_MODE_NAMES[PlayMode.ANIMAL],
            width=90,
            height=32,
            fg_color="#666666",
            command=lambda: self._switch_mode(PlayMode.ANIMAL)
        )
        self.mode_animal_btn.pack(side='left', padx=2)

        # 主容器（左侧38% 右侧62%）
        self.main_container = ctk.CTkFrame(self)
        self.main_container.pack(fill='both', expand=True, padx=0, pady=0)

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


        # 配置grid布局权重：左侧窄 右侧宽（只配置两列，按权重分配）
        self.main_container.grid_columnconfigure(0, weight=38, minsize=420)  # 左侧38%
        self.main_container.grid_columnconfigure(1, weight=62, minsize=700)  # 右侧62%
        self.main_container.grid_rowconfigure(0, weight=1)

        # 左侧：操作区域
        self.left_frame = ctk.CTkFrame(self.main_container)
        self.left_frame.grid(row=0, column=0, sticky='nsew', padx=(8, 4), pady=8)

        # 配置左侧区域的列权重（让内容填满宽度）
        self.left_frame.grid_columnconfigure(0, weight=1)

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


        # 右侧：结果显示容器
        self.right_frame = ctk.CTkFrame(self.main_container)
        self.right_frame.grid(row=0, column=1, sticky='nsew', padx=(4, 8), pady=8)

        # 配置右侧区域的列权重（让内容填满宽度）
        self.right_frame.grid_columnconfigure(0, weight=1)
        # 配置右侧区域的行权重（让表格可扩展）
        self.right_frame.grid_rowconfigure(0, weight=0)  # 统计区固定高度
        self.right_frame.grid_rowconfigure(1, weight=1)  # 表格可扩展

        # 加载默认的号码模式面板
        self._load_number_mode_panel()

        # 临时调试边框
        self.left_frame.configure(border_width=2, border_color="blue")
        self.right_frame.configure(border_width=2, border_color="red")
        self.main_container.configure(border_width=2, border_color="green")

        # 延迟诊断布局
        self.after(500, self._diagnose_layout)

    def _load_number_mode_panel(self):
        """加载号码模式面板（现有功能，不修改逻辑）"""
        # 顶部统计区域：四个统计栏横向排列
        stats_container = ctk.CTkFrame(self.right_frame, height=70)
        stats_container.grid(row=0, column=0, sticky='ew', padx=0, pady=(5, 5))
        stats_container.grid_propagate(False)

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

        # 表格区域 - 使用ResultCanvasTable组件
        self.result_table = ResultCanvasTable(self.right_frame)
        self.result_table.grid(row=1, column=0, sticky='nsew', padx=0, pady=(5, 5))

    def _load_animal_mode_panel(self):
        """加载平特模式面板"""
        from play_mode_config import get_odds, PlayMode
        from ui.animal_result_table import AnimalResultTable

        # 获取平特模式赔率
        odds = get_odds(PlayMode.ANIMAL)

        # 顶部统计区域：四个统计栏横向排列
        stats_container = ctk.CTkFrame(self.right_frame, height=70)
        stats_container.grid(row=0, column=0, sticky='ew', padx=0, pady=(5, 5))
        stats_container.grid_propagate(False)

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

        # 统计栏2：非零生肖（绿色）
        stats2 = ctk.CTkFrame(stats_container)
        stats2.grid(row=0, column=1, sticky='nsew', padx=2, pady=5)
        ctk.CTkLabel(stats2, text="非零生肖", font=("Arial", 12)).pack(pady=(5, 0))
        self.count_label = ctk.CTkLabel(
            stats2,
            text="0",
            font=("Arial", 20, "bold"),
            text_color="#00AA00"
        )
        self.count_label.pack(pady=(0, 5))

        # 统计栏3：最高下注生肖（橙色）
        stats3 = ctk.CTkFrame(stats_container)
        stats3.grid(row=0, column=2, sticky='nsew', padx=2, pady=5)
        ctk.CTkLabel(stats3, text="最高下注生肖", font=("Arial", 12)).pack(pady=(5, 0))
        self.max_num_label = ctk.CTkLabel(
            stats3,
            text="--",
            font=("Arial", 20, "bold"),
            text_color="#FF9800"
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

        # 表格区域 - 使用AnimalResultTable组件
        self.result_table = AnimalResultTable(self.right_frame, odds)
        self.result_table.grid(row=1, column=0, sticky='nsew', padx=0, pady=(5, 5))

    def _switch_mode(self, mode):
        """
        切换玩法模式

        Args:
            mode: PlayMode枚举
        """
        from play_mode import PlayMode

        if self.current_mode == mode:
            return  # 已经是当前模式，不需要切换

        self.current_mode = mode

        # 更新按钮状态
        if mode == PlayMode.NUMBER:
            self.mode_number_btn.configure(fg_color="#1E88E5")
            self.mode_animal_btn.configure(fg_color="#666666")
        else:
            self.mode_number_btn.configure(fg_color="#666666")
            self.mode_animal_btn.configure(fg_color="#1E88E5")

        # 销毁右侧所有widget
        for widget in self.right_frame.winfo_children():
            widget.destroy()

        # 重新配置grid权重
        self.right_frame.grid_columnconfigure(0, weight=1)
        self.right_frame.grid_rowconfigure(0, weight=0)
        self.right_frame.grid_rowconfigure(1, weight=1)

        # 加载对应面板
        if mode == PlayMode.NUMBER:
            self._load_number_mode_panel()
        else:
            self._load_animal_mode_panel()

        # 刷新显示
        self._update_display()

    def _diagnose_layout(self):
        """诊断布局间隙"""
        self.update_idletasks()

        # 获取坐标
        main_w = self.main_container.winfo_width()
        left_x = self.left_frame.winfo_x()
        left_w = self.left_frame.winfo_width()
        right_x = self.right_frame.winfo_x()
        right_w = self.right_frame.winfo_width()

        left_end = left_x + left_w
        gap = right_x - left_end

        print("\n=== 布局诊断 ===")
        print(f"主容器宽度: {main_w}px")
        print(f"左侧区域: x={left_x}, width={left_w}, end={left_end}")
        print(f"右侧区域: x={right_x}, width={right_w}")
        print(f"实际间隙: {gap}px")

        # 列出所有子控件
        print("\n主容器子控件:")
        for widget in self.main_container.winfo_children():
            info = widget.grid_info() if widget.winfo_manager() == "grid" else {}
            print(f"  {widget.winfo_class()}: column={info.get('column', '?')}, {widget.winfo_geometry()}")

        # 检查间隙
        if gap > 16:
            print(f"\n[WARNING] 左右间隙过大 ({gap}px > 16px)")
        elif gap < 0:
            print(f"\n[WARNING] 左右区域重叠 ({gap}px < 0)")
        else:
            print(f"\n[OK] 间隙正常 ({gap}px)")

        print("=== 诊断完成 ===\n")

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

    def _calculate_risk_rows(self, totals_dict, total_bet_int):
        """
        统一计算所有号码的风险数据

        参数:
            totals_dict: {号码: 金额整数} 字典
            total_bet_int: 总下注金额整数

        返回:
            已排序的行数据列表，每行包含 {number, amount, payout, profit}
        """
        total_bet = total_bet_int / AMOUNT_MULTIPLIER

        # 创建所有号码的行数据
        rows = []
        for num in range(MIN_NUMBER, MAX_NUMBER + 1):
            amount_int = totals_dict.get(num, 0)
            amount = amount_int / AMOUNT_MULTIPLIER
            payout = amount * 47
            profit = total_bet - payout

            rows.append({
                'number': num,
                'amount': amount,
                'payout': payout,
                'profit': profit
            })

        # 排序：金额从大到小，金额相同按号码从小到大
        rows.sort(key=lambda x: (-x['amount'], x['number']))

        return rows

    def _update_display(self):
        """更新显示"""
        from play_mode import PlayMode

        # 更新日期和账本信息
        self.date_label.configure(text=f"日期: {self.current_ledger.ledger_date}")
        self.ledger_label.configure(text=f"账本编号: {self.current_ledger.sequence_number}")

        # 根据当前模式更新不同的显示
        if self.current_mode == PlayMode.NUMBER:
            self._update_number_mode_display()
        else:
            self._update_animal_mode_display()

    def _update_number_mode_display(self):
        """更新号码模式显示（保持原有逻辑不变）"""
        # 获取当前累计
        self.current_totals = self.db.get_ledger_totals(self.current_ledger.id)
        self.current_sources = self.db.get_ledger_sources(self.current_ledger.id)

        # 计算总下注和非零号码
        total = 0
        non_zero = 0
        for i in range(MIN_NUMBER, MAX_NUMBER + 1):
            amount_int = self.current_totals.get(i, 0)
            total += amount_int
            if amount_int > 0:
                non_zero += 1

        # 找出最大金额的号码（金额相同时取号码小的）
        max_num = None
        max_amount_int = 0
        for num in range(MIN_NUMBER, MAX_NUMBER + 1):
            amount_int = self.current_totals.get(num, 0)
            if amount_int > max_amount_int:
                max_amount_int = amount_int
                max_num = num

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

        # 计算所有行数据并更新表格
        rows = self._calculate_risk_rows(self.current_totals, total)
        self.result_table.set_rows(rows, total / AMOUNT_MULTIPLIER)

    def _update_animal_mode_display(self):
        """更新平特模式显示"""
        from play_mode_config import get_animals_list, PlayMode
        from calculator_factory import CalculatorFactory

        # 获取当前累计（号码维度）
        self.current_totals = self.db.get_ledger_totals(self.current_ledger.id)
        self.current_sources = self.db.get_ledger_sources(self.current_ledger.id)

        # 获取动物映射和计算器
        animal_mapping = self.db.get_animal_mapping()
        calculator = CalculatorFactory.get_calculator(PlayMode.NUMBER, animal_mapping)

        # 转换为生肖维度
        animals = get_animals_list(PlayMode.ANIMAL)
        animal_amounts = {animal: 0 for animal in animals}

        # 从号码累计转换为生肖累计
        for num, amount_int in self.current_totals.items():
            animal = calculator.number_to_animal.get(str(num).zfill(2))
            if animal and animal in animal_amounts:
                animal_amounts[animal] += amount_int

        # 计算统计
        total = sum(animal_amounts.values())
        non_zero = sum(1 for amt in animal_amounts.values() if amt > 0)

        # 找出最大金额的生肖
        max_animal = "--"
        max_amount_int = 0
        for animal, amount_int in animal_amounts.items():
            if amount_int > max_amount_int:
                max_amount_int = amount_int
                max_animal = animal

        # 更新统计
        self.total_label.configure(text=f"{total / AMOUNT_MULTIPLIER:,.2f}")
        self.count_label.configure(text=f"{non_zero}")
        self.max_num_label.configure(text=max_animal)
        self.max_amount_label.configure(text=f"{max_amount_int / AMOUNT_MULTIPLIER:,.2f}")

        # 更新表格
        self.result_table.update_data(animal_amounts, total)


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

            # 根据当前模式获取计算器
            from calculator_factory import CalculatorFactory
            calculator = CalculatorFactory.get_calculator(self.current_mode, animal_mapping)

            # 计算本次结果
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

            # 根据当前模式获取计算器
            from calculator_factory import CalculatorFactory
            calculator = CalculatorFactory.get_calculator(self.current_mode, animal_mapping)

            # 计算
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

            batch_id = self.db.add_batch_with_allocations(
                self.current_ledger.id,
                batch,
                animal_mapping
            )

            # 保存输入历史记录（传入当前玩法模式）
            self._save_input_history(
                batch_id,
                input_text,
                instructions,
                result,
                animal_mapping,
                str(self.current_mode)
            )

            # 清空输入
            self.input_text.delete("1.0", "end")
            self._clear_preview()
            self._clear_calc()

            # 刷新显示
            self._update_display()

            messagebox.showinfo("成功", "已追加到账本")

        except Exception as e:
            # 打印完整的错误堆栈
            import traceback
            print("\n" + "="*60)
            print("追加失败 - 完整错误堆栈:")
            print("="*60)
            traceback.print_exc()
            print("="*60 + "\n")
            messagebox.showerror("错误", f"追加失败：{str(e)}")

    def _save_input_history(self, batch_id, raw_input, instructions, result, animal_mapping, play_mode='number'):
        """保存输入历史记录 - 失败时抛出异常"""
        from datetime import datetime, timedelta
        import os

        # 打印数据库路径
        print(f"[HISTORY] 数据库路径: {os.path.abspath(self.db.db_path)}")
        print(f"[HISTORY] 当前账本ID: {self.current_ledger.id}")
        print(f"[HISTORY] 批次ID: {batch_id}")
        print(f"[HISTORY] 原始输入: {raw_input}")
        print(f"[HISTORY] 原始输入类型: {type(raw_input)}")
        print(f"[HISTORY] 玩法模式: {play_mode}")

        # 计算当前周起始日期（周一）
        today = datetime.now()
        days_since_monday = today.weekday()
        week_start = today - timedelta(days=days_since_monday)
        week_start_str = week_start.strftime('%Y-%m-%d')

        # 生成解析摘要
        print(f"[HISTORY] 开始生成解析摘要...")
        parsed_summary = self._generate_parsed_summary(instructions, animal_mapping)
        print(f"[HISTORY] 解析摘要: {parsed_summary}")
        print(f"[HISTORY] 解析摘要类型: {type(parsed_summary)}")

        # 生成展开项
        print(f"[HISTORY] 开始生成展开项...")
        expanded_items = self._generate_expanded_items(result)
        print(f"[HISTORY] 展开项数量: {len(expanded_items)}")
        print(f"[HISTORY] 展开项类型: {type(expanded_items)}")
        if expanded_items:
            print(f"[HISTORY] 第一项: {expanded_items[0]}")
            print(f"[HISTORY] 第一项类型: {type(expanded_items[0])}")

        # 类型检查
        assert isinstance(raw_input, str), f"raw_input必须是str，实际是{type(raw_input)}"
        assert isinstance(parsed_summary, str), f"parsed_summary必须是str，实际是{type(parsed_summary)}"
        assert isinstance(expanded_items, list), f"expanded_items必须是list，实际是{type(expanded_items)}"

        for idx, item in enumerate(expanded_items):
            assert isinstance(item, dict), f"expanded_items[{idx}]必须是dict，实际是{type(item)}"
            assert 'number' in item, f"expanded_items[{idx}]缺少number字段"
            assert 'amount' in item, f"expanded_items[{idx}]缺少amount字段"
            assert isinstance(item['number'], str), f"number必须是str，实际是{type(item['number'])}"
            assert isinstance(item['amount'], (int, float)), f"amount必须是数字，实际是{type(item['amount'])}"

        print(f"[HISTORY] 类型检查通过")

        # 保存到数据库 - 失败时会抛出异常
        history_id = self.db.save_input_history(
            ledger_id=self.current_ledger.id,
            batch_id=batch_id,
            record_date=today.strftime('%Y-%m-%d'),
            raw_input=raw_input,
            parsed_summary=parsed_summary,
            expanded_items=expanded_items,
            entry_total=result.total_amount,
            daily_total_after=result.total_amount,
            week_start=week_start_str,
            play_mode=play_mode
        )

        print(f"[HISTORY INSERTED] ID: {history_id}, ledger_id: {self.current_ledger.id}, "
              f"金额: {result.total_amount / AMOUNT_MULTIPLIER:.2f}, 项目数: {len(expanded_items)}")

    def _generate_parsed_summary(self, instructions, animal_mapping):
        """生成解析摘要"""
        summaries = []
        try:
            for idx, inst in enumerate(instructions):
                # 安全地展开targets - 确保最终是字符串列表
                targets = []
                if hasattr(inst, 'targets') and inst.targets:
                    for t in inst.targets:
                        if isinstance(t, (list, tuple)):
                            # 如果是列表或元组，递归展开
                            for item in t:
                                if isinstance(item, (list, tuple)):
                                    targets.extend([str(x) for x in item])
                                else:
                                    targets.append(str(item))
                        else:
                            targets.append(str(t))

                # 确保targets是字符串列表
                targets = [str(t) for t in targets]

                if inst.target_type == 'animal':
                    # 动物 - 先获取动物名称，确保都是字符串
                    animals = []
                    for t in targets:
                        animal_name = animal_mapping.get(t, t)
                        # 确保animal_name是字符串
                        if isinstance(animal_name, (list, tuple)):
                            animals.extend([str(x) for x in animal_name])
                        else:
                            animals.append(str(animal_name))

                    summaries.append(f"动物: {', '.join(animals)}")

                elif inst.target_type == 'number':
                    # 号码
                    numbers = ', '.join(targets[:10])
                    if len(targets) > 10:
                        numbers += f" 等{len(targets)}个"
                    summaries.append(f"号码: {numbers}")
                else:
                    # 混合
                    mixed = ', '.join(targets[:10])
                    if len(targets) > 10:
                        mixed += f" 等{len(targets)}项"
                    summaries.append(f"混合: {mixed}")

            return ' | '.join(summaries) if summaries else "无"

        except Exception as e:
            # 如果解析摘要失败，返回简单描述
            print(f"[ERROR] 生成解析摘要失败: {e}")
            import traceback
            traceback.print_exc()
            return f"{len(instructions)}条指令"

    def _generate_expanded_items(self, result):
        """生成展开项列表 - 只包含本次输入的号码"""
        items = []
        # result.number_amounts是字典: {号码(int): 金额(int)}
        for number, amount_int in result.number_amounts.items():
            if amount_int > 0:  # 只包含本次有金额的号码
                amount = amount_int / AMOUNT_MULTIPLIER
                items.append({
                    'number': str(number).zfill(2),  # 格式化为两位数字
                    'amount': amount
                })
        # 按号码排序
        items.sort(key=lambda x: x['number'])
        return items

    def _undo_last(self):
        """撤销最近一次"""
        last_batch_id = self.db.get_last_batch_id(self.current_ledger.id)
        if not last_batch_id:
            messagebox.showinfo("提示", "当前账本没有记录")
            return

        if messagebox.askyesno("确认", "确定要撤销最近一次追加吗？"):
            try:
                # 查找对应的历史记录
                latest_history = self.db.get_latest_active_history(self.current_ledger.id)

                # 删除批次
                self.db.delete_batch(last_batch_id)

                # 标记历史记录为已撤销
                if latest_history and latest_history['batch_id'] == last_batch_id:
                    self.db.mark_history_as_undone(latest_history['id'])

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
        from ui.history_window import HistoryWindow
        HistoryWindow(self, self.db, self.current_ledger)

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
