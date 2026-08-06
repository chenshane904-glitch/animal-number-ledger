# 🔍 macOS 命名问题最终诊断报告

## 问题确认

✅ **已确认**: 下载的 macOS 安装包仍然是旧名称
- 您下载并安装后，显示的是旧版本名称
- 不是"香港"

## 根本原因分析

### 发现的问题

1. **两个工作流文件冲突**（已解决）
   - ❌ `mac-build.yml` (旧配置) - 已删除
   - ✅ `build-macos.yml` (新配置) - 保留

2. **PyInstaller 可能从其他地方读取了应用信息**
   - 可能的来源：
     - `app_hk.py` 中的某些元数据
     - 自动生成的 `.spec` 文件缓存
     - PyInstaller 的默认行为

3. **验证步骤失败**
   - Run #9 构建失败（这是好事，说明验证在工作）
   - 失败原因需要查看日志

## 建议的解决方案

### 方案A: 使用完整的 .spec 文件（推荐）

创建一个完整的 `hongkong_macos.spec`，明确指定所有参数：

```python
# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['app_hk.py'],
    pathex=[],
    binaries=[],
    datas=[('ui', 'ui'), ('tests', 'tests')],
    hiddenimports=['customtkinter', 'PIL._tkinter_finder'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='香港',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    name='香港',
)

app = BUNDLE(
    coll,
    name='香港.app',
    icon=None,
    bundle_identifier='com.animalledger.hongkong',
    info_plist={
        'CFBundleName': '香港',
        'CFBundleDisplayName': '香港',
        'CFBundleExecutable': '香港',
        'CFBundleIdentifier': 'com.animalledger.hongkong',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '10.13.0',
    },
)
```

### 方案B: 检查 app_hk.py 是否有隐藏的元数据

检查文件开头是否有 `__version__` 或其他元数据：

```python
__version__ = "1.2.2"  # 可能被 PyInstaller 读取
__app_name__ = "十二动物号码归纳器"  # 可能被读取
```

### 方案C: 清理所有缓存的 spec 文件

删除所有自动生成的 spec 文件：
- `香港.spec`
- `hongkong.spec`
- 任何其他 `.spec` 文件

然后只使用命令行参数。

## 当前状态

### Run #9 失败原因

需要查看日志确认，但可能是：
1. 验证步骤发现 `dist/香港.app` 不存在
2. 实际生成的是其他名称的 .app
3. PyInstaller 构建本身失败

### 下一步行动

1. 查看 Run #9 的构建日志
2. 确认实际生成的文件名
3. 根据日志选择上述方案之一
4. 重新构建并验证

## 临时解决方案

如果急需 macOS 版本：

1. 在本地 Mac 上手动构建：
   ```bash
   cd animal-number-ledger
   ./build_macos.sh
   # 选择 3) 香港
   ```

2. 手动重命名下载的文件：
   - 虽然不推荐，但可以将下载的 `.app` 重命名为 `香港.app`
   - 使用 PlistBuddy 修改 Info.plist

## 需要检查的文件

1. Run #9 的构建日志（最重要）
2. `app_hk.py` 的元数据
3. PyInstaller 实际使用的 spec 文件
4. dist 目录中生成的实际文件名

---

**当前等待**: 查看 Run #9 日志以确定下一步
