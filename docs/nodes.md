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

### 2. 六种类型
在我们的节点系统中，一共只有六大类型：
- `int`: 整数类型, 底层通过Python的`int`实现或`int64`实现。
- `float`: 浮点数类型, 底层通过Python的`float`实现或`float64`实现。
- `bool`: 布尔类型, 底层通过Python的`bool`实现。
- `str`: 字符串类型, 底层通过Python的`str`实现。
- `Table`: 表格类型, 底层通过Pandas的`DataFrame`实现。
- `File`: 文件类型, 是对象文件系统的一个抽象，每个用户所产生的全部文件大小受限于其配额（默认5GB）。

其中，前三种由于可以定义各种数学运算，因此也被称作"Prim"类型；前两种也可以被称作"Number"类型。

## 二、节点列表

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

#### 1.5 TableFromCSVNode
从CSV文件加载表格节点，可以读取上传的CSV文件并将其转换为Table类型。

**参数：**
无

**输入：**
- csv_file: 输入的CSV文件，类型为File，格式为CSV。

**输出：**
- table: 输出的表格，类型为Table。

### 2. 计算节点(Compute)
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
- op: 运算类型，类型为str，取值为"ADD", "SUB", "MUL", "COL_DIV_NUM", "NUM_DIV_COL", "COL_POW_NUM", "NUM_POW_COL"。
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

#### 2.10 NumberColWithColUnaryOpNode
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

### 3. 可视化节点(Visualize)
#### 3.1 PlotNode
绘图节点，支持对表格中的指定列进行绘图操作，支持柱状图(bar)、折线图(line)、散点图(scatter)三种图形类型。

**参数：**
- x_col: x轴列名，类型为str，表格中该列的类型必须为int, float或str。
- y_col: y轴列名，类型为str，表格中该列的类型必须为int或float。
- plot_type: 图形类型，类型为str，取值为"scatter", "line", "bar"。
- title: 图形标题，类型为str，可以为空。

**输入：**
- table: 输入的表格，类型为Table。

**输出：**
- plot: 输出的图形，类型为File，格式为PNG。

### 4. 字符串处理节点(StringProcess)

TODO

### 5. 表格处理节点(TableProcess)

TODO

### 6. 文件处理节点(File)
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