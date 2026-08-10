# v1.2.3 下载指南

## 📥 如何下载

由于 GitHub Actions 权限限制，DMG 文件上传到 Artifacts，需要手动下载。

### 步骤 1: 访问 Actions 页面

https://github.com/chenshane904-glitch/animal-number-ledger/actions

### 步骤 2: 找到 v1.2.3 构建

1. 查找 "Build macOS App v1.2.3" workflow
2. 点击最新的成功构建（绿色✓）

### 步骤 3: 下载 Artifacts

滚动到页面底部，找到 **Artifacts** 区域：

**Apple Silicon (M1/M2/M3)**:
```
AnimalNumberLedger-v1.2.3-macOS-arm64
```

**Intel Mac**:
```
AnimalNumberLedger-v1.2.3-macOS-intel
```

点击下载对应的 ZIP 文件。

### 步骤 4: 解压

1. 下载的是 ZIP 文件
2. 双击解压
3. 得到 `.dmg` 文件

### 步骤 5: 安装

1. 双击 DMG 文件
2. 拖动应用到 Applications 文件夹
3. 打开应用

## ✅ 构建状态

两个构建都需要通过：
- ✓ macOS ARM64 (Apple Silicon) - macos-14
- ✓ macOS Intel (x86_64) - macos-13

每个构建包含：
1. ✓ 清理构建
2. ✓ PyInstaller 打包
3. ✓ 结构验证
4. ✓ 代码签名
5. ✓ **启动测试** (后台运行5秒)
6. ✓ 创建 DMG
7. ✓ 上传 Artifact

## 🔍 当前进度

查看: https://github.com/chenshane904-glitch/animal-number-ledger/actions

等待两个构建完成（约3-5分钟）

## 📝 首次运行

macOS 可能提示"无法验证开发者"：

1. 右键点击应用
2. 选择"打开"
3. 点击"打开"确认

之后就可以正常双击启动了。

## 🎯 测试验证

安装后测试：

**测试 1: 头数模式**
```
输入: 1头20
点击: 确认追加
检查: 列表显示 10-19 各20元
```

**测试 2: 历史记录**
```
点击: 历史记录按钮
检查: 显示刚才的输入
```

**测试 3: 重启测试**
```
关闭应用
重新打开
检查: 数据仍然存在
```

## 💾 数据位置

```
~/Library/Application Support/AnimalNumberLedger/
├── data.db          # 数据库（自动迁移）
└── logs/            # 日志文件
```

## ❓ 问题排查

### 启动失败
1. 查看日志: `~/Library/Application Support/AnimalNumberLedger/logs/`
2. 检查权限: 右键 → 打开

### 数据迁移失败
- 旧数据库会自动备份
- 新字段自动添加
- 如有问题查看日志

---

**v1.2.3 构建中，请等待 Actions 完成后下载 Artifacts**
