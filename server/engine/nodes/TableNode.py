from .BaseNode import BaseNode, NodeValidationError, InPort, OutPort, Data, Schema
from pandas import DataFrame
from .Utils import Visualization, add_index_column, validate_no_index_column_conflict, INDEX_COLUMN_NAME
from typing import List, Dict, Any


class TableNode(BaseNode):
    """
    Create a table node from user-provided rows.

    Parameters (provided at construction time):
      - rows: list[dict[column_name -> value]]
      - column_names: optional list[str] to enforce column order/selection
    """
    rows: List[Dict[str, Any]]
    column_names: List[str]

    def validate_parameters(self) -> None:
        if not self.type == "TableNode":
            raise NodeValidationError("Node type must be 'TableNode'.")
        # pydantic ensures rows is List[Dict[str, Any]], no isinstance check needed
        if len(self.rows) == 0:
            # not allow empty table
            raise NodeValidationError("Empty rows require column_names to be provided.")

        first_keys = set(self.rows[0].keys())
        
        # Validate that _index column is not used
        validate_no_index_column_conflict(first_keys)
        
        for r in self.rows:
            # pydantic already validated each r is dict
            if set(r.keys()) != first_keys:
                raise NodeValidationError("All rows must have the same set of keys (columns).")

        if set(self.column_names) != first_keys:
            raise NodeValidationError("column_names must match keys of rows if provided.")
        
        # each column must have a consistent type (or None)
        first_types = {k: self._python_type_to_coltype(v) for k, v in self.rows[0].items()}
        for r in self.rows:
            for k, v in r.items():
                t = self._python_type_to_coltype(v)
                if t is not None and first_types[k] is not None and t != first_types[k]:
                    raise NodeValidationError(f"Column '{k}' has inconsistent types in rows.")

    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [], [OutPort(name="output", description="User provided table")]

    def validate_input(self, input: dict[str, Data]) -> None:
        # no input
        pass

    def _python_type_to_coltype(self, v: Any):
        if v is None:
            raise NodeValidationError("Column values cannot be None.")
        if isinstance(v, bool):
            return Schema.ColumnType.BOOL
        if isinstance(v, int) and not isinstance(v, bool):
            return Schema.ColumnType.INT
        if isinstance(v, float):
            return Schema.ColumnType.FLOAT
        return Schema.ColumnType.STR

    def _compute_output_schema(self) -> Schema:
        """
        Centralized schema computation logic.
        This ensures infer_output_schema and process return consistent schemas.
        """
        cols: Dict[str, set[Schema.ColumnType]] = {}

        # Add _index column (always INT)
        cols[INDEX_COLUMN_NAME] = {Schema.ColumnType.INT}
        
        for c in self.rows[0].keys():
            cols[c] = set()
        for r in self.rows:
            for c, v in r.items():
                t = self._python_type_to_coltype(v)
                cols[c].add(t)

        return Schema(type=Schema.DataType.TABLE, columns=cols)

    def infer_output_schema(self, input_schema: dict[str, Schema]) -> dict[str, Schema]:
        # Delegate to centralized schema computation
        return {"output": self._compute_output_schema()}

    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        # build DataFrame from rows
        if len(self.rows) == 0:
            # build empty frame with columns
            df = DataFrame(columns=self.column_names)
        else:
            df = DataFrame(self.rows)

        # Add automatic index column
        df = add_index_column(df)
        
        # Use centralized schema computation to ensure consistency
        schem = self._compute_output_schema()
        
        self.vis = Visualization(node_id=self.id, type=Visualization.Type.TABLE, payload=df)
        return {"output": Data(sche=schem, payload=df)}
