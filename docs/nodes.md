# NodePy 节点文档

本文档描述了 NodePy 项目中所有已实现的节点。每个节点包括其操作描述、接受的参数、输入和输出类型要求，以及一个简单的使用示例。

## 一、总体设计

### 1. 类型系统
NodePy 的节点系统是一个完全静态类型的节点系统，类型验证分为三个阶段：
- Stage1 参数验证
- Stage2 输入输出静态推导 
注：为了实现 Stage2 的静态推导，部分节点需要在该阶段访问文件系统以读取文件内容，从而推导出更精确的输出类型信息。
- Stage3 运行时验证

**注意：该节点系统是完全静态类型的，没有任何隐式转换，各类运算都要求操作数的类型完全一致。**

### 2. 七种类型
在我们的节点系统中，一共只有七大类型：
- `int`: 整数类型, 底层通过Python的`int`实现或`int64`实现。
- `float`: 浮点数类型, 底层通过Python的`float`实现或`float64`实现。
- `bool`: 布尔类型, 底层通过Python的`bool`实现。
- `str`: 字符串类型, 底层通过Python的`str`实现。
- `Table`: 表格类型, 底层通过Pandas的`DataFrame`实现。
- `File`: 文件类型, 是对象文件系统的一个抽象，每个用户所产生的全部文件大小受限于其配额（默认5GB）。
- `Datetime`: 日期时间类型, 底层通过Python的`datetime`类型实现。

其中，前三种由于可以定义各种数学运算，因此也被称作"Prim"类型；前两种也可以被称作"Number"类型。

在表格中，每一列的数据类型允许是：
- `int`: 整数类型，底层通过Pandas的`int64`实现。
- `float`: 浮点数类型，底层通过Pandas的`float64`实现。
- `bool`: 布尔类型，底层通过Pandas的`bool`实现。
- `str`: 字符串类型，底层通过Pandas的`str`实现。
- `Datetime`: 日期时间类型，底层通过Pandas的`datetime64[ns]`实现，对应Python的`datetime`类型。

## 二、节点列表
尽管有了严格的类型系统，但由于json序列化的特点，在传输数据时，一些类型可能丢失，因此在实现节点时还是允许一下这些隐式转换的：
- 在节点参数中，允许`int` -> `float`的隐式转换。
- 在节点参数中，允许`str` -> `datetime`的隐式转换，要求字符串符合ISO 8601格式。

注意：在节点输入和输出中，不允许任何隐式转换，所有类型必须完全匹配。

### 1. 输入节点(input)
#### 1.1 ConstNode
常量输入节点，可以输出一个固定的值。输出值仅限于float和int。

**参数：**
- value: 常量值，类型为float或int，需与data_type类型一致。
- data_type: 输出数据类型，类型为str，取值为"int"或"float"。

**输入：** 
无

**输出：**
- const: 输出的常量值，类型为data_type指定的类型。

#### 1.2 BoolNode
布尔输入节点，可以输出一个固定的布尔值。

**参数：**
- value: 常量值，类型为bool。

**输入：**
无

**输出：**
- const: 输出的布尔值，类型为bool。

#### 1.3 StringNode
字符串输入节点，可以输出一个固定的字符串值。

**参数：**
- value: 常量值，类型为str。

**输入：**
无

**输出：**
- string: 输出的字符串值，类型为str。

#### 1.4 TableNode
表格输入节点，可以输出一个固定的表格值。
注意：如果用户提供了列名但没有提供行数据，将会抛出错误，因为无法推断列的数据类型。

**参数：**
- rows: `List[Dict[str, str | int | float | bool]]`，表格的行数据，每一行是一个字典，键为列名，值为对应的单元格数据。
- col_names: `List[str]`，表格的列名列表，需要与rows中的字典键一致。

**输入：**
无

**输出：**
- table: 输出的表格值，类型为Table。

***示例：***
```
TableNode(
    rows=[
        {"Name": "Alice", "Age": 30, "Salary": 70000.0, "IsManager": False},
        {"Name": "Bob", "Age": 35, "Salary": 80000.0, "IsManager": True}
    ],
    col_names=["Name", "Age", "Salary", "IsManager"]
)
```
table: 
|   Name   | Age | Salary  | IsManager |
|----------|-----|---------|-----------|
| Alice    | 30  | 70000.0 | False     |
| Bob      | 35  | 80000.0 | True      |

#### 1.5 RandomNode
随机表格生成节点，可以生成一个包含一个由随机数构成的列的表格。

**参数：**
- col_name: 列名，类型为str。
- col_type: 列的数据类型，类型为str，取值为"int"或"float"或"str"或"bool"。

**输入：**
- row_count: 行数，类型为int。
- min_value: 最小值，类型为int或float，可选，如果col_type为"str"或"bool"则不应有该输入。
- max_value: 最大值，类型为int或float，可选，如果col_type为"str"或"bool"则不应有该输入。

**输出：**
- table: 输出的表格，类型为Table。

#### 1.6 RangeNode
范围表格生成节点，可以生成一个包含一个由指定范围内数值构成的列的表格。

**参数：**
- col_name: 列名，类型为str。
- col_type: 列的数据类型，类型为str，取值为"int"或"float"。

**输入：**
- start: 起始值，类型为int或float。
- end: 结束值，类型为int或float。
- step: 步长，类型为int或float，可选，如果未提供则默认为1.0/1/1Day。

**输出：**
- table: 输出的表格，类型为Table。

#### 1.7 DateTimeNode
日期时间输入节点，可以输出一个固定的日期时间值。

**参数：**
- value: 常量值，类型为str，必须符合ISO 8601格式。

**输入：**
无

**输出：**
- datetime: 输出的日期时间值，类型为Datetime。

### 2. 计算节点(compute)
#### 2.1 NumberBinOpNode
二元数值运算节点，支持对两个数值类型(int或float)的输入进行`ADD`, `SUB`, `MUL`, `DIV`, `POW`五种基本运算。

**参数：**
- op: 运算类型，类型为str，取值为"ADD", "SUB", "MUL", "DIV", "POW"。

**输入：**
- x: 第一个操作数，类型为int或float。
- y: 第二个操作数，类型为int或float。

***两个操作数类型必须完全一致。***

**输出：**
- result: 运算结果，类型为输入类型一致的类型(int或float)。***注意：对于除法运算(DIV)和乘方运算(POW)，结果类型始终为float。***

#### 2.2 NumberUnaryOpNode
一元数值运算节点，支持对一个数值类型(int或float)的输入进行`NEG`, `ABS`, `SQRT`三种基本运算。

**参数：**
- op: 运算类型，类型为str，取值为"NEG", "ABS", "SQRT"。

**输入：**
- x: 操作数，类型为int或float。

**输出：**
- result: 运算结果，类型为输入类型一致的类型(int或float)。***注意：对于开方运算(SQRT)，结果类型始终为float。***

#### 2.3 PrimitiveCompareNode
数值比较节点，支持对两个Prim类型(int, float, bool)的输入进行`EQ`, `NEQ`, `LT`, `LTE`, `GT`, `GTE`六种比较运算。

**参数：**
- op: 运算类型，类型为str，取值为"EQ", "NEQ", "LT", "LTE", "GT", "GTE"。

**输入：**
- x: 第一个操作数，类型为Prim类型(int, float, bool)。
- y: 第二个操作数，类型为Prim类型(int, float, bool)。

***两个操作数类型必须完全一致。***

**输出：**
- result: 比较结果，类型为bool。

#### 2.4 BoolBinOpNode
二元布尔运算节点，支持对两个布尔类型(bool)的输入进行`AND`, `OR`, `XOR`, `SUB`四种基本运算。

**参数：**
- op: 运算类型，类型为str，取值为"AND", "OR", "XOR", "SUB"。

**输入：**
- x: 第一个操作数，类型为bool。
- y: 第二个操作数，类型为bool。

**输出：**
- result: 运算结果，类型为bool。

#### 2.5 BoolUnaryOpNode
一元布尔运算节点，支持对一个布尔类型(bool)的输入进行`NOT`运算。

**参数：**
- op: 运算类型，类型为str，取值为"NOT"。

**输入：**
- x: 操作数，类型为bool。

**输出：**
- result: 运算结果，类型为bool。

#### 2.6 ColWithNumberBinOpNode
表格列与数值二元运算节点，支持对表格中的指定列与一个数值类型(int或float)的输入进行`ADD`, `SUB`, `MUL`, `DIV`, `POW`五种基本运算，将结果存储在新的表格列中。

**参数：**
- op: 运算类型，类型为str，取值为"ADD", "COL_SUB_NUM", "NUM_SUB_COL", "MUL", "COL_DIV_NUM", "NUM_DIV_COL", "COL_POW_NUM", "NUM_POW_COL"。
- col: 要操作的表格列名，类型为str，该列必须为数值类型(int或float)。
- result_col: 结果表格列名，类型为str，可以为空，表示使用默认结果列名。

**输入：**
- table: 输入的表格，类型为Table。
- num: 数值操作数，类型为int或float。

**输出：**
- table: 输出的表格，类型为Table，包含新增的结果列。

#### 2.7 ColWithBoolBinOpNode
表格列与布尔二元运算节点，支持对表格中的指定列与一个布尔类型(bool)的输入进行`AND`, `OR`, `XOR`, `SUB`四种基本运算，将结果存储在新的表格列中。

**参数：**
- op: 运算类型，类型为str，取值为"AND", "OR", "XOR", "NUM_SUB_COL", "COL_SUB_NUM"。
- col: 要操作的表格列名，类型为str，该列必须为布尔类型(bool)。
- result_col: 结果表格列名，类型为str，可以为空，表示使用默认结果列名。

**输入：**
- table: 输入的表格，类型为Table。
- bool: 布尔操作数，类型为bool。

**输出：**
- table: 输出的表格，类型为Table，包含新增的结果列。

#### 2.8 NumberColUnaryOpNode
表格列与数值一元运算节点，支持对表格中的指定列进行`ABS`, `NEG`, `EXP`, `LOG`, `SQRT`五种基本运算，将结果存储在新的表格列中。

**参数：**
- op: 运算类型，类型为str，取值为"ABS", "NEG", "EXP", "LOG", "SQRT"。
- col: 要操作的表格列名，类型为str，该列必须为数值类型(int或float)。
- result_col: 结果表格列名，类型为str，可以为空，表示使用默认结果列名。

**输入：**
- table: 输入的表格，类型为Table。

**输出：**
- table: 输出的表格，类型为Table，包含新增的结果列。

#### 2.9 BoolColUnaryOpNode
表格列与布尔一元运算节点，支持对表格中的指定列进行`NOT`运算，将结果存储在新的表格列中。

**参数：**
- op: 运算类型，类型为str，取值为"NOT"。
- col: 要操作的表格列名，类型为str，该列必须为布尔类型(bool)。
- result_col: 结果表格列名，类型为str，可以为空，表示使用默认结果列名。

**输入：**
- table: 输入的表格，类型为Table。

**输出：**
- table: 输出的表格，类型为Table，包含新增的结果列。

#### 2.10 NumberColWithColBinOpNode
表格列与表格列二元运算节点，支持对表格中的两个指定列进行`ADD`, `SUB`, `MUL`, `DIV`, `POW`五种基本运算，将结果存储在新的表格列中。

**参数：**
- op: 运算类型，类型为str，取值为"ADD", "SUB", "MUL", "DIV", "POW"。
- col1: 第一个要操作的表格列名，类型为str，该列必须为数值类型(int或float)。
- col2: 第二个要操作的表格列名，类型为str，该列必须为数值类型(int或float)。
- result_col: 结果表格列名，类型为str，可以为空，表示使用默认结果列名。

**输入：**
- table: 输入的表格，类型为Table。

**输出：**
- table: 输出的表格，类型为Table，包含新增的结果列。

#### 2.11 BoolColWithColBinOpNode
表格列与表格列二元布尔运算节点，支持对表格中的两个指定列进行`AND`, `OR`, `XOR`, `SUB`四种基本运算，将结果存储在新的表格列中。

**参数：**
- op: 运算类型，类型为str，取值为"AND", "OR", "XOR", "SUB"。
- col1: 第一个要操作的表格列名，类型为str，该列必须为布尔类型(bool)。
- col2: 第二个要操作的表格列名，类型为str，该列必须为布尔类型(bool)。
- result_col: 结果表格列名，类型为str，可以为空，表示使用默认结果列名。

**输入：**
- table: 输入的表格，类型为Table。

**输出：**
- table: 输出的表格，类型为Table，包含新增的结果列。

#### 2.12 ToStringNode
节点将输入的任意类型转换为字符串类型。

**参数：**
无

**输入：**
- input: 输入的数据，类型为int, float, bool, Table。Datetime类型请参考DatetimePrintNode节点。

**输出：**
- output: 输出的字符串，类型为str。

#### 2.13 ToIntNode
节点将输入的任意类型转换为整数类型。

**参数：**
method: 转换方法，类型为str，取值为"FLOOR", "CEIL", "ROUND"。

**输入：**
- input: 输入的数据，类型为float, bool或str。对于str类型，字符串必须能转换为float或是int格式。

**输出：**
- output: 输出的整数，类型为int。

#### 2.14 ToFloatNode
节点将输入的任意类型转换为浮点数类型。

**参数：**
无

**输入：**
- input: 输入的数据，类型为int, bool或str。对于str类型，字符串必须能转换为float格式。

**输出：**
- output: 输出的浮点数，类型为float。

#### 2.15 ToBoolNode
节点将输入的任意类型转换为布尔类型。

**参数：**
无

**输入：**
- input: 输入的数据，类型为int, float或str。对于str类型，字符串必须是"true"或"false"（不区分大小写）。

**输出：**
- output: 输出的布尔值，类型为bool。

### 3. 可视化节点(visualize)
#### 3.1 PlotNode
绘图节点，支持对表格中的指定列进行绘图操作，支持柱状图(bar)、折线图(line)、散点图(scatter)、饼图(pie)四种图形类型。

**参数：**
- x_col: x轴列名，类型为str，表格中该列的类型必须为int, float或str。
- y_col: y轴列名，类型为str，表格中该列的类型必须为int或float。
- plot_type: 图形类型，类型为str，取值为"scatter", "line", "bar", "pie"。
- title: 图形标题，类型为str，可以为空。

**输入：**
- table: 输入的表格，类型为Table。

**输出：**
- plot: 输出的图形，类型为File，格式为PNG。

**hint：**
- x_col_choices: 列名列表，类型为List[str]，用于在UI中为x_col参数提供可选值。
- y_col_choices: 列名列表，类型为List[str]，用于在UI中为y_col参数提供可选值。

#### 3.2 WordcloudNode
词云图节点，支持对表格中的指定列进行词云图绘制。

**参数：**
- word_col: 词语列名，类型为str，表格中该列的类型必须为str。
- frequency_col: 频率列名，类型为str，表格中该列的类型必须为int或float。

**输入：**
- input: 输入的表格，类型为Table。

**输出：**
- wordcloud_image: 输出的词云图像，类型为File，格式为PNG。

### 4. 字符串处理节点(stringprocess)
#### 4.1 StripNode
节点用于去除字符串首尾的空白字符或指定字符。

**参数：**
- strip_chars: 可选参数，类型为str，指定要去除的字符集合。如果未提供，则默认去除空白字符。

**输入：**
- input: 输入的字符串，类型为str。
- strip_chars: 去除的字符集合，类型为str（可选），如果不为空，则优先级高于参数中的strip_chars。

**输出：**
- output: 去除指定字符后的字符串，类型为str。

#### 4.2 SliceNode
节点用于对字符串进行切片操作，允许使用类似于Python到负数索引的方式进行切片。

**参数：**
- start: 可选参数，类型为int，指定切片的起始索引（包含）。如果未提供，则默认为0。
- end: 可选参数，类型为int，指定切片的结束索引（不包含）。如果未提供，则默认为字符串的长度。

**输入：**
- input: 输入的字符串，类型为str。
- start: 切片的起始索引，类型为int（可选），如果不为空，则优先级高于参数中的start。
- end: 切片的结束索引，类型为int（可选），如果不为空，则优先级高于参数中的end。
***注意：start end 的输入或参数不能全部为空***

**输出：**
- output: 切片后的字符串，类型为str。

#### 4.3 ReplaceNode
节点用于替换字符串中的指定子串。

**参数：**
- old: 要被替换的子串，类型为str。
- new: 用于替换的新子串，类型为str。

**输入：**
- input: 输入的字符串，类型为str。
- old: 要被替换的子串，类型为str（可选），如果不为空，则优先级高于参数中的old。
- new: 用于替换的新子串，类型为str（可选），如果不为空，则优先级高于参数中的new。
***注意：无论是来自于参数还是输入，old值都不能与new值相同***

**输出：**
- output: 替换后的字符串，类型为str。

#### 4.4 LowerOrUpperNode
节点用于将字符串转换为全小写或全大写。

**参数：**
- to_case: 转换类型，类型为str，取值为"LOWER"或"UPPER"。

**输入：**
- input: 输入的字符串，类型为str。

**输出：**
- output: 转换后的字符串，类型为str。

#### 4.5 ConcatNode
节点用于连接两个字符串。

**参数：**
无

**输入：**
- input1: 第一个输入字符串，类型为str。
- input2: 第二个输入字符串，类型为str。

**输出：**
- output: 连接后的字符串，类型为str。

#### 4.6 BatchStripNode
批量去除字符串首尾的空白字符或指定字符。

**参数：**
- strip_chars: 可选参数，类型为str，指定要去除的字符集合。如果未提供，则默认去除空白字符。
- col: 要操作的表格列名，类型为str，该列必须为字符串类型(str)。
- result_col: 结果表格列名，类型为str，可以为空，表示使用默认结果列名。
***注意：col和result_col不能相同***

**输入：**
- input: 输入的表格，类型为Table。
- strip_chars: 去除的字符集合，类型为str（可选），如果不为空，则优先级高于参数中的strip_chars。

**输出：**
- output: 输出的表格，类型为Table，包含新增的结果列。

#### 4.7 BatchConcatNode
批量连接输入表格中的两个字符串列。

**参数：**
- col1: 第一个要操作的表格列名，类型为str，该列必须为字符串类型(str)。
- col2: 第二个要操作的表格列名，类型为str，该列必须为字符串类型(str)。
- result_col: 结果表格列名，类型为str，可以为空，表示使用默认结果列名。

**输入：**
- input: 输入的表格，类型为Table。

**输出：**
- output: 输出的表格，类型为Table，包含新增的结果列。

### 5. 表格处理节点(tableprocess)
#### 5.1 InsertConstColNode
在表格中插入常量列节点。

**参数：**
- col_name: 列名，类型为str。
- col_type: 列的数据类型，类型为str，取值为"int", "float", "bool", "str", "Datetime"。

**输入：**
- table: 输入的表格，类型为Table。
- const_value: 列的常量值，类型根据col_type而定。

**输出：**
- table: 输出的表格，类型为Table，包含新增的常量列。

#### 5.2 InsertRangeColNode
在表格中插入范围列节点。

**参数：**
- col_name: 列名，类型为str。
- col_type: 列的数据类型，类型为str，取值为"int", "float", "Datetime"。

**输入：**
- table: 输入的表格，类型为Table。
- start: 起始值，类型根据col_type而定。
- step: 步长，类型根据col_type而定，可选，如果未提供则默认为1.0/1/1Day。

（注：end值由表格的行数决定，即生成的列长度与表格行数一致。）

**输出：**
- table: 输出的表格，类型为Table，包含新增的范围列。

#### 5.3 InsertRandomColNode
在表格中插入随机列节点。

**参数：**
- col_name: 列名，类型为str。
- col_type: 列的数据类型，类型为str，取值为"int", "float"。

**输入：**
- table: 输入的表格，类型为Table。
- min_value: 最小值，类型根据col_type而定。
- max_value: 最大值，类型根据col_type而定。

**输出：**
- table: 输出的表格，类型为Table，包含新增的随机列。

#### 5.4 FilterNode
表格过滤节点，根据指定的列中的值来过滤：如果该列的值为True，则将该行输出到True表格中，否则输出到False表格中。

**参数：**
- cond_col: 要操作的表格列名，类型为str，该列必须为布尔类型(bool)。

**输入：**
- table: 输入的表格，类型为Table。

**输出：**
- true_table: 过滤结果为True的表格，类型为Table。
- false_table: 过滤结果为False的表格，类型为Table。

**hint：**
- cond_col_choices: 列名列表，类型为List[str]，用于在UI中为cond_col参数提供可选值。

#### 5.5 DropDuplicatesNode
表格去重节点，根据指定的列名列表对表格进行去重操作。

**参数：**
- subset_cols: 列名列表，类型为List[str]，指定用于去重的列名。

**输入：**
- table: 输入的表格，类型为Table。

**输出：**
- deduplicated_table: 去重后的表格，类型为Table。

**hint：**
- subset_col_choices: 列名列表，类型为List[str]，用于在UI中为subset_cols参数提供可选值。

#### 5.6 DropNaNValueNode
表格缺失值删除节点，根据指定的列名列表删除包含NaN值的行。

**参数：**
- subset_cols: 列名列表，类型为List[str]，指定用于检查NaN值的列名。

**输入：**
- table: 输入的表格，类型为Table。

**输出：**
- cleaned_table: 删除NaN值后的表格，类型为Table。

**hint：**
- subset_col_choices: 列名列表，类型为List[str]，用于在UI中为subset_cols参数提供可选值。

#### 5.7 SortNode
表格排序节点，根据指定的列名列表对表格进行排序操作。

**参数：**
- sort_cols: 列名列表，类型为str，指定用于排序的列名。
- ascending: 布尔列表，类型为bool，指定每个排序列的排序顺序，True表示升序，False表示降序。

**输入：**
- table: 输入的表格，类型为Table。

**输出：**
- sorted_table: 排序后的表格，类型为Table。

**hint：**
- sort_col_choices: 列名列表，类型为List[str]，用于在UI中为sort_cols参数提供可选值。

#### 5.8 GroupNode
表格分组节点，根据指定的列名列表对表格进行分组操作，并对每个分组应用聚合函数。

**参数：**
- group_cols: 列名列表，类型为List[str]，指定用于分组的列名。
- agg_cols: 要聚合的列名，类型为List[str]。
- agg_func: 聚合函数，类型为str，取值为"SUM", "MEAN", "COUNT", "MAX", "MIN", "STD"。

**输入：**
- table: 输入的表格，类型为Table。

**输出：**
- grouped_table: 分组并聚合后的表格，类型为Table。

**hint：**
- group_col_choices: 列名列表，类型为List[str]，用于在UI中为group_cols参数提供可选值。
- agg_col_choices: 列名列表，类型为List[str]，用于在UI中为agg_col参数提供可选值。

#### 5.9 MergeNode
表格合并节点，将两个有着相同列的表格合并为一个表格。

**参数：**
无

**输入：**
- table_1: 第一个输入表格，类型为Table。
- table_2: 第二个输入表格，类型为Table。

**输出：**
- merged_table: 合并后的表格，类型为Table。

#### 5.10 SelectColNode
表格列选择节点，根据指定的列名列表从表格中选择对应的列。

**参数：**
- selected_cols: 列名列表，类型为List[str]，指定要选择的列名。

**输入：**
- table: 输入的表格，类型为Table。

**输出：**
- selected_table: 选择后的表格，类型为Table。
- dropped_table: 被删除列后的表格，类型为Table。

**hint：**
- selected_col_choices: 列名列表，类型为List[str]，用于在UI中为selected_cols参数提供可选值。

#### 5.11 JoinNode
表格连接节点，根据指定的键列将两个表格进行连接操作。

**参数：**
- left_on: 左表的键列名，类型为str。
- right_on: 右表的键列名，类型为str。
- how: 连接方式，类型为str，取值为"INNER", "LEFT", "RIGHT", "OUTER"。

**输入：**
- left_table: 左表，类型为Table。
- right_table: 右表，类型为Table。

**输出：**
- joined_table: 连接后的表格，类型为Table。

**hint：**
- left_on_choices: 列名列表，类型为List[str]，用于在UI中为left_on参数提供可选值。
- right_on_choices: 列名列表，类型为List[str]，用于在UI中为right_on参数提供可选值。

#### 5.12 RenameColNode
表格列重命名节点，根据指定的列名映射关系对表格中的列进行重命名操作。

**参数：**
- rename_map: 列名映射关系，类型为dict[str, str]，键为原列名，值为新列名。

**输入：**
- table: 输入的表格，类型为Table。

**输出：**
- renamed_table: 重命名后的表格，类型为Table。

**hint：**
- rename_col_choices: 列名列表，类型为List[str]，用于在UI中为rename_map参数提供可选值。

### 6. 文件处理节点(file)
#### 6.1 UploadNode
文件上传节点，支持上传本地文件并输出为File类型。

**参数：**
- file: File类型的文件对象，来自于api/file/upload接口上传文件后返回的文件对象。

**输入：**
无

**输出：**
- file: 输出的文件对象，类型为File。

#### 6.2 DisplayNode
文件显示节点，支持显示File类型的文件内容，并允许用户下载该文件。

**参数：**
无

**输入：**
- file: 输入的文件对象，类型为File。

**输出：**
无

#### 6.3 TableFromCSVNode
从CSV文件加载表格节点，可以读取上传的CSV文件并将其转换为Table类型。

**参数：**
无

**输入：**
- csv_file: 输入的CSV文件，类型为File，格式为CSV。

**输出：**
- table: 输出的表格，类型为Table。


### 7. 日期时间处理节点(datetimeprocess)
#### 7.1 DatetimeComputeNode
日期与PRIM类型运算节点，支持对Datetime类型与int或float类型的输入进行`ADD`, `SUB`两种基本运算。

**参数：**
- op: 运算类型，类型为str，取值为"ADD", "SUB"。
- unit: 时间单位，用来指定输入float/int的单位，类型为str，取值为"DAYS", "HOURS", "MINUTES", "SECONDS"。

**输入：**
- datetime: 日期时间操作数，类型为Datetime。
- value: 数值操作数，类型为int或float。

**输出：**
- result: 运算结果，类型为Datetime。

#### 7.2 DatetimeDiffNode
日期时间差值节点，支持计算两个Datetime类型输入之间的差值，结果以指定单位表示。

**参数：**
- unit: 时间单位，用来指定输出差值的单位，类型为str，取值为"DAYS", "HOURS", "MINUTES", "SECONDS"。

**输入：**
- datetime_x: 第一个日期时间操作数，类型为Datetime。
- datetime_y: 第二个日期时间操作数，类型为Datetime。

**输出：**
- difference: 两个日期时间的差值，类型为float。

#### 7.3 ToDatetimeNode
节点将输入的数值类型转换为日期时间类型。

**参数：**
- unit: 时间单位，用来指定输入数值的单位，类型为str，取值为"DAYS", "HOURS", "MINUTES", "SECONDS"。

**输入：**
- value: 输入的数值，类型为INT或FLOAT。

**输出：**
- datetime: 输出的日期时间值，类型为Datetime。

#### 7.4 StrToDatetimeNode
节点将输入的字符串类型转换为日期时间类型。

**参数：**
无

**输入：**
- value: 输入的字符串，类型为STR，必须符合任何Pandas支持的日期时间格式，如：ISO 8601格式等。

**输出：**
- datetime: 输出的日期时间值，类型为Datetime。

#### 7.5 DatetimePrintNode
将Datetime类型格式化为字符串类型节点。

**参数：**
- format: 日期时间格式字符串，类型为str，符合Python的strftime格式规范。

**输入：**
- datetime: 输入的日期时间，类型为Datetime。

**输出：**
- output: 输出的字符串，类型为str。

#### 7.6 DatetimeToTimestampNode
将Datetime类型转换为时间戳类型(float)节点。

**参数：**
- unit: 时间单位，用来指定输出时间戳的单位，类型为str，取值为"DAYS", "HOURS", "MINUTES", "SECONDS"。

**输入：**
- datetime: 输入的日期时间，类型为Datetime。

**输出：**
- timestamp: 输出的时间戳，类型为float。

### 8. 分析节点(analysis)
#### 8.1 StatsNode
统计分析节点，计算输入表格中指定列的基本统计信息，包括计数(count)、均值(mean)、标准差(std)、最小值(min)、 最大值(max)、总和(sum)、25%分位数(25%), 中位数(50%), 75%分位数(75%)。

**参数：**
- col: 要分析的表格列名，类型为str。

**输入：**
- table: 输入的表格，类型为Table。

**输出：**
- mean: 均值，类型为float或int，取决于输入列的数据类型。
- count: 计数，类型为int。
- std: 标准差，类型为float或int，取决于输入列的数据类型。
- min: 最小值，类型为float或int，取决于输入列的数据类型。
- max: 最大值，类型为float或int，取决于输入列的数据类型。
- sum: 总和，类型为float或int，取决于输入列的数据类型。
- quantile_25: 25%分位数，类型为float或int，取决于输入列的数据类型。
- quantile_50: 50%分位数（中位数），类型为float或int，取决于输入列的数据类型。
- quantile_75: 75%分位数，类型为float或int，取决于输入列的数据类型。

**hint：**
- col_choices: 列名列表，类型为List[str]，用于在UI中为col参数提供可选值。

### 9. 控制节点(control)
#### 9.1 CustomScriptNode
用户自定义脚本节点，允许用户编写自定义的Python脚本来处理输入数据并生成输出数据。注意，为了安全起见，用户脚本将在受限的环境中执行，且只能使用预定义的安全库和函数。

注意：在节点中的代码编辑器中，应该为用户提供基本的模版，即`server/engine/nodes/utiliy/custom_template.py`文件中的内容。

**参数：**
- input_ports: 输入端口定义，类型为List[Dict[str, type]]，每个输入端口由名称和类型组成。
- output_ports: 输出端口定义，类型为List[Dict[str, type]]，每个输出端口由名称和类型组成。
- script: 用户自定义的Python脚本，类型为str。脚本必须定义一个名为`script`的函数。

注：上述输入输出类型(Type)允许使用："STR", "INT", "FLOAT", "BOOL", "DATETIME"。

**输入：**
动态定义的输入端口，根据input_ports参数定义。

**输出：**
动态定义的输出端口，根据output_ports参数定义。

**hint：**
- script_template: str，预定义的脚本模版内容，供用户参考和编辑使用。
