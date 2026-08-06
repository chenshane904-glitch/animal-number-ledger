# macOS 兼容性扫描报告

扫描时间: 2026-08-07 00:10:21


## 扫描结果概要

- 发现 105 个文件包含 Windows 特定代码

- 总计 475 处需要检查


### 按类别统计

- Windows 字体: 179 处

- Windows 绝对路径: 111 处

- SQLite 连接: 96 处

- Windows 特定目录: 43 处

- PowerShell/批处理: 33 处

- Windows API: 7 处

- Windows 注册表: 4 处

- ICO 图标: 2 处


## 详细问题列表


### analyze_test_issues.py


#### PowerShell/批处理

- 行 44: `SELECT 1 FROM input_history h WHERE h.batch_id = b.id`

- 行 61: `(SELECT COUNT(*) FROM input_history h WHERE h.batch_id = b.id) as has_history`


#### SQLite 连接

- 行 14: `conn = sqlite3.connect(str(db_path))`

- 行 13: `db_path = get_app_data_dir() / 'ledger.db'`


#### Windows 特定目录

- 行 9: `base = Path(os.environ.get('APPDATA', Path.home()))`


### app.py


#### SQLite 连接

- 行 38: `db_path = app_data_dir / 'ledger.db'`


#### Windows 特定目录

- 行 14: `# Windows: %APPDATA%/AnimalNumberLedger`

- 行 15: `base = Path(os.environ.get('APPDATA', Path.home()))`


### app_hk.py


#### Windows 特定目录

- 行 14: `# Windows: %APPDATA%/HongKong`

- 行 15: `base = Path(os.environ.get('APPDATA', Path.home()))`


### app_v2.py


#### SQLite 连接

- 行 38: `db_path = app_data_dir / 'ledger.db'`


#### Windows 特定目录

- 行 14: `# Windows: %APPDATA%/AnimalNumberLedger`

- 行 15: `base = Path(os.environ.get('APPDATA', Path.home()))`


### backup.py


#### PowerShell/批处理

- 行 487: `JOIN batches b ON i.batch_id = b.id`

- 行 535: `JOIN batches b ON i.batch_id = b.id`


### backup_before_final_dashboard\app.py


#### SQLite 连接

- 行 38: `db_path = app_data_dir / 'ledger.db'`


#### Windows 特定目录

- 行 14: `# Windows: %APPDATA%/AnimalNumberLedger`

- 行 15: `base = Path(os.environ.get('APPDATA', Path.home()))`


### backup_before_final_dashboard\ui\history_window.py


#### Windows 字体

- 行 68: `self.detail_text = ctk.CTkTextbox(self, height=250, font=("Consolas", 10))`


### backup_before_final_dashboard\ui\main_window.py


#### Windows 字体

- 行 157: `self.input_text = ctk.CTkTextbox(input_container, font=("Consolas", 10))`

- 行 174: `self.preview_text = ctk.CTkTextbox(preview_container, font=("Consolas", 9))`

- 行 191: `self.calc_text = ctk.CTkTextbox(calc_container, font=("Consolas", 10, "bold"))`


### backup_before_final_dashboard\ui\main_window_backup.py


#### Windows 字体

- 行 156: `self.input_text = ctk.CTkTextbox(input_container, font=("Consolas", 10))`

- 行 173: `self.preview_text = ctk.CTkTextbox(preview_container, font=("Consolas", 9))`

- 行 190: `self.calc_text = ctk.CTkTextbox(calc_container, font=("Consolas", 10, "bold"))`


### backup_before_final_dashboard\ui\main_window_hk.py


#### Windows 字体

- 行 102: `font=("Microsoft YaHei UI", 28, "bold"),`

- 行 172: `font=("Microsoft YaHei UI", 11),`

- 行 180: `font=("Microsoft YaHei UI", 14, "bold"),`

- 行 190: `font=("Microsoft YaHei UI", 18, "bold"),`

- 行 215: `font=("Microsoft YaHei UI", 14, "bold"),`

- 行 226: `font=("Microsoft YaHei UI", 13),`

- 行 237: `font=("Microsoft YaHei UI", 13),`

- 行 248: `font=("Microsoft YaHei UI", 14, "bold"),`

- 行 267: `font=("Microsoft YaHei UI", 18, "bold"),`

- 行 285: `font=("Microsoft YaHei UI", 18, "bold"),`

- 行 295: `font=("Microsoft YaHei UI", 16, "bold"),`

- 行 306: `font=("Microsoft YaHei UI", 13),`

- 行 318: `font=("Microsoft YaHei UI", 18, "bold"),`

- 行 328: `font=("Microsoft YaHei UI", 16, "bold"),`

- 行 341: `font=("Microsoft YaHei UI", 18, "bold"),`

- 行 355: `font=("Microsoft YaHei UI", 14),`

- 行 365: `font=("Microsoft YaHei UI", 14),`

- 行 375: `font=("Microsoft YaHei UI", 14),`

- 行 385: `font=("Microsoft YaHei UI", 14),`

- 行 397: `font=("Microsoft YaHei UI", 14),`

- 行 516: `font=("Microsoft YaHei UI", 20, "bold"),`

- 行 547: `font=("Microsoft YaHei UI", 13, "bold"),`

- 行 199: `font=("Consolas", 13),`

- 行 256: `font=("Consolas", 11),`

- 行 526: `font=("Consolas", 12),`


### backup_before_final_dashboard\ui\main_window_v2.py


#### Windows 字体

- 行 100: `font=("Microsoft YaHei UI", 28, "bold"),`

- 行 140: `font=("Microsoft YaHei UI", 16, "bold"),`

- 行 165: `font=("Microsoft YaHei UI", 14, "bold"),`

- 行 176: `font=("Microsoft YaHei UI", 13),`

- 行 187: `font=("Microsoft YaHei UI", 13),`

- 行 198: `font=("Microsoft YaHei UI", 13),`

- 行 209: `font=("Microsoft YaHei UI", 13),`

- 行 223: `font=("Microsoft YaHei UI", 16, "bold"),`

- 行 247: `font=("Microsoft YaHei UI", 20, "bold"),`

- 行 255: `font=("Microsoft YaHei UI", 16),`

- 行 276: `font=("Microsoft YaHei UI", 13),`

- 行 287: `font=("Microsoft YaHei UI", 13),`

- 行 296: `font=("Microsoft YaHei UI", 13),`

- 行 305: `font=("Microsoft YaHei UI", 13),`

- 行 314: `font=("Microsoft YaHei UI", 13),`

- 行 355: `font=("Microsoft YaHei UI", 18, "bold"),`

- 行 386: `font=("Microsoft YaHei UI", 12, "bold"),`

- 行 149: `font=("Consolas", 12),`

- 行 365: `font=("Consolas", 12),`


### backup_before_final_dashboard\ui\result_table.py


#### Windows 字体

- 行 114: `font=("Microsoft YaHei", 12, "bold")`

- 行 121: `font=("Microsoft YaHei", 12, "bold"),`

- 行 129: `font=("Microsoft YaHei", 12, "bold"),`

- 行 137: `font=("Microsoft YaHei", 12, "bold"),`

- 行 231: `font=("Microsoft YaHei", 13, "bold")`


### backup_before_final_dashboard\ui\settlement_window.py


#### Windows 字体

- 行 41: `font=("Microsoft YaHei UI", 20, "bold")`

- 行 53: `font=("Microsoft YaHei UI", 14)`

- 行 60: `font=("Microsoft YaHei UI", 14)`

- 行 69: `font=("Microsoft YaHei UI", 14)`

- 行 76: `font=("Microsoft YaHei UI", 14),`

- 行 85: `font=("Microsoft YaHei UI", 14, "bold"),`

- 行 98: `font=("Microsoft YaHei UI", 16, "bold")`

- 行 105: `font=("Consolas", 12),`


### check_allocations.py


#### SQLite 连接

- 行 5: `conn = sqlite3.connect(db_path)`

- 行 4: `db_path = os.path.join(os.environ.get('APPDATA', ''), 'AnimalNumberLedger', 'ledger.db')`


#### Windows 特定目录

- 行 4: `db_path = os.path.join(os.environ.get('APPDATA', ''), 'AnimalNumberLedger', 'ledger.db')`


### check_allocations2.py


#### SQLite 连接

- 行 5: `conn = sqlite3.connect(db_path)`

- 行 4: `db_path = os.path.join(os.environ.get('APPDATA', ''), 'AnimalNumberLedger', 'ledger.db')`


#### Windows 特定目录

- 行 4: `db_path = os.path.join(os.environ.get('APPDATA', ''), 'AnimalNumberLedger', 'ledger.db')`


### check_animal_mapping.py


#### SQLite 连接

- 行 6: `conn = sqlite3.connect(db_path)`

- 行 5: `db_path = os.path.join(os.environ.get('APPDATA', ''), 'AnimalNumberLedger', 'ledger.db')`


#### Windows 特定目录

- 行 5: `db_path = os.path.join(os.environ.get('APPDATA', ''), 'AnimalNumberLedger', 'ledger.db')`


### check_batches_schema.py


#### SQLite 连接

- 行 5: `conn = sqlite3.connect(db_path)`

- 行 4: `db_path = os.path.join(os.environ.get('APPDATA', ''), 'AnimalNumberLedger', 'ledger.db')`


#### Windows 特定目录

- 行 4: `db_path = os.path.join(os.environ.get('APPDATA', ''), 'AnimalNumberLedger', 'ledger.db')`


### check_before_start.py


#### SQLite 连接

- 行 7: `conn = sqlite3.connect(db_path)`

- 行 6: `db_path = 'data.db'`


### check_db_mapping.py


#### SQLite 连接

- 行 6: `conn = sqlite3.connect(db_path)`

- 行 5: `db_path = os.path.join(os.environ.get('APPDATA', ''), 'AnimalNumberLedger', 'ledger.db')`


#### Windows 特定目录

- 行 5: `db_path = os.path.join(os.environ.get('APPDATA', ''), 'AnimalNumberLedger', 'ledger.db')`


### check_db_simple.py


#### SQLite 连接

- 行 3: `conn = sqlite3.connect('data.db')`

- 行 3: `conn = sqlite3.connect('data.db')`


### check_db_tables.py


#### SQLite 连接

- 行 5: `conn = sqlite3.connect(db_path)`

- 行 4: `db_path = os.path.join(os.environ.get('APPDATA', ''), 'AnimalNumberLedger', 'ledger.db')`


#### Windows 特定目录

- 行 4: `db_path = os.path.join(os.environ.get('APPDATA', ''), 'AnimalNumberLedger', 'ledger.db')`


### check_db_write.py


#### SQLite 连接

- 行 25: `conn = sqlite3.connect(str(real_db_path))`

- 行 18: `real_db_path = get_app_data_dir() / 'ledger.db'`


#### Windows 特定目录

- 行 9: `base = Path(os.environ.get('APPDATA', Path.home()))`


### check_flat_tables.py


#### SQLite 连接

- 行 3: `conn = sqlite3.connect('data.db')`

- 行 3: `conn = sqlite3.connect('data.db')`


### check_flat_zodiac_db.py


#### SQLite 连接

- 行 3: `conn = sqlite3.connect('data.db')`

- 行 3: `conn = sqlite3.connect('data.db')`


### check_history_data.py


#### SQLite 连接

- 行 27: `conn = sqlite3.connect(str(real_db_path))`

- 行 18: `real_db_path = get_app_data_dir() / 'ledger.db'`


#### Windows 特定目录

- 行 9: `base = Path(os.environ.get('APPDATA', Path.home()))`


### check_history_db.py


#### SQLite 连接

- 行 7: `conn = sqlite3.connect(db_path)`

- 行 4: `db_path = os.path.join(os.environ['APPDATA'], 'AnimalNumberLedger', 'ledger.db')`


#### Windows 特定目录

- 行 4: `db_path = os.path.join(os.environ['APPDATA'], 'AnimalNumberLedger', 'ledger.db')`


### check_history_table.py


#### SQLite 连接

- 行 4: `conn = sqlite3.connect(db_path)`

- 行 3: `db_path = "data.db"`


### check_input_history.py


#### SQLite 连接

- 行 24: `conn = sqlite3.connect(str(real_db_path))`

- 行 18: `real_db_path = get_app_data_dir() / 'ledger.db'`


#### Windows 特定目录

- 行 9: `base = Path(os.environ.get('APPDATA', Path.home()))`


### check_real_db.py


#### SQLite 连接

- 行 26: `conn = sqlite3.connect(main_db)`

- 行 22: `main_db = "data.db"`


### check_real_db_path.py


#### SQLite 连接

- 行 33: `# 同时检查项目目录的data.db`

- 行 34: `local_db = Path('data.db')`

- 行 35: `print(f"\n项目目录data.db: {local_db.absolute()}")`

- 行 36: `print(f"项目目录data.db存在: {local_db.exists()}")`

- 行 38: `print(f"项目目录data.db大小: {local_db.stat().st_size} 字节")`

- 行 19: `db_path = app_data_dir / 'ledger.db'`


#### Windows 特定目录

- 行 9: `base = Path(os.environ.get('APPDATA', Path.home()))`


### check_real_db_structure.py


#### SQLite 连接

- 行 25: `conn = sqlite3.connect(str(real_db_path))`

- 行 19: `real_db_path = get_app_data_dir() / 'ledger.db'`


#### Windows 特定目录

- 行 9: `base = Path(os.environ.get('APPDATA', Path.home()))`


### check_real_flat_data.py


#### PowerShell/批处理

- 行 67: `JOIN instructions i ON b.id = i.batch_id`

- 行 91: `SELECT a.id, a.number, a.animal, a.amount_integer, i.batch_id`

- 行 94: `JOIN batches b ON i.batch_id = b.id`


#### SQLite 连接

- 行 24: `conn = sqlite3.connect(str(real_db_path))`

- 行 18: `real_db_path = get_app_data_dir() / 'ledger.db'`


#### Windows 特定目录

- 行 9: `base = Path(os.environ.get('APPDATA', Path.home()))`


### check_recent_data.py


#### PowerShell/批处理

- 行 42: `a.id, a.batch_id, a.number, a.animal,`

- 行 45: `JOIN batches b ON a.batch_id = b.id`


#### SQLite 连接

- 行 6: `conn = sqlite3.connect(db_path)`

- 行 5: `db_path = os.path.join(os.environ.get('APPDATA', ''), 'AnimalNumberLedger', 'ledger.db')`


#### Windows 特定目录

- 行 5: `db_path = os.path.join(os.environ.get('APPDATA', ''), 'AnimalNumberLedger', 'ledger.db')`


### check_week_start.py


#### SQLite 连接

- 行 25: `conn = sqlite3.connect(str(real_db_path))`

- 行 19: `real_db_path = get_app_data_dir() / 'ledger.db'`


#### Windows 特定目录

- 行 10: `base = Path(os.environ.get('APPDATA', Path.home()))`


### clean_wrong_data.py


#### SQLite 连接

- 行 5: `conn = sqlite3.connect(db_path)`

- 行 4: `db_path = os.path.join(os.environ.get('APPDATA', ''), 'AnimalNumberLedger', 'ledger.db')`


#### Windows 特定目录

- 行 4: `db_path = os.path.join(os.environ.get('APPDATA', ''), 'AnimalNumberLedger', 'ledger.db')`


### clear_test_data.py


#### SQLite 连接

- 行 6: `conn = sqlite3.connect(db_path)`

- 行 5: `db_path = 'data.db'`


### create_shortcut.py


#### ICO 图标

- 行 28: `shortcut.IconLocation = sys.executable`


#### Windows API

- 行 19: `import win32com.client`

- 行 21: `shell = win32com.client.Dispatch("WScript.Shell")`


#### Windows 绝对路径

- 行 11: `project_dir = Path(r'C:\Users\2SS2\animal-number-ledger')`

- 行 11: `project_dir = Path(r'C:\Users\2SS2\animal-number-ledger')`


### database.py


#### PowerShell/批处理

- 行 245: `JOIN batches b ON i.batch_id = b.id`

- 行 508: `instruction.batch_id = batch_id`

- 行 561: `JOIN batches b ON i.batch_id = b.id`

- 行 584: `JOIN batches b ON i.batch_id = b.id`

- 行 616: `JOIN batches b ON i.batch_id = b.id`

- 行 631: `JOIN batches b ON i.batch_id = b.id`

- 行 657: `JOIN batches b ON i.batch_id = b.id`


#### SQLite 连接

- 行 45: `self.conn = sqlite3.connect(`


### diagnose_db_issue.py


#### SQLite 连接

- 行 51: `conn = sqlite3.connect(db_path)`

- 行 85: `conn = sqlite3.connect(db_path)`

- 行 12: `'data.db',`

- 行 14: `Path.home() / 'AppData' / 'Local' / 'animal-number-ledger' / 'data.db',`

- 行 49: `db_path = 'data.db'`

- 行 13: `'ledger.db',`

- 行 15: `Path.home() / 'AppData' / 'Local' / 'animal-number-ledger' / 'ledger.db',`


#### Windows 特定目录

- 行 14: `Path.home() / 'AppData' / 'Local' / 'animal-number-ledger' / 'data.db',`

- 行 15: `Path.home() / 'AppData' / 'Local' / 'animal-number-ledger' / 'ledger.db',`


### final_acceptance.py


#### PowerShell/批处理

- 行 90: `results.append(check_file_exists("build_windows.bat", "Windows打包脚本"))`

- 行 139: `print("  1. 运行 build_windows.bat 打包 Windows 版本")`


### find_correct_db.py


#### SQLite 连接

- 行 16: `conn = sqlite3.connect(db_path)`


### fix_animal_mapping.py


#### SQLite 连接

- 行 22: `conn = sqlite3.connect(db_path)`

- 行 21: `db_path = os.path.join(os.environ.get('APPDATA', ''), 'AnimalNumberLedger', 'ledger.db')`


#### Windows 特定目录

- 行 21: `db_path = os.path.join(os.environ.get('APPDATA', ''), 'AnimalNumberLedger', 'ledger.db')`


### flat_zodiac_service.py


#### PowerShell/批处理

- 行 123: `JOIN flat_zodiac_batches b ON i.batch_id = b.id`


### generate_report.py


#### PowerShell/批处理

- 行 66: `report.append("1. 运行 build_windows.bat 打包 Windows 版本")`


### git-push.bat


#### Windows 绝对路径

- 行 62: `cd /d C:\Users\2SS2\animal-number-ledger`

- 行 62: `cd /d C:\Users\2SS2\animal-number-ledger`


### install.bat


#### PowerShell/批处理

- 行 37: `powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\十二动物号码归纳器.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\十二动物号码归纳器-v1.1.0.exe'; $Shortcut.Save()"`

- 行 45: `powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%START_MENU%\十二动物号码归纳器.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\十二动物号码归纳器-v1.1.0.exe'; $Shortcut.Save()"`


#### Windows 特定目录

- 行 43: `set "START_MENU=%ProgramData%\Microsoft\Windows\Start Menu\Programs\十二动物号码归纳器"`


### migrate_add_history.py


#### SQLite 连接

- 行 4: `conn = sqlite3.connect(db_path)`

- 行 3: `db_path = "data.db"`


### migrate_add_play_mode.py


#### SQLite 连接

- 行 19: `conn = sqlite3.connect(db_path)`

- 行 11: `db_path = os.path.join(os.environ.get('APPDATA', ''), 'AnimalNumberLedger', 'ledger.db')`


#### Windows 特定目录

- 行 11: `db_path = os.path.join(os.environ.get('APPDATA', ''), 'AnimalNumberLedger', 'ledger.db')`


### migrate_create_flat_zodiac_tables.py


#### SQLite 连接

- 行 20: `conn = sqlite3.connect(db_path)`

- 行 11: `db_path = 'data.db'`


### migrate_fix_play_mode.py


#### SQLite 连接

- 行 21: `conn = sqlite3.connect(db_path)`

- 行 11: `# 使用当前目录的 data.db`

- 行 12: `db_path = 'data.db'`


### package\install.bat


#### PowerShell/批处理

- 行 37: `powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\十二动物号码归纳器.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\十二动物号码归纳器-v1.1.0.exe'; $Shortcut.Save()"`

- 行 45: `powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%START_MENU%\十二动物号码归纳器.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\十二动物号码归纳器-v1.1.0.exe'; $Shortcut.Save()"`


#### Windows 特定目录

- 行 43: `set "START_MENU=%ProgramData%\Microsoft\Windows\Start Menu\Programs\十二动物号码归纳器"`


### package\uninstall.bat


#### Windows 特定目录

- 行 41: `set "START_MENU=%ProgramData%\Microsoft\Windows\Start Menu\Programs\十二动物号码归纳器"`


### rewrite_redraw.py


#### Windows 字体

- 行 45: `font=("Microsoft YaHei", 11, "bold")`

- 行 55: `font=("Consolas", 11),`

- 行 65: `font=("Consolas", 10)`

- 行 75: `font=("Consolas", 11),`

- 行 88: `font=("Consolas", 11, "bold"),`


### scan_macos_compatibility.py


#### ICO 图标

- 行 51: `r'\.ico',`


#### PowerShell/批处理

- 行 25: `r'\.bat',`

- 行 103: `extensions = ['.py', '.bat', '.ps1']`

- 行 26: `r'\.ps1',`

- 行 103: `extensions = ['.py', '.bat', '.ps1']`

- 行 24: `'PowerShell/批处理': [`

- 行 27: `r'PowerShell',`


#### SQLite 连接

- 行 188: `report.append("所有 `sqlite3.connect()` 调用必须使用 `get_database_path()`\n")`


#### Windows API

- 行 31: `r'win32api',`

- 行 32: `r'win32gui',`

- 行 33: `r'win32con',`

- 行 34: `r'win32com',`

- 行 35: `r'pywin32',`


#### Windows 字体

- 行 45: `r'Microsoft YaHei',`

- 行 46: `r'SimHei',`

- 行 47: `r'SimSun',`

- 行 48: `r'Consolas',`


#### Windows 注册表

- 行 40: `r'winreg',`

- 行 41: `r'_winreg',`

- 行 41: `r'_winreg',`

- 行 42: `r'HKEY_',`


#### Windows 特定目录

- 行 19: `r'AppData',`

- 行 21: `r'LocalAppData',`

- 行 180: `report.append("        return Path(os.environ['APPDATA']) / 'AnimalNumberLedger'\n")`

- 行 20: `r'Roaming',`

- 行 21: `r'LocalAppData',`

- 行 22: `r'ProgramData',`


#### Windows 绝对路径

- 行 14: `r'C:\\',`

- 行 15: `r'C:/',`

- 行 14: `r'C:\\',`

- 行 183: `report.append("    else:\n")`


### test_amount_sep.py


#### Windows 绝对路径

- 行 2: `sys.path.insert(0, r"C:\Users\2SS2\animal-number-ledger")`

- 行 2: `sys.path.insert(0, r"C:\Users\2SS2\animal-number-ledger")`


### test_animal_duplicate.py


#### Windows 绝对路径

- 行 2: `sys.path.insert(0, r"C:\Users\2SS2\animal-number-ledger")`

- 行 2: `sys.path.insert(0, r"C:\Users\2SS2\animal-number-ledger")`


### test_complete_flow.py


#### SQLite 连接

- 行 16: `db = Database('data.db')`


### test_db_init.py


#### SQLite 连接

- 行 4: `db = Database('data.db')`


### test_debug.py


#### Windows 绝对路径

- 行 3: `sys.path.insert(0, r"C:\Users\2SS2\animal-number-ledger")`

- 行 3: `sys.path.insert(0, r"C:\Users\2SS2\animal-number-ledger")`


### test_enhanced_parser.py


#### Windows 绝对路径

- 行 2: `sys.path.insert(0, r"C:\Users\2SS2\animal-number-ledger")`

- 行 2: `sys.path.insert(0, r"C:\Users\2SS2\animal-number-ledger")`


### test_final_verification.py


#### SQLite 连接

- 行 20: `db = Database('data.db')`


### test_flat_zodiac_flow.py


#### SQLite 连接

- 行 27: `db = Database('data.db')`


### test_flat_zodiac_service.py


#### SQLite 连接

- 行 20: `conn = sqlite3.connect(db_path)`


### test_hk_version.py


#### SQLite 连接

- 行 67: `db_macao_path = temp_dir / 'ledger.db'`

- 行 182: `print("  澳门版: ledger.db")`


### test_new_parse.py


#### Windows 绝对路径

- 行 2: `sys.path.insert(0, r"C:\Users\2SS2\animal-number-ledger")`

- 行 2: `sys.path.insert(0, r"C:\Users\2SS2\animal-number-ledger")`


### test_no_dedup.py


#### Windows 绝对路径

- 行 2: `sys.path.insert(0, r"C:\Users\2SS2\animal-number-ledger")`

- 行 2: `sys.path.insert(0, r"C:\Users\2SS2\animal-number-ledger")`


### test_number_mode.py


#### SQLite 连接

- 行 15: `db = Database('data.db')`


### test_optimized_parser.py


#### Windows 绝对路径

- 行 2: `sys.path.insert(0, r"C:\Users\2SS2\animal-number-ledger")`

- 行 2: `sys.path.insert(0, r"C:\Users\2SS2\animal-number-ledger")`


### test_parse_debug.py


#### Windows 绝对路径

- 行 2: `sys.path.insert(0, r"C:\Users\2SS2\animal-number-ledger")`

- 行 2: `sys.path.insert(0, r"C:\Users\2SS2\animal-number-ledger")`


### test_parser.py


#### Windows 绝对路径

- 行 2: `sys.path.insert(0, "C:/Users/2SS2/animal-number-ledger")`


### test_semantic_parse.py


#### Windows 绝对路径

- 行 2: `sys.path.insert(0, r"C:\Users\2SS2\animal-number-ledger")`

- 行 2: `sys.path.insert(0, r"C:\Users\2SS2\animal-number-ledger")`


### test_simple.py


#### Windows 绝对路径

- 行 2: `sys.path.insert(0, r"C:\Users\2SS2\animal-number-ledger")`

- 行 2: `sys.path.insert(0, r"C:\Users\2SS2\animal-number-ledger")`


### test_simplified_parser.py


#### Windows 绝对路径

- 行 2: `sys.path.insert(0, r"C:\Users\2SS2\animal-number-ledger")`

- 行 2: `sys.path.insert(0, r"C:\Users\2SS2\animal-number-ledger")`


### test_ui_refresh.py


#### SQLite 连接

- 行 12: `db = Database('data.db')`


### test_unified_query.py


#### PowerShell/批处理

- 行 60: `JOIN batches b ON i.batch_id = b.id`


#### SQLite 连接

- 行 5: `db = Database('data.db')`


### test_v1.2.1.py


#### Windows 绝对路径

- 行 11: `sys.path.insert(0, r"C:\Users\2SS2\animal-number-ledger")`

- 行 11: `sys.path.insert(0, r"C:\Users\2SS2\animal-number-ledger")`


### test_v122_full.py


#### PowerShell/批处理

- 行 137: `WHERE h.batch_id = b.id`

- 行 148: `WHERE i.batch_id = b.id`


#### SQLite 连接

- 行 27: `conn = sqlite3.connect(str(db_path))`

- 行 19: `db_path = get_app_data_dir() / 'ledger.db'`


#### Windows 特定目录

- 行 11: `base = Path(os.environ.get('APPDATA', Path.home()))`


### test_v122_regression.py


#### SQLite 连接

- 行 35: `conn = sqlite3.connect(str(db_path))`

- 行 28: `db_path = db_dir / 'ledger.db'`


#### Windows 特定目录

- 行 19: `base = Path(os.environ.get('APPDATA', Path.home()))`


### test_with_targets.py


#### Windows 绝对路径

- 行 2: `sys.path.insert(0, r"C:\Users\2SS2\animal-number-ledger")`

- 行 2: `sys.path.insert(0, r"C:\Users\2SS2\animal-number-ledger")`


### ui\animal_result_table.py


#### Windows 字体

- 行 111: `font=("Microsoft YaHei", 12, "bold")`

- 行 174: `font=("Microsoft YaHei", 11, "bold")`

- 行 184: `font=("Consolas", 11),`

- 行 194: `font=("Consolas", 10)`

- 行 204: `font=("Consolas", 11),`

- 行 217: `font=("Consolas", 11, "bold"),`


### ui\history_window.py


#### Windows 字体

- 行 49: `font=("Microsoft YaHei", 14, "bold"),`

- 行 118: `font=("Microsoft YaHei", 13),`

- 行 197: `font=("Microsoft YaHei", 12, "bold"),`

- 行 265: `font=("Microsoft YaHei", 10),`

- 行 272: `font=("Microsoft YaHei", 10, "bold"),`

- 行 281: `font=("Microsoft YaHei", 13, "bold"),`

- 行 297: `font=("Microsoft YaHei", 12),`

- 行 304: `font=("Microsoft YaHei", 14, "bold"),`

- 行 311: `font=("Microsoft YaHei", 12),`

- 行 318: `font=("Microsoft YaHei", 12, "bold"),`

- 行 336: `font=("Microsoft YaHei", 10)`

- 行 370: `font=("Microsoft YaHei", 10, "bold"),`

- 行 395: `font=("Microsoft YaHei", 10, "bold"),`

- 行 469: `font=("Microsoft YaHei", 10),`

- 行 476: `font=("Microsoft YaHei", 10, "bold"),`

- 行 485: `font=("Microsoft YaHei", 13, "bold"),`

- 行 502: `font=("Microsoft YaHei", 10),`

- 行 515: `font=("Microsoft YaHei", 11, "bold"),`

- 行 524: `font=("Microsoft YaHei", 11),`

- 行 539: `font=("Microsoft YaHei", 12),`

- 行 546: `font=("Microsoft YaHei", 14, "bold"),`

- 行 553: `font=("Microsoft YaHei", 12),`

- 行 560: `font=("Microsoft YaHei", 12, "bold"),`

- 行 258: `font=("Consolas", 11),`

- 行 406: `font=("Consolas", 10),`

- 行 462: `font=("Consolas", 11),`


### ui\main_window.py


#### Windows 字体

- 行 190: `self.input_text = ctk.CTkTextbox(input_container, font=("Consolas", 10))`

- 行 207: `self.preview_text = ctk.CTkTextbox(preview_container, font=("Consolas", 9))`

- 行 224: `self.calc_text = ctk.CTkTextbox(calc_container, font=("Consolas", 10, "bold"))`


### ui\main_window_backup.py


#### Windows 字体

- 行 156: `self.input_text = ctk.CTkTextbox(input_container, font=("Consolas", 10))`

- 行 173: `self.preview_text = ctk.CTkTextbox(preview_container, font=("Consolas", 9))`

- 行 190: `self.calc_text = ctk.CTkTextbox(calc_container, font=("Consolas", 10, "bold"))`


### ui\main_window_before_animal_mode.py


#### Windows 字体

- 行 160: `self.input_text = ctk.CTkTextbox(input_container, font=("Consolas", 10))`

- 行 177: `self.preview_text = ctk.CTkTextbox(preview_container, font=("Consolas", 9))`

- 行 194: `self.calc_text = ctk.CTkTextbox(calc_container, font=("Consolas", 10, "bold"))`


### ui\main_window_before_fix.py


#### Windows 字体

- 行 190: `self.input_text = ctk.CTkTextbox(input_container, font=("Consolas", 10))`

- 行 207: `self.preview_text = ctk.CTkTextbox(preview_container, font=("Consolas", 9))`

- 行 224: `self.calc_text = ctk.CTkTextbox(calc_container, font=("Consolas", 10, "bold"))`


### ui\main_window_hk.py


#### Windows 字体

- 行 102: `font=("Microsoft YaHei UI", 28, "bold"),`

- 行 172: `font=("Microsoft YaHei UI", 11),`

- 行 180: `font=("Microsoft YaHei UI", 14, "bold"),`

- 行 190: `font=("Microsoft YaHei UI", 18, "bold"),`

- 行 215: `font=("Microsoft YaHei UI", 14, "bold"),`

- 行 226: `font=("Microsoft YaHei UI", 13),`

- 行 237: `font=("Microsoft YaHei UI", 13),`

- 行 248: `font=("Microsoft YaHei UI", 14, "bold"),`

- 行 267: `font=("Microsoft YaHei UI", 18, "bold"),`

- 行 285: `font=("Microsoft YaHei UI", 18, "bold"),`

- 行 295: `font=("Microsoft YaHei UI", 16, "bold"),`

- 行 306: `font=("Microsoft YaHei UI", 13),`

- 行 318: `font=("Microsoft YaHei UI", 18, "bold"),`

- 行 328: `font=("Microsoft YaHei UI", 16, "bold"),`

- 行 341: `font=("Microsoft YaHei UI", 18, "bold"),`

- 行 355: `font=("Microsoft YaHei UI", 14),`

- 行 365: `font=("Microsoft YaHei UI", 14),`

- 行 375: `font=("Microsoft YaHei UI", 14),`

- 行 385: `font=("Microsoft YaHei UI", 14),`

- 行 397: `font=("Microsoft YaHei UI", 14),`

- 行 516: `font=("Microsoft YaHei UI", 20, "bold"),`

- 行 547: `font=("Microsoft YaHei UI", 13, "bold"),`

- 行 199: `font=("Consolas", 13),`

- 行 256: `font=("Consolas", 11),`

- 行 526: `font=("Consolas", 12),`


### ui\main_window_v2.py


#### Windows 字体

- 行 100: `font=("Microsoft YaHei UI", 28, "bold"),`

- 行 140: `font=("Microsoft YaHei UI", 16, "bold"),`

- 行 165: `font=("Microsoft YaHei UI", 14, "bold"),`

- 行 176: `font=("Microsoft YaHei UI", 13),`

- 行 187: `font=("Microsoft YaHei UI", 13),`

- 行 198: `font=("Microsoft YaHei UI", 13),`

- 行 209: `font=("Microsoft YaHei UI", 13),`

- 行 223: `font=("Microsoft YaHei UI", 16, "bold"),`

- 行 247: `font=("Microsoft YaHei UI", 20, "bold"),`

- 行 255: `font=("Microsoft YaHei UI", 16),`

- 行 276: `font=("Microsoft YaHei UI", 13),`

- 行 287: `font=("Microsoft YaHei UI", 13),`

- 行 296: `font=("Microsoft YaHei UI", 13),`

- 行 305: `font=("Microsoft YaHei UI", 13),`

- 行 314: `font=("Microsoft YaHei UI", 13),`

- 行 355: `font=("Microsoft YaHei UI", 18, "bold"),`

- 行 386: `font=("Microsoft YaHei UI", 12, "bold"),`

- 行 149: `font=("Consolas", 12),`

- 行 365: `font=("Consolas", 12),`


### ui\result_canvas_table.py


#### Windows 字体

- 行 96: `font=("Microsoft YaHei", 12, "bold")`

- 行 103: `font=("Microsoft YaHei", 12, "bold"),`

- 行 111: `font=("Microsoft YaHei", 12, "bold"),`

- 行 119: `font=("Microsoft YaHei", 12, "bold"),`

- 行 219: `font=("Microsoft YaHei", 13, "bold")`


### ui\result_table.py


#### Windows 字体

- 行 114: `font=("Microsoft YaHei", 12, "bold")`

- 行 121: `font=("Microsoft YaHei", 12, "bold"),`

- 行 129: `font=("Microsoft YaHei", 12, "bold"),`

- 行 137: `font=("Microsoft YaHei", 12, "bold"),`

- 行 231: `font=("Microsoft YaHei", 13, "bold")`


### ui\settlement_window.py


#### Windows 字体

- 行 41: `font=("Microsoft YaHei UI", 20, "bold")`

- 行 53: `font=("Microsoft YaHei UI", 14)`

- 行 60: `font=("Microsoft YaHei UI", 14)`

- 行 69: `font=("Microsoft YaHei UI", 14)`

- 行 76: `font=("Microsoft YaHei UI", 14),`

- 行 85: `font=("Microsoft YaHei UI", 14, "bold"),`

- 行 98: `font=("Microsoft YaHei UI", 16, "bold")`

- 行 105: `font=("Consolas", 12),`


### uninstall.bat


#### Windows 特定目录

- 行 41: `set "START_MENU=%ProgramData%\Microsoft\Windows\Start Menu\Programs\十二动物号码归纳器"`


### update_play_mode_values.py


#### SQLite 连接

- 行 5: `conn = sqlite3.connect(db_path)`

- 行 4: `db_path = os.path.join(os.environ.get('APPDATA', ''), 'AnimalNumberLedger', 'ledger.db')`


#### Windows 特定目录

- 行 4: `db_path = os.path.join(os.environ.get('APPDATA', ''), 'AnimalNumberLedger', 'ledger.db')`


### verify_data_integrity.py


#### SQLite 连接

- 行 24: `conn = sqlite3.connect(str(real_db_path))`

- 行 18: `real_db_path = get_app_data_dir() / 'ledger.db'`


#### Windows 特定目录

- 行 9: `base = Path(os.environ.get('APPDATA', Path.home()))`


### verify_history_db.py


#### SQLite 连接

- 行 13: `conn = sqlite3.connect(db_path)`

- 行 9: `db_path = "data.db"`


### 启动程序.bat


#### Windows 绝对路径

- 行 2: `cd /d C:\Users\2SS2\animal-number-ledger`

- 行 2: `cd /d C:\Users\2SS2\animal-number-ledger`


### 完整任务.bat


#### Windows 绝对路径

- 行 3: `cd /d C:\Users\2SS2\animal-number-ledger`

- 行 5: `set PATH=C:\Program Files\Git\cmd;%PATH%`

- 行 13: `"C:\Program Files\Git\cmd\git.exe" add .`

- 行 17: `"C:\Program Files\Git\cmd\git.exe" status`

- 行 21: `"C:\Program Files\Git\cmd\git.exe" commit -m "v1.2.1: Sort results by amount and support continuous animal names" -m "Features:" -m "1. Sort results by amount (desc) and number (asc)" -m "2. Support continuous animal names without separator" -m "3. Fix decimal point parsing error" -m "4. Keep two decimal places display format"`

- 行 26: `"C:\Program Files\Git\cmd\git.exe" push origin main`

- 行 3: `cd /d C:\Users\2SS2\animal-number-ledger`

- 行 5: `set PATH=C:\Program Files\Git\cmd;%PATH%`

- 行 13: `"C:\Program Files\Git\cmd\git.exe" add .`

- 行 17: `"C:\Program Files\Git\cmd\git.exe" status`

- 行 21: `"C:\Program Files\Git\cmd\git.exe" commit -m "v1.2.1: Sort results by amount and support continuous animal names" -m "Features:" -m "1. Sort results by amount (desc) and number (asc)" -m "2. Support continuous animal names without separator" -m "3. Fix decimal point parsing error" -m "4. Keep two decimal places display format"`

- 行 26: `"C:\Program Files\Git\cmd\git.exe" push origin main`


### 快速启动.bat


#### Windows 绝对路径

- 行 2: `cd /d C:\Users\2SS2\animal-number-ledger`

- 行 2: `cd /d C:\Users\2SS2\animal-number-ledger`


### 执行推送.bat


#### Windows 绝对路径

- 行 3: `cd /d C:\Users\2SS2\animal-number-ledger`

- 行 5: `set PATH=C:\Program Files\Git\cmd;%PATH%`

- 行 13: `"C:\Program Files\Git\cmd\git.exe" status -sb`

- 行 17: `"C:\Program Files\Git\cmd\git.exe" push origin main`

- 行 3: `cd /d C:\Users\2SS2\animal-number-ledger`

- 行 5: `set PATH=C:\Program Files\Git\cmd;%PATH%`

- 行 13: `"C:\Program Files\Git\cmd\git.exe" status -sb`

- 行 17: `"C:\Program Files\Git\cmd\git.exe" push origin main`


### 推送v1.2.0.bat


#### Windows 绝对路径

- 行 11: `cd /d C:\Users\2SS2\animal-number-ledger`

- 行 11: `cd /d C:\Users\2SS2\animal-number-ledger`


### 推送v1.2.1-final.bat


#### Windows 绝对路径

- 行 3: `cd /d C:\Users\2SS2\animal-number-ledger`

- 行 10: `set PATH=C:\Program Files\Git\cmd;%PATH%`

- 行 13: `"C:\Program Files\Git\cmd\git.exe" add .`

- 行 17: `"C:\Program Files\Git\cmd\git.exe" commit -m "v1.2.1: Sort results by amount and support continuous animal names" -m "1. Sort results by amount (desc) and number (asc)" -m "2. Support continuous animal names: ?????75" -m "3. Keep decimal display format: 168.00" -m "4. Update CHANGELOG with all improvements"`

- 行 21: `"C:\Program Files\Git\cmd\git.exe" push origin main`

- 行 3: `cd /d C:\Users\2SS2\animal-number-ledger`

- 行 10: `set PATH=C:\Program Files\Git\cmd;%PATH%`

- 行 13: `"C:\Program Files\Git\cmd\git.exe" add .`

- 行 17: `"C:\Program Files\Git\cmd\git.exe" commit -m "v1.2.1: Sort results by amount and support continuous animal names" -m "1. Sort results by amount (desc) and number (asc)" -m "2. Support continuous animal names: ?????75" -m "3. Keep decimal display format: 168.00" -m "4. Update CHANGELOG with all improvements"`

- 行 21: `"C:\Program Files\Git\cmd\git.exe" push origin main`


### 推送v1.2.1.bat


#### Windows 绝对路径

- 行 3: `cd /d C:\Users\2SS2\animal-number-ledger`

- 行 10: `set PATH=C:\Program Files\Git\cmd;%PATH%`

- 行 13: `"C:\Program Files\Git\cmd\git.exe" add .`

- 行 17: `"C:\Program Files\Git\cmd\git.exe" commit -m "v1.2.1: Fix parser logic for dot separator" -m "- Fix: Dots in numbers no longer treated as decimal points" -m "- Improved: Find keyword first, then split number and amount" -m "- Now correctly parses: 1.2.3?0.50 as numbers 1,2,3" -m "- Update version to 1.2.1" -m "- Update CHANGELOG.md"`

- 行 21: `"C:\Program Files\Git\cmd\git.exe" push origin main`

- 行 3: `cd /d C:\Users\2SS2\animal-number-ledger`

- 行 10: `set PATH=C:\Program Files\Git\cmd;%PATH%`

- 行 13: `"C:\Program Files\Git\cmd\git.exe" add .`

- 行 17: `"C:\Program Files\Git\cmd\git.exe" commit -m "v1.2.1: Fix parser logic for dot separator" -m "- Fix: Dots in numbers no longer treated as decimal points" -m "- Improved: Find keyword first, then split number and amount" -m "- Now correctly parses: 1.2.3?0.50 as numbers 1,2,3" -m "- Update version to 1.2.1" -m "- Update CHANGELOG.md"`

- 行 21: `"C:\Program Files\Git\cmd\git.exe" push origin main`


### 推送v1.2.2.bat


#### Windows 绝对路径

- 行 3: `cd /d C:\Users\2SS2\animal-number-ledger`

- 行 10: `set PATH=C:\Program Files\Git\cmd;%PATH%`

- 行 13: `"C:\Program Files\Git\cmd\git.exe" add .`

- 行 17: `"C:\Program Files\Git\cmd\git.exe" commit -m "v1.2.2: Smart parser - extract numbers from any format" -m "Features:" -m "- Auto extract all numbers from input" -m "- Last number is always the amount" -m "- Ignore all non-numeric characters" -m "- Support any input format" -m "" -m "Examples:" -m "- ?:05.09.30?8d ? numbers: 05,09,30 amount: 8" -m "- abc 1.2.3 ? 0.50 ? numbers: 1,2,3 amount: 0.50" -m "- ?05-09-30??88? ? numbers: 05,09,30 amount: 88"`

- 行 21: `"C:\Program Files\Git\cmd\git.exe" push origin main`

- 行 3: `cd /d C:\Users\2SS2\animal-number-ledger`

- 行 10: `set PATH=C:\Program Files\Git\cmd;%PATH%`

- 行 13: `"C:\Program Files\Git\cmd\git.exe" add .`

- 行 17: `"C:\Program Files\Git\cmd\git.exe" commit -m "v1.2.2: Smart parser - extract numbers from any format" -m "Features:" -m "- Auto extract all numbers from input" -m "- Last number is always the amount" -m "- Ignore all non-numeric characters" -m "- Support any input format" -m "" -m "Examples:" -m "- ?:05.09.30?8d ? numbers: 05,09,30 amount: 8" -m "- abc 1.2.3 ? 0.50 ? numbers: 1,2,3 amount: 0.50" -m "- ?05-09-30??88? ? numbers: 05,09,30 amount: 88"`

- 行 21: `"C:\Program Files\Git\cmd\git.exe" push origin main`


### 直接推送v1.2.0.bat


#### Windows 绝对路径

- 行 3: `cd /d C:\Users\2SS2\animal-number-ledger`

- 行 10: `set PATH=C:\Program Files\Git\cmd;%PATH%`

- 行 13: `"C:\Program Files\Git\cmd\git.exe" add .`

- 行 17: `"C:\Program Files\Git\cmd\git.exe" commit -m "v1.2.0: Support all punctuation marks as separators"`

- 行 21: `"C:\Program Files\Git\cmd\git.exe" push origin main`

- 行 3: `cd /d C:\Users\2SS2\animal-number-ledger`

- 行 10: `set PATH=C:\Program Files\Git\cmd;%PATH%`

- 行 13: `"C:\Program Files\Git\cmd\git.exe" add .`

- 行 17: `"C:\Program Files\Git\cmd\git.exe" commit -m "v1.2.0: Support all punctuation marks as separators"`

- 行 21: `"C:\Program Files\Git\cmd\git.exe" push origin main`


### 立即推送v1.2.0.bat


#### Windows 绝对路径

- 行 3: `cd /d C:\Users\2SS2\animal-number-ledger`

- 行 3: `cd /d C:\Users\2SS2\animal-number-ledger`


### 重试推送.bat


#### Windows 绝对路径

- 行 3: `cd /d C:\Users\2SS2\animal-number-ledger`

- 行 5: `set PATH=C:\Program Files\Git\cmd;%PATH%`

- 行 13: `"C:\Program Files\Git\cmd\git.exe" status`

- 行 17: `"C:\Program Files\Git\cmd\git.exe" push origin main`

- 行 3: `cd /d C:\Users\2SS2\animal-number-ledger`

- 行 5: `set PATH=C:\Program Files\Git\cmd;%PATH%`

- 行 13: `"C:\Program Files\Git\cmd\git.exe" status`

- 行 17: `"C:\Program Files\Git\cmd\git.exe" push origin main`


## 修复建议


### 1. 路径处理

创建统一的跨平台路径模块 `platform_paths.py`：

```python

def get_user_data_dir():

    if sys.platform == 'win32':

        return Path(os.environ['APPDATA']) / 'AnimalNumberLedger'

    elif sys.platform == 'darwin':

        return Path.home() / 'Library' / 'Application Support' / 'AnimalNumberLedger'

    else:

        return Path.home() / '.local' / 'share' / 'AnimalNumberLedger'

```


### 2. SQLite 连接

所有 `sqlite3.connect()` 调用必须使用 `get_database_path()`


### 3. 字体处理

使用字体回退机制，macOS 使用 PingFang SC 或 Heiti SC


### 4. Windows 特定代码

使用 `sys.platform` 条件判断，保留 Windows 功能的同时添加 macOS 支持
