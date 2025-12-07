from typing import Any, Dict, Literal, override

from pydantic import PrivateAttr

from server.models.data import Data, Table
from server.models.exception import NodeParameterError
from server.models.schema import (
    ColType,
    Pattern,
    Schema,
    check_no_illegal_cols,
    generate_default_col_name,
)

from ..base_node import BaseNode, InPort, OutPort, register_node


@register_node()
class CumulativeNode(BaseNode):
    """
    Calculate cumulative sum, product, min, or max.
    Useful for calculating equity curves (CumProd) or running totals (CumSum).
    """
    col: str
    method: Literal["cumsum", "cumprod", "cummax", "cummin"]
    result_col: str | None = None
    
    _result_col_type: ColType | None = PrivateAttr(default=None)

    @override
    def validate_parameters(self) -> None:
        if not self.type == "CumulativeNode":
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
            self.result_col = generate_default_col_name(self.id, self.method)
        if not check_no_illegal_cols([self.result_col]):
            raise NodeParameterError(
                node_id=self.id, 
                err_param_key="result_col", 
                err_msg="Illegal column name"
            )
        return

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [
            InPort(name="table", description="Input table", 
                   accept=Pattern(
                       types={Schema.Type.TABLE}, 
                       table_columns={self.col: {ColType.FLOAT, ColType.INT}}))
        ], [
            OutPort(name="table", description="Output table with cumulative column")
        ]

    @override
    def infer_output_schemas(self, input_schemas: Dict[str, Schema]) -> Dict[str, Schema]:
        input_schema = input_schemas["table"]
        assert input_schema.tab is not None
        # cumprod always returns float, cumsum/min/max keeps original type usually
        if self.method in {"cummax", "cummin"}:
            self._result_col_type = input_schema.tab.col_types[self.col]
        else:
            self._result_col_type = ColType.FLOAT 
        assert self.result_col is not None
        return {
            "table": input_schema.append_col(
                self.result_col, self._result_col_type
            )
        }

    @override
    def process(self, input: Dict[str, Data]) -> Dict[str, Data]:
        table = input["table"].payload
        assert isinstance(table, Table)
        df = table.df.copy()
        
        if self.method == "cumsum":
            df[self.result_col] = df[self.col].cumsum()
        elif self.method == "cumprod":
            df[self.result_col] = df[self.col].cumprod()
        elif self.method == "cummax":
            df[self.result_col] = df[self.col].cummax()
        elif self.method == "cummin":
            df[self.result_col] = df[self.col].cummin()

        assert self._result_col_type is not None
        assert self.result_col is not None

        return {"table": Data(payload=Table(df=df, col_types={**table.col_types, self.result_col: self._result_col_type}))}
    
    @override
    @classmethod
    def hint(cls, input_schemas: Dict[str, Schema], current_params: Dict) -> Dict[str, Any]:
        hint = {}
        if "table" in input_schemas:
            col_choices = []
            input_schema = input_schemas["table"]
            if input_schema.tab is not None:
                for col_name, col_type in input_schema.tab.col_types.items():
                    if col_type in {ColType.INT, ColType.FLOAT}:
                        col_choices.append(col_name)
                        break
            hint["col_choices"] = col_choices
        return hint
