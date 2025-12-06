export interface MenuNode {
    label: string;
    value: string;
    children?: MenuNode[];
}

export const nodeMenuItems: MenuNode[] = [
    {
        label: '输入节点',
        value: 'input',
        children: [
            {
                label: '布尔节点',
                value: 'BoolNode'
            },
            {
                label: '常数节点',
                value: 'ConstNode'
            },
            {
                label: '字符串节点',
                value: 'StringNode'
            },
            {
                label: '表格节点',
                value: 'TableNode'
            },
            {
                label: '随机表格生成节点',
                value: 'RandomNode'
            },
            {
                label: '范围表格生成节点',
                value: 'RangeNode'
            },
            {
                label: '时间输入节点',
                value: 'DateTimeNode'
            },
            {
                label: 'K线数据节点',
                value: 'KlineNode'
            },
        ]
    },
    {
        label: '运算节点',
        value: 'compute',
        children: [
            {
                label: '数字二元运算节点',
                value: 'NumberBinOpNode'
            },
            {
                label: '数字一元运算节点',
                value: 'NumberUnaryOpNode'
            },
            {
                label: '比较节点',
                value: 'PrimitiveCompareNode'
            },
            {
                label: '布尔二元运算节点',
                value: 'BoolBinOpNode'
            },
            {
                label: '布尔非运算节点',
                value: 'BoolUnaryOpNode'
            },
            {
                label: '列数字二元运算节点',
                value: 'ColWithNumberBinOpNode'
            },
            {
                label: '列数字一元运算节点',
                value: 'NumberColUnaryOpNode'
            },
            {
                label: '列布尔二元运算节点',
                value: 'ColWithBoolBinOpNode'
            },
            {
                label: '列布尔非运算节点',
                value: 'BoolColUnaryOpNode'
            },
            {
                label: '列间数字运算节点',
                value: 'NumberColWithColBinOpNode'
            },
            {
                label: '列间布尔运算节点',
                value: 'BoolColWithColBinOpNode'
            },
            {
                label: '列间比较节点',
                value: 'ColCompareNode'
            },
            {
                label: '字符串转换节点',
                value: 'ToStringNode'
            },
            {
                label: '整数转换节点',
                value: 'ToIntNode'
            },
            {
                label: '浮点数转换节点',
                value: 'ToFloatNode'
            },
            {
                label: '布尔转换节点',
                value: 'ToBoolNode'
            },
        ]
    },
    {
        label: '控制节点',
        value: 'control',
        children: []
    },
    {
        label: '文件节点',
        value: 'file',
        children: [
            {
                label: '文件上传节点',
                value: 'UploadNode'
            },
            {
                label: '文件显示节点',
                value: 'DisplayNode'
            },
            {
                label: '文件表格节点',
                value: 'TableFromFileNode'
            }
        ]
    },
    {
        label: '字符串处理节点',
        value: 'stringProcessing',
        children: [
            {
                label: '字符串切片节点',
                value: 'SliceNode'
            },
            {
                label: '字符串替换节点',
                value: 'ReplaceNode'
            },
            {
                label: '大小写转换节点',
                value: 'LowerOrUpperNode'
            },
            {
                label: '正则表达式提取节点',
                value: 'RegexExtractNode'
            },
            {
                label: '首尾字符清洗节点',
                value: 'StripNode'
            },
            {
                label: '批量首尾字符清洗节点',
                value: 'BatchStripNode'
            },
            {
                label: '字符串拼接节点',
                value: 'ConcatNode'
            },
            {
                label: '批量字符串拼接节点',
                value: 'BatchConcatNode'
            },
            {
                label: '正则表达式匹配节点',
                value: 'RegexMatchNode'
            },
            {
                label: '批量正则表达式匹配节点',
                value: 'BatchRegexMatchNode'
            },
        ]
    },
    {
        label: '表格处理节点',
        value: 'tableProcessing',
        children: [
            {
                label: '常量列添加节点',
                value: 'InsertConstColNode'
            },
            {
                label: '范围数据列添加节点',
                value: 'InsertRangeColNode'
            },
            {
                label: '随机数据列添加节点',
                value: 'InsertRandomColNode'
            },
            {
                label: '表格过滤节点',
                value: 'FilterNode'
            },
            {
                label: '表格去重节点',
                value: 'DropDuplicatesNode'
            },
            {
                label: '表格缺失值删除节点',
                value: 'DropNaNValueNode'
            },
            {
                label: '表格缺失值填充节点',
                value: 'FillNaNValueNode'
            },
            {
                label: '表格排序节点',
                value: 'SortNode'
            },
            {
                label: '表格分组节点',
                value: 'GroupNode'
            },
            {
                label: '表格合并节点',
                value: 'MergeNode'
            },
            {
                label: '表格切片节点',
                value: 'TableSliceNode'
            },
        ]
    },
    {
        label: '分析节点',
        value: 'analysis',
        children: []
    },
    {
        label: '可视化节点',
        value: 'visualization',
        children: [
            {
                label: '绘图节点',
                value: 'PlotNode'
            },
            {
                label: '高级绘图节点',
                value: 'AdvancePlotNode'
            },
            {
                label: '词云节点',
                value: 'WordcloudNode'
            },
        ]
    }
]
