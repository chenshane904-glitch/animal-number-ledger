"""历史记录窗口"""
import customtkinter as ctk
from tkinter import messagebox, filedialog
from database import Database, DatabaseError
from backup import BackupManager, BackupError
from constants import DELETE_CONFIRMATION, DELETE_ALL_CONFIRMATION, AMOUNT_MULTIPLIER, MIN_NUMBER, MAX_NUMBER


class HistoryWindow(ctk.CTkToplevel):
    """历史记录窗口"""

    def __init__(self, parent, db: Database, backup_manager: BackupManager, active_ledger_id: int):
        super().__init__(parent)

        self.db = db
        self.backup_manager = backup_manager
        self.active_ledger_id = active_ledger_id

        self.title("历史记录")
        self.geometry("900x700")

        self._setup_ui()
        self._load_ledgers()

    def _setup_ui(self):
        """设置界面"""
        # 顶部按钮
        top_frame = ctk.CTkFrame(self)
        top_frame.pack(fill='x', padx=10, pady=10)

        refresh_btn = ctk.CTkButton(top_frame, text="刷新", command=self._load_ledgers)
        refresh_btn.pack(side='left', padx=5)

        delete_btn = ctk.CTkButton(
            top_frame,
            text="删除选中",
            command=self._delete_selected,
            fg_color="red"
        )
        delete_btn.pack(side='left', padx=5)

        delete_all_btn = ctk.CTkButton(
            top_frame,
            text="删除全部历史",
            command=self._delete_all_history,
            fg_color="darkred"
        )
        delete_all_btn.pack(side='left', padx=5)

        export_csv_btn = ctk.CTkButton(
            top_frame,
            text="导出CSV",
            command=self._export_csv
        )
        export_csv_btn.pack(side='left', padx=5)

        # 账本列表
        list_label = ctk.CTkLabel(self, text="历史账本：", font=("Arial", 12))
        list_label.pack(anchor='w', padx=10, pady=(5, 5))

        self.ledger_listbox = ctk.CTkScrollableFrame(self, height=300)
        self.ledger_listbox.pack(fill='both', expand=True, padx=10, pady=5)

        # 详情显示
        detail_label = ctk.CTkLabel(self, text="账本详情：", font=("Arial", 12))
        detail_label.pack(anchor='w', padx=10, pady=(10, 5))

        self.detail_text = ctk.CTkTextbox(self, height=250, font=("Consolas", 10))
        self.detail_text.pack(fill='both', expand=True, padx=10, pady=5)

        self.selected_ledger_id = None
        self.ledger_items = []

    def _load_ledgers(self):
        """加载账本列表"""
        # 清空现有列表
        for widget in self.ledger_listbox.winfo_children():
            widget.destroy()

        self.ledger_items = []

        # 获取所有账本
        ledgers = self.db.get_all_ledgers()

        for ledger in ledgers:
            # 已归档账本显示结算时固化的金额；活动账本显示当前累计。
            if ledger.status == 'archived' and ledger.settled_total_integer is not None:
                total_integer = ledger.settled_total_integer
                total_label = "结算总金额"
            else:
                totals = self.db.get_ledger_totals(ledger.id)
                total_integer = sum(totals.values())
                total_label = "当前总金额"
            total_amount = total_integer / AMOUNT_MULTIPLIER

            status_text = "活动中" if ledger.status == 'active' else "已归档"
            is_active = ledger.id == self.active_ledger_id

            frame = ctk.CTkFrame(self.ledger_listbox)
            frame.pack(fill='x', pady=2)

            label_text = (
                f"[{ledger.ledger_date}] 账本#{ledger.sequence_number} - "
                f"{status_text} - {total_label}: {total_amount:.2f}"
            )
            if is_active:
                label_text += " (当前)"

            label = ctk.CTkLabel(
                frame,
                text=label_text,
                anchor='w',
                font=("Arial", 11)
            )
            label.pack(side='left', fill='x', expand=True, padx=10, pady=5)

            # 点击查看详情
            frame.bind('<Button-1>', lambda e, lid=ledger.id: self._show_ledger_detail(lid))
            label.bind('<Button-1>', lambda e, lid=ledger.id: self._show_ledger_detail(lid))

            self.ledger_items.append((ledger.id, frame, is_active))

    def _show_ledger_detail(self, ledger_id: int):
        """显示账本详情"""
        self.selected_ledger_id = ledger_id

        # 高亮选中项
        for lid, frame, _ in self.ledger_items:
            if lid == ledger_id:
                frame.configure(fg_color=("gray70", "gray30"))
            else:
                frame.configure(fg_color=("gray86", "gray17"))

        # 获取账本数据
        ledger = self.db.get_ledger(ledger_id)

        # 获取号码总数
        totals = self.db.get_ledger_totals(ledger_id)

        # 获取来源
        sources = self.db.get_ledger_sources(ledger_id)

        # 显示详情
        lines = []
        if ledger:
            lines.append("=== 结算信息 ===")
            lines.append(f"日期: {ledger.ledger_date}")
            lines.append(f"账本编号: {ledger.sequence_number}")
            lines.append(f"状态: {'活动中' if ledger.status == 'active' else '已归档'}")
            if ledger.settled_total_integer is not None:
                lines.append(
                    f"结算总账金额: "
                    f"{ledger.settled_total_integer / AMOUNT_MULTIPLIER:.2f}"
                )
            lines.append("")

        lines.append("=== 01-49 结果 ===\n")

        for i in range(MIN_NUMBER, MAX_NUMBER + 1):
            amount = totals.get(i, 0) / AMOUNT_MULTIPLIER
            if amount > 0:
                lines.append(f"{i:02d}: {amount:.2f}")

        total = sum(totals.values()) / AMOUNT_MULTIPLIER
        non_zero = sum(1 for v in totals.values() if v > 0)

        lines.append(f"\n总数: {total:.2f}")
        lines.append(f"非零号码: {non_zero}")

        lines.append("\n\n=== 号码来源 ===\n")
        for i in range(MIN_NUMBER, MAX_NUMBER + 1):
            if sources.get(i):
                lines.append(f"\n{i:02d}:")
                for source in sources[i]:
                    lines.append(f"  • {source}")

        self.detail_text.delete("1.0", "end")
        self.detail_text.insert("1.0", '\n'.join(lines))

    def _delete_selected(self):
        """删除选中的账本"""
        if not self.selected_ledger_id:
            messagebox.showinfo("提示", "请先选择要删除的账本")
            return

        # 检查是否是当前活动账本
        for lid, _, is_active in self.ledger_items:
            if lid == self.selected_ledger_id and is_active:
                messagebox.showerror("错误", "无法删除当前活动账本")
                return

        # 创建确认对话框
        dialog = ctk.CTkInputDialog(
            text=f"永久删除选中账本？此操作不可撤销！\n\n请输入确认文本：\n{DELETE_CONFIRMATION}",
            title="确认删除"
        )
        confirmation = dialog.get_input()

        if confirmation == DELETE_CONFIRMATION:
            try:
                self.db.delete_ledgers([self.selected_ledger_id])
                messagebox.showinfo("成功", "已删除")
                self._load_ledgers()
                self.detail_text.delete("1.0", "end")
                self.selected_ledger_id = None
            except DatabaseError as e:
                messagebox.showerror("错误", f"删除失败：{str(e)}")
        elif confirmation:
            messagebox.showerror("错误", "确认文本不正确")

    def _delete_all_history(self):
        """删除全部历史记录"""
        # 创建确认对话框
        dialog = ctk.CTkInputDialog(
            text=f"永久删除全部历史记录？此操作不可撤销！\n\n请输入确认文本：\n{DELETE_ALL_CONFIRMATION}",
            title="确认删除全部"
        )
        confirmation = dialog.get_input()

        if confirmation == DELETE_ALL_CONFIRMATION:
            try:
                self.db.delete_all_archived_ledgers()
                messagebox.showinfo("成功", "已删除全部历史记录")
                self._load_ledgers()
                self.detail_text.delete("1.0", "end")
                self.selected_ledger_id = None
            except DatabaseError as e:
                messagebox.showerror("错误", f"删除失败：{str(e)}")
        elif confirmation:
            messagebox.showerror("错误", "确认文本不正确")

    def _export_csv(self):
        """导出CSV"""
        if not self.selected_ledger_id:
            messagebox.showinfo("提示", "请先选择要导出的账本")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"ledger_{self.selected_ledger_id}.csv"
        )

        if file_path:
            try:
                self.backup_manager.export_csv(self.selected_ledger_id, file_path)
                messagebox.showinfo("成功", f"已导出到：\n{file_path}")
            except BackupError as e:
                messagebox.showerror("错误", f"导出失败：{str(e)}")
