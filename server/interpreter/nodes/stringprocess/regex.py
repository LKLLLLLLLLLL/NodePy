from typing import Any, override

from pydantic import PrivateAttr

from server.models.data import Data, Table
from server.models.exception import NodeParameterError
from server.models.schema import (
    ColType,
    Pattern,
    Schema,
    TableSchema,
    check_no_illegal_cols,
    generate_default_col_name,
)

from ..base_node import BaseNode, InPort, OutPort, register_node

"""
This file defines some regex string processing nodes.
"""

@register_node()
class RegexMatchNode(BaseNode):
    """
    Node to match regex pattern in a string.
    """
    pattern: str
    
    @override
    def validate_parameters(self) -> None:
        if not self.type == "RegexMatchNode":
            raise NodeParameterError(
                node_id = self.id,
                err_param_key="type",
                err_msg = "Node type must be 'RegexMatchNode'."
            )
        return

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [
            InPort(
                name="string",
                description="Input string to match the regex pattern against.",
                accept=Pattern(
                    types={Schema.Type.STR}
                )
            )
        ], [
            OutPort(
                name="is_match",
                description="Boolean indicating whether the regex pattern matches the input string.",
            )
        ]

    @override
    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        import re

        assert isinstance(input["string"].payload, str)
        input_string: str = input["string"].payload
        is_match = bool(re.fullmatch(self.pattern, input_string))
        return {
            "is_match": Data(payload=is_match)
        }

@register_node()
class BatchRegexMatchNode(BaseNode):
    """
    Node to match regex pattern in string columns of a table.
    """
    pattern: str
    col: str
    result_col: str | None = None

    _col_types: dict[str, ColType] | None = PrivateAttr(None)

    @override
    def validate_parameters(self) -> None:
        if not self.type == "BatchRegexMatchNode":
            raise NodeParameterError(
                node_id = self.id,
                err_param_key="type",
                err_msg = "Node type must be 'BatchRegexMatchNode'."
            )
        if self.col.strip() == "":
            raise NodeParameterError(
                node_id = self.id,
                err_param_key="col",
                err_msg = "Column name for regex matching cannot be empty."
            )
        if self.result_col is None:
            self.result_col = generate_default_col_name(self.id, "is_match")
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
                description="Input table with string columns to perform regex matching.",
                accept=Pattern(
                    types={Schema.Type.TABLE}, table_columns={self.col: {ColType.STR}}
                )
            )
        ], [
            OutPort(
                name="output",
                description="Output table with an additional boolean column indicating regex match results.",
            )
        ]

    @override
    def infer_output_schemas(self, input_schemas: dict[str, Schema]) -> dict[str, Schema]:
        input_schema = input_schemas["input"]
        assert self.result_col is not None
        assert input_schema.tab is not None
        if not input_schema.tab.validate_new_col_name(self.result_col):
            raise NodeParameterError(
                node_id = self.id,
                err_param_key="result_col",
                err_msg = f"Result column name '{self.result_col}' is not valid."
            )
        output_schema = input_schema.append_col(self.result_col, ColType.BOOL)
        assert output_schema.tab is not None
        self._col_types = output_schema.tab.col_types
        return {
            "output": output_schema
        }

    @override
    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        assert isinstance(input["input"].payload, Table)
        assert input["input"].payload.df is not None
        df = input["input"].payload.df.copy()
        assert self.result_col is not None
        df[self.result_col] = df[self.col].str.fullmatch(self.pattern, na=False).astype(bool)
        assert self._col_types is not None
        output_table = Data(
            payload=Table(
                df=df,
                col_types=self._col_types
            )
        )

        return {
            "output": output_table
        }

    @override
    @classmethod
    def hint(cls, input_schemas: dict[str, Schema], current_params: dict) -> dict[str, Any]:
        hint = {}
        if "input" in input_schemas:
            input_schema = input_schemas["input"]
            if input_schema.type == Schema.Type.TABLE and input_schema.tab is not None:
                str_cols = [
                    col for col, col_type in input_schema.tab.col_types.items() if col_type == ColType.STR
                ]
                if str_cols:
                    hint["col_choices"] = str_cols[0]
        return hint


@register_node()
class RegexExtractNode(BaseNode):
    """
    Node to find all regex pattern from a string, returning a table of matches.
    """

    pattern: str

    _col_types: dict[str, ColType] | None = PrivateAttr(None)

    @override
    def validate_parameters(self) -> None:
        if not self.type == "RegexExtractNode":
            raise NodeParameterError(
                node_id = self.id,
                err_param_key="type",
                err_msg = "Node type must be 'RegexExtractNode'."
            )
        return

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [
            InPort(
                name="string",
                description="Input string to extract regex pattern matches from.",
                accept=Pattern(
                    types={Schema.Type.STR}
                )
            )
        ], [
            OutPort(
                name="matches",
                description="Table of all regex pattern matches found in the input string.",
            )
        ]

    @override
    def infer_output_schemas(self, input_schemas: dict[str, Schema]) -> dict[str, Schema]:
        import re
        
        # 1. judge number of capturing groups
        try:
            num_groups = re.compile(self.pattern).groups
        except re.error:
            raise NodeParameterError(
                node_id=self.id, 
                err_param_key="pattern", 
                err_msg="Invalid regex pattern.")

        col_types: dict[str, ColType] = {}
        if num_groups == 0:
            col_types["match"] = ColType.STR
        else:
            col_types = {f"group_{i+1}": ColType.STR for i in range(num_groups)}
        # 2. check generated column names
        if not check_no_illegal_cols(list(col_types.keys())):
            raise NodeParameterError(
                node_id=self.id, 
                err_param_key="pattern", 
                err_msg="Generated column names from regex groups are invalid."
            )

        output_schema = Schema(
            type = Schema.Type.TABLE,
            tab = TableSchema(col_types = col_types)
        )

        assert output_schema.tab is not None
        self._col_types = output_schema.tab.col_types

        return {
            "matches": output_schema
        }

    @override
    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        import re

        import pandas as pd

        assert isinstance(input["string"].payload, str)
        input_string: str = input["string"].payload

        matches = re.findall(self.pattern, input_string)

        num_groups = re.compile(self.pattern).groups
        col_names: list[str]
        if num_groups == 0:
            col_names = ["match_0"]
        else:
            col_names = [f"group_{i + 1}" for i in range(num_groups)]

        df = pd.DataFrame(matches, columns=col_names)
        assert self._col_types is not None
        output_table = Data(
            payload=Table(
                df=df,
                col_types=self._col_types
            )
        )
        return {"matches": output_table}
