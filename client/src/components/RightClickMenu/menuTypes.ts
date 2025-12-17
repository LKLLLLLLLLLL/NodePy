export interface MenuNode {
    label: string;
    value: string;
    children?: MenuNode[];
}

export const nodeMenuItems: MenuNode[] = [
    {
        label: '输入',
        value: 'input',
        children: [
            {
                label: '布尔',
                value: 'BoolNode'
            },
            {
                label: '常量',
                value: 'ConstNode'
            },
            {
                label: '字符串',
                value: 'StringNode'
            },
            {
                label: '表格',
                value: 'TableNode'
            },
            {
                label: '随机表格',
                value: 'RandomNode'
            },
            {
                label: '范围表格',
                value: 'RangeNode'
            },
            {
                label: '时间输入',
                value: 'DateTimeNode'
            },
            {
                label: 'K线数据',
                value: 'KlineNode'
            },
        ]
    },
    {
        label: '计算',
        value: 'compute',
        children: [
            {
                label: '数值二元运算',
                value: 'NumberBinOpNode'
            },
            {
                label: '数值一元运算',
                value: 'NumberUnaryOpNode'
            },
            {
                label: '比较',
                value: 'PrimitiveCompareNode'
            },
            {
                label: '布尔二元运算',
                value: 'BoolBinOpNode'
            },
            {
                label: '布尔非',
                value: 'BoolUnaryOpNode'
            },
            {
                label: '列二元运算',
                value: 'ColWithNumberBinOpNode'
            },
            {
                label: '列一元运算',
                value: 'NumberColUnaryOpNode'
            },
            {
                label: '列布尔运算',
                value: 'ColWithBoolBinOpNode'
            },
            {
                label: '列布尔非运算',
                value: 'BoolColUnaryOpNode'
            },
            {
                label: '列间运算',
                value: 'NumberColWithColBinOpNode'
            },
            {
                label: '列间布尔运算',
                value: 'BoolColWithColBinOpNode'
            },
            {
                label: '列间比较',
                value: 'ColCompareNode'
            },
            {
                label: '转为字符串',
                value: 'ToStringNode'
            },
            {
                label: '转为整数',
                value: 'ToIntNode'
            },
            {
                label: '转为浮点',
                value: 'ToFloatNode'
            },
            {
                label: '转为布尔',
                value: 'ToBoolNode'
            },
        ]
    },
    {
        label: '控制',
        value: 'control',
        children: [
            {
                label: '自定义脚本',
                value: 'CustomScriptNode'
            },
            {
                label: '表格逐行循环',
                value: 'ForEachRowNode'
            },
            {
                label: '滑动窗口循环',
                value: 'ForRollingWindowNode'
            },
            {
                label: '解包',
                value: 'UnpackNode'
            },
            {
                label: '打包',
                value: 'PackNode'
            },
            {
                label: '单元格提取',
                value: 'GetCellNode'
            },
            {
                label: '单元格更新',
                value: 'SetCellNode'
            },
        ]
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
                label: '文件表格节点',
                value: 'TableFromFileNode'
            },
            {
                label: '表格文件节点',
                value: 'TableToFileNode'
            },
            {
                label: '文件文本节点',
                value: 'TextFromFileNode'
            },
        ]
    },
    {
        label: '字符串处理节点',
        value: 'stringProcessing',
        children: [
            {
                label: '字符串切片',
                value: 'SliceNode'
            },
            {
                label: '字符串替换',
                value: 'ReplaceNode'
            },
            {
                label: '大小写转换',
                value: 'LowerOrUpperNode'
            },
            {
                label: '正则表达式提取',
                value: 'RegexExtractNode'
            },
            {
                label: '分词',
                value: 'TokenizeNode'
            },
            {
                label: '首尾字符去除',
                value: 'StripNode'
            },
            {
                label: '批量首尾字符去除',
                value: 'BatchStripNode'
            },
            {
                label: '字符串拼接',
                value: 'ConcatNode'
            },
            {
                label: '批量字符串拼接',
                value: 'BatchConcatNode'
            },
            {
                label: '正则表达式匹配',
                value: 'RegexMatchNode'
            },
            {
                label: '批量正则表达式匹配',
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
            {
                label: '表格列选择节点',
                value: 'SelectColNode'
            },
            {
                label: '表格连接节点',
                value: 'JoinNode'
            },
            {
                label: '表格列重命名节点',
                value: 'RenameColNode'
            },
            {
                label: '表格列移动节点',
                value: 'ShiftNode'
            },
        ]
    },
    {
        label: '时间处理节点',
        value: 'datetimeProcess',
        children: [
            {
                label: '时间数值运算节点',
                value: 'DatetimeComputeNode'
            },
            {
                label: '时间差值节点',
                value: 'DatetimeDiffNode'
            },
            {
                label: '数值时间转换节点',
                value: 'ToDatetimeNode'
            },
            {
                label: '字符串时间转换节点',
                value: 'StrToDatetimeNode'
            },
            {
                label: '时间格式化节点',
                value: 'DatetimePrintNode'
            },
            {
                label: '时间戳转换节点',
                value: 'DatetimeToTimestampNode'
            },
        ]
    },
    {
        label: '分析节点',
        value: 'analysis',
        children: [
            {
                label: '统计节点',
                value: 'StatsNode'
            },
            {
                label: '差分节点',
                value: 'DiffNode'
            },
            {
                label: '滑动窗口节点',
                value: 'RollingNode'
            },
            {
                label: '重采样节点',
                value: 'ResampleNode'
            },
            {
                label: '百分比变化计算节点',
                value: 'PctChangeNode'
            },
            {
                label: '累计计算节点',
                value: 'CumulativeNode'
            },
        ]
    },
    {
        label: '可视化',
        value: 'visualization',
        children: [
            {
                label: '快速绘图',
                value: 'QuickPlotNode'
            },
            {
                label: '双轴绘图',
                value: 'DualAxisPlotNode'
            },
            {
                label: '统计绘图',
                value: 'StatisticalPlotNode'
            },
            {
                label: '词云',
                value: 'WordcloudNode'
            },
            {
                label: 'K线图',
                value: 'KlinePlotNode'
            },
        ]
    },
    {
        label: '机器学习节点',
        value: 'machineLearning',
        children: [
            {
                label: '线性回归节点',
                value: 'LinearRegressionNode'
            },
            {
                label: '滞后特征节点',
                value: 'LagFeatureNode'
            },
            {
                label: '随机森林回归节点',
                value: 'RandomForestRegressionNode'
            },
            {
                label: '逻辑回归节点',
                value: 'LogisticRegressionNode'
            },
            {
                label: '支持向量分类节点',
                value: 'SVCNode'
            },
            {
                label: 'K均值节点',
                value: 'KMeansClusteringNode'
            },
            {
                label: '特征标准化节点',
                value: 'StandardScalerNode'
            },
            {
                label: '分类评分节点',
                value: 'ClassificationScoreNode'
            },
            {
                label: '回归评分节点',
                value: 'RegressionScoreNode'
            },
            {
                label: '预测节点',
                value: 'PredictNode'
            },
        ]
    },
]
