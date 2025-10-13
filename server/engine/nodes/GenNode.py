from .BaseNode import BaseNode, NodeValidationError, InPort, OutPort, Data, Schema
from typing import Literal
from .Utils import Visualization


"""
A series of nodes to generate primitive() data.
"""


class ConstNode(BaseNode):
    """
    A node to generate a constant value.
    Only support generate str, float, int, bool.
    """
    value: str | float | int | bool
    data_type: Literal["str", "float", "int", "bool"]

    def validate_parameters(self) -> None:
        if not self.type == "ConstNode":
            raise NodeValidationError("Node type must be 'ConstNode'.")
        if self.data_type == "str":
            if not isinstance(self.value, str):
                raise NodeValidationError("value must be str when data_type is 'str'.")
        elif self.data_type == "float":
            if not isinstance(self.value, float):
                raise NodeValidationError("value must be float when data_type is 'float'.")
        elif self.data_type == "int":
            if not isinstance(self.value, int):
                raise NodeValidationError("value must be int when data_type is 'int'.")
        elif self.data_type == "bool":
            if not isinstance(self.value, bool):
                raise NodeValidationError("value must be bool when data_type is 'bool'.")
        return
    
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [], [OutPort(name="output", description="The constant value")]
    
    def validate_input(self, input: dict[str, Data]) -> None:
        return # no input
    
    def _compute_output_schema(self) -> Schema:
        """
        Centralized schema computation logic.
        This ensures infer_output_schema and process return consistent schemas.
        """
        type_map = {
            "str": Schema.DataType.STR,
            "float": Schema.DataType.FLOAT,
            "int": Schema.DataType.INT,
            "bool": Schema.DataType.BOOL,
        }
        output_type = type_map[self.data_type]
        return Schema(type=output_type, columns=None)
    
    def _set_visualization(self) -> None:
        """Set visualization based on data type"""
        vis_type_map = {
            "str": Visualization.Type.STR,
            "float": Visualization.Type.FLOAT,
            "int": Visualization.Type.INT,
            "bool": Visualization.Type.BOOL,
        }
        self.vis = Visualization(
            type=vis_type_map[self.data_type],
            node_id=self.id,
            payload=self.value
        )
    
    def infer_output_schema(self, input_schema: dict[str, Schema]) -> dict[str, Schema]:
        # Delegate to centralized schema computation
        return {"output": self._compute_output_schema()}
    
    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        self._set_visualization()
        return {"output": Data(sche=self._compute_output_schema(), payload=self.value)}
