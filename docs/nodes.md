# NodePy 节点文档

本文档描述了 NodePy 项目中所有已实现的节点。每个节点包括其操作描述、接受的参数、输入和输出类型要求，以及一个简单的使用示例。

## 目录

- [原始值节点](#原始值节点)
  - [ConstNode](#constnode)
  - [CmpNode](#cmpnode)
- [数值计算节点](#数值计算节点)
  - [BinNumComputeNode](#binnumcomputenode)
  - [UnaryNumComputeNode](#unarynumcomputenode)
- [布尔计算节点](#布尔计算节点)
  - [BoolBinComputeNode](#boolbincomputenode)
  - [BoolNotNode](#boolnotnode)
- [字符串处理节点](#字符串处理节点)
  - [StringNode](#stringnode)
  - [ClipStringNode](#clipstringnode)
  - [StripStringNode](#stripstringnode)
  - [ReplaceStringNode](#replacestringnode)
  - [JoinStringNode](#joinstringnode)
  - [SplitStringNode](#splitstringnode)
  - [UpperStringNode](#upperstringnode)
  - [LowerStringNode](#lowerstringnode)
  - [TableAppendStringNode](#tableappendstringnode)
  - [TablePrependStringNode](#tableprependstringnode)
  - [TableContainsStringNode](#tablecontainsstringnode)
  - [TableStartsWithStringNode](#tablestartswithstringnode)
  - [TableEndsWithStringNode](#tableendswithstringnode)
  - [TableReplaceStringNode](#tablereplacestringnode)
- [表格节点](#表格节点)
  - [TableNode](#tablenode)
  - [RandomNode](#randomnode)
  - [RangeNode](#rangenode)
  - [SelectColNode](#selectcolnode)
  - [SplitNode](#splitnode)
- [表格计算节点](#表格计算节点)
  - [TableCmpNode](#tablecmpnode)
  - [TableBinNumComputeNode](#tablebinnumcomputenode)
  - [TableUnaryNumComputeNode](#tableunarynumcomputenode)
  - [TableBoolBinComputeNode](#tableboolbincomputenode)
- [可视化节点](#可视化节点)
  - [PlotNode](#plotnode)

## 原始值节点

### ConstNode

**操作**: 生成一个常量值。

**参数**:
- `value`: 要生成的常量值 (str | float | int | bool)
- `data_type`: 值的数据类型 ("str", "float", "int", "bool")

**输入**: 无

**输出**:
- `output`: 常量值 (类型根据 data_type)

**示例**:
```json
{
  "id": "const1",
  "name": "阈值常量",
  "type": "ConstNode",
  "value": 100000,
  "data_type": "int"
}
```
预期行为: 输出整数 100000，可用于作为交易金额阈值。

### CmpNode

**操作**: 比较两个相同类型的原始值 (int, float, str, bool)，返回布尔结果。

**参数**:
- `op`: 比较操作 ("EQ", "NE", "GT", "LT", "GE", "LE")

**输入**:
- `input1`: 第一个值 (int | float | str | bool)
- `input2`: 第二个值 (int | float | str | bool，必须与 input1 类型相同)

**输出**:
- `output`: 比较结果 (bool)

**示例**:
```json
{
  "id": "cmp1",
  "name": "价格比较",
  "type": "CmpNode",
  "op": "GT"
}
```
连接 input1=当前股价, input2=买入价，预期行为: 输出 true 表示股价已上涨。

## 数值计算节点

### BinNumComputeNode

**操作**: 对两个数值执行二元运算。

**参数**:
- `op`: 操作类型 ("ADD", "SUB", "MUL", "DIV", "POW")

**输入**:
- `left`: 左操作数 (int | float)
- `right`: 右操作数 (int | float)

**输出**:
- `output`: 计算结果 (int | float，根据操作和输入类型)

**示例**:
```json
{
  "id": "calc1",
  "name": "计算收益率",
  "type": "BinNumComputeNode",
  "op": "DIV"
}
```
连接 left=卖出价, right=买入价，预期行为: 输出收益率比例。

### UnaryNumComputeNode

**操作**: 对单个数值执行一元运算。

**参数**:
- `op`: 操作类型 ("NEG", "ABS", "SQRT")

**输入**:
- `input`: 操作数 (int | float)

**输出**:
- `output`: 计算结果 (int | float)

**示例**:
```json
{
  "id": "unary1",
  "name": "绝对收益率",
  "type": "UnaryNumComputeNode",
  "op": "ABS"
}
```
连接 input=-0.05（-5%亏损），预期行为: 输出 0.05（5%绝对收益率）。

## 布尔计算节点

### BoolBinComputeNode

**操作**: 对两个布尔值执行二元运算。

**参数**:
- `op`: 操作类型 ("AND", "OR", "XOR", "SUB")

**输入**:
- `left`: 左操作数 (bool)
- `right`: 右操作数 (bool)

**输出**:
- `output`: 计算结果 (bool)

**示例**:
```json
{
  "id": "bool1",
  "name": "多条件买入信号",
  "type": "BoolBinComputeNode",
  "op": "AND"
}
```
连接 left=价格上涨信号, right=成交量放大信号，预期行为: 输出 true 表示同时满足买入条件。

### BoolNotNode

**操作**: 对布尔值执行逻辑非运算。

**参数**: 无

**输入**:
- `input`: 操作数 (bool)

**输出**:
- `output`: 非运算结果 (bool)

**示例**:
```json
{
  "id": "not1",
  "name": "反转卖出信号",
  "type": "BoolNotNode"
}
```
连接 input=买入信号，预期行为: 输出卖出信号（买入信号的反转）。

## 字符串处理节点

### StringNode

**操作**: 生成用户提供的字符串。

**参数**:
- `value`: 要生成的字符串 (str)

**输入**: 无

**输出**:
- `output`: 字符串值 (str)

**示例**:
```json
{
  "id": "str1",
  "name": "股票代码",
  "type": "StringNode",
  "value": "000001.SZ"
}
```
预期行为: 输出股票代码字符串 "000001.SZ"。

### ClipStringNode

**操作**: 按起始和结束索引剪切字符串。

**参数**:
- `start`: 起始索引 (int | None)
- `end`: 结束索引 (int | None)

**输入**:
- `input`: 输入字符串 (str)

**输出**:
- `output`: 剪切后的字符串 (str)

**示例**:
```json
{
  "id": "clip1",
  "name": "提取股票代码前缀",
  "type": "ClipStringNode",
  "start": 0,
  "end": 6
}
```
连接 input="000001.SZ"，预期行为: 输出 "000001"。

### StripStringNode

**操作**: 去除字符串两端的指定字符。

**参数**:
- `chars`: 要去除的字符 (str | None)

**输入**:
- `input`: 输入字符串 (str)

**输出**:
- `output`: 处理后的字符串 (str)

**示例**:
```json
{
  "id": "strip1",
  "name": "清理交易备注",
  "type": "StripStringNode",
  "chars": null
}
```
连接 input=" 买入信号  "，预期行为: 输出 "买入信号"。

### ReplaceStringNode

**操作**: 替换字符串中的子串。

**参数**:
- `old`: 要替换的子串 (str)
- `new`: 替换为的子串 (str)

**输入**:
- `input`: 输入字符串 (str)

**输出**:
- `output`: 替换后的字符串 (str)

**示例**:
```json
{
  "id": "replace1",
  "name": "格式化市场代码",
  "type": "ReplaceStringNode",
  "old": "SH",
  "new": "SSE"
}
```
连接 input="600000.SH"，预期行为: 输出 "600000.SSE"。

### MergeStringNode

**操作**: 使用分隔符合并字符串 (当前实现返回原字符串)。

**参数**:
- `sep`: 分隔符 (str，默认 ",")

**输入**:
- `input`: 输入字符串 (str)

**输出**:
- `output`: 合并后的字符串 (str)

**示例**:
```json
{
  "id": "merge1",
  "name": "合并字符串节点",
  "type": "JoinStringNode",
  "sep": ","
}
```
连接 input="a,b,c"，预期行为: 输出 "a,b,c"。

### SplitStringNode

**操作**: 按分隔符分割字符串，返回包含分割结果的表格。

**参数**:
- `delimiter`: 分隔符 (str，默认 ",")
- `column_name`: 输出列名 (str，默认 "value")

**输入**:
- `input`: 输入字符串 (str)

**输出**:
- `output`: 包含分割结果的表格 (TABLE)

**示例**:
```json
{
  "id": "split_str1",
  "name": "分割股票组合",
  "type": "SplitStringNode",
  "delimiter": ",",
  "column_name": "stock_code"
}
```
连接 input="000001,000002,600000"，预期行为: 输出包含列 "stock_code" 和 "_index" 的表格，行数据为 ["000001", "000002", "600000"]。

### UpperStringNode

**操作**: 将字符串转换为大写。

**参数**: 无

**输入**:
- `input`: 输入字符串 (str)

**输出**:
- `output`: 大写字符串 (str)

**示例**:
```json
{
  "id": "upper1",
  "name": "标准化交易指令",
  "type": "UpperStringNode"
}
```
连接 input="buy"，预期行为: 输出 "BUY"。

### LowerStringNode

**操作**: 将字符串转换为小写。

**参数**: 无

**输入**:
- `input`: 输入字符串 (str)

**输出**:
- `output`: 小写字符串 (str)

**示例**:
```json
{
  "id": "lower1",
  "name": "标准化日志级别",
  "type": "LowerStringNode"
}
```
连接 input="ERROR"，预期行为: 输出 "error"。

## 表格节点

### TableNode

**操作**: 从用户提供的行数据创建表格。

**参数**:
- `rows`: 行数据列表，每个元素为字典 (List[Dict[str, Any]])
- `column_names`: 列名列表 (List[str])

**输入**: 无

**输出**:
- `output`: 创建的表格 (TABLE)

**示例**:
```json
{
  "id": "table1",
  "name": "股票价格表",
  "type": "TableNode",
  "rows": [
    {"stock_code": "000001", "price": 10.5, "volume": 1000000},
    {"stock_code": "000002", "price": 8.3, "volume": 500000}
  ],
  "column_names": ["stock_code", "price", "volume"]
}
```
预期行为: 输出包含 "_index", "stock_code", "price", "volume" 列的股票价格表格。

### RandomNode

**操作**: 生成包含随机数列的表格。

**参数**:
- `data_type`: 数据类型 ("int" | "float")
- `top`: 随机数上限 (float | int)
- `bottom`: 随机数下限 (float | int)
- `seed`: 随机种子 (int | None)
- `column_name`: 列名 (str)

**输入**: 无

**输出**:
- `output`: 包含随机数据的表格 (TABLE)

**示例**:
```json
{
  "id": "random1",
  "name": "模拟交易量",
  "type": "RandomNode",
  "data_type": "int",
  "top": 1000000,
  "bottom": 10000,
  "seed": 42,
  "column_name": "simulated_volume"
}
```
预期行为: 输出包含 "_index" 和 "simulated_volume" 列的表格，simulated_volume 列包含 10000-1000000 之间的随机交易量。

### RangeNode

**操作**: 生成包含范围数列的表格。

**参数**:
- `start`: 起始值 (float | int)
- `end`: 结束值 (float | int)
- `step`: 步长 (float | int)
- `column_name`: 列名 (str)

**输入**: 无

**输出**:
- `output`: 包含范围数据的表格 (TABLE)

**示例**:
```json
{
  "id": "range1",
  "name": "价格区间",
  "type": "RangeNode",
  "start": 10.0,
  "end": 20.0,
  "step": 0.5,
  "column_name": "price_levels"
}
```
预期行为: 输出包含 "_index" 和 "price_levels" 列的表格，price_levels 列包含 [10.0, 10.5, 11.0, ..., 19.5]。

### SelectColNode

**操作**: 从输入表格中选择指定的列。

**参数**:
- `selected_columns`: 要选择的列名列表 (List[str])

**输入**:
- `input`: 输入表格 (TABLE)

**输出**:
- `output`: 包含选中列的表格 (TABLE)

**示例**:
```json
{
  "id": "select1",
  "name": "选择关键指标",
  "type": "SelectColNode",
  "selected_columns": ["stock_code", "close_price", "volume"]
}
```
连接包含 "stock_code", "open_price", "close_price", "high", "low", "volume" 列的股票数据表格，预期行为: 输出只包含 "_index", "stock_code", "close_price", "volume" 列的精简表格。

### SplitNode

**操作**: 根据指定列的值将输入表格分割成多个输出表格。

**参数**:
- `split_column`: 用于分割的列名 (str)
- `split_values`: 分割值列表 (List[str])
- `reserved_columns`: 要保留的列名列表 (List[str] | None)

**输入**:
- `input`: 输入表格 (TABLE)

**输出**:
- `out_0`, `out_1`, ...: 分割后的表格 (TABLE)

**示例**:
```json
{
  "id": "split1",
  "name": "按市场分割股票",
  "type": "SplitNode",
  "split_column": "market",
  "split_values": ["沪市主板", "深市主板"],
  "reserved_columns": ["stock_code", "price", "volume"]
}
```
连接包含 "market", "stock_code", "price", "volume", "industry" 列的股票表格，预期行为: 输出两个表格：
- out_0: 沪市主板股票，包含 "_index", "stock_code", "price", "volume" 列
- out_1: 深市主板股票，包含 "_index", "stock_code", "price", "volume" 列

## 表格计算节点

### TableCmpNode

**操作**: 将表格中的指定列与原始值进行比较，添加结果列。

**参数**:
- `op`: 比较操作 ("EQ", "NE", "GT", "LT", "GE", "LE")
- `column`: 要比较的列名 (str)
- `result_col`: 结果列名 (str)

**输入**:
- `table_input`: 输入表格 (TABLE)
- `value_input`: 比较值 (int | float | str | bool)

**输出**:
- `output`: 添加了比较结果列的表格 (TABLE)

**示例**:
```json
{
  "id": "table_cmp1",
  "name": "筛选高价股",
  "type": "TableCmpNode",
  "op": "GT",
  "column": "price",
  "result_col": "is_expensive"
}
```
连接包含 "price" 列的股票表格和 value_input=50.0，预期行为: 输出表格添加 "is_expensive" 列，标识股价是否超过50元。

### TableBinNumComputeNode

**操作**: 对表格列执行二元数值运算，添加结果列。

**参数**:
- `op`: 操作类型 ("ADD", "SUB", "MUL", "DIV", "POW")
- `left_col`: 左操作数列名 (str)
- `right_col`: 右操作数列名 (str | None)
- `result_col`: 结果列名 (str)

**输入**:
- `table`: 输入表格 (TABLE)
- `value`: 右操作数 (int | float，如果 right_col 为 None)
- `table_right`: 右操作数表格 (TABLE，如果 right_col 不为 None)

**输出**:
- `output`: 添加了计算结果列的表格 (TABLE)

**示例**:
```json
{
  "id": "table_calc1",
  "name": "计算涨跌幅",
  "type": "TableBinNumComputeNode",
  "op": "DIV",
  "left_col": "close_price",
  "right_col": "prev_close",
  "result_col": "daily_return"
}
```
连接包含 "close_price", "prev_close" 列的股票表格，预期行为: 输出表格添加 "daily_return" 列，计算日收益率。

### TableUnaryNumComputeNode

**操作**: 对表格列执行一元数值运算，添加结果列。

**参数**:
- `op`: 操作类型 ("NEG", "ABS", "SQRT")
- `column`: 操作数列名 (str)
- `result_col`: 结果列名 (str)

**输入**:
- `table`: 输入表格 (TABLE)

**输出**:
- `output`: 添加了计算结果列的表格 (TABLE)

**示例**:
```json
{
  "id": "table_unary1",
  "name": "计算波动率",
  "type": "TableUnaryNumComputeNode",
  "op": "SQRT",
  "column": "variance",
  "result_col": "volatility"
}
```
连接包含 "variance" 列的表格，预期行为: 输出表格添加 "volatility" 列，包含方差的平方根（波动率）。

### TableBoolBinComputeNode

**操作**: 对表格列执行二元布尔运算，添加结果列。

**参数**:
- `op`: 操作类型 ("AND", "OR", "XOR", "SUB")
- `left_col`: 左操作数列名 (str)
- `right_col`: 右操作数列名 (str | None)
- `result_col`: 结果列名 (str)

**输入**:
- `table`: 输入表格 (TABLE)
- `table_right`: 右操作数表格 (TABLE)

**输出**:
- `output`: 添加了计算结果列的表格 (TABLE)

**示例**:
```json
{
  "id": "table_bool1",
  "name": "组合交易信号",
  "type": "TableBoolBinComputeNode",
  "op": "AND",
  "left_col": "price_signal",
  "right_col": "volume_signal",
  "result_col": "combined_signal"
}
```
连接包含 "price_signal", "volume_signal" 列的信号表格，预期行为: 输出表格添加 "combined_signal" 列，标识价格和成交量信号同时成立。

## 可视化节点

### PlotNode

**操作**: 使用 matplotlib 根据表格数据生成散点图、线图或柱状图。

**参数**:
- `x_column`: X轴列名 (str)
- `y_column`: Y轴列名 (str)
- `plot_type`: 图表类型 ("scatter", "line", "bar")
- `title`: 图表标题 (str | None)

**输入**:
- `input`: 输入表格 (TABLE)

**输出**: 无 (生成图片文件)

**示例**:
```json
{
  "id": "plot1",
  "name": "股价走势图",
  "type": "PlotNode",
  "x_column": "date",
  "y_column": "close_price",
  "plot_type": "line",
  "title": "股票价格走势"
}
```
连接包含 "date", "close_price" 列的股票历史数据表格，预期行为: 生成股价走势的线图图片文件。

## 表格 × 单字符串 操作节点

以下节点把单个字符串（primitive str）与表格的一列进行逐行运算，输出为在表格中新增的一列。所有这些节点在静态分析阶段会推断输出表格的列集合（包含新增 result_col），并在运行时验证输入表格包含指定列且不会与保留的索引列冲突。

### TableAppendStringNode

**操作**: 将给定字符串 append 到每行指定列的字符串末尾，并将结果写入 `result_col`。

**参数**:
- `column`: 要操作的源列名 (str)
- `result_col`: 输出结果列名 (str)

**输入**:
- `table_input`: 输入表格 (TABLE)
- `value_input`: 要追加的字符串 (str)

**输出**:
- `output`: 包含新增列的表格 (TABLE)

**示例**:
```json
{
  "id": "t_append1",
  "name": "给股票代码追加后缀",
  "type": "TableAppendStringNode",
  "column": "stock_code",
  "result_col": "stock_code_tagged"
}
```

### TablePrependStringNode

**操作**: 将给定字符串 prepend 到每行指定列的字符串开头，并将结果写入 `result_col`。

**参数/输入/输出**: 同 `TableAppendStringNode`，只是把字符串放在前面。

**示例**:
```json
{
  "id": "t_prepend1",
  "name": "给代码添加前缀",
  "type": "TablePrependStringNode",
  "column": "stock_code",
  "result_col": "prefixed_code"
}
```

### TableContainsStringNode

**操作**: 检查每行指定列的字符串是否包含给定子串，结果为布尔列写入 `result_col`。

**参数**:
- `column`: 源列名 (str)
- `result_col`: 输出结果列名 (str)

**输入**:
- `table_input`: 输入表格 (TABLE)
- `value_input`: 要搜索的子串 (str)

**输出**:
- `output`: 包含新增布尔列的表格 (TABLE)

**示例**:
```json
{
  "id": "t_contains1",
  "name": "代码是否包含300",
  "type": "TableContainsStringNode",
  "column": "stock_code",
  "result_col": "has_300"
}
```

### TableStartsWithStringNode / TableEndsWithStringNode

**操作**: 分别检测每行指定列的字符串是否以给定前缀开始或以给定后缀结束，结果为布尔列写入 `result_col`。

**参数/输入/输出**: 与 `TableContainsStringNode` 相同。

**示例**:
```json
{
  "id": "t_starts1",
  "name": "是否以6开头",
  "type": "TableStartsWithStringNode",
  "column": "stock_code",
  "result_col": "starts_with_6"
}
```

### TableReplaceStringNode

**操作**: 在每行指定列的字符串中将 `old` 子串替换为 `new`，结果写入 `result_col`。

**参数**:
- `column`: 源列名 (str)
- `result_col`: 输出列名 (str)

**输入**:
- `table_input`: 输入表格 (TABLE)
- `old_input`: 要替换的子串 (str)
- `new_input`: 替换为的子串 (str)

**输出**:
- `output`: 包含替换结果的新列的表格 (TABLE)

**示例**:
```json
{
  "id": "t_replace1",
  "name": "替换后缀",
  "type": "TableReplaceStringNode",
  "column": "stock_code",
  "result_col": "code_fixed"
}
```

注: 这些节点在静态分析（infer_output_schema）阶段即可推断出新增列的名称和类型（STR 或 BOOL），符合项目“编译期已知列集合”要求；在运行时（validate_input）它们会验证输入表格是否包含指定列并防止 result_col 与保留索引列冲突。