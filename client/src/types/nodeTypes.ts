import type {Node} from '@vue-flow/core'


type BaseNode = Omit<Node, 'data' | 'type'>

interface GenerateNode extends BaseNode {}

interface ComputeNode extends BaseNode {
    timerStatus: 'begin' | 'end' | 'inactive'
    exTime?: string
}

interface VisualizeNode extends BaseNode {}

/**************  Generate Nodes ****************/
export interface ConstNodeData{
    value: number|string|boolean
    data_type: 'int' | 'float' | 'str' | 'bool'
}
export interface ConstNode extends GenerateNode{
    type: 'ConstNode'
    data: ConstNodeData
}


export interface StringNodeData {
    value: string
}
export interface StringNode extends GenerateNode{
    data: StringNodeData
    type: 'StringNode'
}


export interface TableNodeData {
    rows: Record<string, number|string|boolean>[]
    col_names: string[]
}
export interface TableNode extends GenerateNode{
    data: TableNodeData
    type: 'TableNode'
}


/**************  Compute Nodes  ****************/
const NumBinOpList = ['ADD', 'SUB', 'MUL', 'DIV', 'POW'] as const
export interface NumBinComputeNodeData {
    op: typeof NumBinOpList[number]
}
export interface NumBinComputeNode extends ComputeNode {
    data: NumBinComputeNodeData
    type: 'NumBinComputeNode'
}


const NumUnaryOpList = ['NEG', 'ABS', 'SQRT'] as const
export interface NumUnaryComputeNodeData {
    op: typeof NumUnaryOpList[number]
}
export interface NumUnaryComputeNode extends ComputeNode{
    data: NumUnaryComputeNodeData
    type: 'NumUnaryComputeNode'
}


const CmpOpList = ['LT', 'LE', 'EQ', 'NE', 'GE', 'GT'] as const
export interface CmpNodeData {
    op : typeof CmpOpList[number]
}
export interface CmpNode extends ComputeNode{
    data: CmpNodeData
    type: 'CmpNode'
}


const BoolBinOpList = ['AND', 'OR', 'XOR', 'SUB'] as const
export interface BoolBinComputeNodeData {
    op : typeof BoolBinOpList[number]
}
export interface BoolBinComputeNode extends ComputeNode{
    data: BoolBinComputeNodeData
    type: 'BoolBinComputeNode'
}


export interface BoolUnaryComputeNode extends ComputeNode{
    type: 'BoolNotNode'
}


// CLIP AND SUBSTRING NODES
export interface ClipOrSubStringNodeData {
    start?: number
    end?: number
    op: 'CLIP' | 'SUBSTRING'
    input?: string
    result?: string
}
export interface ClipOrSubStringNode extends ComputeNode{
    data: ClipOrSubStringNodeData
    type: 'ClipOrSubStringNode'
}


export interface StripStringNodeData {
    chars: string
}
export interface StripStringNode extends ComputeNode{
    data: StripStringNodeData
    type: 'StripStringNode'
}


export interface ReplaceStringNodeData {
    old: string
    new: string
}
export interface ReplaceStringNode extends ComputeNode{
    data: ReplaceStringNodeData
    type: 'ReplaceStringNode'
}


// UPPER AND LOWER NODES
export interface UpperOrLowerStringNodeData {
    op: 'UPPER' | 'LOWER'
    input?: string
    result?: string
}
export interface UpperOrLowerStringNode extends ComputeNode{
    data: UpperOrLowerStringNodeData
    type: 'UpperOrLowerStringNode'
}


// TableAppendStringNode / TablePrependStringNode
export interface TableAppendOrPrependStringNodeData {
    column: string
    result_col: string
    op: 'APPEND' | 'PREPEND'
    input: {
        table_input?: TableNodeData
        value_input?: string
    }
    result?: TableNodeData
}
export interface TableAppendOrPrependStringNode extends ComputeNode{
    data: TableAppendOrPrependStringNodeData
    type: 'TableAppendOrPrependStringNode'
}


// TableContainsStringNode / TableStartWithStringNode / TableEndWithStringNode
const StringOneInputMethodList = ['CONTAIN', 'STARTWITH', 'ENDWITH'] as const
export interface TableOneInputStringMethodNodeData {
    column: string
    result_col: string
    op: typeof StringOneInputMethodList[number]
    input: {
        table?: TableNodeData
        value_input?: string
    }
    result?: TableNodeData
}
export interface TableOneInputStringMethodNode extends ComputeNode{
    data: TableOneInputStringMethodNodeData
    type: 'TableOneInputStringMethodNode'
}


export interface TableStringLengthNodeData {
    column: string
    result_col?: string
}
export interface TableStringLengthNode extends ComputeNode{
    data: TableStringLengthNodeData
    type: 'TableStringLengthNode'
}


export interface TableReplaceStringNodeData {
    column: string
    result_col?: string
}
export interface TableReplaceStringNode extends ComputeNode{
    data: TableReplaceStringNodeData
    type: 'TableReplaceStringNode'
}


/*********************  Visualize Nodes  **************************/
export interface PlotNodeData {
    x_column: string
    y_column: string
    plot_type: 'scatter' | 'line' | 'bar'
    title?: string
}
export interface PlotNode extends VisualizeNode{
    data: PlotNodeData
    type: 'PlotNode'
}