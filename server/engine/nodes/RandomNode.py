from .BaseNode import BaseNode, NodeValidationError, InPort, OutPort, Data, Schema
from pandas import DataFrame
from typing import Literal
import numpy as np
from .Utils import Visualization, add_index_column, validate_no_index_column_conflict, INDEX_COLUMN_NAME

class RandomNode(BaseNode):
    """
    Node to generate a table, with a random column of specified type and range.
    """

    data_type: Literal["int", "float"]
    top: float | int
    bottom: float | int
    seed: int | None
    column_name: str

    def validate_parameters(self) -> None:
        if not self.type == "RandomNode":
            raise NodeValidationError("Node type must be 'RandomNode'.")
        if self.top <= self.bottom:
            raise NodeValidationError("top must be greater than bottom.")
        if self.column_name == "" or self.column_name.strip() == "":
            raise NodeValidationError("column_name cannot be empty.")
        
        # Validate that _index column is not used
        validate_no_index_column_conflict([self.column_name])
        
        if not isinstance(self.seed, int) and self.seed is not None:
            raise NodeValidationError("seed must be an integer or None.")
        if (self.data_type == "int"
            and isinstance(self.top, int)
            and isinstance(self.bottom, int)
        ):
            return
        elif (self.data_type == "float"
            and isinstance(self.bottom, float)
            and isinstance(self.top, float)
        ):
            return
        else:
            raise NodeValidationError(
                "top and bottom must be all int or all float."
            )

    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [], [OutPort(name="output", description="The output table")]

    def validate_input(self, input: dict[str, Data]) -> None:
        """no input"""
        pass

    def _compute_output_schema(self) -> Schema:
        """
        Centralized schema computation logic.
        This ensures infer_output_schema and process return consistent schemas.
        """
        cols = {INDEX_COLUMN_NAME: {Schema.ColumnType.INT}}  # Add _index column
        
        if self.data_type == "int":
            cols[self.column_name] = {Schema.ColumnType.INT}
        else:
            cols[self.column_name] = {Schema.ColumnType.FLOAT}
            
        return Schema(type=Schema.DataType.TABLE, columns=cols)

    def infer_output_schema(self, input_schema: dict[str, Schema]) -> dict[str, Schema]:
        # Delegate to centralized schema computation
        return {"output": self._compute_output_schema()}

    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        """generate random data"""
        if self.data_type == "int" and isinstance(self.top, int) and isinstance(self.bottom, int):
            data = np.random.default_rng(self.seed).integers(
                self.bottom, self.top, size=100
            )
        else:
            data = np.random.default_rng(self.seed).uniform(
                self.bottom, self.top, size=100
            )

        table = DataFrame({self.column_name: data})
        
        # Add automatic index column
        table = add_index_column(table)
        
        self.vis = Visualization(
            node_id=self.id,
            type=Visualization.Type.TABLE,
            payload=table
        )
        
        # Use centralized schema computation to ensure consistency
        return {
            "output": Data(
                sche=self._compute_output_schema(),
                payload=table,
            )
        }
