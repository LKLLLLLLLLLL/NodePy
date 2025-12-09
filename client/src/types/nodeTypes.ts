import type { File, ProjNode, server__models__schema__Schema__Type } from '@/utils/api'
import type { Node } from '@vue-flow/core'


export const dataTypeColor = {
    int: '#1c6bbf',
    float: '#ecbc00',
    str: '#10b981',
    bool: '#77b021',
    Table: 'pink',
    File: '#f97316',
    Datetime: '#00c8ff',
    Model: '#9f03c2',
    default: 'gray'
}

export const nodeCategoryColor = {
    input: '#8b5cf6',
    compute: '#14b8a6',
    control: '#eab308',
    file: dataTypeColor.File,
    str: dataTypeColor.str,
    table: dataTypeColor.Table,
    analysis: '#ef4444',
    visualize: '#6366f1',
    datetime: dataTypeColor.Datetime,
    machine: dataTypeColor.Model,
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
    isNow: boolean
}
export type DateTimeNodeData = BaseData & {
    param: DateTimeNodeParam
}
export interface DateTimeNode extends BaseNode<DateTimeNodeData> {
    type: 'DateTimeNode'
}


export interface KlineNodeParam {
    data_type: 'stock'|'crypto'
    symbol: string
    start_time: string | null
    end_time: string | null
    interval: '1m'|'1h'|'1d'
}
export type KlineNodeData = BaseData & {
    param: KlineNodeParam
}
export interface KlineNode extends BaseNode<KlineNodeData> {
    type: 'KlineNode'
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


export interface ColCompareNodeParam {
    op: typeof CmpOpList[number],
    col1: string,
    col2: string,
    result_col?: string
}
export type ColCompareNodeData = BaseData & {
    param: ColCompareNodeParam
}
export interface ColCompareNode extends BaseNode<ColCompareNodeData>{
    type: 'ColCompareNode'
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


export interface AdvancePlotNodeParam {
    x_col: string
    y_col: string
    hue_col?: string
    plot_type: "bar" | "count" | "scatter" | "strip" | "swarm" | "box" | "violin" | "hist",
    title?: string
}
export type AdvancePlotNodeData = BaseData & {
    param: AdvancePlotNodeParam
}
export interface AdvancePlotNode extends BaseNode<AdvancePlotNodeData>{
    type: 'AdvancePlotNode'
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
    to_case: 'lower'|'upper'
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


export interface RegexMatchNodeParam {
    pattern: string
}
export type RegexMatchNodeData = BaseData & {
    param: RegexMatchNodeParam
}
export interface RegexMatchNode extends BaseNode<RegexMatchNodeData> {
    type: 'RegexMatchNode'
}


export interface BatchRegexMatchNodeParam {
    pattern: string,
    col: string,
    result_col?: string
}
export type BatchRegexMatchNodeData = BaseData & {
    param: BatchRegexMatchNodeParam
}
export interface BatchRegexMatchNode extends BaseNode<BatchRegexMatchNodeData> {
    type: 'BatchRegexMatchNode'
}


export interface RegexExtractNodeParam {
    pattern: string
}
export type RegexExtractNodeData = BaseData & {
    param: RegexExtractNodeParam
}
export interface RegexExtractNode extends BaseNode<RegexExtractNodeData> {
    type: 'RegexExtractNode'
}


export interface TokenizeNodeParam {
    language: "ENGLISH"|"CHINESE"
    delimiter: string | null
    result_col: string | null
}
export type TokenizeNodeData = BaseData & {
    param: TokenizeNodeParam
}
export interface TokenizeNode extends BaseNode<TokenizeNodeData> {
    type: 'TokenizeNode'
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


export interface FillNaNValueNodeParam {
    subset_cols: string[]
    method: "const" | "ffill" | "bfill"
    fill_value?: (number|string|boolean)[]
}
export type FillNaNValueNodeData = BaseData & {
    param: FillNaNValueNodeParam
}
export interface FillNaNValueNode extends BaseNode<FillNaNValueNodeData> {
    type: 'FillNaNValueNode'
}


export interface SortNodeParam {
    sort_col: string
    ascending: boolean
}
export type SortNodeData = BaseData & {
    param: SortNodeParam
}
export interface SortNode extends BaseNode<SortNodeData> {
    type: 'SortNode'
}


export interface GroupNodeParam {
    group_cols: string[]
    agg_cols: string[]
    agg_func: "SUM" | "MEAN" | "COUNT" | "MAX" | "MIN" | "STD"
}
export type GroupNodeData = BaseData & {
    param: GroupNodeParam
}
export interface GroupNode extends BaseNode<GroupNodeData> {
    type: 'GroupNode'
}


export interface MergeNode extends BaseNode {
    type: 'MergeNode'
}


export interface TableSliceNodeParam {
    begin?: number
    end?: number
    step?: number
}
export type TableSliceNodeData = BaseData & {
    param: TableSliceNodeParam
}
export interface TableSliceNode extends BaseNode<TableSliceNodeData> {
    type: 'TableSliceNode'
}


export interface SelectColNodeParam {
    selected_cols: string[]
}
export type SelectColNodeData = BaseData & {
    param: SelectColNodeParam
}
export interface SelectColNode extends BaseNode<SelectColNodeData> {
    type: 'SelectColNode'
}


export interface JoinNodeParam {
    left_on: string
    right_on: string
    how: "INNER" | "LEFT" | "RIGHT" | "OUTER"
}
export type JoinNodeData = BaseData & {
    param: JoinNodeParam
}
export interface JoinNode extends BaseNode<JoinNodeData> {
    type: 'JoinNode'
}


export interface RenameColNodeParam {
    rename_map: Record<string, string>
}
export type RenameColNodeData = BaseData & {
    param: RenameColNodeParam
}
export interface RenameColNode extends BaseNode<RenameColNodeData> {
    type: 'RenameColNode'
}


export interface ShiftNodeParam {
    col: string
    periods: number
    result_col?: string
}
export type ShiftNodeData = BaseData & {
    param: ShiftNodeParam
}
export interface ShiftNode extends BaseNode<ShiftNodeData> {
    type: 'ShiftNode'
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


export interface TableFromFileNode extends BaseNode {
    type: 'TableFromFileNode'
}


export interface TableToFileNodeParam {
    filename?: string
    format: "csv" | "xlsx" | "json"
}
export type TableToFileNodeData = BaseData & {
    param: TableToFileNodeParam
}
export interface TableToFileNode extends BaseNode<TableToFileNodeData> {
    type: 'TableToFileNode'
}


export interface TextFromFileNode extends BaseNode {
    type: 'TextFromFileNode'
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


/*********************  Analysis Nodes  **************************/
export interface StatsNodeParam {
    col: string
}
export type StatsNodeData = BaseData & {
    param: StatsNodeParam
}
export interface StatsNode extends BaseNode<StatsNodeData> {
    type: 'StatsNode'
}


export interface DiffNodeParam {
    col: string
}
export type DiffNodeData = BaseData & {
    param: DiffNodeParam
}
export interface DiffNode extends BaseNode<DiffNodeData> {
    type: 'DiffNode'
}


export interface RollingNodeParam {
    col: string
    window_size: number
    min_periods: number
    result_col?: string
    method: "mean" | "std" | "sum" | "min" | "max"
}
export type RollingNodeData = BaseData & {
    param: RollingNodeParam
}
export interface RollingNode extends BaseNode<RollingNodeData> {
    type: 'RollingNode'
}


export interface ResampleNodeParam {
    col: string
    frequency: "D" | "H" | "T" | "S"
    method: "mean" | "sum" | "max" | "min" | "count"
    result_col?: string
}
export type ResampleNodeData = BaseData & {
    param: ResampleNodeParam
}
export interface ResampleNode extends BaseNode<ResampleNodeData> {
    type: 'ResampleNode'
}


export interface PctChangeNodeParam {
    col: string
    result_col?: string
}
export type PctChangeNodeData = BaseData & {
    param: PctChangeNodeParam
}
export interface PctChangeNode extends BaseNode<PctChangeNodeData> {
    type: 'PctChangeNode'
}


export interface CumulativeNodeParam {
    col: string
    result_col?: string
    method: "cumsum" | "cumprod" | "cummax" | "cummin"
}
export type CumulativeNodeData = BaseData & {
    param: CumulativeNodeParam
}
export interface CumulativeNode extends BaseNode<CumulativeNodeData> {
    type: 'CumulativeNode'
}

/*********************  Control Nodes  **************************/
export interface CustomScriptNodeParam {
    input_ports: Array<Record<string, server__models__schema__Schema__Type>>
    output_ports: Array<Record<string, server__models__schema__Schema__Type>>
    script: string
}
export type CustomScriptNodeData = BaseData & {
    param: CustomScriptNodeParam
}
export interface CustomScriptNode extends BaseNode<CustomScriptNodeData> {
    type: 'CustomScriptNode'
}


export interface ForEachRowBeginNode extends BaseNode {
    type: 'ForEachRowBeginNode'
}


export interface ForEachRowEndNode extends BaseNode {
    type: 'ForEachRowEndNode'
}


export interface ForRollingWindowBeginNode extends BaseNode {
    type: 'ForRollingWindowBeginNode'
}


export interface ForRollingWindowEndNode extends BaseNode {
    type: 'ForRollingWindowEndNode'
}


export interface UnpackNodeParam {
    cols: string[]
}
export type UnpackNodeData = BaseData & {
    param: UnpackNodeParam
}
export interface UnpackNode extends BaseNode<UnpackNodeData> {
    type: 'UnpackNode'
}


export interface PackNodeParam {
    cols: string[]
}
export type PackNodeData = BaseData & {
    param: PackNodeParam
}
export interface PackNode extends BaseNode<PackNodeData> {
    type: 'PackNode'
}


export interface GetCellNodeParam {
    col: string
    row: number
}
export type GetCellNodeData = BaseData & {
    param: GetCellNodeParam
}
export interface GetCellNode extends BaseNode<GetCellNodeData> {
    type: 'GetCellNode'
}


export interface SetCellNodeParam {
    col: string
    row: number
}
export type SetCellNodeData = BaseData & {
    param: SetCellNodeParam
}
export interface SetCellNode extends BaseNode<SetCellNodeData> {
    type: 'SetCellNode'
}



/*********************  MachineLearning Nodes  **************************/
export interface LinearRegressionNodeParam {
    feature_cols: string[]
    target_col: string
}
export type LinearRegressionNodeData = BaseData & {
    param: LinearRegressionNodeParam
}
export interface LinearRegressionNode extends BaseNode<LinearRegressionNodeData> {
    type: 'LinearRegressionNode'
}


export interface PredictNode extends BaseNode {
    type: 'PredictNode'
}


export interface LagFeatureNodeParam {
    window_size: number
    horizon: number
    lag_cols: string[]
    target_col: string
    generate_target: boolean
    drop_nan: boolean
}
export type LagFeatureNodeData = BaseData & {
    param: LagFeatureNodeParam
}
export interface LagFeatureNode extends BaseNode<LagFeatureNodeData> {
    type: 'LagFeatureNode'
}


export interface RandomForestRegressionNodeParam {
    n_estimators: number
    max_depth: number
    feature_cols: string[]
    target_col: string
    limit_max_depth: boolean
}
export type RandomForestRegressionNodeData = BaseData & {
    param: RandomForestRegressionNodeParam
}
export interface RandomForestRegressionNode extends BaseNode<RandomForestRegressionNodeData> {
    type: 'RandomForestRegressionNode'
}


export interface RegressionScoreNodeParam {
    metric: "mse" | "rmse" | "mae" | "r2"
}
export type RegressionScoreNodeData = BaseData & {
    param: RegressionScoreNodeParam
}
export interface RegressionScoreNode extends BaseNode<RegressionScoreNodeData> {
    type: 'RegressionScoreNode'
}


export interface LogisticRegressionNodeParam {
    feature_cols: string[]
    target_col: string
}
export type LogisticRegressionNodeData = BaseData & {
    param: LogisticRegressionNodeParam
}
export interface LogisticRegressionNode extends BaseNode<LogisticRegressionNodeData> {
    type: 'LogisticRegressionNode'
}


export interface SVCNodeParam {
    feature_cols: string[]
    target_col: string
    kernel: "linear" | "poly" | "rbf" | "sigmoid"
}
export type SVCNodeData = BaseData & {
    param: SVCNodeParam
}
export interface SVCNode extends BaseNode<SVCNodeData> {
    type: 'SVCNode'
}


export interface ClassificationScoreNodeParam {
    metric: "accuracy" | "f1" | "precision" | "recall"
}
export type ClassificationScoreNodeData = BaseData & {
    param: ClassificationScoreNodeParam
}
export interface ClassificationScoreNode extends BaseNode<ClassificationScoreNodeData> {
    type: 'ClassificationScoreNode'
}
