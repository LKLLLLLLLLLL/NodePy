from .BaseNode import BaseNode, NodeValidationError, InPort, OutPort, Data, Schema
from pandas import DataFrame
from typing import List
from .Utils import Visualization, INDEX_COLUMN_NAME


"""
A series of node which operate columns of table.
"""


class SplitColNode(BaseNode):
    """
    Split an input table into multiple output tables by values of a column.

    Parameters
    - split_column: the column name to split on (must exist in input table)
    - split_values: list of values; for each value an output port is created
    - reserved_columns: optional list of columns to keep in each output (if None keep all columns)
    """

    split_column: str
    split_values: List[str]
    reserved_columns: List[str] | None = None

    def validate_parameters(self) -> None:
        if not self.type == "SplitNode":
            raise NodeValidationError("Node type must be 'SplitNode'.")
        if not self.split_column or self.split_column.strip() == "":
            raise NodeValidationError("split_column cannot be empty.")
        # pydantic already ensures split_values is List[str], just check non-empty
        if len(self.split_values) == 0:
            raise NodeValidationError("split_values must be a non-empty list.")
        # Check for empty reserved_columns list (use None instead)
        if self.reserved_columns is not None and len(self.reserved_columns) == 0:
            raise NodeValidationError(
                "reserved_columns cannot be an empty list (use None to keep all columns)."
            )

    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        # one input named 'input'
        in_ports = [
            InPort(
                name="input",
                accept_types={Schema.DataType.TABLE},
                table_columns=None,  # Accept any TABLE columns
                description="Input table to split",
                required=True,
            )
        ]
        # create one out port for each split value; names are safe Python identifiers
        out_ports: list[OutPort] = []
        for i, v in enumerate(self.split_values):
            # port name: out_{index}
            out_ports.append(
                OutPort(
                    name=f"out_{i}",
                    description=f"Rows where {self.split_column} == {v}",
                )
            )
        return in_ports, out_ports

    def validate_input(self, input: dict[str, Data]) -> None:
        # runtime check: ensure split_column exists in actual payload
        data = input["input"]
        payload = data.payload
        assert isinstance(payload, DataFrame)  # for type checker
        if self.split_column not in payload.columns:
            raise NodeValidationError(
                f"split_column '{self.split_column}' not in input DataFrame columns."
            )

    def _compute_output_schemas(self, input_schema: Schema) -> dict[str, Schema]:
        """
        Centralized schema computation logic.
        This ensures infer_output_schema and process return consistent schemas.
        Note: _index column is always preserved in all outputs.
        """
        out: dict[str, Schema] = {}

        if input_schema.columns is None:
            # unknown input, return TABLE with arbitrary columns
            for i in range(len(self.split_values)):
                out[f"out_{i}"] = Schema(type=Schema.DataType.TABLE, columns=None)
            return out

        # determine output columns
        if self.reserved_columns is None:
            # keep same columns as input (including _index)
            for i in range(len(self.split_values)):
                out[f"out_{i}"] = Schema(
                    type=Schema.DataType.TABLE, columns=input_schema.columns
                )
        else:
            # restrict to reserved_columns, but always include _index
            cols = {
                INDEX_COLUMN_NAME: input_schema.columns[INDEX_COLUMN_NAME]
            }  # Always include _index
            for c in self.reserved_columns:
                if c in input_schema.columns:
                    cols[c] = input_schema.columns[c]
            for i in range(len(self.split_values)):
                out[f"out_{i}"] = Schema(type=Schema.DataType.TABLE, columns=cols)
        return out

    def infer_output_schema(self, input_schema: dict[str, Schema]) -> dict[str, Schema]:
        # static check: if schema known, ensure split_column exists
        in_schema = input_schema.get("input")
        if in_schema is not None and in_schema.columns is not None:
            if self.split_column not in in_schema.columns:
                raise NodeValidationError(
                    f"split_column '{self.split_column}' not in input schema."
                )
            # static check: if schema known, ensure reserved_columns exist
            if self.reserved_columns is not None:
                missing = [
                    c for c in self.reserved_columns if c not in in_schema.columns
                ]
                if missing:
                    raise NodeValidationError(
                        f"reserved_columns {missing} not in input schema."
                    )

        if in_schema is None:
            # Fallback for unknown input
            in_schema = Schema(type=Schema.DataType.TABLE, columns=None)

        # Delegate to centralized schema computation
        return self._compute_output_schemas(in_schema)

    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        data = input["input"].payload
        assert isinstance(data, DataFrame)

        # Use centralized schema computation
        output_schemas = self._compute_output_schemas(input["input"].sche)

        outputs: dict[str, Data] = {}
        for i, val in enumerate(self.split_values):
            if self.reserved_columns is None:
                # Keep all columns (including _index)
                sub = data.loc[data[self.split_column] == val].copy()
            else:
                # Keep reserved_columns plus _index
                cols_to_keep = [INDEX_COLUMN_NAME] + self.reserved_columns
                sub = data.loc[data[self.split_column] == val, cols_to_keep].copy()

            outputs[f"out_{i}"] = Data(
                sche=output_schemas[f"out_{i}"],
                payload=sub,
            )

        # no visualization for split node
        self.vis = Visualization(
            node_id=self.id, type=Visualization.Type.NONE, payload=None
        )
        return outputs


class SelectColNode(BaseNode):
    """
    Select specific columns from input table.

    The _index column is always preserved automatically and doesn't need to be
    specified in selected_columns.

    Parameters:
    - selected_columns: list of column names to keep (excluding _index which is automatic)
    """

    selected_columns: List[str]

    def validate_parameters(self) -> None:
        if not self.type == "SelectColNode":
            raise NodeValidationError("Node type must be 'SelectColNode'.")

        # Check for non-empty list
        if len(self.selected_columns) == 0:
            raise NodeValidationError("selected_columns must be a non-empty list.")

        # Check for duplicates
        if len(self.selected_columns) != len(set(self.selected_columns)):
            raise NodeValidationError(
                "selected_columns contains duplicate column names."
            )

        # Ensure _index is not in the list (it's automatic)
        if INDEX_COLUMN_NAME in self.selected_columns:
            raise NodeValidationError(
                f"'{INDEX_COLUMN_NAME}' column is automatically preserved and should not be specified in selected_columns."
            )

    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [
            InPort(
                name="input",
                accept_types={Schema.DataType.TABLE},
                table_columns=None,  # Accept any TABLE
                description="Input table",
                required=True,
            )
        ], [OutPort(name="output", description="Table with selected columns")]

    def validate_input(self, input: dict[str, Data]) -> None:
        # Runtime check: ensure all selected columns exist in actual payload
        data = input["input"]
        payload = data.payload
        assert isinstance(payload, DataFrame)

        missing_cols = [
            col for col in self.selected_columns if col not in payload.columns
        ]
        if missing_cols:
            raise NodeValidationError(
                f"Selected columns {missing_cols} not found in input DataFrame."
            )

    def _compute_output_schema(self, input_schema: Schema) -> Schema:
        """
        Centralized schema computation logic.
        This ensures infer_output_schema and process return consistent schemas.
        """
        if input_schema.columns is None:
            # Unknown input columns, return TABLE with unknown columns
            return Schema(type=Schema.DataType.TABLE, columns=None)

        # Always include _index column
        output_cols = {INDEX_COLUMN_NAME: input_schema.columns[INDEX_COLUMN_NAME]}

        # Add selected columns
        for col in self.selected_columns:
            if col in input_schema.columns:
                output_cols[col] = input_schema.columns[col]

        return Schema(type=Schema.DataType.TABLE, columns=output_cols)

    def infer_output_schema(self, input_schema: dict[str, Schema]) -> dict[str, Schema]:
        in_schema = input_schema.get("input")

        # Static validation: ensure all selected columns exist in schema
        if in_schema is not None and in_schema.columns is not None:
            missing_cols = [
                col for col in self.selected_columns if col not in in_schema.columns
            ]
            if missing_cols:
                raise NodeValidationError(
                    f"Selected columns {missing_cols} not found in input schema."
                )

            # Ensure _index column exists in input
            if INDEX_COLUMN_NAME not in in_schema.columns:
                raise NodeValidationError(
                    f"Input table must have '{INDEX_COLUMN_NAME}' column."
                )

        if in_schema is None:
            in_schema = Schema(type=Schema.DataType.TABLE, columns=None)

        return {"output": self._compute_output_schema(in_schema)}

    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        data = input["input"].payload
        assert isinstance(data, DataFrame)

        # Select columns: _index + selected_columns
        cols_to_keep = [INDEX_COLUMN_NAME] + self.selected_columns
        result = data[cols_to_keep].copy()

        # Set visualization
        self.vis = Visualization(
            node_id=self.id, type=Visualization.Type.TABLE, payload=result
        )

        # Use centralized schema computation
        return {
            "output": Data(
                sche=self._compute_output_schema(input["input"].sche), payload=result
            )
        }


class JoinColNode(BaseNode):
    """
    A node to join two tables with given condition.
    Only support simple compare condition(==, !=, >, >=, <, <=) between two columns of the two tables.
    If user provides none condition, meas Cartesian product.
    Only support inner join.
    This node implement can be very slow.
    """
