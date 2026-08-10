# 旧解析逻辑清理报告

## 旧文件清单

### 需要删除的旧文件
1. **parser_new.py** (4.2K) - 旧的新解析器，已被 parser_v2.py 替代
2. **parser_old_backup.py** (9.3K) - 旧的备份文件，不再需要

### 保留的文件
- **parser.py** (22K) - 主解析器，已集成 v2 引擎
- **parser_v2.py** (4.6K) - 新的统一解析引擎
- **flat_zodiac_parser.py** - 平特模式专用解析器
- **play_group_parser.py** - 组合玩法解析器

## 旧函数状态

### parser.py 中的旧函数

#### 1. `_expand_range()` - 已禁用 ✅
**位置**: parser.py:129
**状态**: 已禁用，直接返回原文本，不再自动展开范围
**调用位置**: 
- parser.py:202
- parser.py:438

**修改前**:
```python
def _expand_range(self, text: str) -> str:
    """展开数字范围 14-16 -> 14,15,16"""
    pattern = r'(\d+)-(\d+)'
    def replace_range(match):
        start = int(match.group(1))
        end = int(match.group(2))
        if start < end and end - start <= 50:
            return ','.join(str(i) for i in range(start, end + 1))
        return match.group(0)
    return re.sub(pattern, replace_range, text)
```

**修改后**:
```python
def _expand_range(self, text: str) -> str:
    """禁用自动范围展开"""
    return text
```

#### 2. 其他保留函数
- `_normalize_punctuation()` - 标点标准化，保留
- `_parse_head_input()` - 头数解析，保留（v2 后备）
- `parse_input()` - 主入口，保留并已集成 v2
- `_split_multi_instructions()` - 指令分割，保留并优先调用 v2

## 解析入口验证

### 唯一主入口
**文件**: `parser.py`
**类**: `InstructionParser`
**方法**: `parse_input(input_text: str) -> List[Instruction]`

### 调用路径
```
ui/main_window.py
  ↓
parser.InstructionParser(animal_mapping)
  ↓
parser.parse_input(input_text)
  ↓
_split_multi_instructions(line, line_num)
  ↓
[优先] parser_v2.parse(line)
  ↓ 成功
返回 v2 结果
  ↓ 失败
旧逻辑（已禁用范围展开）
```

### 其他解析器（专用）
- **FlatZodiacParser** - 仅用于平特模式
- **PlayGroupParser** - 仅用于组合玩法

## 删除状态

### 建议删除的文件
```
parser_new.py         - 已替代，可删除
parser_old_backup.py  - 备份文件，可删除
```

### 已禁用的功能
✅ `_expand_range()` - 自动范围展开已完全禁用

### 保留的功能
✅ 动物解析
✅ 组合玩法解析
✅ 头数解析（v2 后备）
✅ 平特模式解析

## 核心改进

### 1. v2 引擎优先
```python
if self.parser_v2:
    try:
        v2_result = self.parser_v2.parse(line)
        if v2_result:
            return v2_result
    except Exception:
        pass  # 回退到旧逻辑
```

### 2. 禁用自动展开
```python
def _expand_range(self, text: str) -> str:
    # 禁用自动展开，直接返回原文本
    return text
```

### 3. v2 支持普通号码列表
```python
def _parse_number_list(self, text: str) -> Instruction:
    # 解析普通号码列表
    # - 是分隔符，不是范围符号
    separators = r'[\s,，\-/]+'
    number_strs = re.split(separators, number_part)
```

## 清理建议

### 可以删除
- `parser_new.py`
- `parser_old_backup.py`
- 各种测试备份文件

### 必须保留
- `parser.py` - 主解析器
- `parser_v2.py` - v2 引擎
- `flat_zodiac_parser.py` - 平特解析器
- `play_group_parser.py` - 组合玩法

---

**报告时间**: 2025-08-10
**状态**: 旧逻辑已禁用，新引擎已生效
