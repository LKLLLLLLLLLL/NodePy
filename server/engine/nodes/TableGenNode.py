from .BaseNode import BaseNode, NodeValidationError, InPort, OutPort, Data, Schema
from pandas import DataFrame
from .Utils import (
    Visualization,
    add_index_column,
    validate_no_index_column_conflict,
    INDEX_COLUMN_NAME,
)
from typing import List, Dict, Any, Literal
import numpy as np


"""
A series of node that generates a table.
Such as generate by user input, generate by range, generate by random, etc.
"""


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
                raise NodeValidationError(
                    "All rows must have the same set of keys (columns)."
                )

        if set(self.column_names) != first_keys:
            raise NodeValidationError(
                "column_names must match keys of rows if provided."
            )

        # each column must have a consistent type (or None)
        first_types = {
            k: self._python_type_to_coltype(v) for k, v in self.rows[0].items()
        }
        for r in self.rows:
            for k, v in r.items():
                t = self._python_type_to_coltype(v)
                if t is not None and first_types[k] is not None and t != first_types[k]:
                    raise NodeValidationError(
                        f"Column '{k}' has inconsistent types in rows."
                    )

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

        self.vis = Visualization(
            node_id=self.id, type=Visualization.Type.TABLE, payload=df
        )
        return {"output": Data(sche=schem, payload=df)}


class RandomNode(BaseNode):
    """
    Node to generate a table, with a random column of specified type and range.
    """

    data_type: Literal["int", "float"]
    top: float | int
    bottom: float | int
    seed: int | None
    column_name: str

    def validate_parameters(self) -> None:
        if not self.type == "RandomNode":
            raise NodeValidationError("Node type must be 'RandomNode'.")
        if self.top <= self.bottom:
            raise NodeValidationError("top must be greater than bottom.")
        if self.column_name == "" or self.column_name.strip() == "":
            raise NodeValidationError("column_name cannot be empty.")

        # Validate that _index column is not used
        validate_no_index_column_conflict([self.column_name])

        if not isinstance(self.seed, int) and self.seed is not None:
            raise NodeValidationError("seed must be an integer or None.")
        if (
            self.data_type == "int"
            and isinstance(self.top, int)
            and isinstance(self.bottom, int)
        ):
            return
        elif (
            self.data_type == "float"
            and isinstance(self.bottom, float)
            and isinstance(self.top, float)
        ):
            return
        else:
            raise NodeValidationError("top and bottom must be all int or all float.")

    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [], [OutPort(name="output", description="The output table")]

    def validate_input(self, input: dict[str, Data]) -> None:
        """no input"""
        pass

    def _compute_output_schema(self) -> Schema:
        """
        Centralized schema computation logic.
        This ensures infer_output_schema and process return consistent schemas.
        """
        cols = {INDEX_COLUMN_NAME: {Schema.ColumnType.INT}}  # Add _index column

        if self.data_type == "int":
            cols[self.column_name] = {Schema.ColumnType.INT}
        else:
            cols[self.column_name] = {Schema.ColumnType.FLOAT}

        return Schema(type=Schema.DataType.TABLE, columns=cols)

    def infer_output_schema(self, input_schema: dict[str, Schema]) -> dict[str, Schema]:
        # Delegate to centralized schema computation
        return {"output": self._compute_output_schema()}

    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        """generate random data"""
        if (
            self.data_type == "int"
            and isinstance(self.top, int)
            and isinstance(self.bottom, int)
        ):
            data = np.random.default_rng(self.seed).integers(
                self.bottom, self.top, size=100
            )
        else:
            data = np.random.default_rng(self.seed).uniform(
                self.bottom, self.top, size=100
            )

        table = DataFrame({self.column_name: data})

        # Add automatic index column
        table = add_index_column(table)

        self.vis = Visualization(
            node_id=self.id, type=Visualization.Type.TABLE, payload=table
        )

        # Use centralized schema computation to ensure consistency
        return {
            "output": Data(
                sche=self._compute_output_schema(),
                payload=table,
            )
        }


class RangeNode(BaseNode):
    """
    Node to generate a table, with a range column of specified type and range.
    """

    start: float | int
    end: float | int
    step: float | int
    column_name: str

    def validate_parameters(self) -> None:
        if not self.type == "RangeNode":
            raise NodeValidationError("Node type must be 'RangeNode'.")
        if self.start >= self.end:
            raise NodeValidationError("start must be less than end.")
        if self.step <= 0:
            raise NodeValidationError("step must be positive.")
        if self.column_name == "" or self.column_name.strip() == "":
            raise NodeValidationError("column_name cannot be empty.")

        # Validate that _index column is not used
        validate_no_index_column_conflict([self.column_name])

        if (
            isinstance(self.start, int)
            and isinstance(self.end, int)
            and isinstance(self.step, int)
        ):
            return
        elif (
            isinstance(self.start, float)
            and isinstance(self.end, float)
            and isinstance(self.step, float)
        ):
            return
        else:
            raise NodeValidationError(
                "start, end, and step must be all int or all float."
            )

    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [], [OutPort(name="output", description="The output table")]

    def validate_input(self, input: dict[str, Data]) -> None:
        """no input"""
        pass

    def _compute_output_schema(self) -> Schema:
        """
        Centralized schema computation logic.
        This ensures infer_output_schema and process return consistent schemas.
        """
        cols = {INDEX_COLUMN_NAME: {Schema.ColumnType.INT}}  # Add _index column

        if (
            isinstance(self.start, int)
            and isinstance(self.end, int)
            and isinstance(self.step, int)
        ):
            cols[self.column_name] = {Schema.ColumnType.INT}
        else:
            cols[self.column_name] = {Schema.ColumnType.FLOAT}

        return Schema(type=Schema.DataType.TABLE, columns=cols)

    def infer_output_schema(self, input_schema: dict[str, Schema]) -> dict[str, Schema]:
        # Delegate to centralized schema computation
        return {"output": self._compute_output_schema()}

    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        """generate range data"""
        if (
            isinstance(self.start, int)
            and isinstance(self.end, int)
            and isinstance(self.step, int)
        ):
            data = list(range(self.start, self.end, self.step))
        else:
            data = []
            current = self.start
            while current < self.end:
                data.append(current)
                current += self.step

        table = DataFrame({self.column_name: data})

        # Add automatic index column
        table = add_index_column(table)

        self.vis = Visualization(
            node_id=self.id, type=Visualization.Type.TABLE, payload=table
        )

        # Use centralized schema computation to ensure consistency
        return {"output": Data(sche=self._compute_output_schema(), payload=table)}
