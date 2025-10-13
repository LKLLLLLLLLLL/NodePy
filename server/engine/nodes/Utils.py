from pydantic import BaseModel, model_validator
from typing_extensions import Self
from enum import Enum
from pandas import DataFrame
from pandas.api import types as ptypes
from pathlib import Path
from typing import Literal

"""
Constants
"""
INDEX_COLUMN_NAME = "_index"  # Reserved column name for automatic row indexing

"""
Errors definitions
"""
class NodeValidationError(Exception):
    """static validation error"""
    pass

class NodeExecutionError(Exception):
    """runtime execution error"""
    pass

"""
Helper functions
"""
def add_index_column(df: DataFrame) -> DataFrame:
    """
    Add automatic index column to a DataFrame.
    This column is required for all table operations and cannot be removed.
    
    Args:
        df: Input DataFrame
        
    Returns:
        DataFrame with _index column added at the beginning
        
    Raises:
        NodeValidationError: If _index column already exists
    """
    if INDEX_COLUMN_NAME in df.columns:
        raise NodeValidationError(
            f"Column name '{INDEX_COLUMN_NAME}' is reserved for automatic indexing."
        )
    
    # Create a copy and add index column at the beginning
    result = df.copy()
    result.insert(0, INDEX_COLUMN_NAME, range(len(result)))
    return result

def validate_no_index_column_conflict(column_names: list[str] | set[str]) -> None:
    """
    Validate that user-provided column names don't conflict with reserved index column.
    
    Args:
        column_names: List or set of column names to validate
        
    Raises:
        NodeValidationError: If _index is used in column names
    """
    if INDEX_COLUMN_NAME in column_names:
        raise NodeValidationError(
            f"Column name '{INDEX_COLUMN_NAME}' is reserved and cannot be used."
        )


"""
Data definations
"""

class Schema(BaseModel):
    """schema defined the data type between nodes"""

    class DataType(str, Enum):
        """data type of object passed between nodes"""
        TABLE = "table"  # dataframe
        STR = "str"  # string
        INT = "int"  # integer
        FLOAT = "float"  # float
        BOOL = "bool"  # boolean
    
    class ColumnType(str, Enum):
        """column type in TABLE schema"""
        INT = "int64"
        FLOAT = "float64"
        STR = "string"
        BOOL = "bool"

    type: DataType
    columns: dict[str, set[ColumnType]] | None = None  # for TABLE type, list of column names

    @model_validator(mode="after")
    def verify(self) -> Self:
        if self.type == Schema.DataType.TABLE and self.columns is None:
            # Allow None for arbitrary columns in TABLE type
            pass
        elif self.type != Schema.DataType.TABLE and self.columns is not None:
            raise NodeValidationError("For non-TABLE type, columns must be None.")
        if self.type == Schema.DataType.TABLE and self.columns is not None:
            for col, col_type in self.columns.items():
                if col.strip() == "":
                    raise NodeValidationError(f"Invalid column name: '{col}'")
                if not col_type:
                    raise NodeValidationError(f"Column '{col}' must have a non-empty set of ColumnType.")
        return self

    def include(self, other: "Schema") -> bool:
        """check if self includes other schema"""
        if self.type != other.type:
            return False
        if self.type == Schema.DataType.TABLE:
            if self.columns is None:
                return True  # Arbitrary columns include any specific columns
            if other.columns is None:
                return False  # Specific columns do not include arbitrary
            return all(col in self.columns for col in other.columns)
        return True


class Data(BaseModel):
    """the data wrapper"""

    sche: Schema
    payload: DataFrame | str | int | bool | float

    model_config = {"arbitrary_types_allowed": True}  # allow DataFrame type

    @model_validator(mode="after")
    def verify(self) -> Self:
        if self.sche.type == Schema.DataType.TABLE:
            if not isinstance(self.payload, DataFrame):
                raise NodeExecutionError(
                    "Payload must be a DataFrame for TABLE schema."
                )
            if self.sche.columns is not None:
                missing_cols = [
                    col for col in self.sche.columns if col not in self.payload.columns
                ]
                if missing_cols:
                    raise NodeExecutionError(
                        f"Payload is missing columns: {missing_cols}"
                    )
        elif self.sche.type == Schema.DataType.STR:
            if not isinstance(self.payload, str):
                raise NodeExecutionError("Payload must be a string for STR schema.")
        elif self.sche.type == Schema.DataType.INT:
            if not isinstance(self.payload, int):
                raise NodeExecutionError("Payload must be an integer for INT schema.")
        elif self.sche.type == Schema.DataType.FLOAT:
            if not isinstance(self.payload, float):
                raise NodeExecutionError("Payload must be a float for FLOAT schema.")
        elif self.sche.type == Schema.DataType.BOOL:
            if not isinstance(self.payload, bool):
                raise NodeExecutionError("Payload must be a boolean for BOOL schema.")
        else:
            raise NodeExecutionError(f"Unsupported schema type: {self.sche.type}")
        # validate real data against schema if TABLE
        if self.sche.type == Schema.DataType.TABLE:
            assert isinstance(self.payload, DataFrame)
            # if no per-column type info provided, skip dtype checks
            if self.sche.columns is None:
                return self
            if not isinstance(self.sche.columns, dict):
                raise NodeExecutionError("Schema.columns must be a dict when provided.")
            for col, expected in self.sche.columns.items():
                if col not in self.payload.columns:
                    raise NodeExecutionError(
                        f"Payload missing column for type check: {col}"
                    )
                ser = self.payload[col]
                # expected is a set[ColumnType]
                if Schema.ColumnType.INT in expected:
                    if not ptypes.is_integer_dtype(ser.dtype):
                        raise NodeExecutionError(f"Column '{col}' is not integer dtype")
                if Schema.ColumnType.FLOAT in expected:
                    if not ptypes.is_float_dtype(ser.dtype):
                        raise NodeExecutionError(f"Column '{col}' is not float dtype")
                if Schema.ColumnType.STR in expected:
                    if not ptypes.is_string_dtype(ser.dtype):
                        raise NodeExecutionError(f"Column '{col}' is not string dtype")
                if Schema.ColumnType.BOOL in expected:
                    if not ptypes.is_bool_dtype(ser.dtype):
                        raise NodeExecutionError(f"Column '{col}' is not bool dtype")
        return self


class InPort(BaseModel):
    """
    Input port definition for nodes.
    
    - accept_types: Set of accepted DataTypes (required, can be single or multiple)
    - table_columns: For TABLE types, specifies required columns and their types (optional)
    - required: Whether this port must be connected
    """
    name: str
    accept_types: set[Schema.DataType]  # Always use this, no more sche field
    table_columns: dict[str, set[Schema.ColumnType]] | None = None  # Only for TABLE types, None means no restriction
    description: str | None = None
    required: bool = True
    
    @model_validator(mode="after")
    def verify(self) -> Self:
        if len(self.accept_types) == 0:
            raise NodeValidationError(f"Port '{self.name}' accept_types cannot be empty.")
        
        # If table_columns is specified, TABLE must be in accept_types
        if self.table_columns is not None:
            if Schema.DataType.TABLE not in self.accept_types:
                raise NodeValidationError(
                    f"Port '{self.name}' specifies table_columns but TABLE not in accept_types."
                )
            # Validate column names
            for col_name in self.table_columns.keys():
                if col_name.strip() == "":
                    raise NodeValidationError(f"Port '{self.name}' has empty column name.")
        
        return self
    
    def accepts(self, schema: Schema) -> bool:
        """Check if this port accepts the given schema."""
        # Check type compatibility
        if schema.type not in self.accept_types:
            return False
        
        # For TABLE types, check column compatibility
        if schema.type == Schema.DataType.TABLE and self.table_columns is not None:
            # If the incoming schema has no column info, raise error
            if schema.columns is None:
                if self.table_columns is None:
                    return True  # Accept any columns
                else:
                    return False  # Cannot verify required columns

            # Ensure every required column is present and its declared types
            # are compatible with what this port expects.
            for req_col, req_types in self.table_columns.items():
                if req_col not in schema.columns:
                    return False
                actual_types = schema.columns[req_col]
                # Require actual types to be a subset of required/allowed types.
                # e.g., if port expects {INT, FLOAT} and actual is {INT}, that's OK.
                # But if actual contains types not allowed by the port, reject.
                if not actual_types.issubset(req_types):
                    return False
            return True
        
        return True


class OutPort(BaseModel):
    name: str
    description: str | None = None


"""
Visualization definations
"""
class Visualization(BaseModel):
    class Type(str, Enum):
        PICTURE = "picture"
        TABLE = "table"
        STR = "str"
        INT = "int"
        FLOAT = "float"
        BOOL = "bool"
        NONE = "None"
    
    node_id: str
    type: Type
    payload: Path | DataFrame | str | int | float | bool | None
    
    model_config = {"arbitrary_types_allowed": True}  # allow DataFrame type

    @model_validator(mode="after")
    def verify(self) -> Self:
        if self.type == self.Type.PICTURE:
            if not isinstance(self.payload, Path):
                raise NodeExecutionError(
                    "Payload must be a Path for picture visualization."
                )
            if not self.payload.exists():
                raise NodeExecutionError(f"Picture path does not exist: {self.payload}")
        elif self.type == self.Type.TABLE:
            if not isinstance(self.payload, DataFrame):
                raise NodeExecutionError(
                    "Payload must be a DataFrame for table visualization."
                )
        elif self.type == self.Type.STR:
            if not isinstance(self.payload, str):
                raise NodeExecutionError(
                    "Payload must be a string for str visualization."
                )
        elif self.type == self.Type.INT:
            if not isinstance(self.payload, int):
                raise NodeExecutionError(
                    "Payload must be an integer for int visualization."
                )
        elif self.type == self.Type.FLOAT:
            if not isinstance(self.payload, float):
                raise NodeExecutionError(
                    "Payload must be a float for float visualization."
                )
        elif self.type == self.Type.BOOL:
            if not isinstance(self.payload, bool):
                raise NodeExecutionError(
                    "Payload must be a boolean for bool visualization."
                )
        elif self.type == self.Type.NONE:
            if self.payload is not None:
                raise NodeExecutionError("Payload must be None for None visualization.")
        else:
            raise NodeExecutionError(f"Unsupported visualization type: {self.type}")
        return self


"""
global_config shared by all nodes for same requests
"""
class GlobalConfig(BaseModel):
    temp_dir: Path  # directory to store temporary files
    user_id: str    # user id for current request
    
    @model_validator(mode="after")
    def verify(self) -> Self:
        if not self.temp_dir.exists():
            self.temp_dir.mkdir(parents=True, exist_ok=True)
        if not self.temp_dir.is_dir():
            raise NodeExecutionError(f"temp_dir is not a directory: {self.temp_dir}")
        if self.user_id == "" or self.user_id.strip() == "":
            raise NodeExecutionError("user_id cannot be empty.")
        return self

"""
Compare Condition definition.
Reused in many nodes.
"""
class CmpCondition(BaseModel):
    """
    Simple comparison condition between two operands.
    Each operand is (input_name, column_name).
    - If column_name is empty string, the operand refers to the input itself (for primitive types).
    - Otherwise, it refers to a column in a TABLE type input.
    """

    op: Literal["EQ", "NE", "GT", "LT", "GE", "LE"]
    left: tuple[str, str | None]  # [input_name, column_name]
    right: tuple[str, str | None]  # [input_name, column_name]

    @model_validator(mode="after")
    def verify(self) -> Self:
        if self.left[0].strip() == "":
            raise NodeValidationError("Left operand must have non-empty input name.")
        if self.right[0].strip() == "":
            raise NodeValidationError("Right operand must have non-empty input name.")
        return self

    def static_validate(self, schemas: dict[str, Schema]) -> None:
        """Stage2: Static check - verify columns exist and types are compatible."""
        left_input, left_col = self.left
        right_input, right_col = self.right

        # Check inputs exist
        if left_input not in schemas:
            raise NodeValidationError(f"Left input '{left_input}' not in schemas.")
        if right_input not in schemas:
            raise NodeValidationError(f"Right input '{right_input}' not in schemas.")

        left_schema = schemas[left_input]
        right_schema = schemas[right_input]

        # Get operand types
        left_type = self._get_operand_type(left_schema, left_col, "left")
        right_type = self._get_operand_type(right_schema, right_col, "right")

        # Check type compatibility
        if left_type != right_type:
            raise NodeValidationError(
                f"Type mismatch: left is {left_type}, right is {right_type}"
            )

    def _get_operand_type(
        self, schema: Schema, col_name: str | None, side: Literal["left", "right"]
    ) -> Schema.DataType:
        """Extract the type of an operand (handles both primitive and TABLE columns)."""
        primitive_types = {
            Schema.DataType.BOOL,
            Schema.DataType.INT,
            Schema.DataType.STR,
            Schema.DataType.FLOAT,
        }

        # None column name means primitive type
        if col_name is None:
            if schema.type not in primitive_types:
                raise NodeValidationError(
                    f"{side.capitalize()} operand has no column name but schema is not primitive."
                )
            return schema.type

        # Column reference in TABLE
        if schema.type != Schema.DataType.TABLE:
            raise NodeValidationError(
                f"{side.capitalize()} operand references column '{col_name}' but schema is not TABLE."
            )
        if schema.columns is None:
            raise NodeValidationError(
                f"{side.capitalize()} operand references column '{col_name}' but schema has no column info."
            )
        if col_name not in schema.columns:
            raise NodeValidationError(
                f"{side.capitalize()} column '{col_name}' not in schema."
            )

        col_types = schema.columns[col_name]
        if len(col_types) != 1:
            raise NodeValidationError(
                f"{side.capitalize()} column '{col_name}' has ambiguous types: {col_types}"
            )

        # Map ColumnType to DataType
        col_type = next(iter(col_types))
        type_map = {
            Schema.ColumnType.INT: Schema.DataType.INT,
            Schema.ColumnType.FLOAT: Schema.DataType.FLOAT,
            Schema.ColumnType.STR: Schema.DataType.STR,
            Schema.ColumnType.BOOL: Schema.DataType.BOOL,
        }
        return type_map[col_type]

    def _get_value(
        self, data: Data, col_name: str | None, idx: int | None
    ) -> int | float | str | bool:
        """Get scalar value from Data (handles primitive and TABLE with row index).

        Returns:
            Scalar value (int, float, str, or bool)
        """
        if col_name is None:
            # Primitive type - return payload directly
            payload = data.payload
            assert isinstance(payload, (int, float, str, bool))
            return payload

        # TABLE type - must have idx to return scalar
        assert isinstance(data.payload, DataFrame)
        if idx is None:
            raise NodeExecutionError(
                f"Cannot get scalar value from column '{col_name}' without row index (idx is None)."
            )

        # Use .iat for fast scalar access by integer position
        col_idx = data.payload.columns.get_loc(col_name)
        if not isinstance(col_idx, int):
            # get_loc can return slice or array for duplicate columns
            raise NodeExecutionError(
                f"Column '{col_name}' has ambiguous location (duplicate columns?)."
            )
        return data.payload.iat[idx, col_idx]  # type: ignore[return-value]

    def dynamic_validate(self, data: dict[str, Data]) -> None:
        pass # no need for more dynamic validation

    def evaluate(
        self,
        data: dict[str, Data],
        left_idx: int | None = None,
        right_idx: int | None = None,
    ) -> bool:
        """
        Evaluate the condition for scalar values.
        - For primitive operands: use payload directly
        - For TABLE operands: MUST provide left_idx/right_idx to get scalar values
        
        Note: This method requires idx parameters when operands are TABLE columns.
        Returns a single boolean value (not Series).
        """
        left_val = self._get_value(data[self.left[0]], self.left[1], left_idx)
        right_val = self._get_value(data[self.right[0]], self.right[1], right_idx)

        # Ensure we have scalar values, not Series
        if hasattr(left_val, '__iter__') and not isinstance(left_val, str):
            raise NodeExecutionError(
                "evaluate() requires idx parameters for TABLE columns to return scalar bool. "
                "Use evaluate_vectorized() for Series operations."
            )

        if self.op == "EQ":
            result = left_val == right_val
        elif self.op == "NE":
            result = left_val != right_val
        elif self.op == "GT":
            result = left_val > right_val  # type: ignore[operator]
        elif self.op == "LT":
            result = left_val < right_val  # type: ignore[operator]
        elif self.op == "GE":
            result = left_val >= right_val  # type: ignore[operator]
        elif self.op == "LE":
            result = left_val <= right_val  # type: ignore[operator]
        else:
            return False

        # Ensure return type is bool (handle numpy bool)
        return bool(result)
