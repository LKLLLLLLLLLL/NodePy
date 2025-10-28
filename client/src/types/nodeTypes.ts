import type {Node} from '@vue-flow/core'
import type { ProjNode, File } from '@/utils/api'


export type AbstractNode = Omit<Node, 'data' | 'type'>

export type BaseData = Omit<ProjNode, 'id' | 'type' | 'position'>

export interface BaseNode<T = BaseData> extends AbstractNode{
    type: string
    data: T
}


/**************  Generate Nodes ****************/
export interface ConstNodeParam{
    value: number
    data_type: 'int' | 'float'
}
export type ConstNodeData = BaseData & {
    param: ConstNodeParam
}
export interface ConstNode extends BaseNode<ConstNodeData>{
    type: 'ConstNode'
}


export interface BoolNodeParam{
    value: boolean
}
export type BoolNodeData = BaseData & {
    param: BoolNodeParam
}
export interface BoolNode extends BaseNode<BoolNodeData>{
    type: 'BoolNode'
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


export interface TableFromCSVNodeParam {}
export type TableFromCSVNodeData = BaseData & {
    param: TableFromCSVNodeParam
}
export interface TableFromCSVNode extends BaseNode<TableFromCSVNodeData>{
    type: 'TableFromCSVNode'
}


/**************  Compute Nodes  ****************/
export const NumBinOpList = ['ADD', 'SUB', 'MUL', 'DIV', 'POW'] as const
export interface NumberBinOpNodeParam {
    op: typeof NumBinOpList[number]
}
export type NumberBinOpNodeData = BaseData & {
    param: NumberBinOpNodeParam
}
export interface NumberBinOpNode extends BaseNode<NumberBinOpNodeData> {
    type: 'NumberBinOpNode'
}


export const NumUnaryOpList = ['NEG', 'ABS', 'SQRT'] as const
export interface NumberUnaryOpNodeParam {
    op: typeof NumUnaryOpList[number]
}
export type NumberUnaryOpNodeData = BaseData & {
    param: NumberUnaryOpNodeParam
}
export interface NumberUnaryOpNode extends BaseNode<NumberUnaryOpNodeData>{
    type: 'NumberUnaryOpNode'
}


export const CmpOpList = ['LT', 'LE', 'EQ', 'NE', 'GE', 'GT'] as const
export interface PrimitiveCompareNodeParam {
    op : typeof CmpOpList[number]
}
export type PrimitiveCompareNodeData = BaseData & {
    param: PrimitiveCompareNodeParam
}
export interface PrimitiveCompareNode extends BaseNode<PrimitiveCompareNodeData>{
    type: 'PrimitiveCompareNode'
}


export const BoolBinOpList = ['AND', 'OR', 'XOR', 'SUB'] as const
export interface BoolBinOpNodeParam {
    op : typeof BoolBinOpList[number]
}
export type BoolBinOpNodeData = BaseData & {
    param: BoolBinOpNodeParam
}
export interface BoolBinOpNode extends BaseNode<BoolBinOpNodeData>{
    type: 'BoolBinOpNode'
}

export interface BoolUnaryOpNodeParam {
    op: 'NOT'
}
export type BoolUnaryOpNodeData = BaseData & {
    param: BoolUnaryOpNodeParam
}
export interface BoolUnaryOpNode extends BaseNode{
    type: 'BoolNotNode'
}


export const ColWithNumberBinOpList = ['ADD', 'COL_SUB_NUM', 'NUM_SUB_COL', 'MUL', 'COL_DIV_NUM', 'NUM_DIV_COL', 'COL_POW_NUM', 'NUM_POW_COL'] as const
export interface ColWithNumberBinOpNodeParam {
    op: typeof ColWithNumberBinOpList[number],
    col: string,
    result_col?: string
}
export type ColWithNumberBinOpNodeData = BaseData & {
    param: ColWithNumberBinOpNodeParam
}
export interface ColWithNumberBinOpNode extends BaseNode<ColWithNumberBinOpNodeData>{
    type: 'ColWithNumberBinOpNode'
}


export const ColWithBoolBinOpList = ['AND', 'OR', 'XOR', 'NUM_SUB_COL', 'COL_SUB_NUM'] as const
export interface ColWithBoolBinOpNodeParam {
    op: typeof ColWithBoolBinOpList[number],
    col: string,
    result_col?: string
}
export type ColWithBoolBinOpNodeData = BaseData & {
    param: ColWithBoolBinOpNodeParam
}
export interface ColWithBoolBinOpNode extends BaseNode<ColWithBoolBinOpNodeData>{
    type: 'ColWithBoolBinOpNode'
}


export const NumberColUnaryOpList = ['ABS', 'NEG', 'EXP', 'LOG', 'SQRT'] as const
export interface NumberColUnaryOpNodeParam {
    op: typeof NumberColUnaryOpList[number],
    col: string,
    result_col?: string
}
export type NumberColUnaryOpNodeData = BaseData & {
    param: NumberColUnaryOpNodeParam
}
export interface NumberColUnaryOpNode extends BaseNode<NumberColUnaryOpNodeData>{
    type: 'NumberColUnaryOpNode'
}


export interface BoolColUnaryOpNodeParam {
    op: 'NOT'
    col: string
    result_col?: string
}
export type BoolColUnaryOpNodeData = BaseData & {
    param: BoolColUnaryOpNodeParam
}
export interface BoolColUnaryOpNode extends BaseNode<BoolColUnaryOpNodeData>{
    type: 'BoolColUnaryOpNode'
}


export const NumberColWithColBinOpList = NumBinOpList
export interface NumberColWithColBinOpNodeParam {
    op: typeof NumberColWithColBinOpList[number],
    col1: string,
    col2: string,
    result_col?: string
}
export type NumberColWithColBinOpNodeData = BaseData & {
    param: NumberColWithColBinOpNodeParam
}
export interface NumberColWithColBinOpNode extends BaseNode<NumberColWithColBinOpNodeData>{
    type: 'NumberColWithColBinOpNode'
}


export const BoolColWithColBinOpList = BoolBinOpList
export interface BoolColWithColBinOpNodeParam {
    op: typeof BoolColWithColBinOpList[number],
    col1: string,
    col2: string,
    result_col?: string
}
export type BoolColWithColBinOpNodeData = BaseData & {
    param: BoolColWithColBinOpNodeParam
}
export interface BoolColWithColBinOpNode extends BaseNode<BoolColWithColBinOpNodeData>{
    type: 'BoolColWithColBinOpNode'
}


/*********************  Visualize Nodes  **************************/
export interface PlotNodeParam {
    x_col: string
    y_col: string
    plot_type: 'scatter' | 'line' | 'bar'
    title?: string
}
export type PlotNodeData = BaseData & {
    param: PlotNodeParam
}
export interface PlotNode extends BaseNode<PlotNodeData>{
    type: 'PlotNode'
}


/*********************  StringProcess Nodes  **************************/


/*********************  TableProcess Nodes  **************************/


/*********************  File Nodes  **************************/
export interface UploadNodeParam {
    file: File
}
export type UploadNodeData = BaseData & {
    param: UploadNodeParam
}
export interface UploadNode extends BaseNode<UploadNodeData>{
    type: 'UploadNode'
}


export interface DisplayNodeParam {}
export type DisplayNodeData = BaseData & {
    param: DisplayNodeParam
}
export interface DisplayNode extends BaseNode<DisplayNodeData>{
    type: 'DisplayNode'
}