from typing import Any, Literal, override

from server.config import FIGURE_DPI
from server.models.data import Data, Table
from server.models.exception import NodeParameterError
from server.models.schema import NO_SPECIFIED_COL, ColType, FileSchema, Pattern, Schema

from ..base_node import BaseNode, InPort, OutPort, register_node


@register_node()
class QuickPlotNode(BaseNode):
    """
    Node to visualize data from input table using matplotlib.
    """
    x_col: str
    y_col: list[str]
    plot_type: list[Literal["scatter", "line", "bar", "area"]]
    title: str | None = None

    @override
    def validate_parameters(self) -> None:
        if not self.type == "QuickPlotNode":
            raise NodeParameterError(
                node_id=self.id, 
                err_param_key="type", 
                err_msg = "Node type must be 'QuickPlotNode'."
            )
        if self.x_col.strip() == "":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="x_col",
                err_msg="x_col cannot be empty."
            )
        if len(self.y_col) != len(self.plot_type):
            raise NodeParameterError(
                node_id=self.id,
                err_param_keys=["y_col", "plot_type"],
                err_msgs=[
                    "y_col and plot_type must have the same length.",
                    "y_col and plot_type must have the same length.",
                ],
            )
        for col in self.y_col:
            if col.strip() == "":
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
        input_col_types = {}
        input_col_types[self.x_col] = {ColType.INT, ColType.FLOAT, ColType.STR, ColType.DATETIME}
        for col in self.y_col:
            input_col_types[col] = {ColType.INT, ColType.FLOAT}
        return [
            InPort(
                name="input",
                description="Input table data to visualize",
                optional=False,
                accept=Pattern(
                    types = {Schema.Type.TABLE},
                    table_columns = input_col_types
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
        import numpy as np

        input_table = input["input"].payload
        assert isinstance(input_table, Table)
        df = input_table.df

        plt.figure(figsize=(10, 6))

        x_data = df[self.x_col]

        # Check if we have any bar plots to handle grouping
        bar_indices = [i for i, t in enumerate(self.plot_type) if t == "bar"]
        num_bars = len(bar_indices)

        if num_bars > 0:
            # Use index-based plotting for grouped bars to avoid overlap
            indices = np.arange(len(x_data))
            total_width = 0.8
            bar_width = total_width / num_bars
            
            current_bar_pos = 0
            
            for i, y_col in enumerate(self.y_col):
                y_data = df[y_col]
                label = y_col
                ptype = self.plot_type[i]

                if ptype == "bar":
                    # Calculate offset to place bars side by side
                    offset = (current_bar_pos - (num_bars - 1) / 2) * bar_width
                    plt.bar(indices + offset, y_data, width=bar_width, label=label, alpha=0.8)
                    current_bar_pos += 1
                elif ptype == "line":
                    plt.plot(indices, y_data, label=label)
                elif ptype == "scatter":
                    plt.scatter(indices, y_data, label=label)
                elif ptype == "area":
                    plt.fill_between(indices, y_data, label=label, alpha=0.4)
            
            # Restore x-axis labels
            if len(x_data) > 20:
                step = len(x_data) // 10
                plt.xticks(indices[::step], x_data.iloc[::step], rotation=45) # type: ignore
            else:
                plt.xticks(indices, x_data, rotation=45) # type: ignore
        else:
            # Standard plotting for non-bar types (preserves x-axis scaling)
            for i, y_col in enumerate(self.y_col):
                y_data = df[y_col]
                label = y_col
                ptype = self.plot_type[i]

                if ptype == "line":
                    plt.plot(x_data, y_data, label=label)
                elif ptype == "scatter":
                    plt.scatter(x_data, y_data, label=label)
                elif ptype == "area":
                    plt.fill_between(x_data, y_data, label=label, alpha=0.4)

        if self.title:
            plt.title(self.title)
        plt.xlabel(self.x_col)
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()  
        # save to byte stream
        file_manager = self.global_config.file_manager
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
                for col, col_type in input_schema.tab.col_types.items():
                    if col_type in {ColType.INT, ColType.FLOAT, ColType.STR, ColType.DATETIME}:
                        if "x_col_choices" not in hint:
                            hint["x_col_choices"] = []
                        hint["x_col_choices"].append(col)
                    if col_type in {ColType.INT, ColType.FLOAT}:
                        if "y_col_choices" not in hint:
                            hint["y_col_choices"] = []
                        hint["y_col_choices"].append(col)
        return hint


@register_node()
class DualAxisPlotNode(BaseNode):
    """
    A dual-axis plotting node.
    """
    x_col: str
    left_y_col: str
    left_plot_type: Literal["line", "bar"]
    right_y_col: str
    right_plot_type: Literal["line", "bar"]
    title: str | None = None

    @override
    def validate_parameters(self) -> None:
        if not self.type == "DualAxisPlotNode":
            raise NodeParameterError(
                node_id=self.id, 
                err_param_key="type", 
                err_msg = "Node type must be 'DualAxisPlotNode'."
            )
        if self.x_col.strip() == "":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="x_col",
                err_msg="x_col cannot be empty."
            )
        if self.left_y_col.strip() == "":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="left_y_col",
                err_msg="left_y_col cannot be empty."
            )
        if self.right_y_col.strip() == "":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="right_y_col",
                err_msg="right_y_col cannot be empty."
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
                        self.x_col: {ColType.INT, ColType.FLOAT, ColType.STR, ColType.DATETIME},
                        self.left_y_col: {ColType.INT, ColType.FLOAT},
                        self.right_y_col: {ColType.INT, ColType.FLOAT}
                    }
                )
            ),
        ], [
            OutPort(name="plot", description="Generated dual-axis plot image in PNG format")
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
        df = input_table.df

        x_data = df[self.x_col]
        left_y_data = df[self.left_y_col]
        right_y_data = df[self.right_y_col]

        fig, ax1 = plt.subplots(figsize=(10, 6))

        if self.left_plot_type == "line":
            ax1.plot(x_data, left_y_data, 'b-', label=self.left_y_col)
        elif self.left_plot_type == "bar":
            ax1.bar(x_data, left_y_data, color='b', alpha=0.6, label=self.left_y_col)
        ax1.set_xlabel(self.x_col)
        ax1.set_ylabel(self.left_y_col, color='b')
        ax1.tick_params(axis='y', labelcolor='b')

        ax2 = ax1.twinx()
        if self.right_plot_type == "line":
            ax2.plot(x_data, right_y_data, 'r-', label=self.right_y_col)
        elif self.right_plot_type == "bar":
            ax2.bar(x_data, right_y_data, color='r', alpha=0.6, label=self.right_y_col)
        ax2.set_ylabel(self.right_y_col, color='r')
        ax2.tick_params(axis='y', labelcolor='r')

        if self.title:
            plt.title(self.title)
        fig.tight_layout()  
        # save to byte stream
        file_manager = self.global_config.file_manager
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
        if "table" in input_schemas:
            input_schema = input_schemas["table"]
            if input_schema.type == Schema.Type.TABLE and input_schema.tab is not None:
                x_col_choices = []
                y_col_choices = []
                for col, col_type in input_schema.tab.col_types.items():
                    if col_type in {ColType.INT, ColType.FLOAT, ColType.STR, ColType.DATETIME}:
                        x_col_choices.append(col)
                    if col_type in {ColType.INT, ColType.FLOAT}:
                        y_col_choices.append(col)
                hint["x_col_choices"] = x_col_choices
                hint["left_y_col_choices"] = y_col_choices
                hint["right_y_col_choices"] = y_col_choices
        return hint

@register_node()
class StatisticalPlotNode(BaseNode):
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
        if not self.type == "StatisticalPlotNode":
            raise NodeParameterError(
                node_id=self.id, 
                err_param_key="type", 
                err_msg = "Node type must be 'StatisticalPlotNode'."
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
                        self.x_col: {ColType.INT, ColType.FLOAT, ColType.STR, ColType.DATETIME},
                        **({self.y_col: {ColType.INT, ColType.FLOAT}} if self.y_col else {}),
                        **({self.hue_col: {ColType.INT, ColType.FLOAT, ColType.STR, ColType.DATETIME}} if self.hue_col else {})
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
            sns.histplot(x=x_data, hue=hue_data, bins=30)
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
                    if col_type in {ColType.INT, ColType.FLOAT}:
                        y_col_choices.append(col)
                    if col_type in {ColType.INT, ColType.FLOAT, ColType.STR, ColType.DATETIME}:
                        x_col_choices.append(col)
                        hue_col_choices.append(col)
                hint["x_col_choices"] = x_col_choices
                if current_params.get("plot_type") not in {"count", "hist"}:
                    hint["y_col_choices"] = y_col_choices
                hint["hue_col_choices"] = hue_col_choices
        return hint
