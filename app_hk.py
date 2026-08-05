"""香港 - 使用独立数据库"""
import sys
import os
from pathlib import Path
import customtkinter as ctk
from database import Database
from daily_rollover import DailyRollover
from ui.main_window_hk import MainWindowHK


def get_app_data_dir_hk() -> Path:
    """获取香港版应用数据目录（独立目录）"""
    if sys.platform == 'win32':
        # Windows: %APPDATA%/HongKong
        base = Path(os.environ.get('APPDATA', Path.home()))
        app_dir = base / 'HongKong'
    elif sys.platform == 'darwin':
        # macOS: ~/Library/Application Support/HongKong
        app_dir = Path.home() / 'Library' / 'Application Support' / 'HongKong'
    else:
        # Linux: ~/.local/share/HongKong
        base = Path(os.environ.get('XDG_DATA_HOME', Path.home() / '.local' / 'share'))
        app_dir = base / 'HongKong'

    # 创建目录
    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir


def main():
    """主函数"""
    # 设置外观模式和主题
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    # 获取香港版数据库路径（独立数据库）
    app_data_dir = get_app_data_dir_hk()
    db_path = app_data_dir / 'ledger_hk.db'

    print(f"香港版数据库路径: {db_path}")

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

    # 创建香港版主窗口
    app = MainWindowHK(db, rollover, app_data_dir)
    app.mainloop()

    # 关闭数据库
    db.close()


if __name__ == '__main__':
    main()
