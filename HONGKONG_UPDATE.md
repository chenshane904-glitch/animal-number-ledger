# 香港版本更新说明

## ✅ 名称简化完成

所有"香港十二生肖投注系统"已统一改为简洁的 **"香港"**

---

## 📝 修改内容

### 1. 窗口标题
```
修改前: 🇭🇰 香港十二生肖投注系统 HK v1.0
修改后: 香港
```

### 2. 应用名称
```
修改前: 香港十二生肖投注系统
修改后: 香港
```

### 3. 数据库目录
```
修改前: %APPDATA%/AnimalNumberLedger_HK/
修改后: %APPDATA%/HongKong/
```

### 4. macOS 应用
```
修改前: 香港十二生肖投注系统.app
修改后: 香港.app
```

### 5. DMG 安装包
```
修改前: 香港十二生肖投注系统.dmg
修改后: 香港.dmg
```

---

## 🚀 启动方式

### Windows
```bash
python app_hk.py
```

### macOS
```bash
python3 app_hk.py
```

### 打包 (macOS)
```bash
./build_macos.sh
# 选择: 3) 香港
# 输出: dist/香港.app
```

---

## 📊 版本对比

| 项目 | 澳门版 | 香港版 |
|------|--------|--------|
| 窗口标题 | 十二动物号码归纳器 v1.2.2 | **香港** |
| 应用名称 | 动物号码归纳器 | **香港** |
| 数据库 | ledger.db | ledger_hk.db |
| 数据目录 | AnimalNumberLedger/ | **HongKong/** |
| 可同时运行 | ❌（与V2版共享数据库） | ✅ |

---

## ✨ 关键特性

### 简洁设计
- ✅ 窗口标题只显示"香港"
- ✅ 应用名称只显示"香港"
- ✅ 无多余文字

### 独立运行
- ✅ 独立数据库目录：`HongKong/`
- ✅ 独立数据文件：`ledger_hk.db`
- ✅ 可与澳门版同时运行

### 功能完整
- ✅ 100% 保留所有计算功能
- ✅ 100% 保留所有解析功能
- ✅ 100% 保留所有统计功能
- ✅ 100% 保留所有结算功能

---

## 🎯 使用场景

### 单独使用
```bash
# 只运行香港版
python app_hk.py
```

### 同时使用
```bash
# 终端1: 运行澳门版
python app.py

# 终端2: 运行香港版
python app_hk.py

# 两个版本互不影响，数据独立
```

---

## 📁 文件结构

```
animal-number-ledger/
├── app.py                      # 澳门版启动
├── app_hk.py                   # 香港版启动 ⭐
│
├── ui/
│   ├── main_window.py          # 澳门版UI
│   └── main_window_hk.py       # 香港版UI ⭐
│
└── build_macos.sh              # macOS打包脚本 ⭐
```

---

## 💾 数据位置

### Windows
```
澳门版: %APPDATA%\AnimalNumberLedger\ledger.db
香港版: %APPDATA%\HongKong\ledger_hk.db
```

### macOS
```
澳门版: ~/Library/Application Support/AnimalNumberLedger/ledger.db
香港版: ~/Library/Application Support/HongKong/ledger_hk.db
```

### Linux
```
澳门版: ~/.local/share/AnimalNumberLedger/ledger.db
香港版: ~/.local/share/HongKong/ledger_hk.db
```

---

## ✅ 验证测试

### 导入测试
```python
from ui.main_window_hk import MainWindowHK
# 应该成功导入，无错误
```

### 窗口标题测试
```python
# 运行 app_hk.py
# 窗口标题应显示: 香港
```

### 数据隔离测试
```python
# 同时运行 app.py 和 app_hk.py
# 两个版本应该互不影响
```

---

## 🎊 总结

香港版本已完成简化：

✅ **名称统一** - 所有地方都显示"香港"  
✅ **简洁大方** - 去除冗余文字  
✅ **独立运行** - 与澳门版完全隔离  
✅ **功能完整** - 所有功能保持不变  

**立即启动：`python app_hk.py`** 🚀
