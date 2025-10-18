import type {Node} from '@vue-flow/core'


type BaseNode = Omit<Node, 'data' | 'type'>


export type FILE = string


// CONST NODE
export interface ConstNodeData{
    value: number|string|boolean
    data_type: 'int' | 'float' | 'str' | 'bool'
}
export interface ConstNode extends BaseNode{
    type: 'ConstNode'
    data: ConstNodeData
}


export interface StringNodeData {
    value: string
}
export interface StringNode extends BaseNode{
    data: StringNodeData
    type: 'StringNode'
}


export interface TableNodeData {
    rows: Record<string, number|string|boolean>[]
    columns: string[]
}
export interface TableNode extends BaseNode{
    data: TableNodeData
    type: 'TableNode'
}


// NUMBER OPERATION NODES
const NumBinOpList = ['ADD', 'SUB', 'MUL', 'DIV', 'POW'] as const
export interface NumBinComputeNodeData {
    input?: {
        x: number
        y: number
    }
    op: typeof NumBinOpList[number]
    result? : number
}
export interface NumBinComputeNode extends BaseNode{
    data: NumBinComputeNodeData
    type: 'NumBinComputeNode'
}


const NumUnaryOpList = ['NEG', 'ABS', 'SQRT'] as const
export interface NumUnaryComputeNodeData {
    input?: number
    op: typeof NumUnaryOpList[number]
    result?: number
}
export interface NumUnaryComputeNode extends BaseNode{
    data: NumUnaryComputeNodeData
    type: 'NumUnaryComputeNode'
}


// COMPARISON NODES
const CmpOpList = ['LT', 'LE', 'EQ', 'NE', 'GE', 'GT'] as const
export interface CmpNodeData {
    input?: {
        x: number|string|boolean
        y: number|string|boolean
    }
    op : typeof CmpOpList[number]
    result? : boolean
}
export interface CmpNode extends BaseNode{
    data: CmpNodeData
    type: 'CmpNode'
}


const BoolBinOpList = ['AND', 'OR', 'XOR', 'SUB'] as const
export interface BoolBinComputeNodeData {
    input?: {
        x: boolean
        y: boolean
    }
    op : typeof BoolBinOpList[number]
    result?: boolean
}
export interface BoolBinComputeNode extends BaseNode{
    data: BoolBinComputeNodeData
    type: 'BoolBinComputeNode'
}


export interface BoolNotNodeData {
    input?: boolean
    result?: boolean
}
export interface BoolNotNode extends BaseNode{
    data: BoolNotNodeData
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
export interface ClipOrSubStringNode extends BaseNode{
    data: ClipOrSubStringNodeData
    type: 'ClipOrSubStringNode'
}


export interface StripStringNodeData {
    chars?: string
    input?: string
    result?: string
}
export interface StripStringNode extends BaseNode{
    data: StripStringNodeData
    type: 'StripStringNode'
}


export interface ReplaceStringNodeData {
    old: string
    new: string
    input?: string
    result?: string
}
export interface ReplaceStringNode extends BaseNode{
    data: ReplaceStringNodeData
    type: 'ReplaceStringNode'
}


// UPPER AND LOWER NODES
export interface UpperOrLowerStringNodeData {
    op: 'UPPER' | 'LOWER'
    input?: string
    result?: string
}
export interface UpperOrLowerStringNode extends BaseNode{
    data: UpperOrLowerStringNodeData
    type: 'UpperOrLowerStringNode'
}


// TableAppendStringNode / TablePrependStringNode
export interface TableAppendOrPrependStringNodeData {
    column: string
    result_col: string
    op: 'APPEND' | 'PREPEND'
    input?: {
        table_input: TableNodeData
        value_input: string
    }
    result?: TableNodeData
}
export interface TableAppendOrPrependStringNode extends BaseNode{
    data: TableAppendOrPrependStringNodeData
    type: 'TableAppendOrPrependStringNode'
}


// TableContainsStringNode / TableStartWithStringNode / TableEndWithStringNode
const StringOneInputMethodList = ['CONTAIN', 'STARTWITH', 'ENDWITH'] as const
export interface TableOneInputStringMethodNodeData {
    column: string
    result_col: string
    op: typeof StringOneInputMethodList[number]
    input?: {
        table: TableNodeData
        value_input: string
    }
    result?: TableNodeData
}
export interface TableOneInputStringMethodNode extends BaseNode{
    data: TableOneInputStringMethodNodeData
    type: 'TableOneInputStringMethodNode'
}


export interface TableStringLengthNodeData {
    column: string
    result_col: string
    input?: {
        table: TableNodeData
    }
    result?: TableNodeData
}
export interface TableStringLengthNode extends BaseNode{
    data: TableStringLengthNodeData
    type: 'TableStringLengthNode'
}


export interface TableReplaceStringNodeData {
    column: string
    result_col?: string
    input?: {
        table: TableNodeData
        old_value: string
        new_value: string
    }
    result?: TableNodeData
}
export interface TableReplaceStringNode extends BaseNode{
    data: TableReplaceStringNodeData
    type: 'TableReplaceStringNode'
}


export interface PlotNodeData {
    x_column: string
    y_column: string
    plot_type: 'scatter' | 'line' | 'bar'
    title?: string
    input?: TableNodeData
    result?: FILE
}
export interface PlotNode extends BaseNode{
    data: PlotNodeData
    type: 'PlotNode'
}