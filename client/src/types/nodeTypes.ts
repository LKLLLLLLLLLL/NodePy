import type {Node} from '@vue-flow/core'
import type { ProjNode, File } from '@/utils/api'


export const dataTypeColor = {
    int: '#1c6bbf',
    float: '#ecbc00',
    str: 'green',
    bool: '#76ab0b',
    Table: 'pink',
    File: 'rgb(216, 105, 91)',
    Datetime: '#00c8ff',
    default: 'gray'
}

export const nodeCategoryColor = {
    input: 'rgb(255, 102, 255)',
    compute: '#00b688',
    control: '#d87e00',
    file: dataTypeColor.File,
    str: dataTypeColor.str,
    table: dataTypeColor.Table,
    utils: 'rgb(183, 0, 70)',
    visualize: '#7572d2',
    datetime: dataTypeColor.Datetime,
    default: 'gray'
}


export type AbstractNode = Omit<Node, 'data' | 'type'>

export type BaseData = Omit<ProjNode, 'id' | 'type' | 'position'> & {
    dbclicked?: boolean
}

export interface BaseNode<T = BaseData> extends AbstractNode{
    type: string
    data: T
}


/**************  Input Nodes ****************/
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


export interface TableFromFileNode extends BaseNode {
    type: 'TableFromFileNode'
}


export interface RandomNodeParam {
    col_name: string,
    col_type: 'int'|'float'|'str'|'bool'
}
export type RandomNodeData = BaseData & {
    param: RandomNodeParam
}
export interface RandomNode extends BaseNode<RandomNodeData> {
    type: 'RandomNode'
}


export interface RangeNodeParam {
    col_name: string,
    col_type: 'int'|'float'|'Datetime'
}
export type RangeNodeData = BaseData & {
    param: RangeNodeParam
}
export interface RangeNode extends BaseNode<RangeNodeData> {
    type: 'RangeNode'
}


export interface DateTimeNodeParam {
    value: string
}
export type DateTimeNodeData = BaseData & {
    param: DateTimeNodeParam
}
export interface DateTimeNode extends BaseNode<DateTimeNodeData> {
    type: 'DateTimeNode'
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


export const CmpOpList = ['LT', 'LTE', 'EQ', 'NEQ', 'GTE', 'GT'] as const
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
export interface BoolUnaryOpNode extends BaseNode<BoolUnaryOpNodeData>{
    type: 'BoolUnaryOpNode'
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


export interface ToStringNode extends BaseNode {
    type: 'ToStringNode'
}


export interface ToIntNodeParam {
    method: 'FLOOR'|'CEIL'|'ROUND'
}
export type ToIntNodeData = BaseData & {
    param: ToIntNodeParam
}
export interface ToIntNode extends BaseNode<ToIntNodeData> {
    type: 'ToIntNode'
}


export interface ToFloatNode extends BaseNode {
    type: 'ToFloatNode'
}


export interface ToBoolNode extends BaseNode {
    type: 'ToBoolNode'
}


/*********************  Visualize Nodes  **************************/
export interface PlotNodeParam {
    x_col: string
    y_col: string
    plot_type: 'scatter' | 'line' | 'bar' | 'pie'
    title?: string
}
export type PlotNodeData = BaseData & {
    param: PlotNodeParam
}
export interface PlotNode extends BaseNode<PlotNodeData>{
    type: 'PlotNode'
}


export interface WordcloudNodeParam {
    word_col: string
    frequency_col: string
}
export type WordcloudNodeData = BaseData & {
    param: WordcloudNodeParam
}
export interface WordcloudNode extends BaseNode<WordcloudNodeData> {
    type: 'WordcloudNode'
}


/*********************  StringProcess Nodes  **************************/
export interface StripNodeParam {
    strip_chars?: string
}
export type StripNodeData = BaseData & {
    param: StripNodeParam
}
export interface StripNode extends BaseNode<StripNodeData> {
    type: 'StripNode'
}


export interface SliceNodeParam {
    start?: number
    end?: number
}
export type SliceNodeData = BaseData & {
    param: SliceNodeParam
}
export interface SliceNode extends BaseNode<SliceNodeData> {
    type: 'SliceNode'
}


export interface ReplaceNodeParam {
    old: string
    new: string
}
export type ReplaceNodeData = BaseData & {
    param: ReplaceNodeParam
}
export interface ReplaceNode extends BaseNode<ReplaceNodeData> {
    type: 'ReplaceNode'
}


export interface LowerOrUpperNodeParam {
    to_case: string
}
export type LowerOrUpperNodeData = BaseData & {
    param: LowerOrUpperNodeParam
}
export interface LowerOrUpperNode extends BaseNode<LowerOrUpperNodeData> {
    type: 'LowerOrUpperNode'
}


export interface ConcatNode extends BaseNode {
    type: 'ConcatNode'
}


export interface BatchStripNodeParam {
    strip_chars?: string
    col: string
    result_col?: string
}
export type BatchStripNodeData = BaseData & {
    param: BatchStripNodeParam
}
export interface BatchStripNode extends BaseNode<BatchStripNodeData> {
    type: 'BatchStripNode'
}


export interface BatchConcatNodeParam {
    col1: string
    col2: string
    result_col?: string
}
export type BatchConcatNodeData = BaseData & {
    param: BatchConcatNodeParam
}
export interface BatchConcatNode extends BaseNode<BatchConcatNodeData> {
    type: 'BatchConcatNode'
}


/*********************  TableProcess Nodes  **************************/
export interface InsertConstColNodeParam {
    col_name: string,
    col_type: 'int'|'float'|'bool'|'str'|'Datetime'
}
export type InsertConstColNodeData = BaseData & {
    param: InsertConstColNodeParam
}
export interface InsertConstColNode extends BaseNode<InsertConstColNodeData> {
    type: 'InsertConstColNode'
}


export interface InsertRangeColNodeParam {
    col_name: string,
    col_type: 'int'|'float'|'Datetime'
}
export type InsertRangeColNodeData = BaseData & {
    param: InsertRangeColNodeParam
}
export interface InsertRangeColNode extends BaseNode<InsertRangeColNodeData> {
    type: 'InsertRangeColNode'
}


export interface InsertRandomColNodeParam {
    col_name: string,
    col_type: 'int'|'float'
}
export type InsertRandomColNodeData = BaseData & {
    param: InsertRandomColNodeParam
}
export interface InsertRandomColNode extends BaseNode<InsertRandomColNodeData> {
    type: 'InsertRandomColNode'
}


export interface FilterNodeParam {
    cond_col: string
}
export type FilterNodeData = BaseData & {
    param: FilterNodeParam
}
export interface FilterNode extends BaseNode<FilterNodeData> {
    type: 'FilterNode'
}


export interface DropDuplicatesNodeParam {
    subset_cols: string[]
}
export type DropDuplicatesNodeData = BaseData & {
    param: DropDuplicatesNodeParam
}
export interface DropDuplicatesNode extends BaseNode<DropDuplicatesNodeData> {
    type: 'DropDuplicatesNode'
}


export interface DropNaNValueNodeParam {
    subset_cols: string[]
}
export type DropNaNValueNodeData = BaseData & {
    param: DropNaNValueNodeParam
}
export interface DropNaNValueNode extends BaseNode<DropNaNValueNodeData> {
    type: 'DropNaNValueNode'
}


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


export interface DisplayNode extends BaseNode {
    type: 'DisplayNode'
}


/*********************  DatetimeProcess Nodes  **************************/
export interface DatetimeComputeNodeParam {
    op: 'ADD'|'SUB'
    unit: 'DAYS'|'HOURS'|'MINUTES'|'SECONDS'
}
export type DatetimeComputeNodeData = BaseData & {
    param: DatetimeComputeNodeParam
}
export interface DatetimeComputeNode extends BaseNode<DatetimeComputeNodeData> {
    type: 'DatetimeComputeNode'
}


export interface DatetimeDiffNodeParam {
    unit: 'DAYS'|'HOURS'|'MINUTES'|'SECONDS'
}
export type DatetimeDiffNodeData = BaseData & {
    param: DatetimeDiffNodeParam
}
export interface DatetimeDiffNode extends BaseNode<DatetimeDiffNodeData> {
    type: 'DatetimeDiffNode'
}


export interface ToDatetimeNodeParam {
    unit: 'DAYS'|'HOURS'|'MINUTES'|'SECONDS'
}
export type ToDatetimeNodeData = BaseData & {
    param: ToDatetimeNodeParam
}
export interface ToDatetimeNode extends BaseNode<ToDatetimeNodeData> {
    type: 'ToDatetimeNode'
}


export interface StrToDatetimeNode extends BaseNode {
    type: 'StrToDatetimeNode'
}


export interface DatetimePrintNodeParam {
    format: string
}
export type DatetimePrintNodeData = BaseData & {
    param: DatetimePrintNodeParam
}
export interface DatetimePrintNode extends BaseNode<DatetimePrintNodeData> {
    type: 'DatetimePrintNode'
}


export interface DatetimeToTimestampNodeParam {
    unit: 'DAYS'|'HOURS'|'MINUTES'|'SECONDS'
}
export type DatetimeToTimestampNodeData = BaseData & {
    param: DatetimeToTimestampNodeParam
}
export interface DatetimeToTimestampNode extends BaseNode<DatetimeToTimestampNodeData> {
    type: 'DatetimeToTimestampNode'
}


/*********************  Utility Nodes  **************************/

/*********************  Control Nodes  **************************/
