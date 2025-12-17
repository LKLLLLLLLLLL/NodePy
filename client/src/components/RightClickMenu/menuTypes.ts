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
                label: '提取单元格',
                value: 'GetCellNode'
            },
            {
                label: '更新单元格',
                value: 'SetCellNode'
            },
        ]
    },
    {
        label: '文件',
        value: 'file',
        children: [
            {
                label: '文件上传',
                value: 'UploadNode'
            },
            {
                label: '文件转表格',
                value: 'TableFromFileNode'
            },
            {
                label: '表格转文件',
                value: 'TableToFileNode'
            },
            {
                label: '提取文本',
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
            {
                label: '分词',
                value: 'TokenizeNode'
            },
            {
                label: '情感分析',
                value: 'SentimentAnalysisNode'
            },
        ]
    },
    {
        label: '表格处理',
        value: 'tableProcessing',
        children: [
            {
                label: '添加常量列',
                value: 'InsertConstColNode'
            },
            {
                label: '添加范围列',
                value: 'InsertRangeColNode'
            },
            {
                label: '添加随机列',
                value: 'InsertRandomColNode'
            },
            {
                label: '筛选列',
                value: 'SelectColNode'
            },
            {
                label: '过滤行',
                value: 'FilterNode'
            },
            {
                label: '排序',
                value: 'SortNode'
            },
            {
                label: '分组',
                value: 'GroupNode'
            },
            {
                label: '去重',
                value: 'DropDuplicatesNode'
            },
            {
                label: '删除缺失值',
                value: 'DropNaNValueNode'
            },
            {
                label: '填充缺失值',
                value: 'FillNaNValueNode'
            },
            {
                label: '合并行',
                value: 'MergeNode'
            },
            {
                label: '表格切片',
                value: 'TableSliceNode'
            },
            {
                label: '连接',
                value: 'JoinNode'
            },
            {
                label: '重命名列',
                value: 'RenameColNode'
            },
            {
                label: '移动行',
                value: 'ShiftNode'
            },
        ]
    },
    {
        label: '日期处理',
        value: 'datetimeProcess',
        children: [
            {
                label: '日期偏移',
                value: 'DatetimeComputeNode'
            },
            {
                label: '日期差值',
                value: 'DatetimeDiffNode'
            },
            {
                label: '转为日期',
                value: 'ToDatetimeNode'
            },
            {
                label: '日期解析',
                value: 'StrToDatetimeNode'
            },
            {
                label: '日期格式化',
                value: 'DatetimePrintNode'
            },
            {
                label: '转为时间戳',
                value: 'DatetimeToTimestampNode'
            },
        ]
    },
    {
        label: '分析',
        value: 'analysis',
        children: [
            {
                label: '统计信息',
                value: 'StatsNode'
            },
            {
                label: '差分',
                value: 'DiffNode'
            },
            {
                label: '滑动窗口',
                value: 'RollingNode'
            },
            {
                label: '日期重采样',
                value: 'ResampleNode'
            },
            {
                label: '数据变化率',
                value: 'PctChangeNode'
            },
            {
                label: '累积计算',
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
        label: '机器学习',
        value: 'machineLearning',
        children: [
            {
                label: '线性回归',
                value: 'LinearRegressionNode'
            },
            {
                label: '随机森林回归',
                value: 'RandomForestRegressionNode'
            },
            {
                label: '回归模型评分',
                value: 'RegressionScoreNode'
            },
            {
                label: '逻辑回归分类',
                value: 'LogisticRegressionNode'
            },
            {
                label: '支持向量机分类',
                value: 'SVCNode'
            },
            {
                label: '分类模型评分',
                value: 'ClassificationScoreNode'
            },
            {
                label: 'K-Means聚类',
                value: 'KMeansClusteringNode'
            },
            {
                label: '特征标准化',
                value: 'StandardScalerNode'
            },
            {
                label: '时序滞后特征',
                value: 'LagFeatureNode'
            },
            {
                label: '预测',
                value: 'PredictNode'
            },
        ]
    },
]
