# macOS 启动测试版本

## 🔧 关键修复

### 1. 资源路径修复

**问题**: 资源文件使用相对路径，打包后无法找到

**修复**:
```python
# play_group_parser.py
- self.config_path = Path(config_path)
+ self.config_path = get_resource_path(config_path)

# play_mode_config.py  
- config_path = Path(__file__).parent / 'assets' / 'play_modes.json'
+ config_path = get_resource_path('assets/play_modes.json')
```

**原理**: `get_resource_path()` 自动处理开发环境和打包环境：
- 开发环境: 使用项目目录
- 打包环境: 使用 `sys._MEIPASS` (PyInstaller临时目录)

### 2. 数据库路径

已经正确使用 `get_database_path()`：
- macOS: `~/Library/Application Support/AnimalNumberLedger/data.db`
- 自动创建目录

## ✅ workflow 改进

### 验证步骤

1. **结构检查**
   ```
   ✓ Contents/ 存在
   ✓ MacOS/ 存在
   ✓ Resources/ 存在
   ✓ Info.plist 存在
   ✓ 可执行文件存在且有权限
   ✓ assets/ 资源文件存在
   ```

2. **签名**
   ```
   codesign --force --deep --sign -
   codesign --verify
   ```

3. **启动测试** ⭐
   ```bash
   # 后台启动应用
   AnimalNumberLedger.app/Contents/MacOS/AnimalNumberLedger &
   
   # 等待5秒
   sleep 5
   
   # 检查进程是否还在运行
   if ps -p $PID; then
     ✓ 启动成功
   else
     ✗ 启动失败 → 不生成 DMG
   fi
   ```

4. **创建 DMG**
   - 只有启动测试通过才执行
   - 失败则构建失败

## 📦 当前构建

- **标签**: v1.2.2-launch-test
- **提交**: 52217ae
- **状态**: 已触发

## 🔗 查看进度

https://github.com/chenshane904-glitch/animal-number-ledger/actions

查找标签 `v1.2.2-launch-test` 的构建

## 🎯 预期结果

### 如果成功
- ✅ 结构检查通过
- ✅ 资源文件找到
- ✅ 应用启动成功（进程运行5秒）
- ✅ DMG 创建
- ✅ 可以下载测试

### 如果失败
- 查看"Test Launch App"步骤的日志
- 确定具体失败原因
- 继续修复

## 💡 关键改进

**之前**: 直接打包，不验证启动
**现在**: 先启动测试，通过才打包

这样确保生成的DMG在Mac上可以正常启动。

---

**等待构建结果，查看启动测试是否通过...**
