# NodePy 节点文档

本文档描述了 NodePy 项目中所有已实现的节点。每个节点包括其操作描述、接受的参数、输入和输出类型要求，以及一个简单的使用示例。

## 总体逻辑

### 类型系统
NodePy 的节点系统是一个完全静态类型的节点系统，类型验证分为三个阶段：
- Stage1 参数验证
- Stage2 输入输出静态推导
- Stage3 运行时验证

## 目录

下面按模块列出已实现节点的说明（构造参数、输入接口、输出接口、示例）。示例以伪代码/简短 python 片段说明期望输入 payload 与期望输出。

### 说明约定
- 构造参数：指在节点实例化时需要/可选传入的字段，类型采用项目中 `Schema`, `ColType`, `TableSchema` 命名。必填项会在 Stage1 校验时被检查。
- 输入接口：列出输入端口名、可接受的数据类型（例如 `TABLE` / `STR` / `INT` / `FLOAT` / `BOOL`），以及对于 `TABLE` 类型的列要求（若有）
- 输出接口：列出输出端口名和其输出的 schema 描述
- 示例：给出节点构造、期望输入 Data（payload 形式）与期望输出 Data（或说明）

## 节点列表

### ConstNode
描述：产生一个常量值（原生标量：int/float/str/bool）。

构造参数：
- `id: str` （必填）
- `name: str` （必填）
- `type: Literal['ConstNode']` （必填，值必须为 'ConstNode'）
- `value: int|float|str|bool` （必填，类型必须和 data_type 匹配）
- `data_type: Literal['int','float','str','bool']` （必填，指定 value 的类型）
- `global_config: GlobalConfig` （必填）

输入接口：无输入端口。

输出接口：
- `const` -> 对应 `Schema.Type.INT|FLOAT|STR|BOOL`，与 `data_type` 一致。

示例：
- 构造参数：type='ConstNode', value=3, data_type='int'
- 输入：无
- 期望输出：输出端口 `const`，payload 为常量值 3（类型 int）

### StringNode
描述：产生一个字符串常量。

构造参数：
- `id,name,type='StringNode'`
- `value: str` （必填）
- `global_config: GlobalConfig`

输入接口：无输入端口。

输出接口：
- `string` -> `Schema.Type.STR`

示例：
- 构造参数：type='StringNode', value='hello'
- 输入：无
- 期望输出：输出端口 `string`，payload 为字符串 'hello'

### TableNode (Generate.Table.TableNode)
描述：由用户提供的行（list[dict]）构造一个表（Table）；在构造阶段会推断并缓存每列的类型。

构造参数：
- `rows: List[Dict[str, int|float|str|bool]]` （必填；每行 dict 的 key 顺序需与 `col_names` 一致）
- `col_names: List[str]` （必填；列名顺序）
- `global_config: GlobalConfig`

约束：
- `rows` 不能为空；所有行必须具有与 `col_names` 相同的键集合与顺序；列类型必须在所有行间可一致推断（int 与 float 可升级为 float，bool 单独识别）。

输入接口：无输入端口。

输出接口：
- `table` -> `Schema.Type.TABLE`，`tab` 字段包含每列的 `ColType`（INT/FLOAT/STR/BOOL）。

示例：
- 构造参数：type='TableNode', col_names=['a','b'], rows = [{a:1,b:'x'}, {a:2,b:'y'}]
- 输入：无
- 期望输出：输出端口 `table`，payload 为一张表，列 a (int) 和 b (str)，含两行数据

### NumBinComputeNode (二元数值运算，Primitive)
描述：对两个原生数值（int/float）执行二元运算（ADD, SUB, MUL, DIV, POW 等），根据输入类型推断输出类型（DIV 或任一为 float 时输出 float）。

构造参数：
- `op: Literal['ADD','SUB','MUL','DIV','POW', ...]`（必填）
- `id,name,type`，`global_config`

输入接口：
- `x`、`y`（端口接受原生数值 `INT`/`FLOAT`）

输出接口：
- `result` -> `Schema.Type.INT` 或 `Schema.Type.FLOAT`（根据输入及 op 决定）

示例：
- 构造参数：op='ADD'
- 输入：两个原生数值输入 x=3, y=4
- 期望输出：输出端口 `result`，payload 为数值 7

异常/边界：
- DIV 运算在运行时如果除数为 0，应抛出 `NodeExecutionError`。

### NumUnaryComputeNode (一元数值运算)
描述：对一个原生数值执行一元运算（NEG, ABS, SQRT, LOG 等）。

构造参数：
- `op: Literal['NEG','ABS','SQRT', ...]`
- `id,name,type,global_config`

输入接口：
- `x` -> 原生数值（INT/FLOAT）

输出接口：
- `result` -> INT/ FLOAT（例如 SQRT 总是 FLOAT）

示例：
- 构造参数：op='SQRT'
- 输入：单个数值 x=9.0
- 期望输出：输出端口 `result`，payload 为数值 3.0（float）

异常/边界：
- SQRT 对负数会在运行时抛出 `NodeExecutionError`。

### CmpNode（比较运算）
描述：对两个原生值进行比较（EQ, NE, GT, LT, GE, LE）。Stage2 会校验两边的静态类型一致。

构造参数：
- `op: Literal['EQ','NE','GT','LT','GE','LE']`
- `id,name,type,global_config`

输入接口：
- `x`, `y` -> 接受任意同类型原生值（INT/FLOAT/STR/BOOL），两侧类型需兼容。

输出接口：
- `result` -> `Schema.Type.BOOL`

示例：
- 构造参数：op='EQ'
- 输入：两个同类型原语 x='a', y='a'
- 期望输出：输出端口 `result`，payload 为布尔值 True

### BoolBinComputeNode / BoolUnaryComputeNode
描述：对布尔值进行二元（AND, OR, XOR, SUB）或一元（NOT）运算。

构造参数：
- `op`（二元节点）或无（一元）以及 `id,name,type,global_config`

输入接口：
- 二元：`x`,`y` -> `Schema.Type.BOOL`
- 一元：`x` -> `Schema.Type.BOOL`

输出接口：
- `result` -> `Schema.Type.BOOL`

示例：
- 构造参数：op='XOR'
- 输入：两个布尔值 x=true, y=false
- 期望输出：输出端口 `result`，payload 为 true

### TableAppendStringNode / TablePrependStringNode
描述：对表中某列的每个值追加或前置一个给定字符串，并写入新的列。

构造参数：
- `column: str`（被操作的列名，必填）
- `result_col: str`（输出列名，必填，不能与保留索引列冲突）
- `id,name,type,global_config`

输入接口：
- `table_input` -> `Schema.Type.TABLE`，要求 `column` 为 `STR` 类型
- `value_input` / `string` -> `Schema.Type.STR`（要追加/前置的字符串）

输出接口：
- `output` -> `Schema.Type.TABLE`（包含原始列 + 新的 `result_col`，类型为 STR）

示例：
- 构造参数：column='s', result_col='s2'
- 输入表格：一列 s 包含 ['a','b']
- 附加字符串输入：'z'
- 期望输出表格：新增列 s2，其值为 ['az','bz']，其余列保持不变

### TableContainsStringNode / TableStartWithStringNode / TableEndWithStringNode / TableReplaceStringNode / TableStringLengthNode
描述：针对表列做字符串相关的向量化操作（包含检测、前缀/后缀检测、替换、长度计算），并将结果写到新列。

构造参数（通用）：
- `column: str`（源列）
- `result_col: str`（输出列）
- `id,name,type,global_config`

输入接口（示例）:
- `table` -> `Schema.Type.TABLE`，要求 `column` 为 STR 类型
- `substring` / `old` / `new` / `string` 视节点而定 -> `Schema.Type.STR`

输出接口：
- `output` -> `Schema.Type.TABLE`，新增 `result_col` 类型根据节点而定（BOOL / STR / INT）

示例（contains）：
- 构造参数：column='s', result_col='has_a'
- 输入表格：列 s 包含 ['a','ab']
- 输入参数：substring='a'
- 期望输出表格：新增列 has_a（布尔），值为 [true, true]

示例（length）：
- 构造参数：column='s', result_col='len_s'
- 输入表格：列 s 包含 ['a','ab']
- 输入：无额外参数
- 期望输出表格：新增列 len_s（整数），值为 [1,2]

### TabBinPrimNumComputeNode / TabUnaryNumComputeNode
描述：向量化地对表列进行数值二元/一元运算（例如表列与原生数值或另一列做算术运算，或对列做 SQRT/LOG 等），并把结果写入新列。

构造参数（通用）：
- `col` / `left_col` / `right_col`：列名
- `result_col`：输出列名
- `op`：操作符（ADD, SUB, DIV 等或 LOG/SQRT/NEG）
- `id,name,type,global_config`

输入接口：
- `table` -> `Schema.Type.TABLE`（要求相应列存在且类型为 INT/FLOAT）
- 可选 `value`（原生数值）或 `table_right`（另一张表，需包含 right_col）

输出接口：
- `table` -> `Schema.Type.TABLE`（包含新增 result_col，类型根据运算与列类型推断；DIV/浮点参与会导致 FLOAT）

异常：
- 除数为 0、缺少列、或类型不匹配会抛出 `NodeExecutionError` 或 `NodeValidationError`。

示例：
- 构造参数：op='ADD', col='a', result_col='r'
- 输入表格：列 a 为 [1,2,3]
- 额外输入：num=2
- 期望输出表格：新增列 r，值为 [3,4,5]

### ColBinNumComputeNode / ColBinBoolComputeNode
描述：对表的两列做按元素（elementwise）运算（数值/布尔），并写回结果列。

构造参数与接口与上类相仿，区别在于两操作数均来自同一张表的不同列。

示例：
- 构造参数：col1='a', col2='b', result_col='r'
- 输入表格：列 a=[1,2]，b=[3,4]
- 期望输出表格：新增列 r=[4,6]

### TabBinPrimBoolComputeNode / TabUnaryBoolComputeNode
描述：向量化布尔运算（表列与原生布尔值或另一列做 AND/OR/XOR/NOT 等），并在表中写回结果列。

参数、接口、示例与数值向量化节点类似，差别仅在列与输入类型为布尔。

### PlotNode (Visualize.Plot.PlotNode)
描述：使用 matplotlib 从输入表生成图片（PNG），并把图片路径作为输出。

构造参数：
- `x_column: str`（必填）
- `y_column: str`（必填）
- `plot_type: Literal['scatter','line','bar']`（必填）
- `title: Optional[str]`（可选，非空字符串）
- `id,name,type='PlotNode', global_config`

输入接口：
- `input` -> `Schema.Type.TABLE`，要求 `x_column` 与 `y_column` 为数值列（INT/FLOAT）。注意：此节点在运行时使用 pandas.DataFrame 直接绘图，因此测试中有时用 `Data.model_construct(payload=df)` 传入原始 DataFrame 以避免在 pydantic 层被严格拦截。

输出接口：
- `plot` -> `Schema.Type.FILE`（输出为文件路径 Path，指向生成的 PNG）

示例：
- 构造参数：x_column='x', y_column='y', plot_type='scatter'
- 输入表格：列 x=[1,2,3]，y=[4,5,6]（作为 DataFrame payload）
- 期望输出：输出端口 `plot`，payload 为生成的 PNG 文件路径，文件包含 xy 散点图

### RandomNode / RangeNode
描述：表格生成类（RandomNode 生成随机列，RangeNode 生成数值序列列）。当前实现为占位或部分实现（见代码），测试将这些类当作 placeholder 进行抽象校验。

构造参数示例（RangeNode）：
- `start: int|float`, `end: int|float`, `step: int|float`, `column_name: str`

输出接口：
- `output` -> `Schema.Type.TABLE`，包含 `_index` 自动索引列以及指定的 `column_name`。

示例（直观）：
- 构造参数：start=0, end=5, step=2, column_name='a'
- 输入：无
- 期望输出表格：列 a 包含 [0,2,4]

### WordCloudNode（占位）
描述：用 wordcloud 库从词频生成词云图片，目前仓库中仅为占位说明，尚未完整实现外部依赖与参数接口。

---
