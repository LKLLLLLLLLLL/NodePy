# 结点工作进度

## 现在已经定义的结点

### 常量结点
- ConstNode
- StringNode
- TableNode

### 数值运算节点
- NumBinComputeNode
- NumUnaryComputeNode

### 比较运算结点
- CmpNode

### 布尔运算结点
- BoolBinCompute
- BoolNotNode

### 字符串运算结点

#### 纯字符串运算结点
- ClipOrSubStringNode
- StripStringNode
- ReplaceStringNode
- UpperOrLowerStringNode

#### table内的字符串运算结点
- TableAppendOrPrependStringNode
- TableOneInputStringMethodNode
- TableStringLengthNode
- TableReplaceStringNode


### 画图节点
- PlotNode


## 对一些形式一样的结点进行了合并

- ClipOrSubStringNode是对ClipStringNode和SubStringNode的合并(中间加入op属性来区分，下同)
- UpperOrLowerStringNode是对UpperStringNode和LowerStringNode的合并
- TableAppendOrPrependStringNode是对TableAppendStringNode和TablePrependStringNode的合并
- TableOneInputStringMethodNode是对TableContainsStringNode和TableStartWithStringNode以及TableEndWithStringNode的合并