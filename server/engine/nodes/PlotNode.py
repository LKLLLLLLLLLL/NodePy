from .BaseNode import BaseNode, NodeValidationError, InPort, OutPort, Data, Schema
from pandas import DataFrame
from typing import Literal
import matplotlib.pyplot as plt
from .Utils import Visualization
from pathlib import Path


"""
A series of nodes to visualize data.
"""


class PlotNode(BaseNode):
    """
    Node to visualize data from input table using matplotlib.
    """
    x_column: str
    y_column: str
    plot_type: Literal["scatter", "line", "bar"]
    title: str | None = None

    def validate_parameters(self) -> None:
        if not self.type == "PlotNode":
            raise NodeValidationError("Node type must be 'PlotNode'.")
        if self.x_column == "" or self.x_column.strip() == "":
            raise NodeValidationError("x_column cannot be empty.")
        if self.y_column == "" or self.y_column.strip() == "":
            raise NodeValidationError("y_column cannot be empty.")
        if self.plot_type not in ["scatter", "line", "bar"]:
            raise NodeValidationError("plot_type must be 'scatter', 'line', or 'bar'.")

    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [
            InPort(
                name="input",
                accept_types={Schema.DataType.TABLE},
                table_columns={
                    self.x_column: {Schema.ColumnType.INT, Schema.ColumnType.FLOAT},
                    self.y_column: {Schema.ColumnType.INT, Schema.ColumnType.FLOAT}
                },
                description="Input table data to visualize",
                required=True
            )
        ], []

    def validate_input(self, input: dict[str, Data]) -> None:
        assert isinstance(input["input"].payload, DataFrame)
        assert isinstance(input["input"].payload, DataFrame)
        assert input["input"].sche.columns is not None
        x_data = input["input"].payload[self.x_column]
        y_data = input["input"].payload[self.y_column]
        if x_data.empty:
            raise NodeValidationError(f"x_column '{self.x_column}' is empty.")
        if y_data.empty:
            raise NodeValidationError(f"y_column '{self.y_column}' is empty.")
        pass

    def infer_output_schema(self, input_schema: dict[str, Schema]) -> dict[str, Schema]:
        return {}

    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        """Generate plot from input data"""
        input_data = input["input"]
        df = input_data.payload
        assert isinstance(df, DataFrame)

        x_data = df[self.x_column]  # type: ignore
        y_data = df[self.y_column]  # type: ignore

        plt.figure(figsize=(8, 6))
        if self.plot_type == "scatter":
            plt.scatter(x_data, y_data)
        elif self.plot_type == "line":
            plt.plot(x_data, y_data)
        elif self.plot_type == "bar":
            plt.bar(x_data, y_data)

        if self.title:
            plt.title(self.title)
        plt.xlabel(self.x_column)
        plt.ylabel(self.y_column)

        path = self.global_config.temp_dir / f"plot_{self.global_config.user_id}_{self.id}.png"

        plt.savefig(path)
        plt.close()

        self.vis = Visualization(
            node_id=self.id,
            type=Visualization.Type.PICTURE,
            payload=Path(path)
        )
        return {}

