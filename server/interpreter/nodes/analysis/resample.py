from typing import Any, Dict, Literal, override

from pydantic import PrivateAttr

from server.models.data import Data, Table
from server.models.exception import NodeExecutionError, NodeParameterError
from server.models.schema import (
    ColType,
    Pattern,
    Schema,
    TableSchema,
    check_no_illegal_cols,
    generate_default_col_name,
)

from ..base_node import BaseNode, InPort, OutPort, register_node


@register_node()
class ResampleNode(BaseNode):
    """
    A node to resample the datetime column of a table to a specified frequency.
    """

    col: str
    frequency: Literal["D", "H", "T", "S"]  # Days, Hours, Minutes, Seconds
    method: Literal["mean", "sum", "max", "min", "count"]
    result_col: str | None = None

    _col_types: Dict[str, ColType] | None = PrivateAttr(default=None)

    @override
    def validate_parameters(self) -> None:
        if not self.type == "ResampleNode":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="type",
                err_msg="Node type parameter mismatch.",
            )
        if self.col.strip() == '':
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="col",
                err_msg="Column name must be a non-empty string.",
            )
        if not self.result_col:
            self.result_col = generate_default_col_name(
                id=self.id,
                annotation="resample",
            )
        if check_no_illegal_cols([self.result_col]) is False:
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="result_col",
                err_msg="Result column name contains illegal characters.",
            )
        return

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [
            InPort(
                name="table",
                description="Input table for resampling.",
                accept=Pattern(
                    types={Schema.Type.TABLE},
                    table_columns={self.col: {ColType.DATETIME}},
                )
            )
        ], [
            OutPort(
                name="table",
                description="Output table with resampled datetime column."
            )
        ]

    @override
    def infer_output_schemas(self, input_schemas: Dict[str, Schema]) -> Dict[str, Schema]:
        input_schema = input_schemas["table"]
        assert input_schema.tab is not None
        assert self.col in input_schema.tab.col_types
        col_type = input_schema.tab.col_types[self.col]
        assert col_type == ColType.DATETIME

        # remove col and add result_col
        output_col_types = input_schema.tab.col_types.copy()
        output_col_types.pop(self.col)
        assert self.result_col is not None
        output_col_types[self.result_col] = ColType.DATETIME
        for col, ctype in input_schema.tab.col_types.items():
            if col == self.col:
                continue
            aggregatable_types = {ColType.FLOAT, ColType.INT}
            if ctype not in aggregatable_types:
                output_col_types.pop(col)
            if self.method == "count":
                output_col_types[col] = ColType.INT  # count is always int
                continue
            if ctype == ColType.INT and self.method in {"mean"}:
                output_col_types[col] = ColType.FLOAT  # mean of int is float

        output_table_schema = TableSchema(
            col_types=output_col_types
        )
        output_schema = Schema(
            type=Schema.Type.TABLE,
            tab=output_table_schema,
        )
        self._col_types = output_table_schema.col_types

        return { "table": output_schema }

    @override
    def process(self, input: Dict[str, Data]) -> Dict[str, Data]:
        input_table_data = input["table"]
        assert isinstance(input_table_data.payload, Table)

        df = input_table_data.payload.df.copy()

        assert self.result_col is not None

        resampled = df.set_index(self.col).resample(self.frequency)

        if self.method == "mean":
            agg_df = resampled.mean()
        elif self.method == "sum":
            agg_df = resampled.sum()
        elif self.method == "max":
            agg_df = resampled.max()
        elif self.method == "min":
            agg_df = resampled.min()
        elif self.method == "count":
            agg_df = resampled.count()
        else:
            raise NodeExecutionError(
                node_id=self.id,
                err_msg=f"Unsupported resampling method: {self.method}",
            )

        agg_df = agg_df.reset_index().rename(columns={self.col: self.result_col}).drop(columns=[Table.INDEX_COL])

        assert self._col_types is not None
        output_data = Data(
            payload=Table(
                df=agg_df,
                col_types=self._col_types,
            ).regenerate_index()
        )

        return {"table": output_data}

    @override
    @classmethod
    def hint(cls, input_schemas: Dict[str, Schema], current_params: Dict) -> Dict[str, Any]:
        hint = {}
        if "table" in input_schemas:
            input_schema = input_schemas["table"]
            if input_schema.tab is not None:
                col_choices = [
                    col_name
                    for col_name, col_type in input_schema.tab.col_types.items()
                    if col_type == ColType.DATETIME
                ]
                hint["col_choices"] = col_choices
        return hint
