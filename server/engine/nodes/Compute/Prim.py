from ..BaseNode import BaseNode, InPort, OutPort, register_node
from typing import Literal, override
from ....models.exception import NodeParameterError, NodeValidationError, NodeExecutionError
from ....models.data import Data, Schema, Pattern

"""
This file defines compute nodes between primitive(float, int, str, bool) data.
"""

@register_node
class NumBinComputeNode(BaseNode):
    """
    A class for binary compute between two numeric inputs(int or float).
    """
    op: Literal["ADD", "SUB", "MUL", "DIV", "POW"]

    @override
    def validate_parameters(self) -> None:
        if not self.type == "NumBinComputeNode":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="type",
                err_msg="Node type must be 'NumBinComputeNode'."
            )

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [
            InPort(name='x', description='First numeric input', accept=Pattern(types={Schema.Type.INT, Schema.Type.FLOAT}), optional=False),
            InPort(name='y', description='Second numeric input', accept=Pattern(types={Schema.Type.INT, Schema.Type.FLOAT}), optional=False)
        ], [
            OutPort(name='result', description='Result of the binary operation')
        ]

    @override
    def infer_output_schemas(self, input_schemas: dict[str, Schema]) -> dict[str, Schema]:
        x_schema = input_schemas['x']
        y_schema = input_schemas['y']
        if not x_schema.type == y_schema.type:
            raise NodeValidationError(
                node_id=self.id,
                err_input=["x", "y"],
                err_msg=f"Input types must match: x is {x_schema.type}, y is {y_schema.type}"
            )
        if x_schema.type == Schema.Type.FLOAT: # avoid implicit int->float conversion
            return {'result': Schema(type=Schema.Type.FLOAT)}
        elif self.op == "DIV":
            return {'result': Schema(type=Schema.Type.FLOAT)}
        elif self.op == "POW":
            return {'result': Schema(type=Schema.Type.FLOAT)}
        else:
            return {'result': Schema(type=Schema.Type.INT)}

    @override
    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        x = input['x'].payload
        y = input['y'].payload
        assert isinstance(x, (int, float))
        assert isinstance(y, (int, float))
        
        res = None
        if self.op == "ADD":
            res = x + y
        elif self.op == "SUB":
            res = x - y
        elif self.op == "MUL":
            res = x * y
        elif self.op == "DIV":
            if y == 0:
                raise NodeExecutionError(
                    node_id=self.id,
                    err_msg=f"Division by zero in node {self.id}."
                )
            res = x / y
        elif self.op == "POW":
            res = float(x ** y)
        else:
            raise NodeExecutionError(
                node_id=self.id,
                err_msg=f"Unsupported operation '{self.op}' in node {self.id}."
            )
        return {'result': Data(payload=res)}
    
@register_node
class NumUnaryComputeNode(BaseNode):
    """
    A node for unary compute on a numeric input(int or float).
    """
    op: Literal["NEG", "ABS", "SQRT"]

    @override
    def validate_parameters(self) -> None:
        if not self.type == "NumUnaryComputeNode":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="type",
                err_msg="Node type must be 'NumUnaryComputeNode'."
            )

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [
            InPort(name='x', description='Numeric input', accept=Pattern(types={Schema.Type.INT, Schema.Type.FLOAT}), optional=False)
        ], [
            OutPort(name='result', description='Result of the unary operation')
        ]

    @override
    def infer_output_schemas(self, input_schemas: dict[str, Schema]) -> dict[str, Schema]:
        x_schema = input_schemas['x']
        if self.op == "SQRT":
            return {'result': Schema(type=Schema.Type.FLOAT)}
        else:
            return {'result': x_schema}

    @override
    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        x = input['x'].payload
        assert isinstance(x, (int, float))
        
        res = None
        if self.op == "NEG":
            res = -x
        elif self.op == "ABS":
            res = abs(x)
        elif self.op == "SQRT":
            if x < 0:
                raise NodeExecutionError(
                    node_id=self.id,
                    err_msg=f"Cannot take square root of negative number in node {self.id}."
                )
            res = x ** 0.5
        else:
            raise NodeExecutionError(
                node_id=self.id,
                err_msg=f"Unsupported operation '{self.op}' in node {self.id}."
            )
        return {'result': Data(payload=res)}

@register_node
class CmpNode(BaseNode):
    """
    A node for primitive comparison.
    The input must be the type of int, float, str or bool.
    """
    op: Literal["EQ", "NE", "GT", "LT", "GE", "LE"]

    @override
    def validate_parameters(self) -> None:
        if not self.type == "CmpNode":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="type",
                err_msg="Node type must be 'CmpNode'."
            )

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        primitive_types = Pattern(types={
            Schema.Type.INT,
            Schema.Type.FLOAT,
            Schema.Type.STR,
            Schema.Type.BOOL
        })
        return [
            InPort(name='x', description='First value', accept=primitive_types, optional=False),
            InPort(name='y', description='Second value', accept=primitive_types, optional=False)
        ], [
            OutPort(name='result', description='Comparison result')
        ]

    @override
    def infer_output_schemas(self, input_schemas: dict[str, Schema]) -> dict[str, Schema]:
        # Check if both inputs have the same type
        x_type = input_schemas['x'].type
        y_type = input_schemas['y'].type
        if x_type != y_type:
            raise NodeValidationError(
                node_id=self.id,
                err_input=["x", "y"],
                err_msg=f"Input types must match: x is {x_type}, y is {y_type}"
            )
        return {'result': Schema(type=Schema.Type.BOOL)}

    @override
    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        x = input['x'].payload
        y = input['y'].payload
        assert isinstance(x, (int, float, str, bool))
        assert isinstance(y, (int, float, str, bool))
        
        res = None
        if self.op == "EQ":
            res = x == y
        elif self.op == "NE":
            res = x != y
        elif self.op == "GT":
            res = x > y  # type: ignore
        elif self.op == "LT":
            res = x < y  # type: ignore
        elif self.op == "GE":
            res = x >= y  # type: ignore
        elif self.op == "LE":
            res = x <= y  # type: ignore
        else:
            raise NodeExecutionError(
                node_id=self.id,
                err_msg=f"Unsupported operation '{self.op}' in node {self.id}."
            )
        return {'result': Data(payload=res)}

@register_node
class BoolBinComputeNode(BaseNode):
    """
    Node to compute binary boolean operations.
    """
    op: Literal["AND", "OR", "XOR", "SUB"]
    
    def validate_parameters(self) -> None:
        if not self.type == "BoolBinComputeNode":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="type",
                err_msg="Node type must be 'BoolBinComputeNode'."
            )

    @override 
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [
            InPort(name='x', description='First boolean input', accept=Pattern(types={Schema.Type.BOOL}), optional=False),
            InPort(name='y', description='Second boolean input', accept=Pattern(types={Schema.Type.BOOL}), optional=False)
        ], [
            OutPort(name='result', description='Result of the boolean operation')
        ]

    @override
    def infer_output_schemas(self, input_schemas: dict[str, Schema]) -> dict[str, Schema]:
        return {'result': Schema(type=Schema.Type.BOOL)}

    @override
    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        x = input['x'].payload
        y = input['y'].payload
        assert isinstance(x, bool)
        assert isinstance(y, bool)
        
        res = None
        if self.op == "AND":
            res = x and y
        elif self.op == "OR":
            res = x or y
        elif self.op == "XOR":
            res = x ^ y
        elif self.op == "SUB":
            res = x and (not y)
        else:
            raise NodeExecutionError(
                node_id=self.id,
                err_msg=f"Unsupported operation '{self.op}' in node {self.id}."
            )
        return {'result': Data(payload=res)}

@register_node
class BoolUnaryComputeNode(BaseNode):
    """
    Node to compute unary boolean operations.
    Only "NOT" is supported.
    """

    @override
    def validate_parameters(self) -> None:
        if not self.type == "BoolUnaryComputeNode":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="type",
                err_msg="Node type must be 'BoolUnaryComputeNode'."
            )

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [
            InPort(name='x', description='Boolean input', accept=Pattern(types={Schema.Type.BOOL}), optional=False)
        ], [
            OutPort(name='result', description='Result of NOT operation')
        ]

    @override
    def infer_output_schemas(self, input_schemas: dict[str, Schema]) -> dict[str, Schema]:
        return {'result': Schema(type=Schema.Type.BOOL)}

    @override
    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        x = input['x'].payload
        assert isinstance(x, bool)
        res = not x
        return {'result': Data(payload=res)}