"""主应用程序"""
import sys
import os
from pathlib import Path
import customtkinter as ctk
from database import Database
from daily_rollover import DailyRollover
from ui.main_window import MainWindow


def get_app_data_dir() -> Path:
    """获取应用数据目录"""
    if sys.platform == 'win32':
        # Windows: %APPDATA%/AnimalNumberLedger
        base = Path(os.environ.get('APPDATA', Path.home()))
        app_dir = base / 'AnimalNumberLedger'
    elif sys.platform == 'darwin':
        # macOS: ~/Library/Application Support/AnimalNumberLedger
        app_dir = Path.home() / 'Library' / 'Application Support' / 'AnimalNumberLedger'
    else:
        # Linux: ~/.local/share/AnimalNumberLedger
        base = Path(os.environ.get('XDG_DATA_HOME', Path.home() / '.local' / 'share'))
        app_dir = base / 'AnimalNumberLedger'

    # 创建目录
    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir


def main():
    """主函数"""
    # 设置外观模式和主题
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    # 获取数据库路径
    app_data_dir = get_app_data_dir()
    db_path = app_data_dir / 'ledger.db'

    # 初始化数据库
    try:
        db = Database(str(db_path))
    except Exception as e:
        # 数据库损坏提示
        root = ctk.CTk()
        root.withdraw()
        error_window = ctk.CTkToplevel(root)
        error_window.title("数据库错误")
        error_window.geometry("500x250")

        label = ctk.CTkLabel(
            error_window,
            text=f"数据库文件可能已损坏或无法访问：\n\n{db_path}\n\n错误信息：{str(e)}\n\n"
                 f"建议：\n1. 如果有备份，请从备份恢复\n2. 如果没有备份，请将数据库文件移走后重新启动",
            wraplength=450,
            justify="left"
        )
        label.pack(pady=20, padx=20)

        close_btn = ctk.CTkButton(
            error_window,
            text="退出",
            command=lambda: sys.exit(1)
        )
        close_btn.pack(pady=10)

        error_window.protocol("WM_DELETE_WINDOW", lambda: sys.exit(1))
        root.mainloop()
        return

    # 初始化归档管理器
    rollover = DailyRollover(db)

    # 创建主窗口
    app = MainWindow(db, rollover, app_data_dir)
    app.mainloop()

    # 关闭数据库
    db.close()


if __name__ == '__main__':
    main()
