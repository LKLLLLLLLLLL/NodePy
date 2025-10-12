from pydantic import BaseModel, model_validator
from typing_extensions import Self
from enum import Enum
from pandas import DataFrame
from pathlib import Path

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
Data definations
"""

class Schema(BaseModel):
    """schema defined the data type between nodes"""

    class DataType(str, Enum):
        """data type of object passed between nodes"""

        TABLE = "table"  # dataframe
        STR = "str"  # string
        INT = "int"  # integer

    type: DataType
    columns: list[str] | None = None  # for TABLE type, list of column names

    @model_validator(mode="after")
    def verify(self) -> Self:
        if self.type == Schema.DataType.TABLE and self.columns is None:
            # Allow None for arbitrary columns in TABLE type
            pass
        elif self.type != Schema.DataType.TABLE and self.columns is not None:
            raise NodeValidationError("For non-TABLE type, columns must be None.")
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

    schem: Schema
    payload: DataFrame | str | int

    model_config = {"arbitrary_types_allowed": True}  # allow DataFrame type

    @model_validator(mode="after")
    def verify(self) -> Self:
        if self.schem.type == Schema.DataType.TABLE:
            if not isinstance(self.payload, DataFrame):
                raise NodeExecutionError(
                    "Payload must be a DataFrame for TABLE schema."
                )
            if self.schem.columns is not None:
                missing_cols = [
                    col for col in self.schem.columns if col not in self.payload.columns
                ]
                if missing_cols:
                    raise NodeExecutionError(
                        f"Payload is missing columns: {missing_cols}"
                    )
        elif self.schem.type == Schema.DataType.STR:
            if not isinstance(self.payload, str):
                raise NodeExecutionError("Payload must be a string for STR schema.")
        elif self.schem.type == Schema.DataType.INT:
            if not isinstance(self.payload, int):
                raise NodeExecutionError("Payload must be an integer for INT schema.")
        else:
            raise NodeExecutionError(f"Unsupported schema type: {self.schem.type}")
        return self


class InPort(BaseModel):
    name: str
    schem: Schema
    description: str | None = None
    required: bool


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
        NONE = "None"
    
    node_id: str
    type: Type
    payload: Path | DataFrame | str | int | None
    
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