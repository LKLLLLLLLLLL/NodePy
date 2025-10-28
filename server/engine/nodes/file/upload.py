from ..base_node import BaseNode, InPort, OutPort, register_node
from typing import List, Dict, override
from server.models.exception import NodeParameterError
from server.models.data import Data, File
from server.models.schema import (
    Schema,
    FileSchema
)

@register_node
class UploadNode(BaseNode):
    """
    Node which allows users to upload files.
    """
    file: File
    
    @override
    def validate_parameters(self) -> None:
        if not self.type == "UploadNode":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="type",
                err_msg="Node type must be 'UploadNode'."
            )
        file_manager = self.global_config.file_manager
        if not file_manager.check_file_exists_sync(self.file):
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="file",
                err_msg=f"File with id {self.file.model_dump()} does not exist."
            )

    @override
    def port_def(self) -> tuple[List[InPort], List[OutPort]]:
        return [], [
            OutPort(
                name="file_out",
                description="The uploaded file.",
            )
        ]

    @override
    def infer_output_schemas(self, input_schemas: Dict[str, Schema]) -> Dict[str, Schema]:
        file_manager = self.global_config.file_manager
        return {
            "file_out": Schema(
                type=Schema.Type.FILE,
                file=FileSchema.from_file(self.file, file_manager=file_manager)
            )
        }

    @override
    def process(self, input: Dict[str, Data]) -> Dict[str, Data]:
        return {
            "file_out": Data(payload=self.file)
        }