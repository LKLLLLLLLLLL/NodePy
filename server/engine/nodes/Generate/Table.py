from ..BaseNode import BaseNode, InPort, OutPort, register_node
from typing import List, Dict, override
from server.models.exception import NodeParameterError
from server.models.data import Data
from server.models.schema import (
    Schema,
    TableSchema,
    check_no_illegal_cols,
    ColType,
)
from pydantic import PrivateAttr
from pandas import DataFrame

"""
A series of node that generates a table.
Such as generate by user input, generate by range, generate by random, etc.
"""

@register_node
class TableNode(BaseNode):
    """
    A node to generate a table from user provided data.
    
    Parameters (provided at construction time):
      - rows: list[dict[column_name -> value]]
      - column_names: optional list[str] to enforce column order/selection
    """

    rows: List[Dict[str, str | int | float | bool]]
    col_names: List[str]
    _col_types: Dict[str, ColType] | None = PrivateAttr(None)  # cache for column types

    @override
    def validate_parameters(self) -> None:
        if not self.type == "TableNode":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="type",
                err_msg="Node type must be 'TableNode'."
            )
        if len(self.col_names) == 0:
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="col_names",
                err_msg="Column names cannot be empty."
            )
        if len(self.rows) == 0:
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="rows",
                err_msg="Rows cannot be empty. Else cannot refer types of columns."
            )
        # check all rows key equals col_names (compare as list to avoid dict_keys mismatch)
        for row in self.rows:
            if list(row.keys()) != list(self.col_names):
                raise NodeParameterError(
                    node_id=self.id,
                    err_param_key="rows",
                    err_msg=f"All rows must have the same keys as col_names. But got row keys: {list(row.keys())}"
                )
        # check no illegal column names
        check_no_illegal_cols(self.col_names)
        # check if all columns has same type
        if len(self.rows) > 0:
            col_types: Dict[str, ColType] = {}
            # traverse first row to initialize types
            first_row = self.rows[0]
            for col in self.col_names:
                val = first_row[col]
                if isinstance(val, str):
                    col_types[col] = ColType.STR
                elif isinstance(val, bool):
                    col_types[col] = ColType.BOOL
                elif isinstance(val, int):
                    col_types[col] = ColType.INT
                elif isinstance(val, float):
                    col_types[col] = ColType.FLOAT
                else:
                    raise NodeParameterError(
                        node_id=self.id,
                        err_param_key="rows",
                        err_msg=f"Unsupported value type {type(val)} in column '{col}'."
                    )
            self._col_types = col_types
            # traverse other rows to check types
            for row in self.rows[1:]:
                for col in self.col_names:
                    val = row[col]
                    if isinstance(val, str):
                        if col_types[col] != ColType.STR:
                            raise NodeParameterError(
                                node_id=self.id,
                                err_param_key="rows",
                                err_msg=f"Column '{col}' has mixed types: {col_types[col]} and STR."
                            )
                    elif isinstance(val, bool):
                        if col_types[col] != ColType.BOOL:
                            raise NodeParameterError(
                                node_id=self.id,
                                err_param_key="rows",
                                err_msg=f"Column '{col}' has mixed types: {col_types[col]} and BOOL."
                            )
                    elif isinstance(val, int):
                        if col_types[col] == ColType.FLOAT:
                            raise NodeParameterError(
                                node_id=self.id,
                                err_param_key="rows",
                                err_msg=f"Column '{col}' has mixed types: FLOAT and INT."
                            )
                        col_types[col] = ColType.INT # INT can be promoted to FLOAT
                    elif isinstance(val, float):
                        col_types[col] = ColType.FLOAT # promote to FLOAT
                    else:
                        raise NodeParameterError(
                            node_id=self.id,
                            err_param_key="rows",
                            err_msg=f"Unsupported value type {type(val)} in column '{col}'."
                        )
        assert self._col_types is not None
        return

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [], [
            OutPort(name="table", description="The generated table.")
        ]

    @override
    def infer_output_schemas(self, input_schemas: Dict[str, Schema]) -> Dict[str, Schema]:
        assert self._col_types is not None
        return {
            "table": Schema(type=Schema.Type.TABLE, tab=TableSchema(col_types=self._col_types))
        }

    @override
    def process(self, input: Dict[str, Data]) -> Dict[str, Data]:
        assert self._col_types is not None
        df = DataFrame(self.rows, columns=self.col_names)
        out_table = Data.from_df(df)
        return {"table": out_table}
        
@register_node
class RandomNode(BaseNode):
    """
    Node to generate a table, with a random column of specified type and range.
    """

@register_node
class RangeNode(BaseNode):
    """
    Node to generate a table, with a range column of specified type and range.
    """