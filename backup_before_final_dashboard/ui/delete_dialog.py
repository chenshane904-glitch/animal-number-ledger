"""删除确认对话框（预留）"""
import customtkinter as ctk


class DeleteDialog(ctk.CTkToplevel):
    """删除确认对话框"""

    def __init__(self, parent, title: str, message: str, confirmation_text: str):
        super().__init__(parent)

        self.title(title)
        self.geometry("400x200")

        self.result = None
        self.confirmation_text = confirmation_text

        self._setup_ui(message)

    def _setup_ui(self, message: str):
        """设置界面"""
        # 消息
        label = ctk.CTkLabel(
            self,
            text=message,
            wraplength=350,
            font=("Arial", 11)
        )
        label.pack(pady=20, padx=20)

        # 输入框
        self.entry = ctk.CTkEntry(self, width=300, font=("Arial", 11))
        self.entry.pack(pady=10)

        # 按钮
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(pady=10)

        confirm_btn = ctk.CTkButton(
            button_frame,
            text="确认",
            command=self._confirm,
            fg_color="red"
        )
        confirm_btn.pack(side='left', padx=5)

        cancel_btn = ctk.CTkButton(
            button_frame,
            text="取消",
            command=self._cancel
        )
        cancel_btn.pack(side='left', padx=5)

        # 设置为模态
        self.transient(self.master)
        self.grab_set()
        self.wait_window()

    def _confirm(self):
        """确认"""
        if self.entry.get() == self.confirmation_text:
            self.result = True
            self.destroy()
        else:
            from tkinter import messagebox
            messagebox.showerror("错误", "确认文本不正确")

    def _cancel(self):
        """取消"""
        self.result = False
        self.destroy()

    def get_result(self) -> bool:
        """获取结果"""
        return self.result
