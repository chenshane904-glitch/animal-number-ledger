# 手动推送 macOS 代码指南

## 问题说明

当前 Git 无法连接到 GitHub（连接超时或重置）。

## 解决方案

### 方案 1: 使用 GitHub Desktop（推荐）

1. **打开 GitHub Desktop**
2. **选择仓库**: animal-number-ledger
3. **切换分支**: 切换到 `macos-packaging` 分支
4. **查看更改**: 应该看到所有新文件
5. **推送**: 点击 "Push origin" 按钮

### 方案 2: 使用 SSH 协议

如果已配置 SSH 密钥：

```bash
cd C:\Users\2SS2\animal-number-ledger
git remote set-url origin git@github.com:chenshane904-glitch/animal-number-ledger.git
git push origin macos-packaging
```

### 方案 3: 等待网络稳定后重试

```bash
cd C:\Users\2SS2\animal-number-ledger
git push origin macos-packaging
```

### 方案 4: 创建 Pull Request（手动上传）

1. 访问 GitHub 网页版
2. 进入仓库页面
3. 使用 "Upload files" 功能
4. 上传以下新文件：
   - platform_paths.py
   - platform_fonts.py
   - requirements-macos.txt
   - packaging/macos.spec
   - .github/workflows/build-macos.yml
   - scan_macos_compatibility.py
   - test_macos_compatibility.py
   - MACOS_COMPATIBILITY_REPORT.md
   - MACOS_PACKAGING_REPORT.md

5. 修改 app.py（替换导入部分）

## 推送成功后的下一步

### 1. 在 GitHub 上触发构建

访问：https://github.com/chenshane904-glitch/animal-number-ledger/actions

1. 点击 "Build macOS App" 工作流
2. 点击 "Run workflow"
3. 选择分支: `macos-packaging`
4. 点击绿色 "Run workflow" 按钮

### 2. 监控构建进度

- Apple Silicon 构建：约 10-15 分钟
- Intel 构建：约 10-15 分钟
- 可以实时查看日志

### 3. 下载 DMG

构建完成后：
1. 进入对应的 workflow run
2. 滚动到 "Artifacts" 部分
3. 下载：
   - AnimalNumberLedger-macOS-arm64
   - AnimalNumberLedger-macOS-Intel

## 当前本地代码状态

### 分支信息
```
main: Windows 稳定版本（未修改）
macos-packaging: macOS 兼容代码（所有新开发）
```

### 已提交但未推送的 commits
```
f1a3830 - Add final macOS packaging report
97a180b - Add macOS compatibility tests
8c3f9ac - Add macOS packaging configuration
dd727ca - Add cross-platform path and font modules
8573137 - stable desktop version before macOS packaging
```

### 新增文件列表
1. platform_paths.py
2. platform_fonts.py
3. requirements-macos.txt
4. packaging/macos.spec
5. .github/workflows/build-macos.yml
6. scan_macos_compatibility.py
7. test_macos_compatibility.py
8. MACOS_COMPATIBILITY_REPORT.md
9. MACOS_PACKAGING_REPORT.md

### 修改文件
1. app.py - 使用统一路径模块

## 验证推送成功

推送成功后，访问：
https://github.com/chenshane904-glitch/animal-number-ledger/tree/macos-packaging

应该能看到：
- 新的 macos-packaging 分支
- 所有新文件
- 最新的 commit

## 如果仍然无法推送

可以将整个项目文件夹打包发给我，或者：

1. 暂时放弃推送，稍后网络稳定时再试
2. 当前所有代码都已在本地 Git 仓库中
3. 可以随时推送到 GitHub
4. 推送后即可触发自动构建

## 网络诊断

如果持续无法连接，可以尝试：

```bash
# 测试 GitHub 连接
ping github.com

# 测试 HTTPS 连接
curl -I https://github.com

# 清除 DNS 缓存
ipconfig /flushdns
```

---

**当前状态**: 代码已完成，本地已提交，等待推送到 GitHub
