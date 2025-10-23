import type {Node} from '@vue-flow/core'
import type { ProjNode } from '@/utils/api'


type AbstractNode = Omit<Node, 'data' | 'type'>

type BaseData = Omit<ProjNode, 'id' | 'type' | 'position'>

interface BaseNode<T = BaseData> extends AbstractNode{
    type: string
    data: T
}


/**************  Generate Nodes ****************/
export interface ConstNodeParam{
    value: number|string|boolean
    data_type: 'int' | 'float' | 'str' | 'bool'
}
export type ConstNodeData = BaseData & {
    param: ConstNodeParam
}
export interface ConstNode extends BaseNode<ConstNodeData>{
    type: 'ConstNode'
}


export interface StringNodeParam {
    value: string
}
export type StringNodeData = BaseData & {
    param: StringNodeParam
}
export interface StringNode extends BaseNode<StringNodeData>{
    type: 'StringNode'
}


export interface TableNodeParam {
    rows: Record<string, number|string|boolean>[]
    col_names: string[]
}
export type TableNodeData = BaseData & {
    param: TableNodeParam
}
export interface TableNode extends BaseNode<TableNodeData>{
    type: 'TableNode'
}


/**************  Compute Nodes  ****************/
const NumBinOpList = ['ADD', 'SUB', 'MUL', 'DIV', 'POW'] as const
export interface NumBinComputeNodeParam {
    op: typeof NumBinOpList[number]
}
export type NumBinComputeNodeData = BaseData & {
    param: NumBinComputeNodeParam
}
export interface NumBinComputeNode extends BaseNode<NumBinComputeNodeData> {
    type: 'NumBinComputeNode'
}


const NumUnaryOpList = ['NEG', 'ABS', 'SQRT'] as const
export interface NumUnaryComputeNodeParam {
    op: typeof NumUnaryOpList[number]
}
export type NumUnaryComputeNodeData = BaseData & {
    param: NumUnaryComputeNodeParam
}
export interface NumUnaryComputeNode extends BaseNode<NumUnaryComputeNodeData>{
    type: 'NumUnaryComputeNode'
}


const CmpOpList = ['LT', 'LE', 'EQ', 'NE', 'GE', 'GT'] as const
export interface CmpNodeParam {
    op : typeof CmpOpList[number]
}
export type CmpNodeData = BaseData & {
    param: CmpNodeParam
}
export interface CmpNode extends BaseNode<CmpNodeData>{
    type: 'CmpNode'
}


const BoolBinOpList = ['AND', 'OR', 'XOR', 'SUB'] as const
export interface BoolBinComputeNodeParam {
    op : typeof BoolBinOpList[number]
}
export type BoolBinComputeNodeData = BaseData & {
    param: BoolBinComputeNodeParam
}
export interface BoolBinComputeNode extends BaseNode<BoolBinComputeNodeData>{
    type: 'BoolBinComputeNode'
}


export interface BoolUnaryComputeNode extends BaseNode{
    type: 'BoolNotNode'
}


// CLIP AND SUBSTRING NODES
// export interface ClipOrSubStringNodeParam {
//     start?: number
//     end?: number
//     op: 'CLIP' | 'SUBSTRING'
//     input?: string
//     result?: string
// }
// export interface ClipOrSubStringNode extends ComputeNode{
//     data: ClipOrSubStringNodeParam
//     type: 'ClipOrSubStringNode'
// }


export interface StripStringNodeParam {
    chars: string
}
export type StripStringNodeData = BaseData & {
    param: StripStringNodeParam
}
export interface StripStringNode extends BaseNode<StripStringNodeData>{
    type: 'StripStringNode'
}


export interface ReplaceStringNodeParam {
    old: string
    new: string
}
export type ReplaceStringNodeData = BaseData & {
    param: StripStringNodeParam
}
export interface ReplaceStringNode extends BaseNode<ReplaceStringNodeData>{
    type: 'ReplaceStringNode'
}


// UPPER AND LOWER NODES
// export interface UpperOrLowerStringNodeParam {
//     op: 'UPPER' | 'LOWER'
//     input?: string
//     result?: string
// }
// export interface UpperOrLowerStringNode extends ComputeNode{
//     data: UpperOrLowerStringNodeParam
//     type: 'UpperOrLowerStringNode'
// }


// TableAppendStringNode / TablePrependStringNode
// export interface TableAppendOrPrependStringNodeParam {
//     column: string
//     result_col: string
//     op: 'APPEND' | 'PREPEND'
//     input: {
//         table_input?: TableNodeParam
//         value_input?: string
//     }
//     result?: TableNodeParam
// }
// export interface TableAppendOrPrependStringNode extends ComputeNode{
//     data: TableAppendOrPrependStringNodeParam
//     type: 'TableAppendOrPrependStringNode'
// }


// TableContainsStringNode / TableStartWithStringNode / TableEndWithStringNode
// const StringOneInputMethodList = ['CONTAIN', 'STARTWITH', 'ENDWITH'] as const
// export interface TableOneInputStringMethodNodeParam {
//     column: string
//     result_col: string
//     op: typeof StringOneInputMethodList[number]
//     input: {
//         table?: TableNodeParam
//         value_input?: string
//     }
//     result?: TableNodeParam
// }
// export interface TableOneInputStringMethodNode extends ComputeNode{
//     data: TableOneInputStringMethodNodeParam
//     type: 'TableOneInputStringMethodNode'
// }


export interface TableStringLengthNodeParam {
    column: string
    result_col?: string
}
export type TableStringLengthNodeData = BaseData & {
    param: StripStringNodeParam
}
export interface TableStringLengthNode extends BaseNode<TableStringLengthNodeData>{
    type: 'TableStringLengthNode'
}


export interface TableReplaceStringNodeParam {
    column: string
    result_col?: string
}
export type TableReplaceStringNodeData = BaseData & {
    param: StripStringNodeParam
}
export interface TableReplaceStringNode extends BaseNode<TableReplaceStringNodeData>{
    type: 'TableReplaceStringNode'
}


/*********************  Visualize Nodes  **************************/
export interface PlotNodeParam {
    x_column: string
    y_column: string
    plot_type: 'scatter' | 'line' | 'bar'
    title?: string
}
export type PlotNodeData = BaseData & {
    param: PlotNodeParam
}
export interface PlotNode extends BaseNode<PlotNodeData>{
    type: 'PlotNode'
}