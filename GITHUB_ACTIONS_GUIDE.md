# GitHub Actions 自动构建指南

## 🚀 如何获取macOS版本

### 方法1：等待自动构建（推荐）

1. **推送代码到GitHub**：
   ```bash
   git add .
   git commit -m "Setup GitHub Actions for macOS build"
   git push origin main
   ```

2. **查看构建进度**：
   - 访问你的GitHub仓库
   - 点击顶部的"Actions"标签
   - 看到正在运行的工作流（橙色圆圈）

3. **等待构建完成**（约5-10分钟）：
   - 构建成功会显示绿色✓
   - 构建失败会显示红色✗

4. **下载构建产物**：
   - 点击成功的构建
   - 滚动到底部"Artifacts"部分
   - 下载：
     - `macos-dmg` - DMG安装包（推荐）
     - `macos-app` - .app应用文件

### 方法2：手动触发构建

如果你想立即构建：

1. 访问GitHub仓库的Actions页面
2. 点击左侧的"Build macOS App"
3. 点击右上角的"Run workflow"按钮
4. 选择分支（main或master）
5. 点击"Run workflow"绿色按钮
6. 等待构建完成并下载

## 📦 使用构建的文件

### DMG安装包（推荐）

1. 解压下载的`macos-dmg.zip`
2. 双击`十二动物号码归纳器-v1.1.0.dmg`
3. 将应用拖到Applications文件夹
4. 打开Applications，右键应用 → 选择"打开"

### .app文件

1. 解压下载的`macos-app.zip`
2. 将`十二动物号码归纳器.app`拖到任意位置
3. 右键应用 → 选择"打开"

## ⚠️ 首次打开必须右键

由于应用未签名，Mac会阻止双击打开。

**正确方式**：
1. 右键点击应用
2. 选择"打开"
3. 在弹出的警告中点击"打开"
4. 以后可以正常双击打开

## 🔧 工作流配置说明

工作流文件：`.github/workflows/mac-build.yml`

**触发条件**：
- 推送到main/master分支
- 提交Pull Request到main/master
- 手动触发（workflow_dispatch）

**构建步骤**：
1. 检出代码
2. 设置Python 3.11环境
3. 安装依赖（requirements.txt）
4. 使用PyInstaller构建.app
5. 创建DMG安装包
6. 上传构建产物（保留30天）

## 📝 常见问题

**Q: 构建失败了怎么办？**
A: 点击失败的构建查看日志，找到红色错误信息

**Q: 找不到Artifacts？**
A: 只有构建成功的工作流才有Artifacts，检查是否显示绿色✓

**Q: Artifacts过期了？**
A: 重新运行工作流（手动触发）生成新的构建

**Q: 如何修改版本号？**
A: 编辑`mac-build.yml`中的DMG文件名

**Q: 需要Apple开发者账号吗？**
A: 不需要！这是未签名的测试版本

## 🎯 下一步

1. **推送到GitHub** - 触发第一次自动构建
2. **等待完成** - 约5-10分钟
3. **下载测试** - 在Mac上测试.app和.dmg
4. **分享给用户** - 告诉他们如何下载和使用

## 💡 提示

- 构建产物保留30天，定期重新构建
- 每次推送代码都会自动构建
- 可以在Actions中取消正在运行的构建
- 查看构建日志可以帮助调试问题
