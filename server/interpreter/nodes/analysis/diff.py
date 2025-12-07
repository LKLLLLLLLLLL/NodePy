from typing import Any, Dict, override

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
)

from ..base_node import BaseNode, InPort, OutPort, register_node


@register_node()
class DiffNode(BaseNode):
    """
    A node to calculate the difference of specified column between each row and the previous row.
    Export a new table with the specific column, and n-1 rows, where n is the number of rows in the input table.
    """
    col: str

    _new_col_name: str | None = PrivateAttr(default=None)

    @override
    def validate_parameters(self) -> None:
        if not self.type == "DiffNode":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="type",
                err_msg="Node type parameter mismatch.",
            )
        return

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        input_table_cols = {self.col: {ColType.FLOAT, ColType.INT}}
        return [
            InPort(
                name="table",
                description="Input table for difference calculation.",
                accept=Pattern(
                    types={Schema.Type.TABLE},
                    table_columns=input_table_cols,
                )
            )
        ], [
            OutPort(
                name="table",
                description="Output table with the difference column."
            )
        ]

    @override
    def infer_output_schemas(self, input_schemas: Dict[str, Schema]) -> Dict[str, Schema]:
        input_schema = input_schemas["table"]
        assert input_schema.tab is not None
        assert self.col in input_schema.tab.col_types
        col_type = input_schema.tab.col_types[self.col]
        assert col_type in {ColType.FLOAT, ColType.INT}
        self._new_col_name = f"{self.col}_diff"
        i = 0
        while not check_no_illegal_cols([self._new_col_name]):
            self._new_col_name = f"{self.col}_diff_{i}"
            i += 1
        return {
            "table": input_schema.append_col(self._new_col_name, col_type)
        }

    @override
    def process(self, input: Dict[str, Data]) -> Dict[str, Data]:
        input_table = input["table"]
        assert isinstance(input_table.payload, Table)
        assert self._new_col_name is not None
        df = input_table.payload.df.copy()
        df[self._new_col_name] = df[self.col].diff()
        df = df.iloc[1:].reset_index(drop=True)  # remove the first row with NaN diff
        new_col_types = input_table.payload.col_types.copy()
        new_col_types[self._new_col_name] = input_table.payload.col_types[self.col]
        output_table = Table(df=df, col_types=new_col_types)
        output_data = Data(payload=output_table)
        return {
            "table": output_data
        }

    @override
    @classmethod
    def hint(cls, input_schemas: Dict[str, Schema], current_params: Dict) -> Dict[str, Any]:
        col_choices = []
        if "table" in input_schemas:
            input_schema = input_schemas["table"]
            assert input_schema.tab is not None
            for col, col_type in input_schema.tab.col_types.items():
                if col_type in {ColType.FLOAT, ColType.INT}:
                    col_choices.append(col)
        return {
            "col_choices": col_choices
        }
