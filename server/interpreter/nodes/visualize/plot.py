from typing import Any, Literal, override

from server.config import FIGURE_DPI
from server.models.data import Data, Table
from server.models.exception import NodeParameterError
from server.models.schema import ColType, FileSchema, Pattern, Schema, NO_SPECIFIED_COL

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
        if self.title is not None and self.title.strip() == "":
            self.title = None
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


@register_node()
class AdvancePlotNode(BaseNode):
    """
    A advanced plotting node with more graph types.
    """
    x_col: str
    y_col: str | None = None
    hue_col: str | None = None
    plot_type: Literal["bar", "count", "scatter", "strip", "swarm", "box", "violin", "hist"]
    title: str | None = None

    @override
    def validate_parameters(self) -> None:
        if not self.type == "AdvancePlotNode":
            raise NodeParameterError(
                node_id=self.id, 
                err_param_key="type", 
                err_msg = "Node type must be 'AdvancePlotNode'."
            )
        if self.x_col.strip() == "":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="x_col",
                err_msg="x_col cannot be empty."
            )
        if self.y_col is not None and self.y_col.strip() == "":
            self.y_col = None
        if self.plot_type not in {"count", "hist"} and self.y_col is None:
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="y_col",
                err_msg="y_col cannot be None for the selected plot_type."
            )
        if ((self.hue_col is not None and self.hue_col.strip() == "")
          or self.hue_col == NO_SPECIFIED_COL):
            self.hue_col = None
        if self.title is not None and self.title.strip() == "":
            self.title = None
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
                        **({self.y_col: {ColType.INT, ColType.FLOAT, ColType.STR}} if self.y_col else {}),
                        **({self.hue_col: {ColType.INT, ColType.FLOAT, ColType.STR}} if self.hue_col else {})
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
        import seaborn as sns
        
        input_table = input["input"].payload
        assert isinstance(input_table, Table)

        x_data = input_table.df[self.x_col]  # type: ignore
        if self.y_col:
            y_data = input_table.df[self.y_col]  # type: ignore
        else:
            y_data = None
        hue_data = input_table.df[self.hue_col] if self.hue_col else None  # type: ignore

        file_manager = self.global_config.file_manager
        
        plt.rcParams['font.sans-serif'] = ['Noto Sans CJK JP', 'Roboto']
        plt.rcParams['axes.unicode_minus'] = False

        plt.figure(figsize=(8, 6))
        if self.plot_type == "scatter":
            sns.scatterplot(x=x_data, y=y_data, hue=hue_data)
        elif self.plot_type == "line":
            sns.lineplot(x=x_data, y=y_data, hue=hue_data)
        elif self.plot_type == "bar":
            sns.barplot(x=x_data, y=y_data, hue=hue_data)
        elif self.plot_type == "count":
            sns.countplot(x=x_data, hue=hue_data)
        elif self.plot_type == "strip":
            sns.stripplot(x=x_data, y=y_data, hue=hue_data)
        elif self.plot_type == "swarm":
            sns.swarmplot(x=x_data, y=y_data, hue=hue_data)
        elif self.plot_type == "box":
            sns.boxplot(x=x_data, y=y_data, hue=hue_data)
        elif self.plot_type == "violin":
            sns.violinplot(x=x_data, y=y_data, hue=hue_data)
        elif self.plot_type == "hist":
            sns.histplot(x=y_data, hue=hue_data, bins=30)
        if self.title:
            plt.title(self.title)
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

    @override
    @classmethod
    def hint(cls, input_schemas: dict[str, Schema], current_params: dict) -> dict[str, Any]:
        hint = {}
        if "input" in input_schemas:
            input_schema = input_schemas["input"]
            if input_schema.type == Schema.Type.TABLE and input_schema.tab is not None:
                x_col_choices = []
                y_col_choices = [NO_SPECIFIED_COL]
                hue_col_choices = [NO_SPECIFIED_COL]
                for col, col_type in input_schema.tab.col_types.items():
                    if col_type in {ColType.INT, ColType.FLOAT, ColType.STR}:
                        x_col_choices.append(col)
                        y_col_choices.append(col)
                        hue_col_choices.append(col)
                hint["x_col_choices"] = x_col_choices
                if current_params.get("plot_type") not in {"count", "hist"}:
                    hint["y_col_choices"] = y_col_choices
                hint["hue_col_choices"] = hue_col_choices
        return hint
