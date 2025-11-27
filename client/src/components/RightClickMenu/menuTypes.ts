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
                label: '常量节点',
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
                label: '日期时间输入节点',
                value: 'DateTimeNode'
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
        children: []
    },
    {
        label: '表格处理节点',
        value: 'tableProcessing',
        children: []
    },
    {
        label: '工具节点',
        value: 'utility',
        children: []
    },
    {
        label: '可视化节点',
        value: 'visualization',
        children: [
            {
                label: '绘图节点',
                value: 'PlotNode'
            }
        ]
    }
]
