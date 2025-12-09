from typing import Any, Literal, override

from server.config import FIGURE_DPI
from server.models.data import Data, Table
from server.models.exception import NodeParameterError
from server.models.schema import ColType, FileSchema, Pattern, Schema

from ..base_node import BaseNode, InPort, OutPort, register_node


@register_node()
class KLinePlotNode(BaseNode):
    """
    A node to create K-Line (Candlestick) plots from financial data.
    """
    title: str | None = None
    x_col: str
    open_col: str
    high_col: str
    low_col: str
    close_col: str
    volume_col: str | None = None
    style_mode: Literal["CN", "EN"]

    @override
    def validate_parameters(self) -> None:
        if not self.type == "KLinePlotNode":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="type",
                err_msg="Node type parameter mismatch.",
            )
        if self.x_col.strip() == "":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="x_col",
                err_msg="x_col cannot be empty.",
            )
        if self.open_col.strip() == "":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="open_col",
                err_msg="open_col cannot be empty.",
            )
        if self.high_col.strip() == "":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="high_col",
                err_msg="high_col cannot be empty.",
            )
        if self.low_col.strip() == "":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="low_col",
                err_msg="low_col cannot be empty.",
            )
        if self.close_col.strip() == "":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="close_col",
                err_msg="close_col cannot be empty.",
            )
        if self.volume_col is not None and self.volume_col.strip() == "":
            self.volume_col = None
        return

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        input_col_types = {}
        input_col_types[self.x_col] = ColType.DATETIME
        input_col_types[self.open_col] = ColType.FLOAT
        input_col_types[self.high_col] = ColType.FLOAT
        input_col_types[self.low_col] = ColType.FLOAT
        input_col_types[self.close_col] = ColType.FLOAT
        if self.volume_col is not None:
            input_col_types[self.volume_col] = {ColType.FLOAT, ColType.INT}
        return [
            InPort(
                name="input",
                description="Input table containing financial data.",
                accept=Pattern(
                    types={Schema.Type.TABLE},
                    table_columns=input_col_types,
                ),
            ),
        ], [
            OutPort(name="plot", description="The generated K-Line plot image."),
        ]

    @override
    def infer_output_schemas(self, input_schemas: dict[str, Schema]) -> dict[str, Schema]:
        output_schema = Schema(
            type=Schema.Type.FILE,
            file=FileSchema(
                format="png",
                col_types={},
            ),
        )
        return {"plot": output_schema}

    @override
    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        import matplotlib.pyplot as plt
        import mplfinance as mpf
        import pandas as pd

        table_data = input["input"].payload
        assert isinstance(table_data, Table)

        df = table_data.df.copy()
        df[self.x_col] = pd.to_datetime(df[self.x_col])
        df.set_index(self.x_col, inplace=True)

        ohlc_cols = [self.open_col, self.high_col, self.low_col, self.close_col]
        mpf_df = df[ohlc_cols].copy()
        mpf_df.columns = ["Open", "High", "Low", "Close"]

        if self.volume_col is not None:
            mpf_df["Volume"] = df[self.volume_col]

        # config style
        up_color = "#ef5350" if self.style_mode == "CN" else "#26a69a"  # 红/绿
        down_color = "#26a69a" if self.style_mode == "CN" else "#ef5350"  # 绿/红

        mc = mpf.make_marketcolors(
            up=up_color,
            down=down_color,
            edge="inherit",
            wick="inherit",
            volume="in",
            ohlc="i",
        )

        s = mpf.make_mpf_style(
            marketcolors=mc,
            gridstyle="--",
            y_on_right=True,
            facecolor="white",
            edgecolor="#e0e0e0",
            figcolor="white",
        )

        fig_title = self.title if self.title is not None else "K-Line Plot"

        fig, axlist = mpf.plot(
            mpf_df,
            type="candle",
            volume=self.volume_col is not None,
            title=fig_title,
            style=s,
            returnfig=True,
            figsize=(10, 6),
            dpi=FIGURE_DPI,
            warn_too_much_data=10000,
        )

        file_manager = self.global_config.file_manager
        buf = file_manager.get_buffer()

        fig.savefig(buf, format="png", dpi=FIGURE_DPI, bbox_inches="tight")
        fig.clf()
        plt.close(fig)

        file = file_manager.write_sync(
            content=buf,
            filename=f"{self.id}.png",
            format="png",
            node_id=self.id,
            project_id=self.global_config.project_id,
            user_id=self.global_config.user_id,
        )
        return {"plot": Data(payload=file)}

    @override
    @classmethod
    def hint(cls, input_schemas: dict[str, Schema], current_params: dict) -> dict[str, Any]:
        hint = {}
        if "input" in input_schemas:
            schema = input_schemas["input"]
            x_col_choices = []
            open_col_choices = []
            high_col_choices = []
            low_col_choices = []
            close_col_choices = []
            volume_col_choices = []
            if schema.type == Schema.Type.TABLE and schema.tab is not None:
                for col, col_type in schema.tab.col_types.items():
                    if col_type == ColType.DATETIME:
                        x_col_choices.append(col)
                    if col_type == ColType.FLOAT:
                        open_col_choices.append(col)
                        high_col_choices.append(col)
                        low_col_choices.append(col)
                        close_col_choices.append(col)
                        volume_col_choices.append(col)
            hint["x_col_choices"] = x_col_choices
            hint["open_col_choices"] = open_col_choices
            hint["high_col_choices"] = high_col_choices
            hint["low_col_choices"] = low_col_choices
            hint["close_col_choices"] = close_col_choices
            hint["volume_col_choices"] = volume_col_choices
        return hint
