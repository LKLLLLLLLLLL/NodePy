from ..BaseNode import InPort, OutPort, BaseNode, register_node
from server.models.data import Data
from server.models.schema import Schema
from typing import Literal, Optional, override
from server.models.exception import NodeParameterError

@register_node
class ConstNode(BaseNode):
    """
    A node to generate a constant value(float, int).
    """
    value: Optional[float | int]
    data_type: Literal["float", "int"]

    @override
    def validate_parameters(self) -> None:
        if not self.type == "ConstNode":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="type",
                err_msg="Node type must be 'ConstNode'."
            )
        if self.data_type == "float":
            if not isinstance(self.value, float):
                raise NodeParameterError(
                    node_id=self.id,
                    err_param_key="value",
                    err_msg="value must be float when data_type is 'float'."
                )
        elif self.data_type == "int":
            if not isinstance(self.value, int):
                raise NodeParameterError(
                    node_id=self.id,
                    err_param_key="value",
                    err_msg="value must be int when data_type is 'int'."
                )
        return

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [], [OutPort(name="const", description="The constant value")]

    @override
    def infer_output_schemas(self, input_schemas: dict[str, Schema]) -> dict[str, Schema]:
        if self.data_type == "float":
            return {"const": Schema(type=Schema.Type.FLOAT)}
        elif self.data_type == "int":
            return {"const": Schema(type=Schema.Type.INT)}
        else:
            raise TypeError(f"Unsupported data_type: {self.data_type}")

    @override
    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        assert self.value is not None
        return {"const": Data(payload = self.value)}