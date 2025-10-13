from .BaseNode import BaseNode, NodeValidationError, InPort, OutPort, Data, Schema
from pandas import DataFrame
from typing import List
from .Utils import Visualization, INDEX_COLUMN_NAME


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
            raise NodeValidationError("selected_columns contains duplicate column names.")
        
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
        ], [
            OutPort(name="output", description="Table with selected columns")
        ]

    def validate_input(self, input: dict[str, Data]) -> None:
        # Runtime check: ensure all selected columns exist in actual payload
        data = input["input"]
        payload = data.payload
        assert isinstance(payload, DataFrame)
        
        missing_cols = [col for col in self.selected_columns if col not in payload.columns]
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
            missing_cols = [col for col in self.selected_columns if col not in in_schema.columns]
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
            node_id=self.id,
            type=Visualization.Type.TABLE,
            payload=result
        )
        
        # Use centralized schema computation
        return {
            "output": Data(
                sche=self._compute_output_schema(input["input"].sche),
                payload=result
            )
        }
