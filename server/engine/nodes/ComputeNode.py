from .BaseNode import BaseNode, InPort, OutPort, Data, Schema, NodeValidationError
from .Utils import Visualization, CmpCondition
from typing import Literal

"""
A series of nodes to compute int, float, bool values (primitive values).
These nodes work on primitive inputs (not TABLE).
"""

class BinNumComputeNode(BaseNode):
    """
    Node to compute binary operations on two numeric inputs(int or float).
    Support operations: ADD, SUB, MUL, DIV, POW.
    """
    op: Literal["ADD", "SUB", "MUL", "DIV", "POW"]

    def validate_parameters(self) -> None:
        if not self.type == "BinNumComputeNode":
            raise NodeValidationError("Node type must be 'BinNumComputeNode'.")

    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        num_types = {Schema.DataType.INT, Schema.DataType.FLOAT}
        return [
            InPort(name="left", accept_types=num_types, description="Left operand"),
            InPort(name="right", accept_types=num_types, description="Right operand"),
        ], [OutPort(name="output", description="Result")]

    def validate_input(self, input: dict[str, Data]) -> None:
        right_operand = input["right"].payload
        assert(isinstance(right_operand, (int, float)))
        if self.op == "DIV" and right_operand == 0:
            raise NodeValidationError("Division by zero")

    def infer_output_schema(self, input_schema: dict[str, Schema]) -> dict[str, Schema]:
        left = input_schema["left"].type
        right = input_schema["right"].type
        # If either is FLOAT, result is FLOAT. For DIV always FLOAT.
        if self.op == "DIV":
            out_type = Schema.DataType.FLOAT
        elif left == Schema.DataType.FLOAT or right == Schema.DataType.FLOAT:
            out_type = Schema.DataType.FLOAT
        else:
            out_type = Schema.DataType.INT
        return {"output": Schema(type=out_type)}

    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        a = input["left"].payload
        b = input["right"].payload
        # ensure numeric python types
        assert isinstance(a, (int, float))
        assert isinstance(b, (int, float))

        res = None
        if self.op == "ADD":
            res = a + b
        elif self.op == "SUB":
            res = a - b
        elif self.op == "MUL":
            res = a * b
        elif self.op == "DIV":
            res = float(a) / float(b)
        elif self.op == "POW":
            res = a ** b
        assert(res is not None)

        out_schema = self.infer_output_schema({"left": input["left"].sche, "right": input["right"].sche})["output"]
        # set visualization
        self.vis = Visualization(node_id=self.id, type=(Visualization.Type.FLOAT if out_schema.type == Schema.DataType.FLOAT else Visualization.Type.INT), payload=res)
        return {"output": Data(sche=out_schema, payload=res)}


class UnaryNumComputeNode(BaseNode):
    """
    Node to compute unary operations on one numeric input(int or float).
    Support operations: NEG, ABS, SQRT.
    """
    op: Literal["NEG", "ABS", "SQRT"]

    def validate_parameters(self) -> None:
        if not self.type == "UnaryNumComputeNode":
            raise NodeValidationError("Node type must be 'UnaryNumComputeNode'.")

    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        num_types = {Schema.DataType.INT, Schema.DataType.FLOAT}
        return [InPort(name="input", accept_types=num_types, description="Operand")], [OutPort(name="output", description="Result")]

    def validate_input(self, input: dict[str, Data]) -> None:
        v = input["input"].payload
        assert isinstance(v, (int, float))
        if self.op == "SQRT" and v < 0:
            raise NodeValidationError("Cannot sqrt negative number")
        pass

    def infer_output_schema(self, input_schema: dict[str, Schema]) -> dict[str, Schema]:
        in_type = input_schema["input"].type
        if self.op == "SQRT":
            out_type = Schema.DataType.FLOAT
        else:
            out_type = in_type
        return {"output": Schema(type=out_type)}

    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        v = input["input"].payload
        assert isinstance(v, (int, float))
        if self.op == "NEG":
            res = -v
        elif self.op == "ABS":
            res = abs(v)
        elif self.op == "SQRT":
            res = float(v) ** 0.5
        else:
            raise NodeValidationError(f"Unsupported op: {self.op}")

        out_schema = self.infer_output_schema({"input": input["input"].sche})["output"]
        self.vis = Visualization(node_id=self.id, type=(Visualization.Type.FLOAT if out_schema.type == Schema.DataType.FLOAT else Visualization.Type.INT), payload=res)
        return {"output": Data(sche=out_schema, payload=res)}

class CmpNode(BaseNode):
    """
    Primitives compare node.
    The two input must be of the same type of int, float, str, bool.
    Return a bool value.
    """

    op: Literal["EQ", "NE", "GT", "LT", "GE", "LE"]
    _cond: CmpCondition | None = None

    def validate_parameters(self) -> None:
        if not self.type == "CmpNode":
            raise NodeValidationError("Node type must be 'CmpNode'.")
        # set CmpCondition
        self._cond = CmpCondition(
            op=self.op, left=("input1", None), right=("input2", None)
        )

    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        # Accept any primitive type (not TABLE)
        primitive_types = {
            Schema.DataType.INT,
            Schema.DataType.FLOAT,
            Schema.DataType.STR,
            Schema.DataType.BOOL,
        }
        return [
            InPort(
                name="input1",
                accept_types=primitive_types,
                required=True,
                description="First input value",
            ),
            InPort(
                name="input2",
                accept_types=primitive_types,
                required=True,
                description="Second input value",
            ),
        ], [OutPort(name="output", description="The comparison result")]

    def validate_input(self, input: dict[str, Data]) -> None:
        # Ensure both inputs have the same type
        type1 = input["input1"].sche.type
        type2 = input["input2"].sche.type
        if type1 != type2:
            raise NodeValidationError(
                f"Input types must match: input1 is {type1}, input2 is {type2}"
            )
        assert self._cond is not None
        # Dynamic validate the condition
        self._cond.dynamic_validate(input)

    def infer_output_schema(self, input_schema: dict[str, Schema]) -> dict[str, Schema]:
        # Static validate: ensure both inputs have the same type
        type1 = input_schema["input1"].type
        type2 = input_schema["input2"].type
        if type1 != type2:
            raise NodeValidationError(
                f"Input types must match: input1 is {type1}, input2 is {type2}"
            )
        assert self._cond is not None
        # Static validate the condition
        self._cond.static_validate(input_schema)

        # Output is always BOOL
        return {"output": Schema(type=Schema.DataType.BOOL)}

    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        # Evaluate the condition (no idx needed for primitive types)
        assert self._cond is not None
        result = self._cond.evaluate(input)

        # Set visualization
        self.vis = Visualization(
            node_id=self.id, type=Visualization.Type.BOOL, payload=result
        )

        return {"output": Data(sche=Schema(type=Schema.DataType.BOOL), payload=result)}

class BoolBinComputeNode(BaseNode):
    """
    Node to compute binary operations on two boolean inputs.
    Support operations: AND, OR, XOR, SUB.
    """
    op: Literal["AND", "OR", "XOR", "SUB"]

    def validate_parameters(self) -> None:
        if not self.type == "BoolBinComputeNode":
            raise NodeValidationError("Node type must be 'BoolBinComputeNode'.")

    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [InPort(name="left", accept_types={Schema.DataType.BOOL}), InPort(name="right", accept_types={Schema.DataType.BOOL})], [OutPort(name="output")]

    def validate_input(self, input: dict[str, Data]) -> None:
        pass

    def infer_output_schema(self, input_schema: dict[str, Schema]) -> dict[str, Schema]:
        return {"output": Schema(type=Schema.DataType.BOOL)}

    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        a = input["left"].payload
        b = input["right"].payload
        assert isinstance(a, bool) and isinstance(b, bool)
        res = None
        if self.op == "AND":
            res = a and b
        elif self.op == "OR":
            res = a or b
        elif self.op == "XOR":
            res = bool(a) ^ bool(b)
        elif self.op == "SUB":
            res = bool(a) and (not bool(b))
        assert(res is not None)

        out_schema = Schema(type=Schema.DataType.BOOL)
        self.vis = Visualization(node_id=self.id, type=Visualization.Type.BOOL, payload=res)
        return {"output": Data(sche=out_schema, payload=res)}


class BoolNotNode(BaseNode):
    """
    Node to compute NOT operation on one boolean input.
    """
    def validate_parameters(self) -> None:
        if not self.type == "BoolNotNode":
            raise NodeValidationError("Node type must be 'BoolNotNode'.")

    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [InPort(name="input", accept_types={Schema.DataType.BOOL})], [OutPort(name="output")]

    def validate_input(self, input: dict[str, Data]) -> None:
        pass

    def infer_output_schema(self, input_schema: dict[str, Schema]) -> dict[str, Schema]:
        return {"output": Schema(type=Schema.DataType.BOOL)}

    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        v = input["input"].payload
        assert isinstance(v, bool)
        res = not v
        out_schema = Schema(type=Schema.DataType.BOOL)
        self.vis = Visualization(node_id=self.id, type=Visualization.Type.BOOL, payload=res)
        return {"output": Data(sche=out_schema, payload=res)}