from typing import Any, Dict, Generator, Literal, override

import pandas as pd
from pydantic import PrivateAttr

from server.interpreter.nodes.base_node import InPort, OutPort
from server.models.data import Data, Table
from server.models.exception import (
    NodeParameterError,
)
from server.models.schema import (
    Pattern,
    Schema,
    TableSchema,
    check_no_illegal_cols,
    generate_default_col_name,
)

from ...base_node import register_node
from .for_base_node import (
    ForBaseBeginNode,
    ForBaseEndNode,
)

"""
This file defines nodes for column mapping loop control.
"""
@register_node()
class MapColumnBeginNode(ForBaseBeginNode):
    """
    Marks the beginning of the column mapping loop.
    """
    col: str

    # _remains_col_types: dict[str, Any] | None = PrivateAttr(None)

    @property
    @override
    def pair_type(self) -> Literal["BEGIN", "END"]:
        return "BEGIN"
    
    @override
    def validate_parameters(self) -> None:
        if not self.type == "MapColumnBeginNode":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="type",
                err_msg="Node type parameter mismatch.",
            )
        if self.col.strip() == "":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="col",
                err_msg="Column name cannot be empty.",
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
                    table_columns={self.col: set()}
                )
            )
        ], [
            OutPort(
                name="cell",
                description="Output cell for the mapped column."
            ),
            OutPort(
                name="remains",
                description="Output row containing the remaining columns."
            )
        ]

    @override
    def infer_output_schemas(self, input_schemas: dict[str, Schema]) -> dict[str, Schema]:
        table_schema = input_schemas["table"]
        assert table_schema.tab is not None
        col_types = table_schema.tab.col_types.copy()
        col_schema = col_types[self.col]
        # remains_col_types = col_types.copy()
        # remains_col_types.pop(self.col, None)
        # self._remains_col_types = remains_col_types
        return {
            "cell": Schema.from_coltype(col_schema),
            "remains": Schema(
                type=Schema.Type.TABLE, 
                tab=TableSchema(col_types=col_types)
            )
        }

    @override
    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        assert False, "Unreachable!"
    
    @override
    def iter_loop(self, inputs: Dict[str, Data]) -> Generator[Dict[str, Data], None, None]:
        input_table_data = inputs["table"]
        assert isinstance(input_table_data, Table)
        input_df = input_table_data.df
        for index in range(0, len(input_df)):
            row = input_df.iloc[index]
            cell = row[self.col]
            cell_data = Data(payload=cell) # type: ignore
            remains = row.copy().to_frame()
            remains_data = Data(
                payload=Table(
                    col_types=input_table_data.col_types,
                    df=remains
                )
            )
            yield {
                "cell": cell_data,
                "remains": remains_data
            }

    @override
    @classmethod
    def hint(cls, input_schemas: Dict[str, Schema], current_params: Dict) -> Dict[str, Any]:
        col_choices: list[str] = []
        if "table" in input_schemas:
            table_schema = input_schemas["table"]
            if table_schema.type == Schema.Type.TABLE:
                assert table_schema.tab is not None
                col_types = table_schema.tab.col_types
                col_choices.extend(col_types.keys())
        return {"col_choices": col_choices}

@register_node()
class MapColumnEndNode(ForBaseEndNode):
    """
    Marks the end of the column loop, collecting results.
    """
    result_col: str | None = None
    
    _output_rows: list[Data] = PrivateAttr([])

    @property
    @override
    def pair_type(self) -> Literal["BEGIN", "END"]:
        return "END"

    @override
    def validate_parameters(self) -> None:
        if not self.type == "MapColumnEndNode":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="type",
                err_msg="Node type parameter mismmatch.",
            )
        if self.result_col is None or self.result_col.strip() == "":
            self.result_col = generate_default_col_name(self.id, "mapped")
        assert self.result_col is not None
        if not check_no_illegal_cols([self.result_col]):
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="result_col",
                err_msg="Result column name contains illegal characters.",
            )
        return

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [
            InPort(
                name="cell",
                description="Output cell for the mapped column.",
                accept=Pattern(
                    types={Schema.Type.BOOL, Schema.Type.INT, Schema.Type.FLOAT, Schema.Type.STR, Schema.Type.DATETIME}
                )
            ),
            InPort(
                name="remains",
                description="Output row containing the remaining columns.",
                accept=Pattern(
                    types={Schema.Type.TABLE}
                )
            )
        ], [
            OutPort(
                name="table",
                description="Output table containing the mapped column."
            )
        ]

    @override
    def infer_output_schemas(self, input_schemas: Dict[str, Schema]) -> Dict[str, Schema]:
        cell = input_schemas["cell"]
        row = input_schemas["table"]
        assert row.tab is not None
        col_types = row.tab.col_types
        if self.result_col in col_types:
            raise NodeParameterError(
                node_id=self.id,
                err_param_key='result_col',
                err_msg="Result column name already exists in the input table."
            )
        assert self.result_col is not None
        col_types[self.result_col] = cell.to_coltype()
        return {"table": Schema(type=Schema.Type.TABLE, tab=row.tab)}

    @override
    def process(self, input: Dict[str, Data]) -> Dict[str, Data]:
        assert False, "Unreachable!"

    @override
    def end_iter_loop(self, loop_outputs: Dict[str, Data]) -> None:
        """Save output rows for each iteration"""
        cell = loop_outputs["cell"]
        row = loop_outputs["remains"]
        assert isinstance(row, Table)
        df = row.df.copy()
        df[self.result_col] = cell
        col_types = row.col_types.copy()
        assert self.result_col is not None
        col_types[self.result_col] = cell.extract_schema().to_coltype()
        iter_data = Data(
            payload=Table(
                df=df,
                col_types=col_types
            )
        )
        self._output_rows.append(iter_data)
        return

    @override
    def finalize_loop(self) -> Dict[str, Data]:
        if len(self._output_rows) == 0:
            return {
                'table': Data(
                    payload=Table(
                        df=pd.DataFrame(),
                        col_types={}
                    )
                )
            }
        
        df_rows = []
        for row in self._output_rows:
            assert isinstance(row.payload, Table)
            df_rows.append(row.payload.df)
        combined_df = pd.concat(
            df_rows, ignore_index=True
        )
        assert isinstance(self._output_rows[0], Table)
        combined_col_types = self._output_rows[0].payload.col_types
        return {
            "table": Data(
                payload=Table(
                    df=combined_df,
                    col_types=combined_col_types
                )
            )
        }