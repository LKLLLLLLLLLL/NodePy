from typing import Any, Dict, override

from server.models.data import Data, Table
from server.models.exception import (
    NodeParameterError,
    NodeValidationError,
)
from server.models.schema import (
    ColType,
    Pattern,
    Schema,
)

from ..base_node import BaseNode, InPort, OutPort, register_node


@register_node()
class SortNode(BaseNode):
    """
    A node to sort rows of a table by given column.
    """
    sort_col: str
    ascending: bool

    @override
    def validate_parameters(self) -> None:
        if not self.type == "SortNode":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="type",
                err_msg="Node type parameter mismatch.",
            )
        return

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [
            InPort(
                name="table",
                description="Input table to be sorted.",
                accept=Pattern(
                    types={Schema.Type.TABLE},
                    table_columns={self.sort_col: {ColType.INT, ColType.FLOAT, ColType.STR, ColType.DATETIME}},
                )
            )
        ], [
            OutPort(
                name="sorted_table",
                description="Output table with rows sorted."
            )
        ]

    @override
    def infer_output_schemas(self, input_schemas: Dict[str, Schema]) -> Dict[str, Schema]:
        table_schema = input_schemas["table"]
        assert table_schema.tab is not None
        if self.sort_col not in table_schema.tab.col_types:
            raise NodeValidationError(
                node_id=self.id,
                err_input="table",
                err_msg=f"Sort column '{self.sort_col}' not found in input table.",
            )
        return {
            "sorted_table": table_schema
        }

    @override
    def process(self, input: Dict[str, Data]) -> Dict[str, Data]:
        table_data = input["table"]
        assert isinstance(table_data.payload, Table)
        df = table_data.payload.df

        sorted_df = df.sort_values(by=self.sort_col, ascending=self.ascending)

        sorted_data = Data(
            payload=Table(
                df=sorted_df,
                col_types=table_data.payload.col_types
            ).regenerate_index()
        )

        return {
            "sorted_table": sorted_data
        }

    @override
    @classmethod
    def hint(cls, input_schemas: Dict[str, Schema], current_params: Dict) -> Dict[str, Any]:
        sort_col_choices = []
        if "table" in input_schemas:
            table_schema = input_schemas["table"]
            assert table_schema.tab is not None
            sort_col_choices = list(table_schema.tab.col_types.keys())
        return {
            "sort_col_choices": sort_col_choices
        }
