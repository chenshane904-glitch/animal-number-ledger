"""
macOS 兼容性扫描工具
扫描项目中所有 Windows 特定代码
"""
import os
from pathlib import Path
import re

PROJECT_ROOT = Path(__file__).parent

# Windows 特定模式
WINDOWS_PATTERNS = {
    'Windows 绝对路径': [
        r'C:\\',
        r'C:/',
        r'[A-Z]:\\',
    ],
    'Windows 特定目录': [
        r'AppData',
        r'Roaming',
        r'LocalAppData',
        r'ProgramData',
    ],
    'PowerShell/批处理': [
        r'\.bat',
        r'\.ps1',
        r'PowerShell',
        r'cmd\.exe',
    ],
    'Windows API': [
        r'win32api',
        r'win32gui',
        r'win32con',
        r'win32com',
        r'pywin32',
        r'ctypes\.windll',
        r'os\.startfile',
    ],
    'Windows 注册表': [
        r'winreg',
        r'_winreg',
        r'HKEY_',
    ],
    'Windows 字体': [
        r'Microsoft YaHei',
        r'SimHei',
        r'SimSun',
        r'Consolas',
    ],
    'ICO 图标': [
        r'\.ico',
    ],
}

# SQLite 连接模式
SQLITE_PATTERNS = [
    r'sqlite3\.connect\(',
    r'data\.db',
    r'ledger\.db',
]

def scan_file(file_path):
    """扫描单个文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
    except:
        return None

    issues = []

    # 检查 Windows 特定模式
    for category, patterns in WINDOWS_PATTERNS.items():
        for pattern in patterns:
            for line_num, line in enumerate(lines, 1):
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append({
                        'category': category,
                        'line': line_num,
                        'content': line.strip(),
                        'pattern': pattern
                    })

    # 检查 SQLite 连接
    for pattern in SQLITE_PATTERNS:
        for line_num, line in enumerate(lines, 1):
            if re.search(pattern, line):
                issues.append({
                    'category': 'SQLite 连接',
                    'line': line_num,
                    'content': line.strip(),
                    'pattern': pattern
                })

    return issues if issues else None

def scan_project():
    """扫描整个项目"""
    print("开始扫描项目...")

    # 需要扫描的文件类型
    extensions = ['.py', '.bat', '.ps1']

    # 排除目录
    exclude_dirs = {'.git', '__pycache__', 'venv', 'env', '.venv', 'dist', 'build', '.pytest_cache'}

    all_issues = {}

    for root, dirs, files in os.walk(PROJECT_ROOT):
        # 排除特定目录
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                file_path = Path(root) / file
                relative_path = file_path.relative_to(PROJECT_ROOT)

                issues = scan_file(file_path)
                if issues:
                    all_issues[str(relative_path)] = issues

    return all_issues

def generate_report(issues):
    """生成报告"""
    report = []
    report.append("# macOS 兼容性扫描报告\n")
    report.append(f"扫描时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("\n## 扫描结果概要\n")

    if not issues:
        report.append("✓ 未发现 Windows 特定代码\n")
        return '\n'.join(report)

    # 统计
    total_files = len(issues)
    total_issues = sum(len(file_issues) for file_issues in issues.values())

    report.append(f"- 发现 {total_files} 个文件包含 Windows 特定代码\n")
    report.append(f"- 总计 {total_issues} 处需要检查\n")

    # 按类别统计
    category_count = {}
    for file_issues in issues.values():
        for issue in file_issues:
            cat = issue['category']
            category_count[cat] = category_count.get(cat, 0) + 1

    report.append("\n### 按类别统计\n")
    for cat, count in sorted(category_count.items(), key=lambda x: -x[1]):
        report.append(f"- {cat}: {count} 处\n")

    # 详细列表
    report.append("\n## 详细问题列表\n")

    for file_path, file_issues in sorted(issues.items()):
        report.append(f"\n### {file_path}\n")

        # 按类别分组
        by_category = {}
        for issue in file_issues:
            cat = issue['category']
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(issue)

        for cat, cat_issues in sorted(by_category.items()):
            report.append(f"\n#### {cat}\n")
            for issue in cat_issues:
                report.append(f"- 行 {issue['line']}: `{issue['content']}`\n")

    # 修复建议
    report.append("\n## 修复建议\n")
    report.append("\n### 1. 路径处理\n")
    report.append("创建统一的跨平台路径模块 `platform_paths.py`：\n")
    report.append("```python\n")
    report.append("def get_user_data_dir():\n")
    report.append("    if sys.platform == 'win32':\n")
    report.append("        return Path(os.environ['APPDATA']) / 'AnimalNumberLedger'\n")
    report.append("    elif sys.platform == 'darwin':\n")
    report.append("        return Path.home() / 'Library' / 'Application Support' / 'AnimalNumberLedger'\n")
    report.append("    else:\n")
    report.append("        return Path.home() / '.local' / 'share' / 'AnimalNumberLedger'\n")
    report.append("```\n")

    report.append("\n### 2. SQLite 连接\n")
    report.append("所有 `sqlite3.connect()` 调用必须使用 `get_database_path()`\n")

    report.append("\n### 3. 字体处理\n")
    report.append("使用字体回退机制，macOS 使用 PingFang SC 或 Heiti SC\n")

    report.append("\n### 4. Windows 特定代码\n")
    report.append("使用 `sys.platform` 条件判断，保留 Windows 功能的同时添加 macOS 支持\n")

    return '\n'.join(report)

if __name__ == '__main__':
    issues = scan_project()
    report = generate_report(issues)

    # 输出到控制台
    print(report)

    # 保存到文件
    report_path = PROJECT_ROOT / 'MACOS_COMPATIBILITY_REPORT.md'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\n报告已保存到: {report_path}")
