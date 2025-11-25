from typing import Any, Literal, override

from server.config import FIGURE_DPI
from server.models.data import Data, Table
from server.models.exception import NodeParameterError
from server.models.schema import ColType, FileSchema, Pattern, Schema

from ..base_node import BaseNode, InPort, OutPort, register_node


@register_node()
class PlotNode(BaseNode):
    """
    Node to visualize data from input table using matplotlib.
    """
    x_col: str
    y_col: str
    plot_type: Literal["scatter", "line", "bar", "pie"]
    title: str | None = None

    @override
    def validate_parameters(self) -> None:
        if not self.type == "PlotNode":
            raise NodeParameterError(
                node_id=self.id, 
                err_param_key="type", 
                err_msg = "Node type must be 'PlotNode'."
            )
        if self.x_col.strip() == "":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="x_col",
                err_msg="x_col cannot be empty."
            )
        if self.y_col.strip() == "":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="y_col",
                err_msg="y_col cannot be empty."
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
                        self.x_col: {ColType.INT, ColType.FLOAT, ColType.STR},
                        self.y_col: {ColType.INT, ColType.FLOAT}
                    }
                )
            ),
        ], [
            OutPort(name="plot", description="Generated plot image in PNG format")
        ]

    @override
    def infer_output_schemas(self, input_schemas: dict[str, Schema]) -> dict[str, Schema]:
        return {
            "plot": Schema(
                type=Schema.Type.FILE,
                file=FileSchema(format="png")
            )
        }

    @override
    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        import matplotlib.pyplot as plt
        
        input_table = input["input"].payload
        assert isinstance(input_table, Table)

        x_data = input_table.df[self.x_col]  # type: ignore
        y_data = input_table.df[self.y_col]  # type: ignore

        file_manager = self.global_config.file_manager
        
        plt.rcParams['font.sans-serif'] = ['Noto Sans CJK JP', 'Roboto']
        plt.rcParams['axes.unicode_minus'] = False

        plt.figure(figsize=(8, 6))
        if self.plot_type == "scatter":
            plt.scatter(x_data, y_data)
        elif self.plot_type == "line":
            plt.plot(x_data, y_data)
        elif self.plot_type == "bar":
            plt.bar(x_data, y_data)
        elif self.plot_type == "pie":
            plt.pie(y_data, labels=x_data, autopct='%1.1f%%') # type: ignore
        if self.title:
            plt.title(self.title)
        plt.xlabel(self.x_col if self.plot_type != "pie" else "")
        plt.ylabel(self.y_col if self.plot_type != "pie" else "")
        plt.grid()
        plt.tight_layout()      
        # save to byte stream
        buf = file_manager.get_buffer()
        plt.savefig(buf, format="png", dpi=FIGURE_DPI)
        plt.close()
        file = file_manager.write_sync(
            content=buf,
            filename=f"{self.id}.png",
            format="png",
            node_id=self.id,
            project_id=self.global_config.project_id,
            user_id=self.global_config.user_id
        )
        return {"plot": Data(payload=file)}

    @classmethod
    @override
    def hint(cls, input_schemas: dict[str, Schema], current_params: dict) -> dict[str, Any]:
        """
        Hint x_col and y_col choices based on input schema.
        """
        hint = {}
        if "input" in input_schemas:
            input_schema = input_schemas["input"]
            if input_schema.type == Schema.Type.TABLE and input_schema.tab is not None:
                columns = list(input_schema.tab.col_types.keys())
                hint["x_col_choices"] = columns
                hint["y_col_choices"] = columns
        return hint
