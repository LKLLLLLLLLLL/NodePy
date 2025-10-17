import type {Node} from '@vue-flow/core'


export type FILE = string


// CONST NODE
interface ConstNodeData{
    value: number|string|boolean
    data_type: 'int' | 'float' | 'str' | 'bool'
}
export type ConstNode = Node<ConstNodeData>


interface StringNodeData {
    value: string
}
export type StringNode = Node<StringNodeData>


interface TableNodeData {
    rows: Record<string, number|string|boolean>[]
    columns: string[]
}
export type TableNode = Node<TableNodeData>


// NUMBER OPERATION NODES
const NumBinOpList = ['ADD', 'SUB', 'MUL', 'DIV', 'POW'] as const
interface NumBinComputeNodeData {
    input?: {
        x: number
        y: number
    }
    op: typeof NumBinOpList[number]
    result? : number
}
export type NumBinComputeNode = Node<NumBinComputeNodeData>


const NumUnaryOpList = ['NEG', 'ABS', 'SQRT'] as const
interface NumUnaryComputeNodeData {
    input?: number
    op: typeof NumUnaryOpList[number]
    result?: number
}
export type NumUnaryComputeNode = Node<NumUnaryComputeNodeData>


// COMPARISON NODES
const CmpOpList = ['LT', 'LE', 'EQ', 'NE', 'GE', 'GT'] as const
interface CmpNodeData {
    input?: {
        x: number|string|boolean
        y: number|string|boolean
    }
    op : typeof CmpOpList[number]
    result? : boolean
}
export type CmpNode = Node<CmpNodeData>


const BoolBinOpList = ['AND', 'OR', 'XOR', 'SUB'] as const
interface BoolBinComputeNodeData {
    input?: {
        x: boolean
        y: boolean
    }
    op : typeof BoolBinOpList[number]
    result?: boolean
}
export type BoolBinComputeNode = Node<BoolBinComputeNodeData>


interface BoolNotNodeData {
    input?: boolean
    result?: boolean
}
export type BoolNotNode = Node<BoolNotNodeData>


// CLIP AND SUBSTRING NODES
interface ClipOrSubStringNodeData {
    start?: number
    end?: number
    op: 'CLIP' | 'SUBSTRING'
    input?: string
    result?: string
}
export type ClipOrSubStringNode = Node<ClipOrSubStringNodeData>


interface StripStringNodeData {
    chars?: string
    input?: string
    result?: string
}
export type StripStringNode = Node<StripStringNodeData>


interface ReplaceStringNodeData {
    old: string
    new: string
    input?: string
    result?: string
}
export type ReplaceStringNode = Node<ReplaceStringNodeData>


// UPPER AND LOWER NODES
interface UpperOrLowerStringNodeData {
    op: 'UPPER' | 'LOWER'
    input?: string
    result?: string
}
export type UpperOrLowerStringNode = Node<UpperOrLowerStringNodeData>


// TableAppendStringNode / TablePrependStringNode
interface TableAppendOrPrependStringNodeData {
    column: string
    result_col: string
    op: 'APPEND' | 'PREPEND'
    input?: {
        table_input: TableNodeData
        value_input: string
    }
    result?: TableNodeData
}
export type TableAppendOrPrependStringNode = Node<TableAppendOrPrependStringNodeData>


// TableContainsStringNode / TableStartWithStringNode / TableEndWithStringNode
const StringOneInputMethodList = ['CONTAIN', 'STARTWITH', 'ENDWITH'] as const
interface TableOneInputStringMethodNodeData {
    column: string
    result_col: string
    op: typeof StringOneInputMethodList[number]
    input?: {
        table: TableNodeData
        value_input: string
    }
    result?: TableNodeData
}
export type TableOneInputStringMethodNode = Node<TableOneInputStringMethodNodeData>


interface TableStringLengthNodeData {
    column: string
    result_col: string
    input?: {
        table: TableNodeData
    }
    result?: TableNodeData
}
export type TableStringLengthNode = Node<TableStringLengthNodeData>


interface TableReplaceStringNodeData {
    column: string
    result_col?: string
    input?: {
        table: TableNodeData
        old_value: string
        new_value: string
    }
    result?: TableNodeData
}
export type TableReplaceStringNode = Node<TableReplaceStringNodeData>


interface PlotNodeData {
    x_column: string
    y_column: string
    plot_type: 'scatter' | 'line' | 'bar'
    title?: string
    input?: TableNodeData
    result?: FILE
}
export type PlotNode = Node<PlotNodeData>