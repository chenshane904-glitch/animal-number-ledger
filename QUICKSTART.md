# 快速开始指南

## 立即运行（开发模式）

### 前提条件
- Python 3.11 或更高版本
- 已安装依赖

### 步骤

1. **安装依赖**
```bash
cd animal-number-ledger
pip install -r requirements.txt
```

2. **运行程序**
```bash
python app.py
```

3. **开始使用**
   - 在输入框输入指令，例如：`1号13`
   - 点击"确认追加"
   - 查看右侧结果

## 运行测试

```bash
# 运行所有测试
python -m pytest tests/ -v

# 运行特定测试
python -m pytest tests/test_parser.py -v

# 生成测试报告
python generate_report.py

# 运行离线测试
python test_offline.py

# 运行最终验收
python final_acceptance.py
```

## 打包发布

### Windows
```cmd
build_windows.bat
```
生成 `dist/十二动物号码归纳器-v1.1.0.exe`

### macOS
```bash
chmod +x build_macos.sh
./build_macos.sh
```
生成 `dist/十二动物号码归纳器-v1.1.0.app`

## 指令示例

```
# 单个号码
1号13

# 多个号码
1、7、20、49各13

# 动物
龙各号20
龙、牛各数15

# 小数
1号0.50

# 多行
1号13
7号20
龙各号15
```

## 数据位置

- Windows: `%APPDATA%\AnimalNumberLedger\`
- macOS: `~/Library/Application Support/AnimalNumberLedger/`
- Linux: `~/.local/share/AnimalNumberLedger/`

## 功能快捷键

- **确认追加**: 输入后点击"确认追加"按钮
- **撤销**: 点击"撤销最近一次"按钮
- **手动结算**: 点击"结算并清空今日"，结算金额会保存在历史记录中
- **清空输入**: 点击"清空输入"按钮
- **查看来源**: 点击任意号码查看其来源
- **历史记录**: 点击"历史记录"按钮
- **备份**: 点击"导出备份"按钮

## 故障排除

### 问题：数据库错误
**解决**: 程序会自动提示，请备份数据文件后移走重试

### 问题：无法启动
**解决**: 
1. 确认 Python 版本 >= 3.11
2. 重新安装依赖：`pip install -r requirements.txt`
3. 检查是否有其他程序占用端口

### 问题：解析错误
**解决**: 
- 确保金额在末尾
- 多个目标必须使用"各号"、"各"等关键词
- 不能混合号码和动物

## 获取帮助

查看完整文档：
- README.md - 详细使用说明
- DELIVERY.md - 完整交付清单
- PROJECT_SUMMARY.md - 项目总结

---

**版本**: 1.1.0  
**更新日期**: 2026-07-23
