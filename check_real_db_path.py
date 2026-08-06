"""确认程序使用的真实数据库路径"""
import sys
import os
from pathlib import Path

def get_app_data_dir() -> Path:
    """获取应用数据目录（从app.py复制）"""
    if sys.platform == 'win32':
        base = Path(os.environ.get('APPDATA', Path.home()))
        app_dir = base / 'AnimalNumberLedger'
    elif sys.platform == 'darwin':
        app_dir = Path.home() / 'Library' / 'Application Support' / 'AnimalNumberLedger'
    else:
        base = Path(os.environ.get('XDG_DATA_HOME', Path.home() / '.local' / 'share'))
        app_dir = base / 'AnimalNumberLedger'
    return app_dir

app_data_dir = get_app_data_dir()
db_path = app_data_dir / 'ledger.db'

print(f"程序实际使用的数据库路径: {db_path.absolute()}")
print(f"数据库文件存在: {db_path.exists()}")

if db_path.exists():
    print(f"文件大小: {db_path.stat().st_size} 字节")
    print(f"最后修改时间: {db_path.stat().st_mtime}")

    import time
    print(f"最后修改时间（可读）: {time.ctime(db_path.stat().st_mtime)}")
else:
    print("文件不存在")

# 同时检查项目目录的data.db
local_db = Path('data.db')
print(f"\n项目目录data.db: {local_db.absolute()}")
print(f"项目目录data.db存在: {local_db.exists()}")
if local_db.exists():
    print(f"项目目录data.db大小: {local_db.stat().st_size} 字节")
