from pydantic import BaseModel, model_validator
from enum import Enum
from typing_extensions import Self
from pandas.api import types as ptypes
import pandas
from typing import Optional, ClassVar, Any, Literal, Union
from server.models.data import File
from server.lib.FileManager import FileManager
from io import StringIO

"""
This file defined schema passed between nodes during static analysis stage.
"""

class ColType(str, Enum):
    INT = "int"  # int64
    FLOAT = "float"  # float64
    STR = "str"  # str
    BOOL = "bool"  # bool
    DATETIME = "datetime"  # datetime64[ns] pandas.Timestamp

    type ColTypeValue = Union[int, float, str, bool, pandas.Timestamp]

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ColType):
            return self.value == other.value
        elif isinstance(other, Schema):
            if other.type == Schema.Type.INT and self == ColType.INT:
                return True
            elif other.type == Schema.Type.FLOAT and self == ColType.FLOAT:
                return True
            elif other.type == Schema.Type.STR and self == ColType.STR:
                return True
            elif other.type == Schema.Type.BOOL and self == ColType.BOOL:
                return True
            else:
                return False
        else:
            raise NotImplementedError(f"Cannot compare ColType with {type(other)}")

    def __hash__(self) -> int:
        return super().__hash__()

    def to_ptype(self):
        coltype_to_dtype = {
            ColType.INT: pandas.Int64Dtype,
            ColType.FLOAT: pandas.Float64Dtype,
            ColType.STR: pandas.StringDtype,
            ColType.BOOL: pandas.BooleanDtype,
            ColType.DATETIME: "datetime64[ns]",
        }
        return coltype_to_dtype[self]

    @classmethod
    def from_ptype(cls, dtype) -> "ColType":
        if ptypes.is_integer_dtype(dtype):
            return ColType.INT
        elif ptypes.is_float_dtype(dtype):
            return ColType.FLOAT
        elif ptypes.is_string_dtype(dtype):
            return ColType.STR
        elif ptypes.is_bool_dtype(dtype):
            return ColType.BOOL
        elif ptypes.is_datetime64_any_dtype(dtype):
            return ColType.DATETIME
        else:
            raise ValueError(f"Unsupported pandas dtype: {dtype}")

class TableSchema(BaseModel):
    """
    The schema of Table data.
    """

    col_types: dict[str, ColType]  # col name -> col type (ColType)
    INDEX_COL: ClassVar[str] = "_index"

    @model_validator(mode="after")
    def verify(self) -> Self:
        # 1. verify if INDEX_COL is not in col_types
        if self.INDEX_COL not in self.col_types:
            self.col_types[self.INDEX_COL] = (
                ColType.INT
            )  # add index col, imitate Table behavior
        # 2. verify if col_types keys are unique
        if len(self.col_types) != len(set(self.col_types.keys())):
            raise ValueError("Column names in col_types must be unique.")
        # 3. check no illegal column names
        if (
            check_no_illegal_cols(list(self.col_types.keys()), allow_index=True)
            is False
        ):
            raise ValueError(
                f"Column names cannot start with reserved prefix '_' or be whitespace only: {list(self.col_types.keys())}"
            )
        return self

    def __hash__(self) -> int:
        # hash based on frozenset of items in col_types
        return hash(frozenset(self.col_types.items()))

    def validate_new_col_name(self, new_col: str) -> bool:
        if new_col in self.col_types:
            return False
        if not check_no_illegal_cols([new_col]):
            return False
        return True

    def __eq__(self, value: object) -> bool:
        assert isinstance(value, TableSchema)
        return self.col_types == value.col_types

    def _append_col(self, new_col: str, col_type: ColType) -> "TableSchema":
        if not self.validate_new_col_name(new_col):
            raise ValueError(
                f"Cannot add column '{new_col}': already exists or illegal name."
            )
        new_col_types = self.col_types.copy()
        new_col_types[new_col] = col_type
        return TableSchema(col_types=new_col_types)

    def to_dict(self) -> dict[str, Any]:
        return {"col_types": {k: v.value for k, v in self.col_types.items()}}


def check_no_illegal_cols(col_names: list[str], allow_index: bool = False) -> bool:
    """Return True if column names don't use reserved prefixes or whitespace-only.

    By default any name starting with '_' is illegal. If allow_index is True,
    the special index column name "_index" is allowed.
    """
    reserved_prefix = "_"
    for col in col_names:
        if col.startswith(reserved_prefix):
            if allow_index and col == TableSchema.INDEX_COL:
                continue
            return False
    # check if col names is not white space only
    for col in col_names:
        if col.strip() == "":
            return False
    return True


def generate_default_col_name(id: str, annotation: str) -> str:
    base_name = f"_{id}_{annotation}"
    if not check_no_illegal_cols([base_name]):
        base_name = base_name + "-"
    return base_name

class FileSchema(BaseModel):
    """
    The schema of File data, including file format and other metadata.
    """
    format: Literal["csv", "png", "jpg", "pdf"]
    col_types: Optional[dict[str, ColType]] = None  # only for csv files
    
    def __hash__(self) -> int:
        return hash((self.format, frozenset(self.col_types.items()) if self.col_types else None))

    def to_dict(self) -> dict[str, Any]:
        return super().model_dump()
    
    @classmethod
    def from_file(cls, file: File, file_manager: FileManager) -> "FileSchema":
        if file.format == "csv":
            file_content = file_manager.read_sync(file=file, user_id=None)
            df = pandas.read_csv(StringIO(file_content.decode('utf-8')))
            col_types = {}
            for col in df.columns:
                dtype = df[col].dtype
                col_type = ColType.from_ptype(dtype)
                col_types[col] = col_type
            return FileSchema(format="csv", col_types=col_types)
        else:
            return FileSchema(format=file.format)

    
class Schema(BaseModel):
    class Type(str, Enum):
        TABLE = "Table"
        STR = "str"
        INT = "int"
        BOOL = "bool"
        FLOAT = "float"
        FILE = "File"
        DATETIME = "Datetime"

    type: Type
    tab: Optional[TableSchema] = None  # not None if type is TABLE
    file: Optional[FileSchema] = None  # not None if type is FILE

    @model_validator(mode="after")
    def verify(self) -> Self:
        if self.type == self.Type.TABLE and self.tab is None:
            raise ValueError("TableSchema must be provided when type is TABLE.")
        if self.type != self.Type.TABLE and self.tab is not None:
            raise ValueError("TableSchema must be None when type is not TABLE.")
        if self.type == self.Type.FILE and self.file is None:
            raise ValueError("FileSchema must be provided when type is FILE.")
        if self.type != self.Type.FILE and self.file is not None:
            raise ValueError("FileSchema must be None when type is not FILE.")
        return self

    def __hash__(self) -> int:
        if self.type == self.Type.TABLE:
            assert self.tab is not None
            return hash((self.type, self.tab))
        elif self.type == self.Type.FILE:
            assert self.file is not None
            return hash((self.type, self.file))
        else:
            return hash(self.type)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ColType):
            if other == ColType.BOOL:
                return self.type == self.Type.BOOL
            elif other == ColType.INT:
                return self.type == self.Type.INT
            elif other == ColType.FLOAT:
                return self.type == self.Type.FLOAT
            elif other == ColType.STR:
                return self.type == self.Type.STR
            elif other == ColType.DATETIME:
                return self.type == self.Type.DATETIME
            else:
                return False
        elif isinstance(other, Schema):
            if self.type != other.type:
                return False
            elif self.type == self.Type.TABLE:
                assert self.tab is not None and other.tab is not None
                return self.tab == other.tab
            elif self.type == self.Type.FILE:
                assert self.file is not None and other.file is not None
                return self.file == other.file
            return True
        else:
            raise NotImplementedError(f"Cannot compare Schema with {type(other)}")

    def append_col(self, new_col: str, col_type: ColType) -> "Schema":
        if self.type != self.Type.TABLE or self.tab is None:
            raise ValueError("Can only append column to non-TABLE schema.")
        new_tab = self.tab._append_col(new_col, col_type)
        return Schema(type=self.Type.TABLE, tab=new_tab)

    def to_dict(self) -> dict[str, Any]:
        result = {}
        result["type"] = self.type.value
        if self.type == self.Type.TABLE:
            assert self.tab is not None
            result["value"] = self.tab.to_dict()
        elif self.type == self.Type.FILE:
            assert self.file is not None
            result["value"] = self.file.to_dict()
        return result


class Pattern(BaseModel):
    """
    The pattern defined a series of acceptable schema.
    Used in InPort to define acceptable input schema.
    """

    types: set[Schema.Type]
    table_columns: dict[str, set[ColType]] | None = None  # only for TABLE type
    file_formats: set[Literal["csv", "png", "jpg", "pdf"]] | None = None  # only for FILE type

    @model_validator(mode="after")
    def verify(self) -> Self:
        if Schema.Type.TABLE not in self.types and self.table_columns is not None:
            raise ValueError("table_columns can only be set if TABLE is in types.")
        if Schema.Type.FILE not in self.types and self.file_formats is not None:
            raise ValueError("file_format can only be set if FILE is in types.")
        return self

    def __contains__(self, schema: Schema) -> bool:
        assert isinstance(schema, Schema)
        if schema.type not in self.types:
            return False
        if schema.type == Schema.Type.TABLE and self.table_columns is not None:
            if schema.tab is None:
                return False
            for col, col_types in self.table_columns.items():
                if col not in schema.tab.col_types:
                    return False
                if schema.tab.col_types[col] not in col_types:
                    return False
        if schema.type == Schema.Type.FILE and self.file_formats is not None:
            if schema.file is None:
                return False
            if schema.file.format not in self.file_formats:
                return False
        return True
