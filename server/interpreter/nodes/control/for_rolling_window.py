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
This file defines a pair for node for ForRollingWindow loop control.
"""

@register_node(pair=True)
class ForRollingWindowBeginNode(BaseNode):
    """
    Marks the beginning of a rolling window loop.
    """
    
    window_size: int
    
    pair_id: int
    _PAIR_TYPE = "BEGIN"
    
    @override
    def validate_parameters(self) -> None:
        if not self.type == "ForRollingWindowBeginNode":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="type",
                err_msg="Node type parameter mismatch.",
            )
        if not isinstance(self.window_size, int) or self.window_size <= 0:
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="window_size",
                err_msg="Window size must be a positive integer.",
            )
        return

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [
            InPort(
                name="table",
                description="Input table to apply rolling window on.",
                accept=Pattern(
                    types={Schema.Type.TABLE},
                )
            )
        ], [
            OutPort(
                name="window",
                description="Output current rolling window as a table."
            )
        ]

    @override
    def infer_output_schemas(self, input_schemas: Dict[str, Schema]) -> Dict[str, Schema]:
        table_schema = input_schemas.get("table")
        assert table_schema is not None
        return {"window": table_schema}

    @override
    def process(self, input: Dict[str, Data]) -> Dict[str, Data]:
        # The actual rolling window logic will be handled by the interpreter's control structure execution.
        raise NotImplementedError("Processing is handled in the interpreter's loop control logic.")

@register_node(pair=True)
class ForRollingWindowEndNode(BaseNode):
    """
    Marks the end of a rolling window loop.
    """
    
    pair_id: int
    _PAIR_TYPE = "END"
    
    @override
    def validate_parameters(self) -> None:
        if not self.type == "ForRollingWindowEndNode":
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
                name="window",
                description="Input current rolling window as a table.",
                accept=Pattern(
                    types={Schema.Type.TABLE},
                )
            )
        ], [
            OutPort(
                name="table",
                description="Output table after rolling window processing."
            )
        ]

    @override
    def infer_output_schemas(self, input_schemas: Dict[str, Schema]) -> Dict[str, Schema]:
        window_schema = input_schemas.get("window")
        assert window_schema is not None
        return {"table": window_schema}

    @override
    def process(self, input: Dict[str, Data]) -> Dict[str, Data]:
        # The actual rolling window logic will be handled by the interpreter's control structure execution.
        raise NotImplementedError("Processing is handled in the interpreter's loop control logic.")
