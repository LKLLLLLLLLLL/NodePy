from typing import Dict, Literal, override

import pandas as pd
from pydantic import PrivateAttr

from server.models.data import Data, Table, TableSchema
from server.models.exception import (
    NodeParameterError,
)
from server.models.schema import (
    ColType,
    Pattern,
    Schema,
    generate_default_col_name,
)

from ..base_node import BaseNode, InPort, OutPort, register_node


@register_node()
class TokenizeNode(BaseNode):
    """
    A node to tokenize strings and output the tokens as a list.
    It support english and chinese tokenization.
    """
    language: Literal["ENGLISH", "CHINESE"]
    delimiter: str | None # Optional delimiter for ENGLISH tokenization
    result_col: str | None = None  # Optional result column name for output table

    _col_types: Dict[str, ColType] | None = PrivateAttr(default=None)

    @override
    def validate_parameters(self) -> None:
        if not self.type == "TokenizeNode":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="type",
                err_msg="Node type parameter mismatch.",
            )
        if self.delimiter is None:
            self.delimiter = " " # Default delimiter for English tokenization
        if self.result_col is not None and self.result_col.strip() == "":
            self.result_col = None
        if self.result_col is None:
            self.result_col = generate_default_col_name(
                id=self.id,
                annotation="tokens"
            )
        return

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [
            InPort(
                name="text",
                description="Input string to be tokenized.",
                accept=Pattern(types={Schema.Type.STR}),
            ),
        ], [
            OutPort(name="tokens", description="The list of tokens extracted from the input string."),
        ]

    @override
    def infer_output_schemas(self, input_schemas: dict[str, Schema]) -> dict[str, Schema]:
        assert self.result_col is not None
        col_types = {
            self.result_col: ColType.STR
        }
        self._col_types = col_types
        output_schema = Schema(
            type=Schema.Type.TABLE,
            tab=TableSchema(col_types=col_types)
        )
        return {"tokens": output_schema}

    @override
    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        import jieba

        text_value = input["text"].payload
        assert isinstance(text_value, str)

        if self.language == "ENGLISH":
            assert self.delimiter is not None
            tokens = text_value.split(self.delimiter)
        else:  # CHINESE
            tokens = list(jieba.cut(text_value))

        assert self.result_col is not None
        assert self._col_types is not None
        table = Table(
            col_types=self._col_types,
            df=pd.DataFrame({self.result_col: tokens}),
        )
        return {"tokens": Data(payload=table)}
