# -*- coding: utf-8 -*-
"""
手动测试头数筛选功能

运行此脚本将启动应用程序，你可以：
1. 点击"一头"按钮，应该自动插入 "10-19"
2. 点击"二头"按钮，应该自动插入 "20-29"
3. 点击"三头"按钮，应该自动插入 "30-39"
4. 点击"四头"按钮，应该自动插入 "40-49"

然后手动输入金额（如 "各10"），点击确认追加即可。
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from database import Database
from daily_rollover import DailyRollover
from ui.main_window import MainWindow
from platform_paths import get_app_data_dir


def main():
    """启动应用程序进行手动测试"""
    print("=" * 60)
    print("启动应用程序测试头数筛选功能")
    print("=" * 60)
    print()
    print("测试步骤：")
    print("1. 在号码模式下，你应该看到4个头数按钮：一头、二头、三头、四头")
    print("2. 点击任意头数按钮，应该自动插入对应的号码范围")
    print("3. 手动添加金额（如：各10 或 各100）")
    print("4. 点击确认追加，验证号码和金额是否正确")
    print("5. 切换到平特模式，头数按钮应该隐藏")
    print()
    print("=" * 60)

    # 初始化数据库和应用
    app_data_dir = get_app_data_dir()
    db_path = app_data_dir / "data.db"

    db = Database(db_path)
    rollover = DailyRollover(db)

    # 创建主窗口
    app = MainWindow(db, rollover, app_data_dir)

    # 运行应用
    app.mainloop()


if __name__ == "__main__":
    main()
