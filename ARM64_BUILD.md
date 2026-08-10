# ARM64 Only Build - macos-14

## 配置

### 当前设置
- **Runner**: `macos-14` (Apple Silicon 专用)
- **架构**: ARM64 only
- **Python**: 3.11
- **标签**: v1.2.2-arm64

### 改动
1. ✅ 明确使用 `macos-14` runner
2. ✅ 移除 Intel 构建 job
3. ✅ 最小化步骤
4. ✅ 只验证 ARM64

### Workflow 步骤

```yaml
1. Checkout
2. Setup Python 3.11
3. Install Dependencies
4. Build App (PyInstaller)
5. Verify App
6. Sign App
7. Create DMG
8. Upload to Release
```

### 输出文件
- `AnimalNumberLedger-macOS-arm64.dmg`

## 当前状态

- **提交**: 6d689db
- **标签**: v1.2.2-arm64
- **状态**: 已触发构建

## 查看进度

https://github.com/chenshane904-glitch/animal-number-ledger/actions

查找标签为 `v1.2.2-arm64` 的构建。

## 成功后

如果 ARM64 构建成功，将添加 Intel 构建：
- 新增 `build-intel` job
- 使用 `macos-13` runner
- 输出 `AnimalNumberLedger-macOS-x86_64.dmg`

---

**等待 ARM64 构建完成...**
