# -*- coding: utf-8 -*-
"""
结算窗口
"""

import customtkinter as ctk
from datetime import datetime
from tkinter import messagebox


class SettlementWindow(ctk.CTkToplevel):
    """结算窗口"""

    def __init__(self, parent, database, settlement_module):
        super().__init__(parent)

        self.database = database
        self.settlement = settlement_module

        # 窗口设置
        self.title("开奖结算")
        self.geometry("600x700")

        # 居中显示
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

        self._create_widgets()

    def _create_widgets(self):
        """创建UI组件"""

        # 标题
        title_label = ctk.CTkLabel(
            self,
            text="🏆 每日开奖结算",
            font=("Microsoft YaHei UI", 20, "bold")
        )
        title_label.pack(pady=20)

        # 输入区域
        input_frame = ctk.CTkFrame(self)
        input_frame.pack(pady=10, padx=20, fill="x")

        # 日期选择
        date_label = ctk.CTkLabel(
            input_frame,
            text="结算日期:",
            font=("Microsoft YaHei UI", 14)
        )
        date_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.date_entry = ctk.CTkEntry(
            input_frame,
            width=200,
            font=("Microsoft YaHei UI", 14)
        )
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.date_entry.grid(row=0, column=1, padx=10, pady=10)

        # 中奖号码输入
        number_label = ctk.CTkLabel(
            input_frame,
            text="中奖号码:",
            font=("Microsoft YaHei UI", 14)
        )
        number_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        self.number_entry = ctk.CTkEntry(
            input_frame,
            width=200,
            font=("Microsoft YaHei UI", 14),
            placeholder_text="输入1-49的号码"
        )
        self.number_entry.grid(row=1, column=1, padx=10, pady=10)

        # 结算按钮
        settle_button = ctk.CTkButton(
            input_frame,
            text="开始结算",
            font=("Microsoft YaHei UI", 14, "bold"),
            command=self._perform_settlement,
            height=40
        )
        settle_button.grid(row=2, column=0, columnspan=2, pady=20)

        # 结果显示区域
        result_frame = ctk.CTkFrame(self)
        result_frame.pack(pady=10, padx=20, fill="both", expand=True)

        result_title = ctk.CTkLabel(
            result_frame,
            text="结算结果",
            font=("Microsoft YaHei UI", 16, "bold")
        )
        result_title.pack(pady=10)

        # 结果文本框
        self.result_text = ctk.CTkTextbox(
            result_frame,
            font=("Consolas", 12),
            wrap="word"
        )
        self.result_text.pack(pady=10, padx=10, fill="both", expand=True)

    def _perform_settlement(self):
        """执行结算"""
        try:
            # 获取输入
            ledger_date = self.date_entry.get().strip()
            winning_number_str = self.number_entry.get().strip()

            if not winning_number_str:
                messagebox.showerror("错误", "请输入中奖号码")
                return

            try:
                winning_number = int(winning_number_str)
            except ValueError:
                messagebox.showerror("错误", "中奖号码必须是数字")
                return

            if not (1 <= winning_number <= 49):
                messagebox.showerror("错误", "中奖号码必须在1-49之间")
                return

            # 执行结算计算
            result = self.settlement.calculate_settlement(winning_number, ledger_date)

            # 显示结果
            self._display_result(result)

        except Exception as e:
            messagebox.showerror("错误", f"结算失败: {str(e)}")

    def _display_result(self, result: dict):
        """显示结算结果"""
        self.result_text.delete("1.0", "end")

        if 'error' in result:
            self.result_text.insert("1.0", f"❌ {result['error']}\n")
            return

        # 格式化显示结果
        output = []
        output.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        output.append("📊 开奖结算结果")
        output.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        output.append("")
        output.append(f"📅 结算日期: {result['ledger_date']}")
        output.append(f"🎯 开奖号码: {result['winning_number']}")
        output.append("")
        output.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        output.append("💰 结算数据")
        output.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        output.append("")
        output.append(f"中奖号码下注金额: ￥{result['winning_amount_display']}")
        output.append(f"赔率: {result['odds']}倍")
        output.append(f"中奖赔付金额: ￥{result['payout_amount_display']}")
        output.append("")
        output.append(f"今日总下注: ￥{result['total_bet_display']}")

        # 盈亏显示带正负号和颜色标记
        profit_loss = result['profit_loss']
        if profit_loss > 0:
            profit_loss_text = f"+￥{result['profit_loss_display']}"
            status_text = "✅ 今日盈利"
            status_color = "green"
        elif profit_loss < 0:
            profit_loss_text = f"-￥{abs(profit_loss / 100):.2f}"
            status_text = "❌ 今日亏损"
            status_color = "red"
        else:
            profit_loss_text = f"￥{result['profit_loss_display']}"
            status_text = "➖ 今日持平"
            status_color = "gray"

        output.append(f"今日盈亏: {profit_loss_text}")
        output.append("")
        output.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        output.append("📈 统计信息")
        output.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        output.append("")
        output.append(f"总记录数: {result['total_records']}")
        output.append(f"涉及号码: {result['number_with_bet']}")
        output.append("")
        output.append(status_text)
        output.append("")
        output.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        self.result_text.insert("1.0", "\n".join(output))
