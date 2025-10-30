from ..base_node import BaseNode, InPort, OutPort, register_node
from server.models.exception import NodeParameterError
from server.models.data import Data
from server.models.schema import (
    Pattern,
    Schema,
)
from typing import override, Literal

"""
This file defines string processing nodes for simple string type data.
"""

@register_node
class StripNode(BaseNode):
    """
    Node to strip leading and trailing whitespace or specified characters from string columns in a table.
    """
    strip_chars: str | None
    
    @override
    def validate_parameters(self) -> None:
        if not self.type == "StripNode":
            raise NodeParameterError(
                node_id = self.id,
                err_param_key="type",
                err_msg = "Node type must be 'StripNode'."
            )

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [
            InPort(
                name="input",
                description="Input string to be stripped.",
                accept=Pattern(types={Schema.Type.STR}),
                optional=False
            )
        ], [
            OutPort(
                name="output",
                description="Output string after stripping."
            )
        ]

    @override
    def infer_output_schemas(self, input_schemas: dict[str, Schema]) -> dict[str, Schema]:
        return {"output": Schema(type=Schema.Type.STR)}

    @override
    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        input_str = input["input"].payload
        assert isinstance(input_str, str)
        res = input_str.strip(self.strip_chars)
        return {"output": Data(payload=res)}

@register_node
class SliceNode(BaseNode):
    """
    Sliece the input string from start index to end index.
    """
    start: int | None
    end: int | None
    
    @override
    def validate_parameters(self) -> None:
        if not self.type == "SliceNode":
            raise NodeParameterError(
                node_id = self.id,
                err_param_key="type",
                err_msg = "Node type must be 'SliceNode'."
            )
        if self.start is None and self.end is None:
            raise NodeParameterError(
                node_id = self.id,
                err_param_key="start/end",
                err_msg = "At least one of start or end must be specified."
            )

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [
            InPort(
                name="input",
                description="Input string to be sliced.",
                accept=Pattern(types={Schema.Type.STR}),
                optional=False
            )
        ], [
            OutPort(
                name="output",
                description="Output string after slicing."
            )
        ]

    @override
    def infer_output_schemas(self, input_schemas: dict[str, Schema]) -> dict[str, Schema]:
        return {"output": Schema(type=Schema.Type.STR)}

    @override
    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        input_str = input["input"].payload
        assert isinstance(input_str, str)
        res = input_str[self.start:self.end]
        return {"output": Data(payload=res)}

@register_node
class ReplaceNode(BaseNode):
    """
    Node to replace occurrences of a substring with another substring in a string.
    """
    old: str
    new: str
    
    @override
    def validate_parameters(self) -> None:
        if not self.type == "ReplaceNode":
            raise NodeParameterError(
                node_id = self.id,
                err_param_key="type",
                err_msg = "Node type must be 'ReplaceNode'."
            )
        if not isinstance(self.old, str) or not isinstance(self.new, str):
            raise NodeParameterError(
                node_id = self.id,
                err_param_key="old/new",
                err_msg = "Both old and new must be strings."
            )

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [
            InPort(
                name="input",
                description="Input string for replacement.",
                accept=Pattern(types={Schema.Type.STR}),
                optional=False
            )
        ], [
            OutPort(
                name="output",
                description="Output string after replacement."
            )
        ]

    @override
    def infer_output_schemas(self, input_schemas: dict[str, Schema]) -> dict[str, Schema]:
        return {"output": Schema(type=Schema.Type.STR)}

    @override
    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        input_str = input["input"].payload
        assert isinstance(input_str, str)
        res = input_str.replace(self.old, self.new)
        return {"output": Data(payload=res)}

@register_node
class LowerOrUpperNode(BaseNode):
    """
    Node to convert string to lower case or upper case.
    """
    to_case: Literal["lower", "upper"]

    @override
    def validate_parameters(self) -> None:
        if not self.type == "LowerOrUpperNode":
            raise NodeParameterError(
                node_id = self.id,
                err_param_key="type",
                err_msg = "Node type must be 'LowerOrUpperNode'."
            )

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [
            InPort(
                name="input",
                description="Input string to be converted.",
                accept=Pattern(types={Schema.Type.STR}),
                optional=False
            )
        ], [
            OutPort(
                name="output",
                description="Output string after conversion."
            )
        ]

    @override
    def infer_output_schemas(self, input_schemas: dict[str, Schema]) -> dict:
        return {"output": Schema(type=Schema.Type.STR)}

    @override
    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        input_str = input["input"].payload
        assert isinstance(input_str, str)
        if self.to_case == "lower":
            res = input_str.lower()
        elif self.to_case == "upper":
            res = input_str.upper()
        else:
            raise NodeParameterError(
                node_id = self.id,
                err_param_key="to_case",
                err_msg = "to_case must be either 'lower' or 'upper'."
            )
        return {"output": Data(payload=res)}

@register_node
class ConcatNode(BaseNode):
    """
    Node to concatenate two strings.
    """
    
    @override
    def validate_parameters(self) -> None:
        if not self.type == "ConcatNode":
            raise NodeParameterError(
                node_id = self.id,
                err_param_key="type",
                err_msg = "Node type must be 'ConcatNode'."
            )

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [
            InPort(
                name="input1",
                description="First input string.",
                accept=Pattern(types={Schema.Type.STR}),
                optional=False
            ),
            InPort(
                name="input2",
                description="Second input string.",
                accept=Pattern(types={Schema.Type.STR}),
                optional=False
            )
        ], [
            OutPort(
                name="output",
                description="Output concatenated string."
            )
        ]

    @override
    def infer_output_schemas(self, input_schemas: dict[str, Schema]) -> dict[str, Schema]:
        return {"output": Schema(type=Schema.Type.STR)}

    @override
    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        str1 = input["input1"].payload
        str2 = input["input2"].payload
        assert isinstance(str1, str)
        assert isinstance(str2, str)
        res = str1 + str2
        return {"output": Data(payload=res)}
