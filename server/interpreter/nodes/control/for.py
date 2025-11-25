from typing import Dict, override

from server.models.data import Data
from server.models.exception import (
    NodeParameterError,
)
from server.models.schema import (
    Pattern,
    Schema,
)

from ..base_node import BaseNode, InPort, OutPort, register_node

"""
This file defines a pair for node for ForEachRow loop control.
"""

@register_node(pair=True)
class ForEachRowBeginNode(BaseNode):
    """
    Marks the beginning of a row-by-row loop.
    """

    pair_id: int # ID to link with its corresponding end node
    _PAIR_TYPE = "BEGIN"

    @override
    def validate_parameters(self) -> None:
        if not self.type == "ForEachRowBeginNode":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="type",
                err_msg="Node type parameter mismatch.",
            )
        return

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [
            InPort(
                name="table",
                description="Input table to iterate over.",
                accept=Pattern(
                    types={Schema.Type.TABLE},
                )
            )
        ], [
            OutPort(
                name="row",
                description="Output current row as a record."
            )
        ]

    @override
    def infer_output_schemas(self, input_schemas: Dict[str, Schema]) -> Dict[str, Schema]:
        table_schema = input_schemas.get("table")
        assert table_schema is not None
        return {"row": table_schema}

    @override
    def process(self, input: Dict[str, Data]) -> Dict[str, Data]:
        # Processing is handled in the interpreter's loop control logic
        return {}


@register_node(pair=True)
class ForEachRowEndNode(BaseNode):
    """
    Marks the end of a loop, collecting results.
    """

    pair_id: int # ID to link with its corresponding begin node
    _PAIR_TYPE = "END"

    @override
    def validate_parameters(self) -> None:
        if not self.type == "ForEachRowEndNode":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="type",
                err_msg="Node type parameter mismatch.",
            )
        return

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [
            InPort(
                name="row",
                description="Input current row as a record.",
                accept=Pattern(
                    types={Schema.Type.TABLE},
                    table_columns={},  # Accept any record schema
                )
            )
        ], [
            OutPort(
                name="table",
                description="Output table containing all processed rows."
            )
        ]

    @override
    def infer_output_schemas(self, input_schemas: Dict[str, Schema]) -> Dict[str, Schema]:
        row_schema = input_schemas.get("row")
        assert row_schema is not None
        return {"table": row_schema}

    @override
    def process(self, input: Dict[str, Data]) -> Dict[str, Data]:
        # Processing is handled in the interpreter's loop control logic
        return {}
