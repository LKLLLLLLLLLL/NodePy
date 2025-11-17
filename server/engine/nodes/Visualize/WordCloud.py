from typing import override

from server.config import FIGURE_DPI
from server.engine.nodes.base_node import InPort, OutPort
from server.models.data import Data, Table
from server.models.exception import NodeParameterError
from server.models.schema import ColType, FileSchema, Pattern, Schema

from ..base_node import BaseNode, register_node


@register_node
class WordcloudNode(BaseNode):
    """
    Node to generate a word cloud from table.
    Requires two user-specified columns as "word" and "frequency".
    """

    word_col: str
    frequency_col: str

    @override
    def validate_parameters(self) -> None:
        if not self.type == "WordcloudNode":
            raise NodeParameterError(
                node_id=self.id, 
                err_param_key="type", 
                err_msg = "Node type must be 'WordcloudNode'."
            )
        if self.word_col.strip() == "":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="word_col",
                err_msg="word_col cannot be empty."
            )
        if self.frequency_col.strip() == "":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="frequency_col",
                err_msg="frequency_col cannot be empty."
            )
        return

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [
            InPort(
                name="input",
                description="Input table data to generate word cloud",
                optional=False,
                accept=Pattern(
                    types = {Schema.Type.TABLE},
                    table_columns = {
                        self.word_col: {ColType.STR},
                        self.frequency_col: {ColType.INT, ColType.FLOAT}
                    }
                )
            ),
        ], [
            OutPort(
                name="wordcloud_image",
                description="Generated word cloud image file",
            )
        ]

    @override
    def infer_output_schemas(self, input_schemas: dict[str, Schema]) -> dict[str, Schema]:
        return {
            "wordcloud_image": Schema(
                type=Schema.Type.FILE,
                file=FileSchema(format="png")
            )
        }

    @override
    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        from matplotlib import pyplot as plt
        from wordcloud import WordCloud
        
        table_data = input["input"]
        assert isinstance(table_data, Table)
        table_df = Table.df
        
        file_manager = self.global_config.file_manager

        plt.rcParams["font.sans-serif"] = ["Noto Sans CJK JP", "Roboto"]
        plt.rcParams["axes.unicode_minus"] = False

        # generate word cloud
        word_freq = dict(zip(
            table_df[self.word_col],
            table_df[self.frequency_col]
        ))
        wc = WordCloud(
            font_path="/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            background_color="white",
            width=1200,
            height=800,
            max_words=200,
            max_font_size=120,
            min_font_size=10,
            random_state=50,
            repeat=False,
            colormap="viridis",
        )
        wc.generate_from_frequencies(word_freq)

        _, ax = plt.subplots(figsize=(12, 8), dpi=FIGURE_DPI)
        ax.imshow(wc, interpolation="bilinear")
        ax.axis("off")
        plt.tight_layout(pad=0)
    
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
        return {"wordcloud_image": Data(payload=file)}
