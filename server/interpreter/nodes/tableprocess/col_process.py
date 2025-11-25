from typing import Any, Dict, Literal, override

from server.models.data import Data, Table
from server.models.exception import NodeParameterError, NodeValidationError
from server.models.schema import Pattern, Schema, TableSchema, check_no_illegal_cols

from ..base_node import BaseNode, InPort, OutPort, register_node

"""
This file defines some node for columns operations in tables.
"""

@register_node
class SelectColNode(BaseNode):
    """
    The node to select specified columns from the input table.
    """
    
    selected_cols: list[str]
    
    @override
    def validate_parameters(self) -> None:
        if not self.type == "SelectColNode":
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
                description="Input table to select columns from.",
                accept=Pattern(
                    types={Schema.Type.TABLE},
                    table_columns={col: set() for col in self.selected_cols},
                )
            )
        ], [
            OutPort(
                name="selected_table",
                description="Output table with selected columns."
            ),
            OutPort(
                name="dropped_table",
                description="Output table with dropped columns."
            )
        ]

    @override
    def infer_output_schemas(self, input_schemas: Dict[str, Schema]) -> Dict[str, Schema]:
        table_schema = input_schemas["table"]
        assert table_schema.tab is not None

        selected_col_types = {
            col: table_schema.tab.col_types[col] 
            for col in self.selected_cols
        }
        dropped_col_types = {
            col: col_type 
            for col, col_type in table_schema.tab.col_types.items() 
            if col not in self.selected_cols
        }

        return {
            "selected_table": Schema(
                type=Schema.Type.TABLE,
                tab=TableSchema(col_types=selected_col_types)
            ),
            "dropped_table": Schema(
                type=Schema.Type.TABLE,
                tab=TableSchema(col_types=dropped_col_types)
            )
        }

    @override
    def process(self, input: Dict[str, Data]) -> Dict[str, Data]:
        table_data = input["table"]
        assert isinstance(table_data.payload, Table)
        df = table_data.payload.df
        selected_df = df[self.selected_cols]
        dropped_df = df.drop(columns=self.selected_cols)

        return {
            "selected_table": Data.from_df(selected_df),
            "dropped_table": Data.from_df(dropped_df)
        }

    @override
    @classmethod
    def hint(cls, input_schemas: Dict[str, Schema], current_params: Dict) -> Dict[str, Any]:
        selected_col_choices = []
        if "table" in input_schemas:
            table_schema = input_schemas["table"]
            assert table_schema.tab is not None
            selected_col_choices = list(table_schema.tab.col_types.keys())
        return {
            "selected_col_choices": selected_col_choices
        }

@register_node
class JoinNode(BaseNode):
    """
    The node to join two tables on specified columns.
    """

    left_on: str
    right_on: str
    how: Literal['INNER', 'LEFT', 'RIGHT', 'OUTER']

    @override
    def validate_parameters(self) -> None:
        if not self.type == "JoinNode":
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
                name="left_table",
                description="Left input table to join.",
                accept=Pattern(
                    types={Schema.Type.TABLE},
                    table_columns={self.left_on: set()},
                )
            ),
            InPort(
                name="right_table",
                description="Right input table to join.",
                accept=Pattern(
                    types={Schema.Type.TABLE},
                    table_columns={self.right_on: set()},
                )
            )
        ], [
            OutPort(
                name="joined_table",
                description="Output table after joining."
            )
        ]

    @override
    def infer_output_schemas(self, input_schemas: Dict[str, Schema]) -> Dict[str, Schema]:
        left_schema = input_schemas["left_table"]
        right_schema = input_schemas["right_table"]
        assert left_schema.tab is not None
        assert right_schema.tab is not None
        
        # check if left column and right column have the same type
        left_col_type = left_schema.tab.col_types[self.left_on]
        right_col_type = right_schema.tab.col_types[self.right_on]
        if left_col_type != right_col_type:
            raise NodeValidationError(
                node_id=self.id,
                err_inputs=["left_table", "right_table"],
                err_msgs=[f"Column '{self.left_on}' in left table has type {left_col_type}, "
                          f"while column '{self.right_on}' in right table has type {right_col_type}."],
            )

        # remove _index column
        left_cols = left_schema.tab.col_types.copy()
        left_cols.pop('_index')
        right_cols = right_schema.tab.col_types.copy()
        right_cols.pop('_index')

        # combine the column types from both tables
        new_col_types = left_cols
        for col, col_type in right_cols.items():
            if col not in new_col_types:
                new_col_types[col] = col_type
            else:
                # handle column name conflict by suffixing with _right
                new_col_types[f"{col}_right"] = col_type

        new_tab = TableSchema(col_types=new_col_types)
        return {
            "joined_table": Schema(type=Schema.Type.TABLE, tab=new_tab)
        }

    @override
    def process(self, input: Dict[str, Data]) -> Dict[str, Data]:
        left_table_data = input["left_table"]
        right_table_data = input["right_table"]
        assert isinstance(left_table_data.payload, Table)
        assert isinstance(right_table_data.payload, Table)
        left_df = left_table_data.payload.df.copy()
        right_df = right_table_data.payload.df.copy()
        
        # remove _index column
        if '_index' in left_df.columns:
            left_df = left_df.drop(columns=['_index'])
        if '_index' in right_df.columns:
            right_df = right_df.drop(columns=['_index'])

        joined_df = left_df.merge(
            right_df,
            how=self.how.lower(), # type: ignore
            left_on=self.left_on,
            right_on=self.right_on,
            suffixes=('', '_right')
        )

        return {
            "joined_table": Data.from_df(joined_df)
        }

    @override
    @classmethod
    def hint(cls, input_schemas: Dict[str, Schema], current_params: Dict) -> Dict[str, Any]:
        left_col_choices = []
        right_col_choices = []
        if "left_table" in input_schemas:
            left_schema = input_schemas["left_table"]
            assert left_schema.tab is not None
            for col in left_schema.tab.col_types.keys():
                left_col_choices.append(col)
        if "right_table" in input_schemas:
            right_schema = input_schemas["right_table"]
            assert right_schema.tab is not None
            for col in right_schema.tab.col_types.keys():
                right_col_choices.append(col)
        return {
            "left_on_choices": left_col_choices,
            "right_on_choices": right_col_choices
        }

@register_node
class RenameColNode(BaseNode):
    """
    The node to rename columns in the input table.
    """

    rename_map: dict[str, str]

    @override
    def validate_parameters(self) -> None:
        if not self.type == "RenameColNode":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="type",
                err_msg="Node type parameter mismatch.",
            )
        for new_name in self.rename_map.values():
            if check_no_illegal_cols([new_name]) is False:
                raise NodeParameterError(
                    node_id=self.id,
                    err_param_key="rename_map",
                    err_msg=f"Illegal column name '{new_name}' in rename map.",
                )
        return

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [
            InPort(
                name="table",
                description="Input table to rename columns.",
                accept=Pattern(
                    types={Schema.Type.TABLE},
                    table_columns={col: set() for col in self.rename_map.keys()},
                )
            )
        ], [
            OutPort(
                name="renamed_table",
                description="Output table with renamed columns."
            )
        ]

    @override
    def infer_output_schemas(self, input_schemas: Dict[str, Schema]) -> Dict[str, Schema]:
        table_schema = input_schemas["table"]
        assert table_schema.tab is not None

        new_col_types = {}
        for col, col_type in table_schema.tab.col_types.items():
            if col in self.rename_map:
                new_col_types[self.rename_map[col]] = col_type
            else:
                new_col_types[col] = col_type

        return {
            "renamed_table": Schema(
                type=Schema.Type.TABLE,
                tab=TableSchema(col_types=new_col_types)
            )
        }

    @override
    def process(self, input: Dict[str, Data]) -> Dict[str, Data]:
        table_data = input["table"]
        assert isinstance(table_data.payload, Table)
        df = table_data.payload.df
        renamed_df = df.rename(columns=self.rename_map)

        return {
            "renamed_table": Data.from_df(renamed_df)
        }

    @override
    @classmethod
    def hint(cls, input_schemas: Dict[str, Schema], current_params: Dict) -> Dict[str, Any]:
        rename_col_choices = []
        if "table" in input_schemas:
            table_schema = input_schemas["table"]
            assert table_schema.tab is not None
            rename_col_choices = list(table_schema.tab.col_types.keys())
        return {
            "rename_col_choices": rename_col_choices
        }
