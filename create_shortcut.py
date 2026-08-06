"""创建桌面快捷方式"""
import os
import sys
from pathlib import Path

# 获取桌面路径
desktop = Path.home() / 'Desktop'
print(f"桌面路径: {desktop}")

# 项目路径
project_dir = Path(r'C:\Users\2SS2\animal-number-ledger')
app_file = project_dir / 'app.py'

print(f"应用路径: {app_file}")
print(f"应用存在: {app_file.exists()}")

if sys.platform == 'win32':
    # Windows: 创建快捷方式 (.lnk)
    import win32com.client

    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut_path = desktop / "动物号码账本.lnk"

    shortcut = shell.CreateShortCut(str(shortcut_path))
    shortcut.TargetPath = sys.executable  # Python解释器路径
    shortcut.Arguments = f'"{app_file}"'
    shortcut.WorkingDirectory = str(project_dir)
    shortcut.IconLocation = sys.executable
    shortcut.Description = "动物号码账本 v1.22"
    shortcut.save()

    print(f"\n✓ 快捷方式已创建: {shortcut_path}")
    print(f"✓ 可以双击桌面上的'动物号码账本'图标启动程序")

else:
    print("非Windows系统，需要手动创建快捷方式")
