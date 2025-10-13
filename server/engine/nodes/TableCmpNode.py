from .Utils import Data
from .BaseNode import BaseNode, InPort, OutPort, Schema, NodeValidationError
from .Utils import CmpCondition, Visualization, validate_no_index_column_conflict
from typing import Literal
from pandas import DataFrame
import operator

class TableCmpNode(BaseNode):
    """
    Node to compare a column in a table with a primitive value.
    The input must be a table and a primitive value of int, float, str, bool.
    """
    
    # Operator mapping for vectorized operations
    _OP_MAP = {
        "EQ": operator.eq,
        "NE": operator.ne,
        "GT": operator.gt,
        "LT": operator.lt,
        "GE": operator.ge,
        "LE": operator.le,
    }
    
    op: Literal["EQ", "NE", "GT", "LT", "GE", "LE"]
    column: str
    result_col: str
    _cond: CmpCondition | None = None
    
    def validate_parameters(self) -> None:
        if not self.type == "TableCmpNode":
            raise NodeValidationError("Node type must be 'TableCmpNode'.")
        if self.column == "" or self.column.strip() == "":
            raise NodeValidationError("column cannot be empty.")
        if self.result_col == "" or self.result_col.strip() == "":
            raise NodeValidationError("result_col cannot be empty.")
        
        # Validate that result_col doesn't conflict with reserved _index column
        validate_no_index_column_conflict([self.result_col])
        
        # set CmpCondition
        self._cond = CmpCondition(
            op=self.op,
            left = ("table_input", self.column),
            right = ("value_input", None)
        )

    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        # Accept TABLE and any primitive type (not TABLE)
        primitive_types = {
            Schema.DataType.INT,
            Schema.DataType.FLOAT,
            Schema.DataType.STR,
            Schema.DataType.BOOL
        }
        return [
            InPort(
                name="table_input",
                accept_types={Schema.DataType.TABLE},
                table_columns={self.column : {Schema.ColumnType.INT, Schema.ColumnType.FLOAT, Schema.ColumnType.STR, Schema.ColumnType.BOOL}},
                description="Input table data",
                required=True
            ),
            InPort(
                name="value_input",
                accept_types=primitive_types,
                description="Primitive value to compare with",
                required=True
            )
        ], [
            OutPort(name="output", description="The comparison result table")
        ]
    
    def validate_input(self, input: dict[str, Data]) -> None:
        assert(self._cond is not None)
        # Dynamic validate the condition
        self._cond.dynamic_validate(input)
    
    def _compute_output_schema(self, input_schema: dict[str, Schema]) -> Schema:
        """
        Centralized schema computation logic.
        This ensures infer_output_schema and process return consistent schemas.
        """
        input_cols = input_schema["table_input"].columns
        assert(input_cols is not None)
        # ensure col_name not exists in input table
        if self.result_col in input_cols:
            raise NodeValidationError(f"result_col '{self.result_col}' already exists in input table.")
        return Schema(
            type=Schema.DataType.TABLE,
            columns={self.result_col: {Schema.ColumnType.BOOL}} | input_cols
        )
    
    def infer_output_schema(self, input_schema: dict[str, Schema]) -> dict[str, Schema]:
        # Static validate via condition if available
        if self._cond is not None:
            self._cond.static_validate(input_schema)
        # Delegate to centralized schema computation
        return {"output": self._compute_output_schema(input_schema)}
    
    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        assert(self._cond is not None)
        table_data = input["table_input"].payload
        value_data = input["value_input"].payload
        assert(isinstance(table_data, DataFrame))
        assert(len(table_data) > 0)
        assert(isinstance(value_data, (int, float, str, bool)))
        
        # Vectorized evaluation using operator mapping
        result_rows = table_data.copy()
        op_func = self._OP_MAP[self.op]
        result_series = op_func(result_rows[self.column], value_data)
        result_rows[self.result_col] = result_series.astype(bool)
        
        # Set visualization
        self.vis = Visualization(
            type=Visualization.Type.TABLE,
            payload=result_rows,
            node_id=self.id
        )
        
        # Use centralized schema computation to ensure consistency
        return {
            "output": Data(
                payload=result_rows,
                sche=self._compute_output_schema({
                    "table_input": input["table_input"].sche,
                    "value_input": input["value_input"].sche
                }),
            )
        }