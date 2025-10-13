from .BaseNode import BaseNode, NodeValidationError, InPort, OutPort, Data, Schema
from pandas import DataFrame
from .Utils import Visualization

class RangeNode(BaseNode):
    """
    Node to generate a table, with a range column of specified type and range.
    """
    start: float | int
    end: float | int
    step: float | int
    column_name: str
    
    def validate_parameters(self) -> None:
        if not self.type == "RangeNode":
            raise NodeValidationError("Node type must be 'RangeNode'.")
        if self.start >= self.end:
            raise NodeValidationError("start must be less than end.")
        if self.step <= 0:
            raise NodeValidationError("step must be positive.")
        if self.column_name == "" or self.column_name.strip() == "":
            raise NodeValidationError("column_name cannot be empty.")
        if isinstance(self.start, int) and isinstance(self.end, int) and isinstance(self.step, int):
            return
        elif isinstance(self.start, float) and isinstance(self.end, float) and isinstance(self.step, float):
            return
        else:
            raise NodeValidationError("start, end, and step must be all int or all float.")

    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [], [OutPort(name="output", description="The output table")]
    
    def validate_input(self, input: dict[str, Data]) -> None:
        """ no input """
        pass
    
    def _compute_output_schema(self) -> Schema:
        """
        Centralized schema computation logic.
        This ensures infer_output_schema and process return consistent schemas.
        """
        if isinstance(self.start, int) and isinstance(self.end, int) and isinstance(self.step, int):
            return Schema(
                type=Schema.DataType.TABLE,
                columns={self.column_name: {Schema.ColumnType.INT}}
            )
        else:
            return Schema(
                type=Schema.DataType.TABLE,
                columns={self.column_name: {Schema.ColumnType.FLOAT}}
            )
    
    def infer_output_schema(self, input_schema: dict[str, Schema]) -> dict[str, Schema]:
        # Delegate to centralized schema computation
        return {"output": self._compute_output_schema()}
    
    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        """ generate range data """
        if isinstance(self.start, int) and isinstance(self.end, int) and isinstance(self.step, int):
            data = list(range(self.start, self.end, self.step))
        else:
            data = []
            current = self.start
            while current < self.end:
                data.append(current)
                current += self.step
        
        table = DataFrame({self.column_name: data})
        self.vis = Visualization(
            node_id=self.id,
            type=Visualization.Type.TABLE,
            payload=table
        )
        
        # Use centralized schema computation to ensure consistency
        return {
            "output": Data(
                sche=self._compute_output_schema(),
                payload=table
            )
        }

