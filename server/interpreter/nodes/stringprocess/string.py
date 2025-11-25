from typing import Literal, override

from server.models.data import Data
from server.models.exception import (
    NodeExecutionError,
    NodeParameterError,
    NodeValidationError,
)
from server.models.schema import (
    Pattern,
    Schema,
)

from ..base_node import BaseNode, InPort, OutPort, register_node

"""
This file defines string processing nodes for simple string type data.
"""

@register_node()
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
            ),
            InPort(
                name="strip_chars",
                description="Characters to be stripped from both ends of the string. If not provided, whitespace will be stripped.",
                accept=Pattern(types={Schema.Type.STR}),
                optional=True
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
        strip_chars: str | None
        if input.get("strip_chars") is not None:
            assert isinstance(input['strip_chars'].payload, str)
            strip_chars = input['strip_chars'].payload
        elif self.strip_chars is not None:
            strip_chars = self.strip_chars
        else:
            strip_chars = None
        res = input_str.strip(strip_chars)
        return {"output": Data(payload=res)}

@register_node()
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

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [
            InPort(
                name="input",
                description="Input string to be sliced.",
                accept=Pattern(types={Schema.Type.STR}),
                optional=False
            ),
            InPort(
                name="start",
                description="Start index for slicing.",
                accept=Pattern(types={Schema.Type.INT}),
                optional=True
            ),
            InPort(
                name="end",
                description="End index for slicing.",
                accept=Pattern(types={Schema.Type.INT}),
                optional=True
            )
        ], [
            OutPort(
                name="output",
                description="Output string after slicing."
            )
        ]

    @override
    def infer_output_schemas(self, input_schemas: dict[str, Schema]) -> dict[str, Schema]:
        if self.start is not None and self.end is not None:
            if input_schemas.get("start") is None and input_schemas.get("end") is None:
                raise NodeValidationError(
                    node_id = self.id,
                    err_inputs=["start", "end"],
                    err_msg = "Either both start and end parameters or both start and end inputs must be provided."
                )
        return {"output": Schema(type=Schema.Type.STR)}

    @override
    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        input_str = input["input"].payload
        assert isinstance(input_str, str)
        start: int
        if input.get("start") is not None:
            assert isinstance(input['start'].payload, int)
            start = input['start'].payload
        elif self.start is not None:
            start = self.start
        else:
            start = 0
        end: int
        if input.get("end") is not None:
            assert isinstance(input['end'].payload, int)
            end = input['end'].payload
        elif self.end is not None:
            end = self.end
        else:
            end = len(input_str)
        if start < 0 or end > len(input_str) or start > end:
            raise NodeExecutionError(
                node_id = self.id,
                err_msg = f"Slicing indices out of range: start={start}, end={end}, string length={len(input_str)}."
            )
        res = input_str[start:end]
        return {"output": Data(payload=res)}

@register_node()
class ReplaceNode(BaseNode):
    """
    Node to replace occurrences of a substring with another substring in a string.
    """
    old: str | None
    new: str | None
    
    @override
    def validate_parameters(self) -> None:
        if not self.type == "ReplaceNode":
            raise NodeParameterError(
                node_id = self.id,
                err_param_key="type",
                err_msg = "Node type must be 'ReplaceNode'."
            )
        if self.old is not None and self.new is not None:
            if self.old == self.new:
                raise NodeParameterError(
                    node_id = self.id,
                    err_param_key="old/new",
                    err_msg = "Old and new substrings for replacement cannot be the same."
                )

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [
            InPort(
                name="input",
                description="Input string for replacement.",
                accept=Pattern(types={Schema.Type.STR}),
                optional=False
            ),
            InPort(
                name="old",
                description="Substring to be replaced.",
                accept=Pattern(types={Schema.Type.STR}),
                optional=True
            ),
            InPort(
                name="new",
                description="Substring to replace with.",
                accept=Pattern(types={Schema.Type.STR}),
                optional=True
            )
        ], [
            OutPort(
                name="output",
                description="Output string after replacement."
            )
        ]

    @override
    def infer_output_schemas(self, input_schemas: dict[str, Schema]) -> dict[str, Schema]:
        if self.old is None and input_schemas.get("old") is None:
            raise NodeValidationError(
                node_id = self.id,
                err_msg = "Old substring for replacement must be provided."
            )
        if self.new is None and input_schemas.get("new") is None:
            raise NodeValidationError(
                node_id = self.id,
                err_msg = "New substring for replacement must be provided."
            )
        return {"output": Schema(type=Schema.Type.STR)}

    @override
    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        input_str = input["input"].payload
        assert isinstance(input_str, str)
        old: str
        if input.get("old") is not None:
            assert isinstance(input['old'].payload, str)
            old = input['old'].payload
        else:
            assert self.old is not None
            old = self.old
        new: str
        if input.get("new") is not None:
            assert isinstance(input['new'].payload, str)
            new = input['new'].payload
        else:
            assert self.new is not None
            new = self.new
        if old == new:
            raise NodeExecutionError(
                node_id = self.id,
                err_msg = "Old and new substrings for replacement cannot be the same."
            )
        res = input_str.replace(old, new)
        return {"output": Data(payload=res)}

@register_node()
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

@register_node()
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
