# 交付清单

## 项目信息

**项目名称**: 十二动物号码归纳器  
**版本**: 1.1.0  
**交付日期**: 2026-07-22  
**开发语言**: Python 3.11.9  

## 交付内容

### 1. 完整源代码

所有源代码位于 `animal-number-ledger/` 目录：

```
animal-number-ledger/
├── app.py                    # 主程序入口
├── parser.py                 # 指令解析器 (221 行)
├── calculator.py             # 计算器 (83 行)
├── database.py               # 数据库操作 (355 行)
├── models.py                 # 数据模型 (62 行)
├── daily_rollover.py         # 每日归档 (42 行)
├── backup.py                 # 备份恢复 (212 行)
├── constants.py              # 常量定义 (51 行)
├── ui/                       # 界面模块
│   ├── __init__.py
│   ├── main_window.py        # 主窗口 (476 行)
│   ├── history_window.py     # 历史记录窗口 (193 行)
│   ├── mapping_window.py     # 动物号码表设置 (110 行)
│   └── delete_dialog.py      # 删除确认对话框 (62 行)
├── tests/                    # 测试模块
│   ├── __init__.py
│   ├── test_parser.py        # 解析器测试 (14 个测试)
│   ├── test_calculator.py    # 计算器测试 (5 个测试)
│   ├── test_database.py      # 数据库测试 (9 个测试)
│   ├── test_rollover.py      # 跨日归档测试 (4 个测试)
│   ├── test_deletion.py      # 删除功能测试 (3 个测试)
│   ├── test_backup.py        # 备份恢复测试 (2 个测试)
│   └── test_runner.py        # 测试运行器
├── requirements.txt          # 依赖列表
├── build_windows.bat         # Windows 打包脚本
├── build_macos.sh            # macOS 打包脚本
├── VERSION                   # 版本号文件
├── README.md                 # 使用说明文档
├── test_offline.py           # 离线测试脚本
└── generate_report.py        # 测试报告生成器
```

**总代码量**: 约 2,000 行（不含空行和注释）

### 2. 可运行安装包

#### Windows 版本

**打包方法**:
```cmd
cd animal-number-ledger
build_windows.bat
```

**输出文件**: `dist/十二动物号码归纳器-v1.1.0.exe`  
**文件大小**: 约 14 MB（包含所有依赖）  
**运行要求**: Windows 10 或更高版本，无需安装 Python  

#### macOS 版本

**打包方法**:
```bash
cd animal-number-ledger
chmod +x build_macos.sh
./build_macos.sh
```

**输出文件**: `dist/十二动物号码归纳器-v1.1.0.app`  
**运行要求**: macOS 10.15 (Catalina) 或更高版本  

**注意**: macOS 打包必须在 macOS 系统上进行，Windows 系统无法生成 macOS 应用。

### 3. requirements.txt

```
customtkinter==5.2.1
```

**说明**: 项目仅使用一个第三方库 customtkinter，其他全部使用 Python 标准库。

### 4. 数据库结构说明

#### 表结构

**settings** - 软件设置
- key (TEXT, PRIMARY KEY): 设置键
- value (TEXT): 设置值

**ledgers** - 账本表
- id (INTEGER, PRIMARY KEY)
- ledger_date (TEXT): 日期 YYYY-MM-DD
- sequence_number (INTEGER): 当日序号
- status (TEXT): 状态 'active'/'archived'
- created_at (TIMESTAMP): 创建时间
- archived_at (TIMESTAMP): 归档时间

**batches** - 批次表
- id (INTEGER, PRIMARY KEY)
- ledger_id (INTEGER, FOREIGN KEY → ledgers.id)
- created_at (TIMESTAMP): 创建时间
- raw_input (TEXT): 原始输入
- total_before (INTEGER): 追加前总数
- total_after (INTEGER): 追加后总数
- mapping_snapshot (TEXT): 动物映射快照 (JSON)

**instructions** - 指令表
- id (INTEGER, PRIMARY KEY)
- batch_id (INTEGER, FOREIGN KEY → batches.id)
- source_line (INTEGER): 源行号
- original_text (TEXT): 原始文本
- normalized_text (TEXT): 标准化文本
- target_type (TEXT): 目标类型 'number'/'animal'
- targets (TEXT): 目标列表 (JSON)
- amount_integer (INTEGER): 金额（整数，扩大100倍）
- warning (TEXT): 警告信息

**allocations** - 分配表
- id (INTEGER, PRIMARY KEY)
- instruction_id (INTEGER, FOREIGN KEY → instructions.id)
- number (INTEGER): 号码 (1-49)
- animal (TEXT): 动物名
- amount_integer (INTEGER): 金额（整数，扩大100倍）

#### 外键约束

所有外键启用 CASCADE DELETE，删除父记录时自动删除子记录。

### 5. README.md

完整的使用说明文档，包含：
- 功能特性
- 系统要求
- 安装方法
- 使用说明
- 指令格式
- 数据库结构
- 测试说明
- 卸载方法

### 6. 自动化测试结果

37 项自动化测试 **全部通过** ✓

- 解析器测试 14 项：包含精确小数、超长金额和非法精度
- 计算器测试 5 项：包含号码、动物、累计和来源
- 数据库测试 9 项：包含原子追加、失败回滚、旧库升级和结算金额固化
- 跨日结算测试 4 项：包含持续运行跨日及隔夜重启
- 删除功能测试 3 项
- 备份恢复测试 2 项：包含结算金额恢复及残缺备份拒绝

实际测试名称及结果以 pytest 输出和 `TEST_REPORT.txt` 为准。

### 7. 断网测试结果

✓ **网络导入检查**: 通过 - 未发现任何网络相关导入  
✓ **离线单元测试**: 通过 - 所有测试在离线环境下通过  

**断网测试项目**:
- ✓ 启动程序
- ✓ 指令解析
- ✓ 追加累计
- ✓ 历史查询
- ✓ 跨日结算与归档
- ✓ 永久删除
- ✓ JSON 备份
- ✓ JSON 恢复
- ✓ CSV 导出

**结论**: 源码无网络调用，核心自动化测试可在完全断网环境运行。

### 8. 已知限制

1. **不支持撤销删除**: 永久删除后无法恢复，建议操作前先导出备份
2. **单机使用**: 不支持多用户或网络同步
3. **跨平台打包**: Windows 打包只能在 Windows 上进行，macOS 打包只能在 macOS 上进行
4. **数据库大小**: 长期使用建议定期导出备份并清理历史数据
5. **界面语言**: 仅支持简体中文

### 9. 安装方法

#### Windows

1. 下载 `十二动物号码归纳器-v1.1.0.exe`
2. 双击运行，无需安装
3. 首次运行会在 `%APPDATA%\AnimalNumberLedger\` 创建数据目录

#### macOS

1. 下载 `十二动物号码归纳器-v1.1.0.app`
2. 拖动到应用程序文件夹
3. 右键点击选择"打开"（首次运行，绕过安全检查）
4. 数据保存在 `~/Library/Application Support/AnimalNumberLedger/`

#### 从源代码运行

```bash
# 安装依赖
pip install -r requirements.txt

# 运行程序
python app.py
```

### 10. 数据文件位置

- **Windows**: `%APPDATA%\AnimalNumberLedger\ledger.db`
- **macOS**: `~/Library/Application Support/AnimalNumberLedger/ledger.db`
- **Linux**: `~/.local/share/AnimalNumberLedger/ledger.db`

### 11. 卸载前备份说明

**重要**: 卸载前必须手动导出备份，否则数据将永久丢失！

卸载步骤：
1. 打开软件
2. 点击"导出备份"按钮
3. 保存 JSON 备份文件到安全位置
4. 删除应用程序
5. 手动删除数据目录（参考上方"数据文件位置"）

### 12. SHA-256 文件校验值

打包完成后，构建脚本会自动生成 `dist/SHA256.txt` 文件，包含可执行文件的 SHA-256 校验值。

用户可使用以下命令验证文件完整性：

**Windows**:
```cmd
certutil -hashfile "十二动物号码归纳器-v1.1.0.exe" SHA256
```

**macOS**:
```bash
shasum -a 256 "十二动物号码归纳器-v1.1.0.app/Contents/MacOS/十二动物号码归纳器-v1.1.0"
```

## 验收标准

所有验收标准 **全部满足** ✓

- ✓ 完整源代码（模块化设计，非单文件）
- ✓ 可运行的 Windows 安装包（.exe）
- ✓ requirements.txt（仅1个第三方库）
- ✓ 数据库结构说明（5个表，完整外键）
- ✓ README.md（完整文档）
- ✓ 37项测试全部通过
- ✓ 断网测试通过
- ✓ 已知限制说明
- ✓ 安装方法说明
- ✓ 数据文件位置说明
- ✓ 卸载前备份说明
- ✓ SHA-256 校验值（自动生成）

## 技术亮点

1. **精确计算**: 使用整数存储金额（扩大100倍），完全避免浮点误差
2. **事务安全**: 所有写操作使用数据库事务，失败自动回滚
3. **历史追溯**: 每个批次保存动物映射快照，修改映射不影响历史记录
4. **完全离线**: 零网络依赖，可在断网环境下完全正常运行
5. **跨日智能**: 自动结算总账金额并归档，保留未提交输入
6. **测试验证**: 37个自动化测试覆盖关键业务与回归场景
7. **数据安全**: 支持完整JSON备份恢复，删除需二次确认

## 后续支持

如需功能扩展或问题修复，源代码结构清晰，易于维护：

- 解析器: 修改 `parser.py` 和 `constants.py`
- 计算逻辑: 修改 `calculator.py`
- 数据库: 修改 `database.py`（需要迁移脚本）
- 界面: 修改 `ui/` 目录下的文件
- 测试: 在 `tests/` 目录添加新测试

## 联系信息

项目已完整交付，所有功能正常运行。

---

**交付日期**: 2026-07-22  
**交付状态**: ✓ 完成
