from typing import Any, Dict, Literal, override

from server.models.data import Data, Table, TableSchema
from server.models.exception import (
    NodeParameterError,
)
from server.models.schema import (
    Pattern,
    Schema,
)

from ..base_node import BaseNode, InPort, OutPort, register_node


@register_node
class GroupNode(BaseNode):
    """
    A node to group by specified columns, and aggregate other columns with specified aggregation functions.
    """
    group_cols: list[str]
    agg_cols: list[str]
    agg_func: Literal["SUM", "MEAN", "COUNT", "MAX", "MIN", "STD", "FIRST", "LAST"]

    @override
    def validate_parameters(self) -> None:
        if not self.type == "GroupNode":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="type",
                err_msg="Node type parameter mismatch.",
            )
        return

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        input_table_cols = {col: set() for col in self.group_cols}
        input_table_cols |= {agg_col: set() for agg_col in self.agg_cols}
        return [
            InPort(
                name="table",
                description="Input table to be grouped.",
                accept=Pattern(
                    types={Schema.Type.TABLE},
                    table_columns=input_table_cols,
                )
            )
        ], [
            OutPort(
                name="grouped_result_table",
                description="Output table after grouping and aggregation."
            )
        ]

    @override
    def infer_output_schemas(self, input_schemas: Dict[str, Schema]) -> Dict[str, Schema]:
        table_schema = input_schemas["table"]
        assert table_schema.tab is not None
        # 2. only keep the grouping column and the aggregated column
        new_col_types = {}
        for col_name in self.group_cols:
            new_col_types[col_name] = table_schema.tab.col_types[col_name]
        for col_name in self.agg_cols:
            new_col_types[col_name] = table_schema.tab.col_types[col_name]
        new_tab = TableSchema(col_types=new_col_types)
        result_table_schema = Schema(type=Schema.Type.TABLE, tab=new_tab)
        return {
            "grouped_result_table": result_table_schema
        }

    @override
    def process(self, input: Dict[str, Data]) -> Dict[str, Data]:
        table_data = input["table"]
        assert isinstance(table_data.payload, Table)
        df = table_data.payload.df

        agg_func_map = {
            "SUM": "sum",
            "MEAN": "mean",
            "COUNT": "size",
            "MAX": "max",
            "MIN": "min",
            "STD": "std",
            "FIRST": "first",
            "LAST": "last"
        }
        
        grouped_df = df.groupby(self.group_cols)[self.agg_cols].agg(agg_func_map[self.agg_func]).reset_index()
        
        result_data = Data.from_df(grouped_df)
        
        return {
            "grouped_result_table": result_data
        }

    @override
    @classmethod
    def hint(cls, input_schemas: Dict[str, Schema], current_params: Dict) -> Dict[str, Any]:
        col_choices = []
        agg_col_choices = []
        if "table" in input_schemas:
            table_schema = input_schemas["table"]
            assert table_schema.tab is not None
            for col in table_schema.tab.col_types.keys():
                col_choices.append(col)
                agg_col_choices.append(col)
        return {
            "group_col_choices": col_choices,
            "agg_col_choices": agg_col_choices
        }
