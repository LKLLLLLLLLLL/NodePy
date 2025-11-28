from typing import Any, Dict, Literal, override

from pydantic import PrivateAttr

from server.models.data import Data, Table
from server.models.exception import (
    NodeParameterError,
)
from server.models.schema import (
    ColType,
    Pattern,
    Schema,
    check_no_illegal_cols,
    generate_default_col_name,
)

from ..base_node import BaseNode, InPort, OutPort, register_node


@register_node()
class RollingNode(BaseNode):
    """
    A node to calculate the rolling statistics of a specified column over a defined window size.
    """
    col: str
    result_col: str | None = None
    window_size: int
    min_periods: int = 1
    method: Literal["mean", "std", "sum", "min", "max"]

    _result_col_type: ColType | None = PrivateAttr(default=None)

    @override
    def validate_parameters(self) -> None:
        if not self.type == "RollingNode":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="type",
                err_msg="Node type parameter mismatch.",
            )
        if self.window_size <= 0:
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="window_size",
                err_msg="Window size must be a positive integer.",
            )
        if not self.result_col:
            self.result_col = generate_default_col_name(
                id=self.id,
                annotation="ma",
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
        input_table_cols = {self.col: {ColType.FLOAT, ColType.INT}}
        return [
            InPort(
                name="table",
                description="Input table for moving average calculation.",
                accept=Pattern(
                    types={Schema.Type.TABLE},
                    table_columns=input_table_cols,
                )
            )
        ], [
            OutPort(
                name="table",
                description="Output table with the moving average column."
            )
        ]

    @override
    def infer_output_schemas(
        self, input_schemas: Dict[str, Schema]
    ) -> Dict[str, Schema]:
        input_schema = input_schemas["table"]
        assert self.result_col is not None
        # infer result_col type
        assert input_schema.tab is not None
        col_type = input_schema.tab.col_types[self.col]
        if self.method in {"mean", "std"}:
            result_col_type = ColType.FLOAT
        else:
            result_col_type = col_type
        self._result_col_type = result_col_type
        return {"table": input_schema.append_col(self.result_col, result_col_type)}

    @override
    def process(self, input: Dict[str, Data]) -> Dict[str, Data]:
        input_table_data = input["table"]
        assert isinstance(input_table_data.payload, Table)

        df = input_table_data.payload.df.copy()

        assert self.result_col is not None

        df[self.result_col] = df[self.col].rolling(window=self.window_size, min_periods=self.min_periods).agg(self.method)

        assert self._result_col_type is not None
        output_data = Data(
            payload=Table(
                df=df,
                col_types={
                    **input_table_data.payload.col_types,
                    self.result_col: self._result_col_type,
                },
            )
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
                    if col_type in {ColType.FLOAT, ColType.INT}
                ]
                hint["col_choices"] = col_choices
        return hint
