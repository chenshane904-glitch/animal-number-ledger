# macOS 打包重构方案

## 目标

生成一个真实可安装的 macOS DMG 安装包，支持 Apple Silicon (ARM64)。

## 项目结构重构

### 固定结构
```
animal-number-ledger/
├── app.py                          # 主入口
├── assets/                         # 资源目录（新增）
│   ├── play_groups.json           # 组合玩法配置
│   └── play_modes.json            # 玩法模式配置
├── packaging/
│   └── macos.spec                 # PyInstaller配置
├── .github/
│   └── workflows/
│       └── build-macos.yml        # 仅ARM64构建
└── requirements-macos.txt         # macOS依赖
```

### 关键改动

1. **创建 assets 目录**
   - 所有资源文件统一放在 `assets/` 目录
   - JSON配置文件：`play_groups.json`, `play_modes.json`
   - 未来可添加图标、图片等资源

2. **更新资源引用**
   - `play_group_parser.py`: `play_groups.json` → `assets/play_groups.json`
   - `play_mode_config.py`: `play_modes.json` → `assets/play_modes.json`
   - `test_macos_compatibility.py`: 测试路径更新

3. **重写 macos.spec**
   - 使用 `app.py` 作为入口点
   - 自动递归包含 `assets/` 目录下所有文件
   - 完整的 hiddenimports 列表
   - 包含所有UI模块和核心模块

4. **简化 GitHub Actions**
   - 删除 Intel 构建（只保留 ARM64）
   - 增加完整的构建后验证
   - 发布到 GitHub Release（不使用 Artifacts）

## PyInstaller 配置详解

### macos.spec 关键点

```python
# 1. 递归包含 assets 目录
assets_dir = os.path.join(project_root, 'assets')
for root, dirs, files in os.walk(assets_dir):
    for file in files:
        file_path = os.path.join(root, file)
        rel_path = os.path.relpath(file_path, project_root)
        dest_dir = os.path.dirname(rel_path)
        datas.append((file_path, dest_dir))

# 2. 完整的 hiddenimports
hiddenimports = [
    'customtkinter',
    'PIL',
    'sqlite3',
    'database',
    'calculator_factory',
    'ui.main_window',
    # ... 所有运行时需要的模块
]

# 3. 排除不需要的模块
excludes = [
    'tkinter.test',
    'unittest',
    'darkdetect',  # 避免兼容性问题
]
```

### 打包命令

```bash
pyinstaller packaging/macos.spec --clean --noconfirm
```

**不允许**直接使用 `pyinstaller app.py`，必须通过 spec 文件。

## GitHub Actions 工作流

### 构建阶段

1. **环境准备**
   - 使用 `macos-latest` (Apple Silicon runner)
   - Python 3.11 ARM64

2. **验证阶段**
   - 检查 assets 目录存在
   - 检查 spec 文件存在
   - 验证所有资源文件

3. **构建阶段**
   - 执行 `pyinstaller packaging/macos.spec`
   - 清理构建缓存

4. **验证构建结果**
   - ✓ `.app` 是否存在
   - ✓ `Info.plist` 是否存在
   - ✓ 可执行文件是否存在
   - ✓ 可执行文件是否有执行权限
   - ✓ `assets` 是否打包到 `.app` 内
   - ✓ 验证可执行文件架构 (ARM64)

5. **签名阶段**
   - Ad-hoc 签名（开发测试用）
   - 验证签名

6. **创建 DMG**
   - 创建标准 DMG 布局
   - 包含 Applications 快捷方式
   - 验证 DMG 完整性

7. **发布到 Release**
   - 仅在 tag 推送时触发
   - 文件名：`AnimalNumberLedger-arm64.dmg`
   - 自动生成 Release Notes

### 验证检查点

```yaml
- name: Verify app bundle structure
  run: |
    # 检查 .app
    [ -d "dist/AnimalNumberLedger.app" ] || exit 1
    
    # 检查 Contents
    [ -d "dist/AnimalNumberLedger.app/Contents" ] || exit 1
    
    # 检查 Info.plist
    [ -f "dist/AnimalNumberLedger.app/Contents/Info.plist" ] || exit 1
    
    # 检查可执行文件
    [ -f "dist/AnimalNumberLedger.app/Contents/MacOS/AnimalNumberLedger" ] || exit 1
    
    # 检查执行权限
    [ -x "dist/AnimalNumberLedger.app/Contents/MacOS/AnimalNumberLedger" ] || exit 1
    
    # 检查 assets
    [ -d "dist/AnimalNumberLedger.app/Contents/MacOS/assets" ] || exit 1
```

## 本地测试

### 测试脚本

运行 `test_macos_build.sh`:

```bash
chmod +x test_macos_build.sh
./test_macos_build.sh
```

脚本会执行：
1. 检查项目结构
2. 安装依赖
3. 运行 PyInstaller
4. 验证构建结果
5. 创建 DMG

### 手动测试流程

1. **构建应用**
   ```bash
   pip install -r requirements-macos.txt
   pyinstaller packaging/macos.spec --clean --noconfirm
   ```

2. **验证构建**
   ```bash
   # 检查 .app
   ls -la dist/AnimalNumberLedger.app
   
   # 检查 assets
   ls -la dist/AnimalNumberLedger.app/Contents/MacOS/assets/
   
   # 检查架构
   file dist/AnimalNumberLedger.app/Contents/MacOS/AnimalNumberLedger
   ```

3. **签名**
   ```bash
   codesign --force --deep --sign - dist/AnimalNumberLedger.app
   codesign --verify --verbose dist/AnimalNumberLedger.app
   ```

4. **创建 DMG**
   ```bash
   mkdir -p dmg
   cp -r dist/AnimalNumberLedger.app dmg/
   ln -s /Applications dmg/Applications
   hdiutil create -volname "AnimalNumberLedger" \
     -srcfolder dmg -ov -format UDZO \
     AnimalNumberLedger-arm64.dmg
   ```

5. **测试 DMG**
   ```bash
   # 挂载 DMG
   hdiutil attach AnimalNumberLedger-arm64.dmg
   
   # 检查内容
   ls -la /Volumes/AnimalNumberLedger/
   
   # 卸载
   hdiutil detach /Volumes/AnimalNumberLedger
   ```

## 安装验证流程

### 完整验证步骤

1. **下载 DMG**
   - 从 GitHub Release 下载 `AnimalNumberLedger-arm64.dmg`

2. **安装应用**
   - 双击打开 DMG
   - 将 `AnimalNumberLedger.app` 拖动到 `Applications` 文件夹
   - 等待复制完成

3. **首次启动**
   - 打开 `Applications` 文件夹
   - 找到 `AnimalNumberLedger`
   - **右键点击** → **打开**（绕过 Gatekeeper）
   - 在弹出对话框中点击**打开**

4. **验证功能**
   - ✓ 应用正常启动
   - ✓ 主窗口显示
   - ✓ 号码模式正常
   - ✓ 平特模式正常
   - ✓ 头数按钮显示
   - ✓ 输入、计算、结算功能正常
   - ✓ 数据库读写正常
   - ✓ 历史记录正常

5. **验证资源文件**
   - 测试组合玩法（确认 `play_groups.json` 加载成功）
   - 切换玩法模式（确认 `play_modes.json` 加载成功）
   - 测试头数功能（确认代码更新生效）

## 系统要求

- **操作系统**: macOS 10.13 或更高版本
- **处理器**: Apple Silicon (M1/M2/M3)
- **Python**: 3.11（构建时）
- **磁盘空间**: 约 100MB

## 已知问题和解决方案

### 问题1: Gatekeeper 阻止启动

**现象**: 双击应用时提示"无法打开，因为它来自身份不明的开发者"

**解决方案**:
```bash
# 方法1: 右键打开
右键点击应用 → 打开 → 打开

# 方法2: 移除隔离属性
xattr -cr /Applications/AnimalNumberLedger.app
```

### 问题2: 资源文件找不到

**现象**: 启动时提示找不到 JSON 配置文件

**原因**: assets 目录未正确打包

**解决方案**:
1. 检查 spec 文件中的 datas 配置
2. 重新构建并验证 `dist/AnimalNumberLedger.app/Contents/MacOS/assets/`

### 问题3: darkdetect 兼容性

**现象**: 启动崩溃，日志显示 darkdetect 错误

**解决方案**: 
- spec 文件中已排除 darkdetect
- customtkinter 会自动降级到默认模式

## 版本历史

### v1.2.2 (当前版本)
- ✓ 重构资源文件到 assets 目录
- ✓ 新增头数筛选功能
- ✓ 优化 PyInstaller 配置
- ✓ 简化 GitHub Actions（仅 ARM64）
- ✓ 发布到 GitHub Release

## 下一步计划

1. **添加应用图标**
   - 设计 1024x1024 图标
   - 转换为 .icns 格式
   - 更新 spec 文件

2. **代码签名**
   - 获取 Apple Developer 账号
   - 配置代码签名证书
   - 公证应用

3. **Intel 支持**
   - 添加 x86_64 构建
   - 创建 Universal Binary

4. **自动更新**
   - 集成 Sparkle 框架
   - 实现应用内更新检查

## 总结

本次重构完成了：
- ✓ 资源文件统一管理
- ✓ PyInstaller 配置优化
- ✓ GitHub Actions 简化
- ✓ 完整的构建验证
- ✓ GitHub Release 发布
- ✓ 详细的安装验证流程

**必须完成的验证步骤**：
1. 下载 DMG
2. 安装到 Applications
3. 首次启动（右键打开）
4. 验证所有功能正常

只有完成以上4步，才算真正完成 macOS 打包。
