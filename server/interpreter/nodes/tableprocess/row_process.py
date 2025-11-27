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
        return {"true_table": table_schema, "false_table": table_schema}

    @override
    def process(self, input: Dict[str, Data]) -> Dict[str, Data]:
        table_data = input["table"]
        assert isinstance(table_data.payload, Table)
        df = table_data.payload.df

        true_df = df[df[self.cond_col].eq(True)]
        false_df = df[df[self.cond_col].eq(False)]

        return {
            "true_table": Data.from_df(true_df),
            "false_table": Data.from_df(false_df),
        }

    @override
    @classmethod
    def hint(
        cls, input_schemas: Dict[str, Schema], current_params: Dict
    ) -> Dict[str, Any]:
        cond_col_choices = []
        if "table" in input_schemas:
            table_schema = input_schemas["table"]
            assert table_schema.tab is not None
            for col, type in table_schema.tab.col_types.items():
                if type == ColType.BOOL:
                    cond_col_choices.append(col)
        return {"cond_col_choices": cond_col_choices}


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
        return {"deduplicated_table": table_schema}

    @override
    def process(self, input: Dict[str, Data]) -> Dict[str, Data]:
        table_data = input["table"]
        assert isinstance(table_data.payload, Table)
        df = table_data.payload.df

        deduplicated_df = df.drop_duplicates(subset=self.subset_cols)

        return {"deduplicated_table": Data.from_df(deduplicated_df)}

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
        return {"cleaned_table": table_schema}

    @override
    def process(self, input: Dict[str, Data]) -> Dict[str, Data]:
        table_data = input["table"]
        assert isinstance(table_data.payload, Table)
        df = table_data.payload.df

        cleaned_df = df.dropna(subset=self.subset_cols)

        return {"cleaned_table": Data.from_df(cleaned_df)}

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

        return {"merged_table": Data.from_df(merged_df)}


@register_node()
class SliceNode(BaseNode):
    """
    Slice table rows by specified indices.
    """
    begin: int | None = None
    end: int | None = None
    step: int = 1

    @override
    def validate_parameters(self) -> None:
        if not self.type == "SliceNode":
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
            )
        ]

    @override
    def infer_output_schemas(self, input_schemas: Dict[str, Schema]) -> Dict[str, Schema]:
        table_schema = input_schemas["table"]
        return {"sliced_table": table_schema}

    @override
    def process(self, input: Dict[str, Data]) -> Dict[str, Data]:
        table_data = input["table"]
        assert isinstance(table_data.payload, Table)
        df = table_data.payload.df

        sliced_df = df.iloc[self.begin:self.end:self.step]

        return {"sliced_table": Data.from_df(sliced_df)}
