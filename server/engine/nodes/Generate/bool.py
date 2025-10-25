from ..BaseNode import InPort, OutPort, BaseNode, register_node
from server.models.data import Data
from server.models.schema import Schema
from typing import override
from server.models.exception import NodeParameterError


@register_node
class BoolNode(BaseNode):
    """
    A node to generate a constant boolean value.
    """

    value: bool

    @override
    def validate_parameters(self) -> None:
        if not self.type == "ConstNode":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="type",
                err_msg="Node type must be 'ConstNode'.",
            )
        return

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [], [OutPort(name="const", description="The constant value")]

    @override
    def infer_output_schemas(
        self, input_schemas: dict[str, Schema]
    ) -> dict[str, Schema]:
        return {"const": Schema(type=Schema.Type.BOOL)}

    @override
    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        assert self.value is not None
        return {"const": Data(payload=self.value)}
