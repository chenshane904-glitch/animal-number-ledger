"""主应用程序"""
import sys
import customtkinter as ctk
from database import Database
from daily_rollover import DailyRollover
from ui.main_window import MainWindow
from platform_paths import get_database_path, get_user_data_dir


def main():
    """主函数"""
    # 设置外观模式和主题
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    # 获取数据库路径（使用统一的跨平台路径模块）
    db_path = get_database_path()

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

    # 创建主窗口（传递用户数据目录）
    app = MainWindow(db, rollover, get_user_data_dir())
    app.mainloop()

    # 关闭数据库
    db.close()


if __name__ == '__main__':
    main()
