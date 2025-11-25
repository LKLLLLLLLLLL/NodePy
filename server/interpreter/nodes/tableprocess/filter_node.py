from typing import Any, Dict, override

from server.models.data import Data, Table
from server.models.exception import (
    NodeParameterError,
)
from server.models.schema import (
    ColType,
    Pattern,
    Schema,
)

from ..base_node import BaseNode, InPort, OutPort, register_node


@register_node
class FilterNode(BaseNode):
    """
    Filter rows with specified columns.
    Requires the condition column to be of boolean type.
    """
    cond_col: str

    @override
    def validate_parameters(self) -> None:
        if not self.type == "FilterNode":
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
                description="Input table to be filtered.",
                accept=Pattern(
                    types={Schema.Type.TABLE},
                    table_columns={self.cond_col: {ColType.BOOL}},
                )
            )
        ], [
            OutPort(
                name="true_table",
                description="Output table with rows where the condition is true."
            ),
            OutPort(
                name="false_table",
                description="Output table with rows where the condition is false."
            )
        ]

    @override
    def infer_output_schemas(self, input_schemas: Dict[str, Schema]) -> Dict[str, Schema]:
        table_schema = input_schemas["table"]
        return {
            "true_table": table_schema,
            "false_table": table_schema
        }

    @override
    def process(self, input: Dict[str, Data]) -> Dict[str, Data]:
        table_data = input["table"]
        assert isinstance(table_data.payload, Table)
        df = table_data.payload.df
        
        true_df = df[df[self.cond_col].eq(True)]
        false_df = df[df[self.cond_col].eq(False)]
        
        return {
            "true_table": Data.from_df(true_df),
            "false_table": Data.from_df(false_df)
        }

    @override
    @classmethod
    def hint(cls, input_schemas: Dict[str, Schema], current_params: Dict) -> Dict[str, Any]:
        cond_col_choices = []
        if "table" in input_schemas:
            table_schema = input_schemas["table"]
            assert table_schema.tab is not None
            for col, type in table_schema.tab.col_types.items():
                if type == ColType.BOOL:
                    cond_col_choices.append(col)
        return {
            "cond_col_choices": cond_col_choices
        }
