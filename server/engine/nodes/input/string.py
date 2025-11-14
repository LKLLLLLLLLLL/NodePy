from typing import override

from server.models.data import Data
from server.models.exception import NodeParameterError
from server.models.schema import Schema

from ..base_node import BaseNode, InPort, OutPort, register_node


@register_node
class StringNode(BaseNode):
    """
    A node to generate a string.
    """
    value: str

    @override
    def validate_parameters(self) -> None:
        if not self.type == "StringNode":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="type",
                err_msg="Node type must be 'StringNode'."
            )
        return

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [], [OutPort(name="string", description="The string value")]

    @override
    def infer_output_schemas(self, input_schemas: dict[str, Schema]) -> dict[str, Schema]:
        return {"string": Schema(type=Schema.Type.STR)}

    @override
    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        return {"string": Data(payload=self.value)}