import math
from typing import Literal, override

from server.models.data import Data
from server.models.exception import (
    NodeExecutionError,
    NodeParameterError,
)
from server.models.schema import Pattern, Schema

from ..base_node import BaseNode, InPort, OutPort, register_node

"""
This file defines nodes for converting data types.
"""

@register_node()
class ToStringNode(BaseNode):
    """
    Convert input data to string type.
    """
    
    @override
    def validate_parameters(self) -> None:
        if not self.type == "ToStringNode":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="type",
                err_msg="Type must be 'ToStringNode'",
            )
        return

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [
            InPort(
                name='input',
                description='Input data to be converted to string type.',
                optional=False,
                accept=Pattern(
                    types={Schema.Type.BOOL, Schema.Type.INT, Schema.Type.FLOAT}
                )
            )
        ], [
            OutPort(
                name="output",
                description="Output data converted to string type.",
            )
        ]

    @override
    def infer_output_schemas(self, input_schemas: dict[str, Schema]) -> dict[str, Schema]:
        return {'out': Schema(type=Schema.Type.STR)}

    @override
    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        assert 'input' in input
        input_data = input['input'].payload
        assert isinstance(input_data, (bool, int, float))

        output: str
        output = str(input_data)
        return {'output': Data(payload=output)}

@register_node()
class ToIntNode(BaseNode):
    """
    Convert input data to integer type. Inputs of type float will be rounded down.
    """
    method: Literal['FLOOR', 'CEIL', 'ROUND']

    @override
    def validate_parameters(self) -> None:
        if not self.type == "ToIntNode":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="type",
                err_msg="Type must be 'ToIntNode'",
            )
        return

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [
            InPort(
                name="input",
                description="Input data to be converted to integer type.",
                optional=False,
                accept=Pattern(
                    types={Schema.Type.BOOL, Schema.Type.FLOAT, Schema.Type.STR}
                )
            )
        ], [
            OutPort(
                name='output',
                description='Output data converted to integer type.',
            )
        ]

    @override
    def infer_output_schemas(self, input_schemas: dict[str, Schema]) -> dict[str, Schema]:
        return {'output': Schema(type=Schema.Type.INT)}

    @override
    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        assert 'input' in input
        input_data = input['input'].payload
        assert isinstance(input_data, (bool, float, str))

        def float_to_int(val: float) -> int:
            if self.method == 'floor':
                return math.floor(val)
            elif self.method == 'ceil':
                return math.ceil(val)
            elif self.method == 'round':
                return round(val)
            else:
                raise NodeExecutionError(
                    node_id=self.id,
                    err_msg=f"Invalid method '{self.method}' for ToIntNode."
                )

        output: int
        if isinstance(input_data, bool):
            output = int(input_data)
        elif isinstance(input_data, float):
            output = float_to_int(input_data)
        elif isinstance(input_data, str):
            try:
                output = int(input_data)
            except ValueError:
                try:
                    float_val = float(input_data)
                    output = float_to_int(float_val)
                except ValueError:
                    raise NodeExecutionError(
                        node_id=self.id,
                        err_msg=f"Cannot convert string '{input_data}' to integer."
                    )
        else:
            raise NodeExecutionError(
                node_id=self.id,
                err_msg=f"Unsupported input type '{type(input_data)}' for ToIntNode."
            )
        return {'output': Data(payload=output)}

@register_node()
class ToFloatNode(BaseNode):
    """
    Convert input data to float type.
    """
    
    @override
    def validate_parameters(self) -> None:
        if not self.type == "ToFloatNode":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="type",
                err_msg="Type must be 'ToFloatNode'",
            )
        return

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [
            InPort(
                name="input",
                description="Input data to be converted to float type.",
                optional=False,
                accept=Pattern(
                    types={Schema.Type.BOOL, Schema.Type.INT, Schema.Type.STR}
                )
            )
        ], [
            OutPort(
                name='output',
                description='Output data converted to float type.',
            )
        ]

    @override
    def infer_output_schemas(self, input_schemas: dict[str, Schema]) -> dict[str, Schema]:
        return {'output': Schema(type=Schema.Type.FLOAT)}

    @override
    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        assert 'input' in input
        input_data = input['input'].payload
        assert isinstance(input_data, (bool, int, str))

        output: float
        if isinstance(input_data, bool):
            output = float(input_data)
        elif isinstance(input_data, int):
            output = float(input_data)
        elif isinstance(input_data, str):
            try:
                output = float(input_data)
            except ValueError:
                raise NodeExecutionError(
                    node_id=self.id,
                    err_msg=f"Cannot convert string '{input_data}' to float."
                )
        else:
            raise NodeExecutionError(
                node_id=self.id,
                err_msg=f"Unsupported input type '{type(input_data)}' for ToFloatNode."
            )
        return {'output': Data(payload=output)}

@register_node()
class ToBoolNode(BaseNode):
    """
    Convert input data to boolean type.
    """
    
    @override
    def validate_parameters(self) -> None:
        if not self.type == "ToBoolNode":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="type",
                err_msg="Type must be 'ToBoolNode'",
            )
        return

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [
            InPort(
                name="input",
                description="Input data to be converted to boolean type.",
                optional=False,
                accept=Pattern(
                    types={Schema.Type.INT, Schema.Type.FLOAT, Schema.Type.STR}
                )
            )
        ], [
            OutPort(
                name='output',
                description='Output data converted to boolean type.',
            )
        ]

    @override
    def infer_output_schemas(self, input_schemas: dict[str, Schema]) -> dict[str, Schema]:
        return {'output': Schema(type=Schema.Type.BOOL)}

    @override
    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        assert 'input' in input
        input_data = input['input'].payload
        assert isinstance(input_data, (int, float, str))

        output: bool
        if isinstance(input_data, int):
            output = bool(input_data)
        elif isinstance(input_data, float):
            output = bool(input_data)
        elif isinstance(input_data, str):
            lowered = input_data.strip().lower()
            if lowered in {'true', '1', 'yes'}:
                output = True
            elif lowered in {'false', '0', 'no'}:
                output = False
            else:
                raise NodeExecutionError(
                    node_id=self.id,
                    err_msg=f"Cannot convert string '{input_data}' to boolean."
                )
        else:
            raise NodeExecutionError(
                node_id=self.id,
                err_msg=f"Unsupported input type '{type(input_data)}' for ToBoolNode."
            )
        return {'output': Data(payload=output)}
