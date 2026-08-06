# 📦 安装和使用指南

## 当前位置

```
C:\Users\2SS2\animal-number-ledger
```

---

## 🖥️ Windows 上使用（当前系统）

### 方法1：直接双击运行

在文件资源管理器中，双击以下文件：

- **app.py** - 澳门版（传统布局）
- **app_v2.py** - V2版（卡片布局）
- **app_hk.py** - 香港版（标签页布局）⭐ 推荐

### 方法2：命令行运行

```cmd
python app.py      # 澳门版
python app_v2.py   # V2版
python app_hk.py   # 香港版
```

---

## 🍎 macOS 上使用

### 步骤1：复制项目到 Mac

将整个 `animal-number-ledger` 文件夹复制到 macOS

### 步骤2：安装依赖

打开终端（Terminal），运行：

```bash
cd /path/to/animal-number-ledger
pip3 install customtkinter
```

### 步骤3：运行程序

```bash
python3 app_hk.py    # 香港版（推荐）
python3 app_v2.py    # V2版
python3 app.py       # 澳门版
```

### 步骤4：打包成 macOS 应用（可选）

```bash
# 运行自动打包脚本
chmod +x build_macos.sh
./build_macos.sh

# 选择要打包的版本
# 打包完成后在 dist/ 文件夹中找到 .app 文件
```

---

## 📊 三个版本对比

| 版本 | 特点 | 推荐场景 |
|------|------|----------|
| **澳门版** | 传统左右分栏，49行号码 | 习惯传统界面 |
| **V2版** | 卡片布局，12个动物卡片 | 喜欢现代设计 |
| **香港版** ⭐ | 标签页设计，功能分区清晰 | 大屏幕，多功能 |

---

## 🎯 推荐使用

### Windows
```cmd
python app_hk.py
```

### macOS
```bash
python3 app_hk.py
```

---

## 💡 重要提示

1. **香港版和澳门版可以同时运行**（独立数据库）
2. **澳门版和V2版不建议同时运行**（共享数据库）
3. 数据库位置：
   - Windows: `%APPDATA%\AnimalNumberLedger\`
   - macOS: `~/Library/Application Support/AnimalNumberLedger/`

---

## 📞 需要帮助？

查看详细文档：
- `README_HK.md` - 香港版说明
- `MACOS_INSTALL_GUIDE.md` - macOS详细指南
- `HK_VERSION_REPORT.md` - 开发报告
