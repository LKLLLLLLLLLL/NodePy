from ..BaseNode import BaseNode, InPort, OutPort, Data, Schema
from ..Exceptions import NodeParameterError

class StringNode(BaseNode):
    """
    A node to generate a string.
    """
    value: str
    
    def validate_parameters(self) -> None:
        if not self.type == "StringNode":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="type",
                err_msg="Node type must be 'StringNode'."
            )
        return
    
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [], [OutPort(name="string", description="The string value")]
    
    def infer_output_schemas(self, input_schemas: dict[str, Schema]) -> dict[str, Schema]:
        return {"string": Schema(type=Schema.Type.STR)}

    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        return {"string": Data(payload=self.value)}