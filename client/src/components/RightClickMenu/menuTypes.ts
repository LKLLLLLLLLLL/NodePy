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
                label: '分词节点',
                value: 'TokenizeNode'
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
        label: '可视化节点',
        value: 'visualization',
        children: [
            {
                label: '快速绘图节点',
                value: 'QuickPlotNode'
            },
            {
                label: '双轴绘图节点',
                value: 'DualAxisPlotNode'
            },
            {
                label: '统计绘图节点',
                value: 'StatisticalPlotNode'
            },
            {
                label: '词云节点',
                value: 'WordcloudNode'
            },
            {
                label: 'K线图节点',
                value: 'KlinePlotNode'
            },
        ]
    },
    {
        label: '机器学习节点',
        value: 'machineLearning',
        children: [
            {
                label: '分类评分节点',
                value: 'ClassificationScoreNode'
            },
            {
                label: '回归评分节点',
                value: 'RegressionScoreNode'
            },
            {
                label: '线性回归节点',
                value: 'LinearRegressionNode'
            },
            {
                label: '预测节点',
                value: 'PredictNode'
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
        ]
    },
]
