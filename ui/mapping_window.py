"""动物号码表设置窗口"""
import json
import customtkinter as ctk
from tkinter import messagebox
from database import Database, DatabaseError
from constants import MIN_NUMBER, MAX_NUMBER


class MappingWindow(ctk.CTkToplevel):
    """动物号码表设置窗口"""

    def __init__(self, parent, db: Database, on_update_callback):
        super().__init__(parent)

        self.db = db
        self.on_update_callback = on_update_callback

        self.title("动物号码表设置")
        self.geometry("600x700")

        self.animal_entries = {}

        self._setup_ui()
        self._load_mapping()

    def _setup_ui(self):
        """设置界面"""
        # 说明
        info_label = ctk.CTkLabel(
            self,
            text="编辑动物号码表（号码之间用逗号分隔）：",
            font=("Arial", 12)
        )
        info_label.pack(anchor='w', padx=10, pady=10)

        # 滚动区域
        scroll_frame = ctk.CTkScrollableFrame(self, height=500)
        scroll_frame.pack(fill='both', expand=True, padx=10, pady=5)

        # 12个动物输入框
        animals = ["马", "蛇", "龙", "兔", "虎", "牛", "鼠", "猪", "狗", "鸡", "猴", "羊"]
        for animal in animals:
            frame = ctk.CTkFrame(scroll_frame)
            frame.pack(fill='x', pady=5)

            label = ctk.CTkLabel(frame, text=f"{animal}:", width=60, font=("Arial", 12))
            label.pack(side='left', padx=5)

            entry = ctk.CTkEntry(frame, width=400, font=("Arial", 11))
            entry.pack(side='left', padx=5)

            self.animal_entries[animal] = entry

        # 按钮
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(fill='x', padx=10, pady=10)

        save_btn = ctk.CTkButton(
            button_frame,
            text="保存",
            command=self._save_mapping
        )
        save_btn.pack(side='left', padx=5)

        cancel_btn = ctk.CTkButton(
            button_frame,
            text="取消",
            command=self.destroy
        )
        cancel_btn.pack(side='left', padx=5)

        reset_btn = ctk.CTkButton(
            button_frame,
            text="恢复默认",
            command=self._reset_to_default
        )
        reset_btn.pack(side='left', padx=5)

    def _load_mapping(self):
        """加载当前映射"""
        mapping = self.db.get_animal_mapping()
        for animal, numbers in mapping.items():
            if animal in self.animal_entries:
                numbers_str = ','.join(str(n) for n in sorted(numbers))
                self.animal_entries[animal].delete(0, 'end')
                self.animal_entries[animal].insert(0, numbers_str)

    def _save_mapping(self):
        """保存映射"""
        try:
            # 解析输入
            new_mapping = {}
            for animal, entry in self.animal_entries.items():
                text = entry.get().strip()
                if not text:
                    messagebox.showerror("错误", f"动物'{animal}'的号码不能为空")
                    return

                # 分割并解析号码
                parts = [p.strip() for p in text.replace('，', ',').split(',')]
                numbers = []
                for part in parts:
                    if not part.isdigit():
                        messagebox.showerror("错误", f"动物'{animal}'的号码格式错误: {part}")
                        return
                    num = int(part)
                    if num < MIN_NUMBER or num > MAX_NUMBER:
                        messagebox.showerror("错误", f"动物'{animal}'的号码超出范围(1-49): {num}")
                        return
                    numbers.append(num)

                new_mapping[animal] = numbers

            # 验证并保存
            self.db.update_animal_mapping(new_mapping)
            messagebox.showinfo("成功", "动物号码表已更新")

            # 回调刷新主窗口
            if self.on_update_callback:
                self.on_update_callback()

            self.destroy()

        except DatabaseError as e:
            messagebox.showerror("错误", f"保存失败：{str(e)}")

    def _reset_to_default(self):
        """恢复默认"""
        from constants import DEFAULT_ANIMAL_MAPPING

        if messagebox.askyesno("确认", "确定要恢复默认动物号码表吗？"):
            for animal, numbers in DEFAULT_ANIMAL_MAPPING.items():
                if animal in self.animal_entries:
                    numbers_str = ','.join(str(n) for n in sorted(numbers))
                    self.animal_entries[animal].delete(0, 'end')
                    self.animal_entries[animal].insert(0, numbers_str)
