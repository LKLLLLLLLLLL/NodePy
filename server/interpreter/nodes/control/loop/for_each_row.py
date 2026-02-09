from typing import Dict, Generator, Literal, override

import pandas as pd
from pydantic import PrivateAttr

from server.models.data import Data, Table
from server.models.exception import (
    NodeParameterError,
)
from server.models.schema import (
    Pattern,
    Schema,
)

from ...base_node import InPort, OutPort, register_node
from .for_base_node import ForBaseBeginNode, ForBaseEndNode

"""
This file defines a pair for node for ForEachRow loop control.
"""

@register_node()
class ForEachRowBeginNode(ForBaseBeginNode):
    """
    Marks the beginning of a row-by-row loop.
    """

    @property
    @override
    def pair_type(self) -> Literal["BEGIN", "END"]:
        return "BEGIN"

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
        # Processing is handled in iter loop
        raise NotImplementedError("Processing is handled in the interpreter's loop control logic.")

    @override
    def iter_loop(
        self, inputs: Dict[str, Data]
    ) -> Generator[Dict[str, Data], None, None]:
        """ForEachRow control structure"""
        input_table_data = inputs.get("table")
        assert input_table_data is not None
        assert isinstance(input_table_data.payload, Table)
        input_table_df = input_table_data.payload.df
        for index in range(0, len(input_table_df)):
            row_data = Data(
                payload=Table(
                    df=input_table_df.iloc[index : index + 1],
                    col_types=input_table_data.payload.col_types,
                )
            )
            yield {"row": row_data}

@register_node()
class ForEachRowEndNode(ForBaseEndNode):
    """
    Marks the end of a loop, collecting results.
    """

    _output_rows: list[Data] = PrivateAttr(default=[])

    @property
    @override
    def pair_type(self) -> Literal["BEGIN", "END"]:
        return "END"

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

    @override
    def end_iter_loop(self, loop_outputs: Dict[str, Data]) -> None:
        """save outputs for each iteration"""
        row_data = loop_outputs.get("row")
        assert row_data is not None
        self._output_rows.append(row_data)

    @override
    def finalize_loop(self) -> Dict[str, Data]:
        """combine all output rows into a single table"""
        if len(self._output_rows) == 0:
            return {
                "table": Data(
                    payload=Table(
                        df=pd.DataFrame(),
                        col_types={},
                    )
                )
            }

        df_rows = []
        for row in self._output_rows:
            assert isinstance(row.payload, Table)
            df_rows.append(row.payload.df)
        combined_df = pd.concat(
            df_rows, ignore_index=True
        )  # type: ignore
        assert isinstance(self._output_rows[0].payload, Table)
        combined_col_types = self._output_rows[0].payload.col_types
        return {
            "table": Data(
                payload=Table(
                    df=combined_df,
                    col_types=combined_col_types
                )
            )
        }
