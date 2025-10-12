from .BaseNode import BaseNode, NodeValidationError, InPort, OutPort, Data, Schema
from pandas import DataFrame
from typing import Literal
from numpy import random

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

    def infer_output_schema(self, input_schema: dict[str, Schema]) -> dict[str, Schema]:
        output_schema = Schema(type=Schema.DataType.TABLE, columns=[self.column_name])
        return {"output": output_schema}

    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        """generate random data"""
        if self.data_type == "int" and isinstance(self.top, int) and isinstance(self.bottom, int):
            data = random.RandomState(self.seed).randint(
                self.top, self.bottom, size=100
            )
        else:
            data = random.RandomState(self.seed).uniform(
                self.top, self.bottom, size=100
            )

        table = DataFrame({self.column_name: data})
        return {
            "output": Data(
                schem=Schema(type=Schema.DataType.TABLE, columns=[self.column_name]),
                payload=table,
            )
        }
