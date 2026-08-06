# 新增平特模式实现计划

## 目标
在现有号码模式基础上，新增平特模式（12生肖玩法），两种模式可自由切换，互不影响。

## 核心原则
1. **绝对不修改现有号码模式的任何代码**
2. 通过PlayMode枚举统一管理玩法
3. 使用配置文件驱动赔率和行为
4. UI采用面板切换而非控件隐藏
5. 数据库字段向后兼容

---

## 阶段一：基础架构（已完成）

### 1.1 PlayMode枚举 ✅
- 文件：`play_mode.py`
- 内容：
  - `PlayMode.NUMBER` - 号码模式
  - `PlayMode.ANIMAL` - 平特模式
  - `PLAY_MODE_NAMES` - 显示名称映射

### 1.2 玩法配置 ✅
- 文件：`play_modes.json`
- 内容：
  ```json
  {
    "number": {
      "name": "号码模式",
      "expand_numbers": true,
      "odds": 47,
      "display_type": "numbers"
    },
    "animal": {
      "name": "平特模式",
      "expand_numbers": false,
      "odds": 1.0,
      "display_type": "animals",
      "animals": ["鼠", "牛", "虎", "兔", "龙", "蛇", "马", "羊", "猴", "鸡", "狗", "猪"]
    }
  }
  ```

### 1.3 平特计算器 ✅
- 文件：`animal_calculator.py`
- 类：`AnimalCalculator`
- 功能：
  - 基于生肖累计金额
  - 不展开号码
  - 支持可配置赔率
  - 计算统计信息（总下注、非零生肖、最高生肖）

### 1.4 数据库扩展 ✅
- 迁移脚本：`migrate_add_play_mode.py`
- 新增字段：
  - `input_history.play_mode` (默认'number')
  - `batches.play_mode` (默认'number')
- `database.py` 方法更新：
  - `save_input_history()` 增加 `play_mode` 参数（默认'number'）
  - `get_input_history_by_week()` 增加 `play_mode` 过滤参数

---

## 阶段二：平特模式UI组件（待实现）

### 2.1 平特结果表格组件
- 文件：`ui/animal_result_table.py`
- 类：`AnimalResultTable`
- 功能：
  - 显示12个生肖
  - 列：生肖、金额、赔率、赔付、盈利
  - 固定顺序：鼠、牛、虎、兔、龙、蛇、马、羊、猴、鸡、狗、猪
  - 使用Canvas绘制（与ResultCanvasTable风格一致）
  - 支持滚轮滚动
  - 赔率从配置读取

### 2.2 平特统计面板
- 位置：右侧顶部
- 4个统计栏：
  - 今日总下注（蓝色）
  - 非零生肖（绿色）
  - 最高下注生肖（橙色）
  - 最高金额（红色）
- 样式与号码模式统计面板一致

---

## 阶段三：主窗口集成（待实现）

### 3.1 模式切换按钮
- 位置：顶部信息栏右侧（settlement_label 右边）
- 两个按钮：
  - "号码模式"（默认选中）
  - "平特模式"
- 样式：
  - 选中：蓝色背景
  - 未选中：灰色背景
  - 使用 `CTkSegmentedButton` 实现

### 3.2 右侧面板切换机制
- 当前状态：`self.current_mode = PlayMode.NUMBER`
- 右侧容器：`self.right_content_frame`
- 切换逻辑：
  1. 销毁当前右侧所有widget
  2. 根据mode加载对应面板
  3. `_load_number_panel()` - 号码模式面板（现有代码）
  4. `_load_animal_panel()` - 平特模式面板（新增）

### 3.3 号码模式面板封装
- 方法：`_load_number_panel()`
- 内容：
  - 现有的4个统计栏
  - 现有的ResultCanvasTable
  - **不修改任何逻辑**，只是封装成方法

### 3.4 平特模式面板
- 方法：`_load_animal_panel()`
- 内容：
  - 4个统计栏（文字改为生肖相关）
  - AnimalResultTable（12生肖表格）

### 3.5 计算逻辑分支
- 方法：`_preview()`、`_confirm_add()`
- 修改点：
  ```python
  if self.current_mode == PlayMode.NUMBER:
      # 使用现有Calculator（不修改）
      result = self.calculator.calculate(instructions, self.current_totals)
  else:
      # 使用AnimalCalculator
      config = load_config('animal')
      animal_calc = AnimalCalculator(config)
      result = animal_calc.calculate(instructions, self.animal_mapping)
  ```

### 3.6 历史记录保存
- 传入 `play_mode` 参数：
  ```python
  self.db.save_input_history(
      ...,
      play_mode=str(self.current_mode)
  )
  ```

---

## 阶段四：历史记录扩展（待实现）

### 4.1 历史窗口过滤
- 文件：`ui/history_window.py`
- 修改：`__init__()` 接收 `current_mode` 参数
- 查询时过滤：
  ```python
  records = self.db.get_input_history_by_week(
      week_start_str,
      play_mode=str(current_mode)
  )
  ```

### 4.2 记录显示
- 在每条记录的时间旁显示玩法类型：
  - `[号码]` - 号码模式
  - `[平特]` - 平特模式
- 颜色区分：
  - 号码模式：蓝色
  - 平特模式：绿色

---

## 阶段五：配置加载工具（待实现）

### 5.1 配置加载器
- 文件：`play_mode_config.py`
- 函数：
  ```python
  def load_play_mode_config(mode: PlayMode) -> dict:
      """加载玩法配置"""
      with open('play_modes.json', 'r', encoding='utf-8') as f:
          config = json.load(f)
      return config[str(mode)]
  
  def get_odds(mode: PlayMode) -> float:
      """获取赔率"""
      config = load_play_mode_config(mode)
      return config['odds']
  
  def should_expand_numbers(mode: PlayMode) -> bool:
      """是否展开号码"""
      config = load_play_mode_config(mode)
      return config['expand_numbers']
  ```

---

## 阶段六：测试（待实现）

### 6.1 单元测试
- 文件：`test_animal_mode.py`
- 测试点：
  - AnimalCalculator计算正确性
  - 平特模式赔率读取
  - 生肖金额累计
  - 统计信息计算

### 6.2 集成测试
- 号码模式功能保持100%正常
- 平特模式功能正常
- 模式切换流畅
- 历史记录分离正确
- 数据库字段向后兼容

### 6.3 手动测试清单
```
✅ 号码模式：
   - 输入"01各20"，号码01增加20
   - 输入"红双各50"，9个号码各增加50
   - 赔率仍为47
   - 历史记录正常

✅ 平特模式：
   - 输入"虎100"，虎生肖增加100
   - 输入"龙200"，龙生肖增加200
   - 赔率为1.0（从配置读取）
   - 统计显示：总下注300、非零生肖2、最高生肖龙、最高金额200
   - 历史记录正常

✅ 模式切换：
   - 从号码切换到平特，右侧变为12生肖
   - 从平特切换到号码，右侧恢复49号码
   - 两种模式数据独立

✅ 历史记录：
   - 号码模式历史只显示号码记录
   - 平特模式历史只显示平特记录
   - 每条记录显示玩法类型标记
```

---

## 关键技术点

### 1. 面板切换而非控件隐藏
```python
def _switch_mode(self, mode: PlayMode):
    """切换玩法模式"""
    self.current_mode = mode
    
    # 销毁右侧所有widget
    for widget in self.right_frame.winfo_children():
        widget.destroy()
    
    # 加载对应面板
    if mode == PlayMode.NUMBER:
        self._load_number_panel()
    else:
        self._load_animal_panel()
    
    # 刷新显示
    self._update_display()
```

### 2. 保持号码模式代码不变
- 现有的 `Calculator`、`ResultCanvasTable`、所有计算逻辑 **一行不改**
- 通过 `if self.current_mode ==` 分支实现不同逻辑
- 新增代码都在独立文件中

### 3. 配置驱动
- 赔率、是否展开号码等行为全部从 `play_modes.json` 读取
- 未来新增玩法只需修改配置文件

### 4. 数据库向后兼容
- `play_mode` 字段默认值 `'number'`
- 查询时 `play_mode=None` 表示不过滤（兼容旧代码）
- 所有现有数据自动标记为 `'number'`

---

## 文件清单

### 新增文件
1. `play_mode.py` - PlayMode枚举 ✅
2. `play_modes.json` - 玩法配置 ✅
3. `animal_calculator.py` - 平特计算器 ✅
4. `play_mode_config.py` - 配置加载工具 ⏳
5. `ui/animal_result_table.py` - 平特结果表格 ⏳
6. `test_animal_mode.py` - 单元测试 ⏳
7. `migrate_add_play_mode.py` - 数据库迁移 ✅

### 修改文件
1. `database.py` - 添加play_mode参数 ✅
2. `ui/main_window.py` - 添加模式切换和面板 ⏳
3. `ui/history_window.py` - 添加玩法过滤 ⏳

### 不修改文件
1. `calculator.py` - 保持不变 ✅
2. `parser.py` - 保持不变 ✅
3. `ui/result_canvas_table.py` - 保持不变 ✅
4. 所有测试文件 - 保持不变 ✅

---

## 实施顺序

1. ✅ 基础架构（已完成）
2. ⏳ 创建 `play_mode_config.py`
3. ⏳ 创建 `ui/animal_result_table.py`
4. ⏳ 修改 `ui/main_window.py` 添加模式切换
5. ⏳ 修改 `ui/history_window.py` 添加过滤
6. ⏳ 编写单元测试
7. ⏳ 完整功能测试
8. ⏳ 交付

---

## 风险控制

1. **回归风险**：通过分支隔离，号码模式代码完全不动
2. **数据兼容**：play_mode默认值保证旧数据正常
3. **UI一致性**：平特表格复用Canvas绘制风格
4. **测试覆盖**：每个阶段完成后立即测试号码模式

---

## 预期效果

用户打开软件后：
1. 默认显示号码模式（现有界面）
2. 点击"平特模式"按钮，右侧切换为12生肖
3. 输入"虎100"，虎生肖增加100，赔率1.0
4. 点击"号码模式"按钮，右侧恢复49号码
5. 两种模式历史记录独立显示
6. 所有旧功能100%正常
