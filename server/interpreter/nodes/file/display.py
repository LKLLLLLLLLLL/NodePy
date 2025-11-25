from typing import Dict, List, override

from server.models.data import Data
from server.models.exception import NodeParameterError
from server.models.schema import Pattern, Schema

from ..base_node import BaseNode, InPort, OutPort, register_node


@register_node()
class DisplayNode(BaseNode):
    """
    Node which allows users to display files.
    It also allow users to download the files displayed.
    """

    @override
    def validate_parameters(self) -> None:
        if not self.type == "DisplayNode":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="type",
                err_msg="Node type must be 'DisplayNode'."
            )

    @override
    def port_def(self) -> tuple[List[InPort], List[OutPort]]:
        return [
            InPort(
                name="file",
                description="The file to be displayed.",
                accept=Pattern(
                    types={Schema.Type.FILE},
                    file_formats={"csv", "png", "jpg", "pdf"}
                )
            )
        ], []

    @override
    def infer_output_schemas(self, input_schemas: Dict[str, Schema]) -> Dict[str, Schema]:
        return {}

    @override
    def process(self, input: Dict[str, Data]) -> Dict[str, Data]:
        return {}
