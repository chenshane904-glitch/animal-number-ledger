# PyInstaller 版本修复

## 问题诊断

### 失败模式
- 所有构建都在 30-41 秒后快速失败
- 不是 runner 资源问题
- 可能是依赖兼容性问题

### 根本原因（推测）
```
pyinstaller==6.21.0  # 太新，可能有兼容性问题
pyinstaller-hooks-contrib==2026.6  # 版本过新
```

## 解决方案

### 降级到稳定版本
```
pyinstaller==6.3.0  # 稳定版本
pyinstaller-hooks-contrib==2024.0  # 匹配版本
```

## 当前构建

- **标签**: v1.2.2-stable
- **提交**: df3cf67
- **改动**: requirements-macos.txt
- **状态**: 已触发

## 查看进度

https://github.com/chenshane904-glitch/animal-number-ledger/actions

查找标签 `v1.2.2-stable` 的构建

## 预期

如果是 PyInstaller 版本问题：
- ✅ 构建应该成功
- ✅ 生成 DMG
- ✅ 发布到 Release

如果仍然失败：
- 点击查看详细日志
- 检查具体错误信息

---

**等待构建结果...**
