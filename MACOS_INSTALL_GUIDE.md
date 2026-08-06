# macOS 安装和打包指南

## 🍎 在 macOS 上运行

### 方法1：直接运行（最简单）

1. **打开终端（Terminal）**
   - 按 `Command + 空格`
   - 输入 "Terminal"
   - 回车

2. **进入项目目录**
   ```bash
   cd /path/to/animal-number-ledger
   ```

3. **运行程序**
   ```bash
   # 澳门版（传统布局）
   python3 app.py
   
   # V2版（卡片布局）
   python3 app_v2.py
   
   # 香港版（标签页布局）
   python3 app_hk.py
   ```

---

## 📦 打包成 macOS 应用（.app）

### 方法2：使用 PyInstaller 打包

#### 步骤1：安装 PyInstaller

```bash
pip3 install pyinstaller
```

#### 步骤2：创建打包脚本

将项目复制到 macOS 后，运行以下命令：

```bash
# 打包澳门版
pyinstaller --name="动物号码归纳器-澳门版" \
    --windowed \
    --icon=icon.icns \
    --add-data="ui:ui" \
    --add-data="tests:tests" \
    app.py

# 打包V2版
pyinstaller --name="动物号码归纳器-V2版" \
    --windowed \
    --icon=icon.icns \
    --add-data="ui:ui" \
    --add-data="tests:tests" \
    app_v2.py

# 打包香港版
pyinstaller --name="香港十二生肖投注系统" \
    --windowed \
    --icon=icon.icns \
    --add-data="ui:ui" \
    --add-data="tests:tests" \
    app_hk.py
```

打包完成后，在 `dist` 文件夹中会生成 `.app` 应用。

---

## 📦 打包成 DMG 安装包

### 方法3：创建 DMG 镜像文件

#### 步骤1：先打包成 .app（参考方法2）

#### 步骤2：创建 DMG

```bash
# 安装 create-dmg 工具
brew install create-dmg

# 创建澳门版 DMG
create-dmg \
  --volname "动物号码归纳器-澳门版" \
  --window-pos 200 120 \
  --window-size 600 400 \
  --icon-size 100 \
  --icon "动物号码归纳器-澳门版.app" 175 120 \
  --hide-extension "动物号码归纳器-澳门版.app" \
  --app-drop-link 425 120 \
  "动物号码归纳器-澳门版.dmg" \
  "dist/动物号码归纳器-澳门版.app"

# 创建香港版 DMG
create-dmg \
  --volname "香港十二生肖投注系统" \
  --window-pos 200 120 \
  --window-size 600 400 \
  --icon-size 100 \
  --icon "香港十二生肖投注系统.app" 175 120 \
  --hide-extension "香港十二生肖投注系统.app" \
  --app-drop-link 425 120 \
  "香港十二生肖投注系统.dmg" \
  "dist/香港十二生肖投注系统.app"
```

---

## 🎯 快速打包脚本

我可以为您创建一键打包脚本。需要我创建吗？

---

## 📋 当前您需要做的

### 如果在 Windows 上：

```bash
# 直接双击运行
app.py           # 澳门版
app_v2.py        # V2版
app_hk.py        # 香港版

# 或命令行运行
python app.py
python app_v2.py
python app_hk.py
```

### 如果要转移到 macOS：

1. **将整个项目文件夹复制到 macOS**
2. **在 macOS 上安装依赖**：
   ```bash
   pip3 install customtkinter
   ```
3. **运行程序**：
   ```bash
   python3 app_hk.py
   ```

---

## 💡 推荐方案

### 最简单：直接运行
- 不需要打包
- 直接运行 Python 脚本
- 适合个人使用

### 专业版：打包成 .app
- 双击即可运行
- 不需要终端
- 看起来更专业

### 分发版：打包成 .dmg
- 可以分享给其他人
- 拖拽安装
- 最专业的方式

---

## ❓ 您想要哪种方式？

1. **在 Windows 上直接运行** - 现在就可以用
2. **转移到 macOS 运行** - 需要复制文件
3. **打包成 macOS .app** - 需要我创建打包脚本
4. **打包成 DMG 安装包** - 完整的安装包

请告诉我您的需求，我可以提供相应的帮助！
