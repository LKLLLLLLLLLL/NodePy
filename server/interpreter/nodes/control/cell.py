from datetime import datetime
from typing import Any, Dict, override

from pydantic import PrivateAttr

from server.models.data import Data, Table
from server.models.exception import (
    NodeExecutionError,
    NodeParameterError,
    NodeValidationError,
)
from server.models.schema import (
    ColType,
    Pattern,
    Schema,
)

from ..base_node import BaseNode, InPort, OutPort, register_node


@register_node()
class GetCellNode(BaseNode):
    """
    Get a cell value from specified column in a specific row.
    Support negative indexing for row.
    The row index can be specified as parameters or as inputs.
    """

    row: int | None = None
    col: str

    _infered_value_type: ColType | None = PrivateAttr(default=None)

    @override
    def validate_parameters(self) -> None:
        if not self.type == "GetCellNode":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="type",
                err_msg="Node type parameter mismatch.",
            )
        if self.col.strip() == "":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="col",
                err_msg="Column name cannot be empty or whitespace only.",
            )
        return

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [
            InPort(
                name="table",
                description="Input table to get cell from.",
                accept=Pattern(
                    types={Schema.Type.TABLE},
                    table_columns={self.col: set()} if self.col is not None else {},
                ),
            ),
            InPort(
                name="row",
                description="Row index to get cell from. Supports negative indexing.",
                optional=True,
                accept=Pattern(
                    types={Schema.Type.INT},
                ),
            ),
        ], [
            OutPort(
                name="value",
                description="The value of the specified cell.",
            )
        ]

    @override
    def infer_output_schemas(self, input_schemas: Dict[str, Schema]) -> Dict[str, Schema]:
        table_schema = input_schemas["table"]
        assert table_schema.tab is not None
        if self.col not in table_schema.tab.col_types:
            raise NodeValidationError(
                node_id=self.id,
                err_input="table",
                err_msg=f"Column '{self.col}' does not exist in the input table.",
            )
        col_type = table_schema.tab.col_types[self.col]
        # validate if row input is provided
        if "row" not in input_schemas and self.row is None:
            raise NodeValidationError(
                node_id=self.id,
                err_input="row",
                err_msg="Row index must be provided either as input or parameter.",
            )
        self._infered_value_type = col_type
        return {"value": Schema.from_coltype(col_type)}

    @override
    def process(self, input: Dict[str, Data]) -> Dict[str, Data]:
        input_table = input["table"]
        assert isinstance(input_table.payload, Table)
        df = input_table.payload.df
        # determine the row index
        if "row" in input:
            row_data = input["row"]
            assert isinstance(row_data.payload, int)
            row_index = row_data.payload
        else:
            assert self.row is not None
            row_index = self.row
        # handle negative indexing
        if row_index < 0:
            row_index = len(df) + row_index
        if row_index < 0 or row_index >= len(df):
            raise NodeExecutionError(
                node_id=self.id,
                err_msg=f"Row index {row_index} is out of bounds for table with {len(df)} rows.",
            )
        if self.col not in df.columns:
            raise NodeExecutionError(
                node_id=self.id,
                err_msg=f"Column '{self.col}' does not exist in the input table.",
            )
        cell_value = df.iloc[row_index][self.col]
        assert self._infered_value_type is not None
        output_data = Data(payload=cell_value)
        return {"value": output_data}

    @override
    @classmethod
    def hint(cls, input_schemas: Dict[str, Schema], current_params: Dict) -> Dict[str, Any]:
        hint = {}
        if "table" in input_schemas:
            col_choices = []
            if input_schemas["table"].tab is not None:
                for col in input_schemas["table"].tab.col_types.keys():
                    col_choices.append(col)
            hint["col_choices"] = col_choices
        return hint


@register_node()
class SetCellNode(BaseNode):
    """
    Set a cell value in specified column in a specific row.
    Support negative indexing for row.
    The row index can be specified as parameters or as inputs.
    """

    row: int | None = None
    col: str

    _col_types: Dict[str, ColType] | None = PrivateAttr(default=None)

    @override
    def validate_parameters(self) -> None:
        if not self.type == "SetCellNode":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="type",
                err_msg="Node type parameter mismatch.",
            )
        if self.col.strip() == "":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="col",
                err_msg="Column name cannot be empty or whitespace only.",
            )
        return

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [
            InPort(
                name="table",
                description="Input table to set cell in.",
                accept=Pattern(
                    types={Schema.Type.TABLE},
                    table_columns={self.col: set()} if self.col is not None else {},
                ),
            ),
            InPort(
                name="value",
                description="The value to set in the specified cell.",
                accept=Pattern(
                    types={Schema.Type.INT, Schema.Type.FLOAT, Schema.Type.STR, Schema.Type.BOOL, Schema.Type.DATETIME},
                ),
            ),
            InPort(
                name="row",
                description="Row index to set cell in. Supports negative indexing.",
                optional=True,
                accept=Pattern(
                    types={Schema.Type.INT},
                ),
            ),
        ], [
            OutPort(
                name="table",
                description="The table with the updated cell value.",
            )
        ]

    @override
    def infer_output_schemas(self, input_schemas: Dict[str, Schema]) -> Dict[str, Schema]:
        table_schema = input_schemas["table"]
        assert table_schema.tab is not None
        if self.col not in table_schema.tab.col_types:
            raise NodeValidationError(
                node_id=self.id,
                err_input="table",
                err_msg=f"Column '{self.col}' does not exist in the input table.",
            )
        # validate if row input is provided
        if "row" not in input_schemas and self.row is None:
            raise NodeValidationError(
                node_id=self.id,
                err_input="row",
                err_msg="Row index must be provided either as input or parameter.",
            )
        self._col_types = table_schema.tab.col_types
        # validate if the cell_value type matches the column type
        col_type = table_schema.tab.col_types[self.col]
        cell_value_type = input_schemas["value"].to_coltype()
        if col_type != cell_value_type:
            raise NodeValidationError(
                node_id=self.id,
                err_input="value",
                err_msg=f"Type of value ({cell_value_type}) does not match column '{self.col}' type ({col_type}).",
            )
        return {"table": table_schema}

    @override
    def process(self, input: Dict[str, Data]) -> Dict[str, Data]:
        input_table = input["table"]
        assert isinstance(input_table.payload, Table)
        df = input_table.payload.df.copy()
        # determine the row index
        row_index: int
        if "row" in input:
            row_data = input["row"]
            assert isinstance(row_data.payload, int)
            row_index = int(row_data.payload)
        else:
            assert self.row is not None
            row_index = self.row
        # handle negative indexing
        if row_index < 0:
            row_index = len(df) + row_index
        if row_index < 0 or row_index >= len(df):
            raise NodeExecutionError(
                node_id=self.id,
                err_msg=f"Row index {row_index} is out of bounds for table with {len(df)} rows.",
            )
        if self.col not in df.columns:
            raise NodeExecutionError(
                node_id=self.id,
                err_msg=f"Column '{self.col}' does not exist in the input table.",
            )
        value = input["value"].payload
        assert isinstance(row_index, int)
        assert isinstance(value, (int, float, str, bool, datetime))
        col_idx = df.columns.get_loc(self.col)
        assert isinstance(col_idx, int)
        df.iat[row_index, col_idx] = value
        assert self._col_types is not None
        updated_table = Table(col_types=self._col_types, df=df)
        output_data = Data(payload=updated_table)
        return {"table": output_data}

    @override
    @classmethod
    def hint(cls, input_schemas: Dict[str, Schema], current_params: Dict) -> Dict[str, Any]:
        hint = {}
        if "table" in input_schemas:
            col_choices = []
            if input_schemas["table"].tab is not None:
                for col in input_schemas["table"].tab.col_types.keys():
                    col_choices.append(col)
            hint["col_choices"] = col_choices
        return hint
