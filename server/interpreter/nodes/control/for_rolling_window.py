from typing import Any, Dict, Generator, override

import pandas as pd
from pydantic import PrivateAttr

from server.interpreter.nodes.control.for_base_node import (
    ForBaseBeginNode,
    ForBaseEndNode,
)
from server.models.data import Data, Table
from server.models.exception import (
    NodeExecutionError,
    NodeParameterError,
)
from server.models.schema import (
    Pattern,
    Schema,
)

from ..base_node import InPort, OutPort, register_node

"""
This file defines a pair for node for ForRollingWindow loop control.
"""

@register_node(pair=True)
class ForRollingWindowBeginNode(ForBaseBeginNode):
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

    @override
    def iter_loop(self, inputs: Dict[str, Data]) -> Generator[dict[str, Data], Any, None]:
        input_table_data = inputs.get("table")
        assert input_table_data is not None
        assert isinstance(input_table_data.payload, Table)
        df = input_table_data.payload.df

        # if windows size is too small, raise error
        if self.window_size > len(df):
            raise NodeExecutionError(
                node_id=self.id,
                err_msg=f"Window size {self.window_size} is larger than the number of rows {len(df)} in the input table.",
            )

        for index in range(0, len(df) - self.window_size + 1):
            # set the current window data to the output port of the begin node
            window_data = Data(
                payload=Table(
                    df=df.iloc[index: index + self.window_size],
                    col_types=input_table_data.payload.col_types
                )
            )
            yield {"window": window_data}


@register_node(pair=True)
class ForRollingWindowEndNode(ForBaseEndNode):
    """
    Marks the end of a rolling window loop.
    """
    
    pair_id: int
    _PAIR_TYPE = "END"

    _outputs_tables: list[Data] = PrivateAttr(default=[])
    
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

    @override
    def end_iter_loop(self, loop_outputs: Dict[str, Data]) -> None:
        """save outputs for each iteration"""
        window_data = loop_outputs.get("window")
        assert window_data is not None
        self._outputs_tables.append(window_data)

    @override
    def finalize_loop(self) -> Dict[str, Data]:
        """combine all output rows into a single table"""
        if len(self._outputs_tables) == 0:
            return {
                "table": Data(
                    payload=Table(
                        df=pd.DataFrame(),
                        col_types={},
                    )
                )
            }

        dfs = []
        for row in self._outputs_tables:
            assert isinstance(row.payload, Table)
            dfs.append(row.payload.df)
        combined_df = pd.concat(dfs, ignore_index=True)
        combined_col_types = self._outputs_tables[0].payload.col_types
        assert combined_col_types is not None
        return {
            "table": Data(
                payload=Table(
                    df=combined_df,
                    col_types=combined_col_types
                )
            )
        }
