# 十二动物号码归纳器

**版本**: 1.1.0

生产级离线桌面应用，用于管理和归纳十二动物号码数据。

## 特性

- ✅ 完全离线运行，无需网络连接
- ✅ SQLite 本地数据库，数据安全可靠
- ✅ 每日自动结算并归档总账金额
- ✅ 完整的历史记录查询
- ✅ JSON 备份与恢复
- ✅ CSV 导出
- ✅ 动物号码表自定义
- ✅ 精确的小数计算（无浮点误差）
- ✅ 永久删除功能（需二次确认）
- ✅ 37 项自动化测试

## 系统要求

- **Windows**: Windows 10 或更高版本
- **macOS**: macOS 10.15 (Catalina) 或更高版本
- **Python**: 3.11 或更高版本（仅开发需要）

## 安装

### Windows

1. 下载 `十二动物号码归纳器-v1.1.0.exe`
2. 双击运行即可，无需安装

### macOS

**通过GitHub Actions自动构建（推荐）**：

1. 访问项目的 [Actions页面](../../actions)
2. 点击最新的成功构建（绿色✓）
3. 在"Artifacts"部分下载：
   - `macos-dmg` - DMG安装包（推荐，双击安装）
   - `macos-app` - .app文件（解压后直接使用）

**首次打开**：
- 右键点击应用 → 选择"打开" → 点击"打开"确认
- （由于应用未签名，必须右键打开）

**注意**：GitHub Actions构建的文件会保留30天

### 从源代码运行

```bash
# 克隆或解压源代码
cd animal-number-ledger

# 安装依赖
pip install -r requirements.txt

# 运行
python app.py
```

## 数据文件位置

### Windows
```
%APPDATA%\AnimalNumberLedger\
  ├── ledger.db      # 数据库文件
```

### macOS
```
~/Library/Application Support/AnimalNumberLedger/
  ├── ledger.db      # 数据库文件
```

### Linux
```
~/.local/share/AnimalNumberLedger/
  ├── ledger.db      # 数据库文件
```

## 使用说明

### 基本操作

1. **输入指令**：在输入框中输入指令，每行一条
2. **解析预览**：输入后自动显示解析结果
3. **确认追加**：确认无误后点击"确认追加"按钮
4. **查看结果**：右侧显示 01-49 的累计金额
5. **查看来源**：点击任意号码查看其来源

### 指令格式

支持以下格式：

```
1号13
1号13斤
1、7、20、49各13
1、7、20、49个13斤
1号、7号、20号、49号各13斤
龙各号20
龙每号20斤
龙、牛各数20
龙/牛个号20斤
```

### 关键词说明

- **各号、各、每号、每个、个、各数**：表示对每个目标分别应用金额
- **号**：仅作为号码的修饰词
- **斤**：仅作为金额单位
- **分隔符**：支持逗号（中英文）、顿号、空格、加号、斜杠

### 动物号码表

默认映射：

- 马：1、13、25、37、49
- 蛇：2、14、26、38
- 龙：3、15、27、39
- 兔：4、16、28、40
- 虎：5、17、29、41
- 牛：6、18、30、42
- 鼠：7、19、31、43
- 猪：8、20、32、44
- 狗：9、21、33、45
- 鸡：10、22、34、46
- 猴：11、23、35、47
- 羊：12、24、36、48

可通过"动物号码表"按钮自定义，但必须满足：
- 12 个动物
- 号码 1-49 全部出现且不重复
- 1 个动物有 5 个号码，其余 11 个各有 4 个号码

### 每日结算与归档

- 软件启动时检查并结算跨日遗留账本
- 程序运行中每分钟检查一次
- 跨日（00:00 后）自动计算并固化当天总账金额
- 主界面显示最近一次结算日期和总账金额
- 历史记录显示每个已归档账本的结算总账金额
- 归档后创建新账本，累计从 0 开始
- 输入框中未提交的文字会保留
- “结算并清空今日”可在当天手动完成一次结算并开启新账本

### 历史记录

功能：
- 按日期查看历史账本
- 查看每个账本的详细结果
- 查看号码来源
- 导出为 CSV
- 永久删除（需输入确认文本）

### 备份与恢复

**导出备份**：
- 完整的 JSON 格式备份
- 包含所有设置、账本、批次、指令、分配
- 包含历史动物映射快照
- 包含每个已归档账本的结算总账金额

**恢复备份**：
- 从 JSON 恢复数据
- 自动验证备份完整性
- 使用数据库事务，失败自动回滚
- 恢复前自动在应用数据目录创建安全备份
- ⚠️ 恢复前会清空当前所有数据

### 永久删除

支持：
- 删除选中的历史账本
- 删除全部历史记录

安全措施：
- 无法删除当前活动账本
- 删除前必须输入确认文本
- 使用数据库事务，失败自动回滚
- 删除后无法恢复（建议先导出备份）

确认文本：
- 删除选中：`永久删除`
- 删除全部：`永久删除全部记录`

## 测试

运行全部测试：

```bash
python -m pytest tests/ -v
```

或使用软件内的"运行自检"按钮。

### 测试覆盖

当前共有 37 项自动化测试，实际测试名称及结果以 pytest 输出为准。重点覆盖：

- 指令解析、动物及号码计算和多行累计
- `0.29`、`1.15`、`2.30` 等小数的精确转换
- 超长金额和超过两位小数的拒绝处理
- 批次、指令及分配记录的原子保存与失败回滚
- 程序持续运行跨日及关闭后隔日重启结算
- 结算总账金额的固化、历史查询和备份恢复
- 动物映射校验、级联删除及残缺备份拒绝

## 已知限制

1. **不支持撤销删除**：永久删除后无法恢复，请谨慎操作
2. **单机使用**：不支持多用户或网络同步
3. **操作系统限制**：
   - Windows 打包只能在 Windows 上进行
   - macOS 打包只能在 macOS 上进行
4. **数据库大小**：建议定期导出备份并清理历史数据

## 卸载

### 卸载前备份

**重要**：卸载前请导出备份，否则数据将永久丢失！

1. 打开软件
2. 点击"导出备份"按钮
3. 保存 JSON 备份文件到安全位置

### 卸载步骤

1. **删除应用程序**
   - Windows: 删除 `十二动物号码归纳器-v1.1.0.exe`
   - macOS: 将应用拖入废纸篓

2. **删除数据文件**（参考上方"数据文件位置"）
   - Windows: 删除 `%APPDATA%\AnimalNumberLedger\`
   - macOS: 删除 `~/Library/Application Support/AnimalNumberLedger/`
   - Linux: 删除 `~/.local/share/AnimalNumberLedger/`

## 数据库结构

### 表结构

- **settings**: 软件设置和动物号码表
- **ledgers**: 账本表（日期、编号、状态）
- **batches**: 批次表（原始输入、累计金额、映射快照）
- **instructions**: 指令表（解析后的指令详情）
- **allocations**: 分配表（每个号码的具体分配）

### 外键约束

- `batches.ledger_id` → `ledgers.id` (CASCADE)
- `instructions.batch_id` → `batches.id` (CASCADE)
- `allocations.instruction_id` → `instructions.id` (CASCADE)

### 金额存储

所有金额扩大 100 倍存储为整数，避免浮点误差：
- 13.00 → 1300
- 0.50 → 50
- 0.10 → 10

## 技术栈

- **界面**: CustomTkinter (基于 Tkinter)
- **数据库**: SQLite 3
- **打包**: PyInstaller
- **测试**: unittest/pytest
- **Python 版本**: 3.11+

## 开发

### 项目结构

```
animal-number-ledger/
├── app.py                    # 主程序入口
├── parser.py                 # 指令解析器
├── calculator.py             # 计算器
├── database.py               # 数据库操作
├── models.py                 # 数据模型
├── daily_rollover.py         # 每日归档
├── backup.py                 # 备份恢复
├── constants.py              # 常量定义
├── ui/                       # 界面模块
│   ├── main_window.py
│   ├── history_window.py
│   ├── mapping_window.py
│   └── delete_dialog.py
├── tests/                    # 测试模块
│   ├── test_parser.py
│   ├── test_calculator.py
│   ├── test_database.py
│   ├── test_rollover.py
│   ├── test_deletion.py
│   ├── test_backup.py
│   └── test_runner.py
├── requirements.txt          # 依赖列表
├── build_windows.bat         # Windows 打包脚本
├── build_macos.sh            # macOS 打包脚本
├── VERSION                   # 版本号
└── README.md                 # 本文件
```

### 自动构建（推荐）

项目使用GitHub Actions自动构建macOS版本：

- **自动触发**：推送到main/master分支时自动构建
- **手动触发**：在Actions页面点击"Run workflow"按钮
- **构建产物**：.app文件和.dmg安装包
- **保留时间**：30天

配置文件：`.github/workflows/mac-build.yml`

### 本地构建

**macOS本地打包**（需要Mac电脑）：
```bash
pip install pyinstaller
pyinstaller --name="十二动物号码归纳器" \
  --windowed \
  --onefile \
  --add-data="ui:ui" \
  --osx-bundle-identifier="com.animal-number-ledger.app" \
  app.py
```

**Windows**:
```cmd
build_windows.bat
```

## 许可证

此项目为专用软件，未授权不得分发或修改。

## 联系方式

如有问题或建议，请联系开发者。

---

**版本**: 1.1.0  
**最后更新**: 2026-07-23
