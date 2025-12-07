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
    TableSchema,
    check_no_illegal_cols,
    generate_default_col_name,
)

from ..base_node import BaseNode, InPort, OutPort, register_node


@register_node()
class PctChangeNode(BaseNode):
    """
    A node to calculate the percentage change of a specified column between each row and the previous row.
    Export a new table with the specific column, and n-1 rows, where n is the number of rows in the input table.
    """
    col: str
    result_col: str | None = None

    _result_col_type: ColType | None = PrivateAttr(default=None)

    @override
    def validate_parameters(self) -> None:
        if not self.type == "PctChangeNode":
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
                annotation="pct_change",
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
                description="Input table for percentage change calculation.",
                accept=Pattern(
                    types={Schema.Type.TABLE},
                    table_columns=input_table_cols,
                )
            )
        ], [
            OutPort(
                name="table",
                description="Output table with the percentage change column."
            )
        ]

    @override
    def infer_output_schemas(self, input_schemas: Dict[str, Schema]) -> Dict[str, Schema]:
        input_schema = input_schemas["table"]
        assert input_schema.tab is not None
        assert self.col in input_schema.tab.col_types
        col_type = input_schema.tab.col_types[self.col]
        assert col_type in {ColType.FLOAT, ColType.INT}
        self._result_col_type = ColType.FLOAT
        output_col_types = input_schema.tab.col_types.copy()
        assert self.result_col is not None
        output_col_types[self.result_col] = self._result_col_type
        table_schema = Schema(
            type=Schema.Type.TABLE,
            tab=TableSchema(
                col_types=output_col_types,
            )
        )
        return {"table": table_schema}

    @override
    def process(self, input: Dict[str, Data]) -> Dict[str, Data]:
        input_table_data = input["table"]
        assert isinstance(input_table_data.payload, Table)
        assert self._result_col_type is not None
        assert self.result_col is not None

        df = input_table_data.payload.df.copy()

        df[self.result_col] = df[self.col].pct_change()

        new_col_types = input_table_data.payload.col_types.copy()
        new_col_types[self.result_col] = self._result_col_type

        output_table = Table(df=df, col_types=new_col_types)
        output_data = Data(payload=output_table)
        return {"table": output_data}

    @override
    @classmethod
    def hint(cls, input_schemas: Dict[str, Schema], current_params: Dict) -> Dict[str, Any]:
        hint = {}
        if "table" in input_schemas:
            col_choices = []
            input_schema = input_schemas["table"]
            assert input_schema.tab is not None
            for col_name, col_type in input_schema.tab.col_types.items():
                if col_type in {ColType.FLOAT, ColType.INT}:
                    col_choices.append(col_name)
            hint["col_choices"] = col_choices
        return hint
