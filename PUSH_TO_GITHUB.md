# 推送到GitHub的完整步骤

## ⚠️ 前提条件

### 1. 安装Git
如果还没有安装Git：
- 访问：https://git-scm.com/download/win
- 下载并安装Git for Windows
- 安装完成后重启PowerShell或命令提示符

### 2. 配置Git（首次使用）
```bash
git config --global user.name "你的名字"
git config --global user.email "你的邮箱@example.com"
```

### 3. 创建GitHub账号
- 访问：https://github.com/signup
- 如果已有账号，请登录

---

## 🚀 推送步骤

### 步骤1: 在GitHub创建仓库

1. 访问：https://github.com/new
2. 填写信息：
   - Repository name: `animal-number-ledger`（或其他名称）
   - Description: 十二动物号码归纳器
   - 选择 Public 或 Private
   - **不要**勾选"Add a README file"
   - **不要**勾选"Add .gitignore"
3. 点击"Create repository"
4. **记下仓库地址**，格式为：`https://github.com/你的用户名/仓库名.git`

---

### 步骤2: 初始化本地Git仓库

打开PowerShell或命令提示符，执行：

```bash
cd C:\Users\2SS2\animal-number-ledger

# 初始化Git仓库
git init

# 添加所有文件
git add .

# 查看要提交的文件
git status

# 提交
git commit -m "Setup GitHub Actions for macOS build"
```

---

### 步骤3: 连接到GitHub仓库

```bash
# 添加远程仓库（替换为你的仓库地址）
git remote add origin https://github.com/你的用户名/仓库名.git

# 设置主分支为main
git branch -M main

# 推送到GitHub
git push -u origin main
```

**第一次推送时可能需要登录GitHub账号**

---

### 步骤4: 查看自动构建

1. 访问：`https://github.com/你的用户名/仓库名/actions`
2. 你会看到"Build macOS App"工作流正在运行（橙色圆圈）
3. 等待5-10分钟，直到显示绿色✓
4. 点击成功的构建

---

### 步骤5: 下载构建产物

1. 在构建详情页面，滚动到底部
2. 在"Artifacts"部分，你会看到：
   - **macos-dmg** - DMG安装包（推荐）
   - **macos-app** - .app应用文件
3. 点击下载（会下载为zip文件）

---

## 📦 使用构建的文件

### DMG安装包（推荐）

1. 解压下载的`macos-dmg.zip`
2. 得到`十二动物号码归纳器-v1.1.0.dmg`
3. 发送给Mac用户：
   - 双击DMG文件
   - 将应用拖到Applications文件夹
   - 右键应用 → 选择"打开"

### .app文件

1. 解压下载的`macos-app.zip`
2. 得到`十二动物号码归纳器.app`
3. 发送给Mac用户：
   - 右键应用 → 选择"打开"

---

## ⚠️ 重要提示

### 首次打开必须右键
由于应用未签名，Mac会阻止双击打开。

**正确方式**：
1. 右键点击应用
2. 选择"打开"
3. 在弹出的警告中点击"打开"
4. 以后可以正常双击打开

### 告诉Mac用户的输入格式
```
⚠️ 输入号码时用逗号分隔，不要用句号！

✅ 正确: 1,2,3各0.50
❌ 错误: 1.2.3各0.50
```

---

## 🔧 故障排除

### 问题1: Git命令不识别
**解决**：安装Git for Windows并重启终端

### 问题2: 推送时要求登录
**解决**：
- 输入GitHub用户名和密码
- 或使用Personal Access Token（推荐）
  1. GitHub Settings → Developer settings → Personal access tokens
  2. Generate new token (classic)
  3. 勾选 `repo` 权限
  4. 生成后复制token
  5. 推送时用token代替密码

### 问题3: 构建失败
**解决**：
1. 访问Actions页面查看错误日志
2. 常见问题：
   - requirements.txt文件格式错误
   - Python代码语法错误
   - 缺少必要文件

### 问题4: 找不到Artifacts
**解决**：
- 只有构建成功（绿色✓）才有Artifacts
- 检查构建是否完成
- 检查工作流是否启用

---

## 📝 快速命令参考

```bash
# 检查Git状态
git status

# 添加新文件
git add .

# 提交更改
git commit -m "描述信息"

# 推送到GitHub
git push

# 查看远程仓库
git remote -v

# 查看提交历史
git log --oneline
```

---

## 🎯 下一次更新代码

以后修改代码后，只需：

```bash
cd C:\Users\2SS2\animal-number-ledger
git add .
git commit -m "描述你的更改"
git push
```

每次推送都会自动触发GitHub Actions构建！

---

## 💡 手动触发构建

不推送代码也可以重新构建：

1. 访问：`https://github.com/你的用户名/仓库名/actions`
2. 点击左侧"Build macOS App"
3. 点击右上角"Run workflow"
4. 选择分支（main）
5. 点击"Run workflow"按钮

---

## 📞 需要帮助？

查看详细指南：`GITHUB_ACTIONS_GUIDE.md`
