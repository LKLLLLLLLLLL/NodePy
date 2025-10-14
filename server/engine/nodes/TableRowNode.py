from .BaseNode import BaseNode, NodeValidationError, InPort, OutPort, Data, Schema
from .Utils import INDEX_COLUMN_NAME, Visualization, CmpCondition
from pandas import DataFrame
from typing import Literal
import operator
from pydantic import PrivateAttr


"""
A series of node to manipulate table rows.
"""


class TableFilterNode(BaseNode):
    """
    A node to filter rows of a table by given condition.
    Output two subtable of input table,
    one with rows satisfying the condition, 
    the other with rows not satisfying the condition.
    """
    column: str
    op: Literal["EQ", "NE", "GT", "LT", "GE", "LE"]
    # value is provided as an input port (primitive) — use CmpCondition for validation/evaluation
    _cond: CmpCondition | None = PrivateAttr(default=None)

    _OP_MAP = {
        "EQ": operator.eq,
        "NE": operator.ne,
        "GT": operator.gt,
        "LT": operator.lt,
        "GE": operator.ge,
        "LE": operator.le,
    }

    def validate_parameters(self) -> None:
        if not self.type == "TableFilterNode":
            raise NodeValidationError("Node type must be 'TableFilterNode'.")
        if self.column.strip() == "":
            raise NodeValidationError("column cannot be empty")
        # build comparison condition using CmpCondition so static/dynamic checks
        # left refers to the table column, right refers to the primitive input named 'value'
        self._cond = CmpCondition(op=self.op, left=("input", self.column), right=("value", None))

    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        primitive_types = {Schema.DataType.INT, Schema.DataType.FLOAT, Schema.DataType.STR, Schema.DataType.BOOL}
        return [
            InPort(name="input", accept_types={Schema.DataType.TABLE}, table_columns={self.column: {Schema.ColumnType.INT, Schema.ColumnType.FLOAT, Schema.ColumnType.STR, Schema.ColumnType.BOOL}}, description="Input table", required=True),
            InPort(name="value", accept_types=primitive_types, description="Value to compare with", required=True),
        ], [OutPort(name="matched"), OutPort(name="unmatched")]

    def validate_input(self, input: dict[str, Data]) -> None:
        if "input" not in input:
            raise NodeValidationError("Missing 'input' table at runtime")
        df = input["input"].payload
        if not isinstance(df, DataFrame):
            raise NodeValidationError("Payload for 'input' must be a DataFrame")
        if len(df) == 0:
            raise NodeValidationError("Input table is empty")
        if self.column not in df.columns:
            raise NodeValidationError(f"Column '{self.column}' not found in input payload")
        # dynamic validate via CmpCondition (this will ensure the 'value' input exists and types are compatible)
        assert(self._cond is not None)
        self._cond.dynamic_validate(input)

    def infer_output_schema(self, input_schema: dict[str, Schema]) -> dict[str, Schema]:
        if "input" not in input_schema:
            raise NodeValidationError("Missing schema for 'input'")
        # static validate condition if available
        assert(self._cond is not None)
        self._cond.static_validate(input_schema)
        ins = input_schema["input"]
        if ins.columns is None:
            return {"matched": Schema(type=Schema.DataType.TABLE, columns=None), "unmatched": Schema(type=Schema.DataType.TABLE, columns=None)}
        # result tables have same columns as input
        return {"matched": Schema(type=Schema.DataType.TABLE, columns=ins.columns), "unmatched": Schema(type=Schema.DataType.TABLE, columns=ins.columns)}

    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        df = input["input"].payload
        assert isinstance(df, DataFrame)
        # evaluate per-row using CmpCondition.evaluate (non-vectorized, simpler & consistent)
        if self._cond is None:
            raise NodeValidationError("Internal error: comparison condition not initialized")
        # build boolean mask by evaluating condition per row
        import pandas as _pd
        mask_list: list[bool] = []
        # data mapping passed to evaluate should include the inputs by name
        data_map = {k: v for k, v in input.items()}
        for i in range(len(df)):
            res = self._cond.evaluate(data_map, left_idx=i, right_idx=None)
            mask_list.append(bool(res))
        mask = _pd.Series(mask_list, index=df.index)
        matched_df = df.loc[mask].copy()
        unmatched_df = df.loc[~mask].copy()

        # set visualization to none
        self.vis = Visualization(node_id=self.id, type=Visualization.Type.TABLE, payload=matched_df)

        sche = input["input"].sche
        return {
            "matched": Data(sche=sche, payload=matched_df),
            "unmatched": Data(sche=sche, payload=unmatched_df),
        }


class TableRowAppendNode(BaseNode):
    """
    A node to append rows into one table.
    """
    def validate_parameters(self) -> None:
        if not self.type == "TableRowAppendNode":
            raise NodeValidationError("Node type must be 'TableRowAppendNode'.")

    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [
            InPort(name="table", accept_types={Schema.DataType.TABLE}),
            InPort(name="to_append", accept_types={Schema.DataType.TABLE}),
        ], [OutPort(name="output")]

    def validate_input(self, input: dict[str, Data]) -> None:
        if "table" not in input or "to_append" not in input:
            raise NodeValidationError("Both 'table' and 'to_append' are required at runtime")
        df = input["table"].payload
        rdf = input["to_append"].payload
        if not isinstance(df, DataFrame) or not isinstance(rdf, DataFrame):
            raise NodeValidationError("Both inputs must be DataFrame payloads")
        # ensure both have columns info in schema
        if input["table"].sche.columns is None or input["to_append"].sche.columns is None:
            raise NodeValidationError("Both table schemas must include columns information")
        # ensure columns (except _index) align
        left_cols = set(input["table"].sche.columns.keys())
        right_cols = set(input["to_append"].sche.columns.keys())
        if left_cols != right_cols:
            raise NodeValidationError("Input tables must have the same columns")

    def infer_output_schema(self, input_schema: dict[str, Schema]) -> dict[str, Schema]:
        if "table" not in input_schema or "to_append" not in input_schema:
            raise NodeValidationError("Missing schema for table or to_append")
        if input_schema["table"].columns is None or input_schema["to_append"].columns is None:
            return {"output": Schema(type=Schema.DataType.TABLE, columns=None)}
        # require same columns
        if set(input_schema["table"].columns.keys()) != set(input_schema["to_append"].columns.keys()):
            raise NodeValidationError("Input tables must have identical columns")
        return {"output": Schema(type=Schema.DataType.TABLE, columns=input_schema["table"].columns)}

    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        df = input["table"].payload
        rdf = input["to_append"].payload
        assert isinstance(df, DataFrame) and isinstance(rdf, DataFrame)
        from pandas import concat
        # drop existing _index columns then concat and re-create sequential _index
        def _drop_index_col(d: DataFrame) -> DataFrame:
            if INDEX_COLUMN_NAME in d.columns:
                return d.drop(columns=[INDEX_COLUMN_NAME])
            return d

        left_noidx = _drop_index_col(df)
        right_noidx = _drop_index_col(rdf)
        res = concat([left_noidx, right_noidx], ignore_index=True)
        res.insert(0, INDEX_COLUMN_NAME, range(len(res)))

        self.vis = Visualization(node_id=self.id, type=Visualization.Type.TABLE, payload=res)
        out_schema = self.infer_output_schema({"table": input["table"].sche, "to_append": input["to_append"].sche})["output"]
        return {"output": Data(sche=out_schema, payload=res)}


class TableSortNode(BaseNode):
    """
    A node to sort rows of a table by given column.
    """
    column: str
    ascending: bool = True

    def validate_parameters(self) -> None:
        if not self.type == "TableSortNode":
            raise NodeValidationError("Node type must be 'TableSortNode'.")
        if self.column.strip() == "":
            raise NodeValidationError("column cannot be empty")

    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [InPort(name="input", accept_types={Schema.DataType.TABLE}, table_columns=None)], [OutPort(name="output")]

    def validate_input(self, input: dict[str, Data]) -> None:
        if "input" not in input:
            raise NodeValidationError("Missing 'input' at runtime")
        df = input["input"].payload
        if not isinstance(df, DataFrame):
            raise NodeValidationError("Payload for 'input' must be a DataFrame")
        if len(df) == 0:
            raise NodeValidationError("Input table is empty")
        if self.column not in df.columns:
            raise NodeValidationError(f"Column '{self.column}' not found in payload")

    def infer_output_schema(self, input_schema: dict[str, Schema]) -> dict[str, Schema]:
        if "input" not in input_schema:
            raise NodeValidationError("Missing schema for 'input'")
        ins = input_schema["input"]
        return {"output": Schema(type=Schema.DataType.TABLE, columns=ins.columns if ins.columns is not None else None)}

    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        df = input["input"].payload
        assert isinstance(df, DataFrame)
        res = df.sort_values(by=self.column, ascending=self.ascending).copy()
        self.vis = Visualization(node_id=self.id, type=Visualization.Type.TABLE, payload=res)
        return {"output": Data(sche=self.infer_output_schema({"input": input["input"].sche})["output"], payload=res)}
    
