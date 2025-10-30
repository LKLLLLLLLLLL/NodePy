from ..base_node import BaseNode, InPort, OutPort, register_node
from server.models.exception import NodeParameterError
from server.models.data import Data, Table
from server.models.schema import (
    ColType,
    Pattern,
    Schema,
    generate_default_col_name,
    check_no_illegal_cols
)
from typing import override


"""
This file defines some batch string processing nodes for string columns in tables.
"""

@register_node
class BatchStripNode(BaseNode):
    """
    Node to strip leading and trailing whitespace or specified characters from string columns in a table.
    """
    strip_chars: str | None
    col: str
    result_col: str | None = None
    
    @override
    def validate_parameters(self) -> None:
        if not self.type == "BatchStripNode":
            raise NodeParameterError(
                node_id = self.id,
                err_param_key="type",
                err_msg = "Node type must be 'BatchStripNode'."
            )
        if self.col.strip() == "":
            raise NodeParameterError(
                node_id = self.id,
                err_param_key="col",
                err_msg = "Column name for stripping cannot be empty."
            )
        if self.result_col is None:
            self.result_col = generate_default_col_name(self.id, "result")
        if self.result_col.strip() == "":
            raise NodeParameterError(
                node_id = self.id,
                err_param_key="result_col",
                err_msg = "Result column name cannot be empty."
            )
        if check_no_illegal_cols([self.result_col]) is False:
            raise NodeParameterError(
                node_id = self.id,
                err_param_key="result_col",
                err_msg = f"Result column name '{self.result_col}' contains illegal characters."
            )
        return

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [
            InPort(
                name="input",
                description="Input table with string columns to be stripped.",
                accept=Pattern(
                    types={Schema.Type.TABLE}, table_columns={self.col: {ColType.STR}}
                ),
                optional=False,
            )
        ], [
            OutPort(
                name="output",
                description="Output table after stripping string columns.",
            )
        ]

    @override
    def infer_output_schemas(self, input_schemas: dict[str, Schema]) -> dict[str, Schema]:
        assert self.result_col is not None
        output_schema = input_schemas["input"].append_col(self.result_col, ColType.STR)
        return {"output": output_schema}

    @override
    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        input_table = input["input"].payload
        assert isinstance(input_table, Table)
        df = input_table.df
        df[self.result_col] = df[self.col].astype(str).str.strip(self.strip_chars)
        output_data = Data.from_df(df)
        return {"output": output_data}

@register_node
class BatchConcatNode(BaseNode):
    """
    Node to Concat two string columns in input table.
    """
    col1: str
    col2: str
    result_col: str | None = None
    
    @override
    def validate_parameters(self) -> None:
        if not self.type == "BatchConcatNode":
            raise NodeParameterError(
                node_id = self.id,
                err_param_key="type",
                err_msg = "Node type must be 'BatchConcatNode'."
            )
        if self.col1.strip() == "":
            raise NodeParameterError(
                node_id = self.id,
                err_param_key="col1",
                err_msg = "First column name for concatenation cannot be empty."
            )
        if self.col2.strip() == "":
            raise NodeParameterError(
                node_id = self.id,
                err_param_key="col2",
                err_msg = "Second column name for concatenation cannot be empty."
            )
        if self.result_col is None:
            self.result_col = generate_default_col_name(self.id, "result")
        if self.result_col.strip() == "":
            raise NodeParameterError(
                node_id = self.id,
                err_param_key="result_col",
                err_msg = "Result column name cannot be empty."
            )
        if check_no_illegal_cols([self.result_col]) is False:
            raise NodeParameterError(
                node_id = self.id,
                err_param_key="result_col",
                err_msg = f"Result column name '{self.result_col}' contains illegal characters."
            )
        return

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [
            InPort(
                name="input",
                description="Input table with string columns to be concatenated.",
                accept=Pattern(
                    types={Schema.Type.TABLE}, table_columns={self.col1: {ColType.STR}, self.col2: {ColType.STR}}
                ),
                optional=False,
            )
        ], [
            OutPort(
                name="output",
                description="Output table after concatenating string columns.",
            )
        ]

    @override
    def infer_output_schemas(self, input_schemas: dict[str, Schema]) -> dict[str, Schema]:
        assert self.result_col is not None
        output_schema = input_schemas["input"].append_col(self.result_col, ColType.STR)
        return {"output": output_schema}

    @override
    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        input_table = input["input"].payload
        assert isinstance(input_table, Table)
        df = input_table.df
        df[self.result_col] = df[self.col1].astype(str) + df[self.col2].astype(str)
        output_data = Data.from_df(df)
        return {"output": output_data}
