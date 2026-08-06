# 🔍 macOS 构建文件名验证报告

## 当前状态

### GitHub Actions 显示
- Artifact 名称：**macos-dmg**
- 这是旧的名称，不是我们要的 "香港-macOS-dmg"

### 工作流配置（已修改）
```yaml
- name: Upload 香港.dmg
  uses: actions/upload-artifact@v3
  with:
    name: 香港-macOS-dmg    # 配置正确
    path: 香港.dmg
```

---

## 问题分析

### 可能原因
1. **GitHub Actions 缓存** - 使用了旧的工作流版本
2. **并发构建** - 有两个 run (#25 和 #6) 同时进行
3. **工作流未更新** - 推送时 GitHub 还没刷新配置

### Run #25 的情况
- ✅ 构建成功
- ❌ 但 Artifact 名称显示为 "macos-dmg"（旧名称）
- 📦 大小：15.73 MB

---

## 解决方案

### 方案1：触发新构建（推荐）
```bash
git commit --allow-empty -m "Force rebuild"
git push origin main
```
- 等待网络恢复后执行
- 强制使用最新的工作流配置

### 方案2：手动下载验证
1. 下载 Run #25 的 "macos-dmg" artifact
2. 解压查看里面的实际文件名
3. 确认是 "香港.dmg" 还是 "十二动物号码归纳器-v1.2.2.dmg"

### 方案3：等待自动触发
- 下次代码推送会自动触发新构建
- 新构建应该使用最新配置

---

## 文件名检查清单

需要验证的实际文件名：

### 在 Artifact 压缩包内
- [ ] 香港.app（不是 十二动物号码归纳器.app）
- [ ] 香港.dmg（不是 十二动物号码归纳器-v1.2.2.dmg）

### Info.plist 内容
- [ ] CFBundleName = 香港
- [ ] CFBundleDisplayName = 香港
- [ ] CFBundleIdentifier = com.animalledger.hongkong

### Finder 显示
- [ ] App 名称显示：香港
- [ ] DMG 卷标显示：香港

---

## 下一步操作

### 等待网络恢复后
1. ✅ 推送空提交触发新构建
2. ⏳ 监控新构建（Run #26 或更高）
3. ✅ 验证新构建的 Artifact 名称
4. ✅ 下载并检查实际文件名

### 如果新构建成功
- Artifact 名称应该是：**香港-macOS-dmg**
- 内部文件应该是：**香港.dmg**

### 如果还是旧名称
需要检查：
1. PyInstaller 的 --name 参数是否生效
2. create-dmg 的 volume name 是否正确
3. 是否有其他配置覆盖了名称

---

## 当前工作流配置摘要

```yaml
# 构建命令
pyinstaller \
  --name="香港" \                    # ✅ 设置 app 名称
  --windowed \
  --noconsole \
  --osx-bundle-identifier=com.animalledger.hongkong \  # ✅ 唯一ID
  --hidden-import=customtkinter \
  --collect-all customtkinter \
  --onedir \
  app_hk.py

# DMG 创建
hdiutil create \
  -volname "香港" \                  # ✅ DMG 卷标
  -srcfolder "dist/香港.app" \      # ✅ 源 app
  -ov -format UDZO "香港.dmg"       # ✅ 输出文件名

# 上传
name: 香港-macOS-dmg                # ✅ Artifact 名称
path: 香港.dmg                      # ✅ 文件路径
```

---

## 待办事项

- [ ] 等待网络恢复
- [ ] 推送空提交触发构建
- [ ] 验证 Run #26+ 的 Artifact 名称
- [ ] 下载并解压验证实际文件名
- [ ] 确认所有名称都是"香港"

---

**状态**: 等待网络恢复以触发新构建  
**最新提交**: 已准备好空提交  
**下次构建**: Run #26（预期）
