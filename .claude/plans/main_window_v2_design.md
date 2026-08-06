# 新版UI设计方案 - main_window_v2.py

## 目标
创建现代化桌面UI，保留所有旧版功能，不影响现有代码。

## 核心可复用代码

### 1. 数据获取
```python
self.current_totals = self.db.get_ledger_totals(self.current_ledger.id)
self.current_sources = self.db.get_ledger_sources(self.current_ledger.id)
```

### 2. 排序算法
```python
sorted_numbers = []
for i in range(MIN_NUMBER, MAX_NUMBER + 1):
    amount_int = self.current_totals.get(i, 0)
    sorted_numbers.append((i, amount_int))
sorted_numbers.sort(key=lambda x: (-x[1], x[0]))
```

### 3. 最大金额查找
```python
max_amount_int = 0
for amount_int in self.current_totals.values():
    if amount_int > max_amount_int:
        max_amount_int = amount_int
```

### 4. 解析和计算
```python
parser = InstructionParser(animal_mapping)
instructions = parser.parse_input(input_text)
calculator = Calculator(animal_mapping)
result = calculator.calculate(instructions, self.current_totals)
```

## 新UI布局设计

### 结构
```
┌─────────────────────────────────────────────────────┐
│  顶部标题栏                                          │
│  十二动物号码归纳器 v2.0 | 日期: 2026-08-05        │
├─────────────────────────────────────────────────────┤
│                                                     │
│  输入区域                                           │
│  ┌───────────────────────────────────────────────┐ │
│  │ 大输入框（支持任意符号）                       │ │
│  │                                               │ │
│  └───────────────────────────────────────────────┘ │
│  [开始计算]  [清空]  [撤销]  [历史]  [结算]       │
│                                                     │
├─────────────────────────────────────────────────────┤
│                                                     │
│  结果区域（卡片式布局）                              │
│  ┌──────┬──────┬──────┬──────┐                    │
│  │ 🐴马 │ 🐍蛇 │ 🐲龙 │ 🐰兔 │                    │
│  │ 1,13 │ 2,14 │ 3,15 │ 4,16 │                    │
│  │ 25,37│ 26,38│ 27,39│ 28,40│                    │
│  │ 49   │      │      │      │                    │
│  │ ￥xxx│ ￥xxx│ ￥xxx│ ￥xxx│                    │
│  └──────┴──────┴──────┴──────┘                    │
│  ┌──────┬──────┬──────┬──────┐                    │
│  │ 🐯虎 │ 🐮牛 │ 🐭鼠 │ 🐷猪 │                    │
│  │ ...  │ ...  │ ...  │ ...  │                    │
│  └──────┴──────┴──────┴──────┘                    │
│  ┌──────┬──────┬──────┬──────┐                    │
│  │ 🐶狗 │ 🐔鸡 │ 🐵猴 │ 🐑羊 │                    │
│  │ ...  │ ...  │ ...  │ ...  │                    │
│  └──────┴──────┴──────┴──────┘                    │
│                                                     │
├─────────────────────────────────────────────────────┤
│  底部统计栏                                          │
│  今日总金额: ￥1234.56 | 盈亏: +￥234.56           │
│  [开奖结算]  [导出]  [备份]                        │
└─────────────────────────────────────────────────────┘
```

## 实现细节

### 1. 顶部标题栏
- 软件名称（加大字体）
- 版本号 v2.0
- 当前日期
- 账本编号

### 2. 输入区域
- 大输入框（高度增加到200px）
- 支持实时预览解析结果
- 明显的"开始计算"按钮（绿色/蓝色大按钮）
- 功能按钮组：清空、撤销、历史、结算

### 3. 结果卡片设计
每个动物一个卡片：
- 动物emoji + 名称
- 该动物对应的所有号码
- 该动物的总金额
- 卡片按金额排序
- 最大金额卡片：红色边框（3px）+ 淡红背景 + 阴影效果

### 4. 底部统计
- 今日总金额（大字体）
- 盈亏显示（带颜色：绿色正/红色负）
- 结算按钮（金色）
- 其他功能按钮

## 关键特性

### 按动物分组显示
- 不是按单个号码显示
- 而是按12个动物卡片显示
- 每个卡片显示该动物的所有号码和总金额
- 卡片按该动物的总金额排序

### 最大金额高亮
```python
# 计算每个动物的总金额
animal_totals = {}
for animal, numbers in animal_mapping.items():
    total = sum(self.current_totals.get(num, 0) for num in numbers)
    animal_totals[animal] = total

# 找出最大金额
max_animal_amount = max(animal_totals.values()) if animal_totals else 0

# 判断并高亮
is_max = animal_totals[animal] > 0 and animal_totals[animal] == max_animal_amount
```

### 卡片样式
```python
if is_max:
    card.configure(
        border_width=3,
        border_color="red",
        fg_color="#FFE5E5"  # 淡红背景
    )
```

## 文件结构
```
ui/
├── main_window.py          # 旧版（保持不变）
└── main_window_v2.py       # 新版（本次创建）
```

## 兼容性
- 继承自 `ctk.CTk`
- 使用相同的初始化参数
- 可以通过修改 `app.py` 中的导入来切换版本
- 完全独立，不影响旧版本

## 测试计划
1. 创建新文件
2. 实现基础UI布局
3. 复用核心计算逻辑
4. 测试不影响旧版本
5. 功能测试：解析、计算、排序、高亮
