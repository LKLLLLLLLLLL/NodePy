from .BaseNode import BaseNode, InPort, OutPort, Schema, Data, NodeValidationError
from .Utils import CmpCondition, Visualization
from typing import Literal

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
            op=self.op,
            left = ("input1", None),
            right = ("input2", None)
        )
    
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        # Accept any primitive type (not TABLE)
        primitive_types = {
            Schema.DataType.INT,
            Schema.DataType.FLOAT,
            Schema.DataType.STR,
            Schema.DataType.BOOL
        }
        return [
            InPort(
                name="input1",
                accept_types=primitive_types,
                required=True,
                description="First input value"
            ),
            InPort(
                name="input2",
                accept_types=primitive_types,
                required=True,
                description="Second input value"
            )
        ], [
            OutPort(name="output", description="The comparison result")
        ]
    
    def validate_input(self, input: dict[str, Data]) -> None:
        # Ensure both inputs have the same type
        type1 = input["input1"].sche.type
        type2 = input["input2"].sche.type
        if type1 != type2:
            raise NodeValidationError(
                f"Input types must match: input1 is {type1}, input2 is {type2}"
            )
        assert(self._cond is not None)
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
        assert(self._cond is not None)
        # Static validate the condition
        self._cond.static_validate(input_schema)
        
        # Output is always BOOL
        return {"output": Schema(type=Schema.DataType.BOOL)}
    
    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        # Evaluate the condition (no idx needed for primitive types)
        assert(self._cond is not None)
        result = self._cond.evaluate(input)
        
        # Set visualization
        self.vis = Visualization(
            node_id=self.id,
            type=Visualization.Type.BOOL,
            payload=result
        )
        
        return {"output": Data(sche=Schema(type=Schema.DataType.BOOL), payload=result)}
