export interface MenuNode {
    label: string;
    value: string;
    children?: MenuNode[];
}

export const nodeMenuItems: MenuNode[] = [
    {
        label: '基础节点',
        value: 'basic',
        children: [
            {
                label: '常量',
                value: 'constant',
                children: [
                    {
                        label: '数值常量',
                        value: 'ConstNode'
                    },
                    {
                        label: '字符串常量',
                        value: 'StringNode'
                    }
                ]
            },
            {
                label: '表格',
                value: 'table',
                children: [
                    {
                        label: '表格节点',
                        value: 'TableNode'
                    }
                ]
            }
        ]
    },
    {
        label: '运算节点',
        value: 'compute',
        children: [
            {
                label: '数值运算',
                value: 'number',
                children: [
                    {
                        label: '二元运算',
                        value: 'NumBinComputeNode'
                    },
                    {
                        label: '一元运算',
                        value: 'NumUnaryComputeNode'
                    }
                ]
            },
            {
                label: '布尔运算',
                value: 'boolean',
                children: [
                    {
                        label: '比较运算',
                        value: 'CmpNode'
                    },
                    {
                        label: '布尔二元运算',
                        value: 'BoolBinComputeNode'
                    },
                    {
                        label: '布尔非运算',
                        value: 'BoolNotNode'
                    }
                ]
            }
        ]
    }
]