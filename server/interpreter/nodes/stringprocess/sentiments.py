from typing import override

from server.models.data import Data
from server.models.exception import NodeExecutionError, NodeParameterError
from server.models.schema import (
    Pattern,
    Schema,
)

from ..base_node import BaseNode, InPort, OutPort, register_node


@register_node()
class SentimentAnalysisNode(BaseNode):
    """
    Node to analyze sentiment of text in a column using advanced libraries.
    - Uses SnowNLP for Chinese text.
    - Uses VADER for English text.
    """

    @override
    def validate_parameters(self) -> None:
        if self.type != "SentimentAnalysisNode":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="type",
                err_msg="Node type mismatch."
            )
        return

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [
            InPort(
                name="text",
                description="Input string containing text for sentiment analysis.",
                accept=Pattern(
                    types={Schema.Type.STR},
                )
            )
        ], [
            OutPort(
                name="score",
                description="Output float representing the sentiment score.",
            )
        ]

    @override
    def infer_output_schemas(self, input_schemas: dict[str, Schema]) -> dict[str, Schema]:
        return {
            "score": Schema(
                type=Schema.Type.FLOAT
            )
        }

    def _is_chinese(self, text: str) -> bool:
        chinese_char_count = 0
        for char in text:
            if '\u4e00' <= char <= '\u9fff':
                chinese_char_count += 1
        if chinese_char_count / max(len(text), 1) > 0.3:
            return True
        return False

    @override
    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        from snownlp import SnowNLP
        from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

        assert isinstance(input["text"].payload, str)
        text = input["text"].payload

        score: float
        # Chinese Analysis using SnowNLP
        if self._is_chinese(text):
            try:
                s = SnowNLP(text)
                # SnowNLP returns [0, 1], where 0.5 is neutral.
                # Map to [-1, 1]: (x - 0.5) * 2
                score =  (s.sentiments - 0.5) * 2
            except Exception:
                raise NodeExecutionError(
                    node_id=self.id,
                    err_msg="Error occurred during Chinese sentiment analysis with SnowNLP."
                )
        # 2. English Analysis using VADER
        else:   
            vader_analyzer = SentimentIntensityAnalyzer()
            try:
                scores = vader_analyzer.polarity_scores(text)
                # VADER 'compound' score is already [-1, 1]
                score = scores['compound']
            except Exception:
                raise NodeExecutionError(
                    node_id=self.id,
                    err_msg="Error occurred during English sentiment analysis with VADER."
                )
        return {
            "score": Data(payload=score)
        }
