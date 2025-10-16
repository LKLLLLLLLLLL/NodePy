from ..BaseNode import BaseNode, InPort, OutPort, register_node
from typing import Literal, override
from ..Exceptions import NodeParameterError
from ..DataType import Schema, ColType, Pattern, Data, Table
import matplotlib.pyplot as plt

@register_node
class PlotNode(BaseNode):
    """
    Node to visualize data from input table using matplotlib.
    """
    x_column: str
    y_column: str
    plot_type: Literal["scatter", "line", "bar"]
    title: str | None = None

    @override
    def validate_parameters(self) -> None:
        if not self.type == "PlotNode":
            raise NodeParameterError(
                node_id=self.id, 
                err_param_key="type", 
                err_msg = "Node type must be 'PlotNode'."
            )
        if self.x_column.strip() == "":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="x_column",
                err_msg="x_column cannot be empty."
            )
        if self.y_column.strip() == "":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="y_column",
                err_msg="y_column cannot be empty."
            )
        if self.title is not None and self.title.strip() == "":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="title",
                err_msg="If provided, title cannot be empty."
            )
        return

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [
            InPort(
                name="input",
                description="Input table data to visualize",
                optional=False,
                accept=Pattern(
                    types = {Schema.Type.TABLE},
                    table_columns = {
                        self.x_column: {ColType.INT, ColType.FLOAT, ColType.STR},
                        self.y_column: {ColType.INT, ColType.FLOAT}
                    }
                )
            ),
        ], [
            OutPort(name="plot", description="Generated plot image in PNG format")
        ]

    @override
    def infer_output_schemas(self, input_schemas: dict[str, Schema]) -> dict[str, Schema]:
        return {
            "plot": Schema(type=Schema.Type.FILE)
        }

    @override
    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        input_table = input["input"].payload
        assert isinstance(input_table, Table)

        x_data = input_table.df[self.x_column]  # type: ignore
        y_data = input_table.df[self.y_column]  # type: ignore

        file_manager = self.global_config.file_manager
        
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
        plt.grid()
        plt.tight_layout()      
        # save to byte stream
        buf = file_manager.get_buffer()
        plt.savefig(buf, format="png")
        plt.close()
        file = file_manager.write_from_buffer(
            user_id=self.global_config.user_id, 
            filename=f"{self.id}_plot.png",
            buffer=buf
        )
        return {"plot": Data(payload=file)}