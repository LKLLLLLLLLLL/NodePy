from ..BaseNode import InPort, OutPort, BaseNode, register_node
from ..DataType import Schema, Data
from typing import Literal, Optional, override
from ..Exceptions import NodeParameterError

@register_node
class ConstNode(BaseNode):
    """
    A node to generate a constant value(float, bool, int).
    """
    value: Optional[float | int | str | bool]
    data_type: Literal["float", "int", "str", "bool"]

    @override
    def validate_parameters(self) -> None:
        if not self.type == "ConstNode":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="type",
                err_msg="Node type must be 'ConstNode'."
            )
        if self.data_type == "str":
            if not isinstance(self.value, str):
                raise NodeParameterError(
                    node_id=self.id,
                    err_param_key="value",
                    err_msg="value must be str when data_type is 'str'."
                )
        elif self.data_type == "float":
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
        elif self.data_type == "bool":
            if not isinstance(self.value, bool):
                raise NodeParameterError(
                    node_id=self.id,
                    err_param_key="value",
                    err_msg="value must be bool when data_type is 'bool'."
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
        elif self.data_type == 'bool':
            return {"const": Schema(type=Schema.Type.BOOL)}
        else:
            raise TypeError(f"Unsupported data_type: {self.data_type}")

    @override
    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        assert self.value is not None
        return {"const": Data(payload = self.value)}