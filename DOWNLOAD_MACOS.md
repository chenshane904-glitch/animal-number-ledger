# 📦 macOS 安装包下载指南

## 🚀 GitHub Actions 自动构建

macOS 版本的 **香港.app** 和 **香港.dmg** 正在通过 GitHub Actions 自动构建。

---

## 📍 下载地址

### GitHub Actions 页面
```
https://github.com/chenshane904-glitch/animal-number-ledger/actions
```

---

## 📥 下载步骤（详细图文）

### 步骤 1：访问 GitHub Actions
1. 打开浏览器
2. 访问：https://github.com/chenshane904-glitch/animal-number-ledger/actions

### 步骤 2：找到最新构建
1. 在页面中找到最新的 **"Build macOS App"** 工作流
2. 查看状态：
   - 🟡 黄色圆圈 = 正在构建中（请等待）
   - ✅ 绿色勾号 = 构建成功
   - ❌ 红色叉号 = 构建失败（请联系开发者）

### 步骤 3：点击进入构建详情
1. 点击最新的 "Build macOS App" 工作流
2. 进入构建详情页面

### 步骤 4：下载 Artifacts
1. 滚动到页面底部
2. 找到 **"Artifacts"** 区域
3. 会看到两个下载链接：
   - **香港-macOS-app** (包含 香港.app)
   - **香港-macOS-dmg** (包含 香港.dmg)

### 步骤 5：选择下载
- **推荐下载**: **香港-macOS-dmg** (DMG 安装镜像)
- **高级用户**: **香港-macOS-app** (.app 应用程序包)

---

## 📦 文件说明

### 香港.dmg（推荐）
- **格式**: macOS 磁盘镜像
- **大小**: 约 40-60 MB
- **安装方式**:
  1. 双击 `香港.dmg`
  2. 拖拽 `香港.app` 到应用程序文件夹
  3. 弹出磁盘镜像
  4. 从启动台或应用程序文件夹运行

### 香港.app
- **格式**: macOS 应用程序包
- **大小**: 约 40-60 MB
- **使用方式**:
  1. 解压下载的 zip 文件
  2. 双击 `香港.app` 运行
  3. 或拖到应用程序文件夹

---

## ⏱️ 构建时间

- **预计时间**: 5-10 分钟
- **开始时间**: 推送代码后立即开始
- **完成后**: Artifacts 会自动出现在页面底部

---

## 🍎 macOS 使用说明

### 首次运行
1. 双击运行 `香港.app`
2. 如果遇到 "无法打开" 提示：
   - 右键点击 `香港.app`
   - 选择 "打开"
   - 在弹出的对话框中点击 "打开"
3. 以后就可以直接双击运行

### 数据位置
```
~/Library/Application Support/HongKong/
```

### 卸载方法
1. 将 `香港.app` 拖到废纸篓
2. 删除数据文件夹（可选）：
   ```
   ~/Library/Application Support/HongKong/
   ```

---

## 🔄 如果构建失败

### 检查日志
1. 在 GitHub Actions 页面点击失败的构建
2. 点击 "build-macos" 任务
3. 查看错误日志

### 重新触发构建
1. 访问：https://github.com/chenshane904-glitch/animal-number-ledger/actions
2. 点击 "Build macOS App" 工作流
3. 点击右上角的 "Re-run all jobs"

---

## ✨ 特性说明

### 独立运行
- ✅ 无需安装 Python
- ✅ 双击即可运行
- ✅ 自包含所有依赖

### 数据独立
- ✅ 独立的数据目录（HongKong/）
- ✅ 可与澳门版同时运行
- ✅ 互不影响

### 功能完整
- ✅ 100% 保留所有功能
- ✅ 数字解析
- ✅ 生肖识别
- ✅ 金额统计
- ✅ 47倍赔率结算

---

## 📞 需要帮助？

如果下载或安装遇到问题：
1. 检查 GitHub Actions 构建状态
2. 查看构建日志
3. 确认 macOS 版本兼容性（需要 macOS 10.13+）

---

## 🎯 快速链接

- **GitHub Actions**: https://github.com/chenshane904-glitch/animal-number-ledger/actions
- **仓库主页**: https://github.com/chenshane904-glitch/animal-number-ledger
- **问题反馈**: https://github.com/chenshane904-glitch/animal-number-ledger/issues

---

## 📊 构建状态

构建完成后，您可以在此处看到：

```
✅ Build macOS App
   └─ Artifacts
      ├─ 香港-macOS-app (点击下载)
      └─ 香港-macOS-dmg (点击下载) ⭐ 推荐
```

---

**⏰ 请等待 5-10 分钟让 GitHub Actions 完成构建**

构建完成后，刷新页面即可看到下载链接！
