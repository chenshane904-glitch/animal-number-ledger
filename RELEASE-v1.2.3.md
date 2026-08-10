# v1.2.3 稳定版发布

## 🎉 版本信息

- **版本号**: v1.2.3
- **发布日期**: 2025年
- **提交**: 441e576
- **状态**: 稳定版

## ✨ 新功能

### 1. 头数模式

支持快速输入一组号码：

**输入格式**:
```
1头20    或    一头20    →  10-19 各20元
2头30    或    二头30    →  20-29 各30元
3头10    或    三头10    →  30-39 各10元
4头50    或    四头50    →  40-49 各50元
```

**自动展开**:
- 输入 `1头20` 
- 自动生成 10个号码（10, 11, 12, 13, 14, 15, 16, 17, 18, 19）
- 每个号码金额 20元
- 总计: 10号码 × 20元 = 200元

**不影响普通输入**:
- 输入 `20` 仍然代表号码20
- 只有 `1头/一头/2头/二头/3头/三头/4头/四头` 才触发头数模式

### 2. 数据库自动迁移

**问题**: 旧版本数据库缺少 `play_mode` 字段

**解决**: 
- ✅ 应用启动时自动检测数据库结构
- ✅ 缺少字段时自动添加
- ✅ 不丢失任何历史数据
- ✅ 不需要用户手动操作

**迁移逻辑**:
```sql
-- 检查字段是否存在
PRAGMA table_info(input_history)

-- 如果不存在，自动添加
ALTER TABLE input_history
ADD COLUMN play_mode TEXT NOT NULL DEFAULT 'number'
```

### 3. 双架构支持

**两个安装包**:
- `AnimalNumberLedger-v1.2.3-macOS-arm64.dmg` - Apple Silicon (M1/M2/M3)
- `AnimalNumberLedger-v1.2.3-macOS-intel.dmg` - Intel Mac

**构建流程**:
1. ✅ 清理旧构建
2. ✅ PyInstaller 构建 .app
3. ✅ 验证应用结构
4. ✅ 代码签名
5. ✅ **启动测试** (运行5秒)
6. ✅ 创建 DMG
7. ✅ 上传到 Release

## 🐛 修复问题

### 1. 头数输入识别错误
- **问题**: `1头20` 被识别为号码1金额20
- **修复**: 添加头数解析逻辑，正确识别并展开

### 2. 确认追加失败
- **问题**: `table input_history has no column named play_mode`
- **修复**: 数据库自动迁移，添加缺失字段

### 3. 模式数据隔离
- **号码模式**: 保存号码 + 金额
- **平特模式**: 保存动物 + 金额
- **完全隔离**: 切换模式不会混合数据

## 📦 安装包

### 下载地址

https://github.com/chenshane904-glitch/animal-number-ledger/releases/tag/v1.2.3

### 如何选择

**Apple Silicon (M1/M2/M3)**:
```
AnimalNumberLedger-v1.2.3-macOS-arm64.dmg
```

**Intel Mac**:
```
AnimalNumberLedger-v1.2.3-macOS-intel.dmg
```

### 安装步骤

1. 下载对应架构的 DMG
2. 双击打开 DMG
3. 拖动应用到 Applications 文件夹
4. 打开应用

### 首次运行

macOS 可能提示"无法验证开发者"：
1. 右键点击应用
2. 选择"打开"
3. 点击"打开"确认

## ✅ 测试验证

构建流程包含完整测试：

**结构验证**:
- ✓ Contents/ 目录
- ✓ MacOS/ 可执行文件
- ✓ Resources/ 资源文件
- ✓ Info.plist 配置

**启动测试**:
- ✓ 后台启动应用
- ✓ 等待5秒
- ✓ 检查进程存活
- ✓ 未通过不生成 DMG

## 🔍 查看构建进度

https://github.com/chenshane904-glitch/animal-number-ledger/actions

查找 "Build macOS App v1.2.3" workflow

## 📝 使用示例

### 头数模式

```
输入: 1头20
结果: 
  10 → 20元
  11 → 20元
  12 → 20元
  13 → 20元
  14 → 20元
  15 → 20元
  16 → 20元
  17 → 20元
  18 → 20元
  19 → 20元
  
总计: 200元
```

### 混合输入

```
输入:
1头20
虎50
25 30

结果:
- 10-19 各20元 (头数模式)
- 虎的号码 各50元 (动物模式)  
- 号码25 30元 (普通模式)
```

## 🔄 升级说明

### 从旧版本升级

1. 下载新版本 DMG
2. 覆盖安装（拖动到 Applications）
3. 启动应用
4. **数据库自动迁移**
5. 历史数据完整保留

### 数据位置

```
~/Library/Application Support/AnimalNumberLedger/
├── data.db          # 数据库
└── logs/            # 日志文件
```

## 🎯 已知问题

无已知严重问题

## 🚀 下一步计划

- 更多快捷输入模式
- 数据导出功能
- 统计图表

---

**v1.2.3 稳定版已发布，包含头数模式、数据库自动迁移、双架构支持。**

**立即下载**: https://github.com/chenshane904-glitch/animal-number-ledger/releases/tag/v1.2.3
