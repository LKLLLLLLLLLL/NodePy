from typing import Any, Dict, Literal, override

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

"""
This file defines some node to split, merge, delete the rows in tables.
"""

@register_node()
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
        if self.cond_col.strip() == "":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="cond_col",
                err_msg="Condition column cannot be empty.",
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
                ),
            )
        ], [
            OutPort(
                name="true_table",
                description="Output table with rows where the condition is true.",
            ),
            OutPort(
                name="false_table",
                description="Output table with rows where the condition is false.",
            ),
        ]

    @override
    def infer_output_schemas(
        self, input_schemas: Dict[str, Schema]
    ) -> Dict[str, Schema]:
        table_schema = input_schemas["table"]
        assert table_schema.tab is not None
        if self.cond_col not in table_schema.tab.col_types:
            raise NodeValidationError(
                node_id=self.id,
                err_input="table",
                err_msg=f"Condition column '{self.cond_col}' not found in input table schema.",
            )
        return {"true_table": table_schema, "false_table": table_schema}

    @override
    def process(self, input: Dict[str, Data]) -> Dict[str, Data]:
        table_data = input["table"]
        assert isinstance(table_data.payload, Table)
        df = table_data.payload.df

        true_df = df[df[self.cond_col].eq(True)]
        false_df = df[df[self.cond_col].eq(False)]

        true_data = Data(
            payload=Table(
                df=true_df,
                col_types=table_data.payload.col_types
            )
        )

        false_data = Data(
            payload=Table(
                df=false_df,
                col_types=table_data.payload.col_types
            )
        )

        return {
            "true_table": true_data,
            "false_table": false_data,
        }

    @override
    @classmethod
    def hint(
        cls, input_schemas: Dict[str, Schema], current_params: Dict
    ) -> Dict[str, Any]:
        hint = {}
        if "table" in input_schemas:
            cond_col_choices = []
            table_schema = input_schemas["table"]
            assert table_schema.tab is not None
            for col, type in table_schema.tab.col_types.items():
                if type == ColType.BOOL:
                    cond_col_choices.append(col)
            hint["cond_col_choices"] = cond_col_choices
        return hint


@register_node()
class DropDuplicatesNode(BaseNode):
    """
    Drop duplicate rows based on specified columns.
    """

    subset_cols: list[str]

    @override
    def validate_parameters(self) -> None:
        if not self.type == "DropDuplicatesNode":
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
                description="Input table to drop duplicates from.",
                accept=Pattern(
                    types={Schema.Type.TABLE},
                    table_columns={col: set() for col in self.subset_cols},
                ),
            )
        ], [
            OutPort(
                name="deduplicated_table",
                description="Output table with duplicate rows dropped.",
            )
        ]

    @override
    def infer_output_schemas(
        self, input_schemas: Dict[str, Schema]
    ) -> Dict[str, Schema]:
        table_schema = input_schemas["table"]
        assert table_schema.tab is not None
        for col in self.subset_cols:
            if col not in table_schema.tab.col_types:
                raise NodeValidationError(
                    node_id=self.id,
                    err_input="table",
                    err_msg=f"Subset column '{col}' not found in input table schema.",
                )
        return {"deduplicated_table": table_schema}

    @override
    def process(self, input: Dict[str, Data]) -> Dict[str, Data]:
        table_data = input["table"]
        assert isinstance(table_data.payload, Table)
        df = table_data.payload.df
        if self.subset_cols == []:
            deduplicated_df = df.drop_duplicates()
        else:
            deduplicated_df = df.drop_duplicates(subset=self.subset_cols)

        deduplicated_data = Data(
            payload=Table(
                df=deduplicated_df,
                col_types=table_data.payload.col_types
            )
        )

        return {"deduplicated_table": deduplicated_data}

    @override
    @classmethod
    def hint(
        cls, input_schemas: Dict[str, Schema], current_params: Dict
    ) -> Dict[str, Any]:
        subset_col_choices = []
        if "table" in input_schemas:
            table_schema = input_schemas["table"]
            assert table_schema.tab is not None
            subset_col_choices = list(table_schema.tab.col_types.keys())
        return {"subset_col_choices": subset_col_choices}


@register_node()
class DropNaNValueNode(BaseNode):
    """
    Drop rows with NaN values in specified columns.
    """

    subset_cols: list[str]

    @override
    def validate_parameters(self) -> None:
        if not self.type == "DropNaNValueNode":
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
                description="Input table to drop NaN values from.",
                accept=Pattern(
                    types={Schema.Type.TABLE},
                    table_columns={col: set() for col in self.subset_cols},
                ),
            )
        ], [
            OutPort(
                name="cleaned_table",
                description="Output table with rows containing NaN values dropped.",
            )
        ]

    @override
    def infer_output_schemas(
        self, input_schemas: Dict[str, Schema]
    ) -> Dict[str, Schema]:
        table_schema = input_schemas["table"]
        assert table_schema.tab is not None
        for col in self.subset_cols:
            if col not in table_schema.tab.col_types:
                raise NodeValidationError(
                    node_id=self.id,
                    err_input="table",
                    err_msg=f"Subset column '{col}' not found in input table schema.",
                )
        return {"cleaned_table": table_schema}

    @override
    def process(self, input: Dict[str, Data]) -> Dict[str, Data]:
        table_data = input["table"]
        assert isinstance(table_data.payload, Table)
        df = table_data.payload.df

        cleaned_df = df.dropna(subset=self.subset_cols)

        cleaned_data = Data(
            payload=Table(
                df=cleaned_df,
                col_types=table_data.payload.col_types
            )
        )

        return {"cleaned_table": cleaned_data}

    @override
    @classmethod
    def hint(
        cls, input_schemas: Dict[str, Schema], current_params: Dict
    ) -> Dict[str, Any]:
        subset_col_choices = []
        if "table" in input_schemas:
            table_schema = input_schemas["table"]
            assert table_schema.tab is not None
            subset_col_choices = list(table_schema.tab.col_types.keys())
        return {"subset_col_choices": subset_col_choices}


@register_node()
class FillNaNValueNode(BaseNode):
    """
    Fill NaN values in specified columns with a given value.
    """

    subset_cols: list[str]
    method: Literal["const", "ffill", "bfill"]
    fill_value: list[int | float | str | bool] | None = None # the datetime type will be input as iso format string

    @override
    def validate_parameters(self) -> None:
        if not self.type == "FillNaNValueNode":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="type",
                err_msg="Node type parameter mismatch.",
            )
        if len(self.subset_cols) == 0:
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="subset_cols",
                err_msg="Subset columns cannot be empty.",
            )
        if self.method == "const":
            if self.fill_value is None:
                raise NodeParameterError(
                    node_id=self.id,
                    err_param_key="fill_value",
                    err_msg="Fill value must be provided when method is 'const'.",
                )
            if len(self.fill_value) != len(self.subset_cols):
                raise NodeParameterError(
                    node_id=self.id,
                    err_param_key="fill_value",
                    err_msg="Fill value length must match subset columns length.",
                )
        return

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [
            InPort(
                name="table",
                description="Input table to fill NaN values in.",
                accept=Pattern(
                    types={Schema.Type.TABLE},
                    table_columns={col: set() for col in self.subset_cols},
                ),
            )
        ], [
            OutPort(
                name="filled_table",
                description="Output table with NaN values filled.",
            )
        ]

    @override
    def infer_output_schemas(
        self, input_schemas: Dict[str, Schema]
    ) -> Dict[str, Schema]:
        from datetime import datetime
        
        table_schema = input_schemas["table"]
        assert table_schema.tab is not None
        for col in self.subset_cols:
            if col not in table_schema.tab.col_types:
                raise NodeValidationError(
                    node_id=self.id,
                    err_input="table",
                    err_msg=f"Subset column '{col}' not found in input table schema.",
                )
        # check if fill_value type matches column type
        if self.method == "const":
            converted_fill_values = []
            assert self.fill_value is not None
            for col, value in zip(self.subset_cols, self.fill_value):
                col_type = table_schema.tab.col_types[col]
                if col_type == ColType.INT:
                    if not isinstance(value, int):
                        raise NodeValidationError(
                            node_id=self.id,
                            err_input="table",
                            err_msg=f"Fill value for column '{col}' must be of type int.",
                        )
                    converted_fill_values.append(value)
                elif col_type == ColType.FLOAT:
                    if not isinstance(value, (int, float)):
                        raise NodeValidationError(
                            node_id=self.id,
                            err_input="table",
                            err_msg=f"Fill value for column '{col}' must be of type float.",
                        )
                    converted_fill_values.append(float(value))
                elif col_type == ColType.STR:
                    if not isinstance(value, str):
                        raise NodeValidationError(
                            node_id=self.id,
                            err_input="table",
                            err_msg=f"Fill value for column '{col}' must be of type str.",
                        )
                    converted_fill_values.append(value)
                elif col_type == ColType.BOOL:
                    if not isinstance(value, bool):
                        raise NodeValidationError(
                            node_id=self.id,
                            err_input="table",
                            err_msg=f"Fill value for column '{col}' must be of type bool.",
                        )
                    converted_fill_values.append(value)
                elif col_type == ColType.DATETIME:
                    if not isinstance(value, str):
                        raise NodeValidationError(
                            node_id=self.id,
                            err_input="table",
                            err_msg=f"Fill value for column '{col}' must be of type str representing datetime.",
                        )
                    converted_fill_values.append(datetime.fromisoformat(value))
                else:
                    assert False, "Unsupported column type"
            self.fill_value = converted_fill_values
        return {"filled_table": table_schema}

    @override
    def process(self, input: Dict[str, Data]) -> Dict[str, Data]:
        table_data = input["table"]
        assert isinstance(table_data.payload, Table)
        df = table_data.payload.df.copy()

        if self.method == "const":
            # fill with constant value
            assert self.fill_value is not None
            filled_df = df.fillna(
                value={col: val for col, val in zip(self.subset_cols, self.fill_value)}
            )
        elif self.method == "ffill":
            # fill with forward fill
            df[self.subset_cols] = df[self.subset_cols].ffill()
            filled_df = df
        elif self.method == "bfill":
            # fill with backward fill
            df[self.subset_cols] = df[self.subset_cols].bfill()
            filled_df = df
        else:
            filled_df = df

        filled_data = Data(
            payload=Table(df=filled_df, col_types=table_data.payload.col_types)
        )

        return {"filled_table": filled_data}

    @override
    @classmethod
    def hint(
        cls, input_schemas: Dict[str, Schema], current_params: Dict
    ) -> Dict[str, Any]:
        hint = {}
        if "table" in input_schemas:
            table_schema = input_schemas["table"]
            if table_schema.tab is not None:
                subset_col_choices = list(table_schema.tab.col_types.keys())
                hint["subset_col_choices"] = subset_col_choices
            table_schema = input_schemas["table"]
            if table_schema.tab is not None:
                subset_col_choices = list(table_schema.tab.col_types.keys())
                fill_value_types = []
                for col in subset_col_choices:
                    if col in table_schema.tab.col_types:
                        fill_value_types.append(table_schema.tab.col_types[col].value)
                hint["fill_value_types"] = fill_value_types
        return hint


@register_node()
class MergeNode(BaseNode):
    """
    Merge two tables with same columns.
    """
    
    @override
    def validate_parameters(self) -> None:
        if not self.type == "MergeNode":
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
                name="table_1",
                description="First input table to be merged.",
                accept=Pattern(
                    types={Schema.Type.TABLE},
                ),
            ),
            InPort(
                name="table_2",
                description="Second input table to be merged.",
                accept=Pattern(
                    types={Schema.Type.TABLE},
                ),
            )
        ], [
            OutPort(
                name="merged_table",
                description="Output table after merging the two input tables.",
            )
        ]

    @override
    def infer_output_schemas(self, input_schemas: Dict[str, Schema]) -> Dict[str, Schema]:
        # validate if the two tables have the same schema
        table_schema_1 = input_schemas["table_1"]
        table_schema_2 = input_schemas["table_2"]
        if table_schema_1 != table_schema_2:
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="input_schemas",
                err_msg="Input tables have different schemas and cannot be merged.",
            )
        return {"merged_table": table_schema_1}

    @override
    def process(self, input: Dict[str, Data]) -> Dict[str, Data]:
        import pandas as pd

        table_data_1 = input["table_1"]
        table_data_2 = input["table_2"]
        assert isinstance(table_data_1.payload, Table)
        assert isinstance(table_data_2.payload, Table)
        df_1 = table_data_1.payload.df
        df_2 = table_data_2.payload.df

        merged_df = pd.concat([df_1, df_2], ignore_index=True)

        merged_data = Data(
            payload=Table(
                df=merged_df,
                col_types=table_data_1.payload.col_types
            ).regenerate_index()
        )

        return {"merged_table": merged_data}


@register_node()
class TableSliceNode(BaseNode):
    """
    Slice table rows by specified indices.
    """
    begin: int | None = None
    end: int | None = None
    step: int = 1

    @override
    def validate_parameters(self) -> None:
        if not self.type == "TableSliceNode":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="type",
                err_msg="Node type parameter mismatch.",
            )
        if self.step == 0:
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="step",
                err_msg="Step cannot be zero.",
            )
        return

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [
            InPort(
                name="table",
                description="Input table to be sliced.",
                accept=Pattern(
                    types={Schema.Type.TABLE},
                ),
            )
        ], [
            OutPort(
                name="sliced_table",
                description="Output table after slicing the input table.",
            ),
            OutPort(
                name="remaining_table",
                description="Output table containing the rows not included in the slice.",
            )
        ]

    @override
    def infer_output_schemas(self, input_schemas: Dict[str, Schema]) -> Dict[str, Schema]:
        table_schema = input_schemas["table"]
        remaind_schema = input_schemas['table']
        return {"sliced_table": table_schema, "remaining_table": remaind_schema}

    @override
    def process(self, input: Dict[str, Data]) -> Dict[str, Data]:
        table_data = input["table"]
        assert isinstance(table_data.payload, Table)
        df = table_data.payload.df.copy()

        sliced_df = df.iloc[self.begin:self.end:self.step]
        slice_data = Data(
            payload=Table(
                df=sliced_df,
                col_types=table_data.payload.col_types
            )
        )  
        
        remaining_df = df.drop(sliced_df.index)
        remaining_data = Data(
            payload=Table(
                df=remaining_df,
                col_types=table_data.payload.col_types
            )
        )

        return {
            "sliced_table": slice_data,
            "remaining_table": remaining_data,
        }
