from pandas import DataFrame, Series
from pydantic import BaseModel, model_validator
from enum import Enum
from typing_extensions import Self
from pandas.api import types as ptypes
import pandas
from typing import Union, Optional, List, ClassVar, Any
from server.lib.FileManager import File

"""
This file defined types of data passed between nodes.
"""

class ColType(str, Enum):
    INT = "int"            # int64
    FLOAT = "float"        # float64
    STR = "str"      # str
    BOOL = "bool"          # bool
    DATETIME = "datetime"  # datetime64[ns]

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
            ColType.INT: pandas.Int64Dtype(),
            ColType.FLOAT: pandas.Float64Dtype(),
            ColType.STR: pandas.StringDtype(),
            ColType.BOOL: pandas.BooleanDtype(),
            ColType.DATETIME: pandas.DatetimeTZDtype(tz=None),
        }
        return coltype_to_dtype[self]

    @classmethod
    def from_ptype(cls, dtype) -> 'ColType':
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

"""
Schema passed between nodes during static analysis stage.
"""
class TableSchema(BaseModel):
    """
    The schema of Table data.
    """

    col_types: dict[str, ColType] # col name -> col type (ColType)
    INDEX_COL: ClassVar[str] = "_index"

    @model_validator(mode="after")
    def verify(self) -> Self:
        # 1. verify if INDEX_COL is not in col_types
        if self.INDEX_COL not in self.col_types:
            self.col_types[self.INDEX_COL] = ColType.INT # add index col, imitate Table behavior
        # 2. verify if col_types keys are unique
        if len(self.col_types) != len(set(self.col_types.keys())):
            raise ValueError("Column names in col_types must be unique.")
        # 3. check no illegal column names
        if check_no_illegal_cols(list(self.col_types.keys()), allow_index=True) is False:
            raise ValueError(f"Column names cannot start with reserved prefix '_' or be whitespace only: {list(self.col_types.keys())}")
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
    
    def _append_col(self, new_col: str, col_type: ColType) -> 'TableSchema':
        if not self.validate_new_col_name(new_col):
            raise ValueError(f"Cannot add column '{new_col}': already exists or illegal name.")
        new_col_types = self.col_types.copy()
        new_col_types[new_col] = col_type
        return TableSchema(col_types=new_col_types)
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "col_types": {k: v.value for k, v in self.col_types.items()}
        }

def check_no_illegal_cols(col_names: List[str], allow_index: bool = False) -> bool:
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
        base_name = base_name + '-'
    return base_name

class Schema(BaseModel):
    class Type(str, Enum):
        TABLE = "table"
        STR = "str"
        INT = "int"
        BOOL = "bool"
        FLOAT = "float"
        FILE = "file"

    type: Type
    tab: Optional[TableSchema] = None # not None if type is TABLE
    
    @model_validator(mode="after")
    def verify(self) -> Self:
        if self.type == self.Type.TABLE and self.tab is None:
            raise ValueError("TableSchema must be provided when type is TABLE.")
        if self.type != self.Type.TABLE and self.tab is not None:
            raise ValueError("TableSchema must be None when type is not TABLE.")
        return self
    
    def __hash__(self) -> int:
        if self.type != self.Type.TABLE:
            return hash(self.type)
        else:
            assert self.tab is not None
            return hash((self.type, self.tab))
    
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
                return False # no datetime type in Schema.Type
            else:
                return False
        elif isinstance(other, Schema):
            if self.type != other.type:
                return False
            if self.type == self.Type.TABLE:
                assert(self.tab is not None and other.tab is not None)
                return self.tab == other.tab
            return True
        else:
            raise NotImplementedError(f"Cannot compare Schema with {type(other)}")

    def append_col(self, new_col: str, col_type: ColType) -> 'Schema':
        if self.type != self.Type.TABLE or self.tab is None:
            raise ValueError("Can only append column to non-TABLE schema.")
        new_tab = self.tab._append_col(new_col, col_type)
        return Schema(type=self.Type.TABLE, tab=new_tab)

    def to_dict(self) -> dict[str, Any]:
        result = {}
        result["type"] = self.type.value
        if self.type == self.Type.TABLE:
            assert self.tab is not None
            result["tab"] = self.tab.to_dict()
        return result

class Pattern(BaseModel):
    """
    The pattern defined a series of acceptable schema.
    Used in InPort to define acceptable input schema.
    """
    types: set[Schema.Type]
    table_columns: dict[str, set[ColType]] | None = None # only for TABLE type
    
    @model_validator(mode="after")
    def verify(self) -> Self:
        if Schema.Type.TABLE not in self.types and self.table_columns is not None:
            raise ValueError("table_columns can only be set if TABLE is in types.")
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
        return True

"""
Actual data passed between nodes.
"""

class Table(BaseModel):
    """
    The Table data.
    Wrapping the pandas DataFrame.
    This class will implicitly add index column as "_index", and reserve all column names begin with "_".
    """
    
    INDEX_COL: ClassVar[str] = "_index"

    # allow arbitrary types like pandas.DataFrame
    model_config = {"arbitrary_types_allowed": True}

    df: DataFrame
    col_types: dict[str, ColType] # col name -> col type (ColType)
    
    @model_validator(mode="after")
    def verify(self) -> Self:#
        # 1. check if df is aligned with col_types
        # Check for missing columns
        missing_cols = [col for col in self.col_types if col not in self.df.columns]
        if missing_cols:
            raise TypeError(f"DataFrame is missing columns: {missing_cols}")
        # Check column types
        for col, expected in self.col_types.items():
            ser = self.df[col]
            if not expected == ColType.from_ptype(ser.dtype):
                raise TypeError(f"Column '{col}' expected type {expected}, got {ser.dtype}")
        # 2. check if index column exists, if not, add it
        if self.INDEX_COL not in self.df.columns:
            self.df[self.INDEX_COL] = range(len(self.df))
        # 3. check if the colnames is not illegal
        if check_no_illegal_cols(list(self.col_types.keys()), allow_index=True) is False:
            raise ValueError(f"Column names cannot start with reserved prefix '_' or be whitespace only: {list(self.col_types.keys())}")
        return self
    
    def extract_schema(self) -> TableSchema:
        return TableSchema(
            col_types=self.col_types
        )
    
    def _append_col(self, new_col: str, col: Series) -> 'Table':
        if new_col in self.col_types:
            raise ValueError(f"Cannot add column '{new_col}': already exists.")
        if not check_no_illegal_cols([new_col]):
            raise ValueError(f"Cannot add column '{new_col}': illegal name.")
        if len(self.df) != len(col):
            raise ValueError(f"Cannot add column '{new_col}': length mismatch {len(self.df)} vs {len(col)}.")
        new_df = self.df.copy()
        new_df[new_col] = col
        new_col_types = self.col_types.copy()
        new_col_types[new_col] = ColType.from_ptype(col.dtype)
        return Table(df=new_df, col_types=new_col_types)
    
    @classmethod
    def _from_df(cls, df: DataFrame) -> 'Table':
        col_types = {}
        for col in df.columns:
            col_types[col] = ColType.from_ptype(df[col].dtype)
        return Table(df=df, col_types=col_types)
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "data": self.df.to_dict(orient="list"),
            "col_types": {k: v.value for k, v in self.col_types.items()}
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'Table':
        df = pandas.DataFrame.from_dict(data["data"])
        col_types = {k: ColType(v) for k, v in data["col_types"].items()}
        return Table(df=df, col_types=col_types)


class Data(BaseModel):
    payload: Union[Table, str, int, bool, float, File]

    def extract_schema(self) -> Schema:
        if isinstance(self.payload, Table):
            return Schema(
                type=Schema.Type.TABLE,
                tab=self.payload.extract_schema()
            )
        elif isinstance(self.payload, str):
            return Schema(type=Schema.Type.STR)
        elif isinstance(self.payload, int):
            return Schema(type=Schema.Type.INT)
        elif isinstance(self.payload, bool):
            return Schema(type=Schema.Type.BOOL)
        elif isinstance(self.payload, float):
            return Schema(type=Schema.Type.FLOAT)
        elif isinstance(self.payload, File):
            return Schema(type=Schema.Type.FILE)
        else:
            raise TypeError(f"Unsupported data payload type: {type(self.payload)}")

    def append_col(self, new_col: str, ser: Series) -> 'Data':
        if not isinstance(self.payload, Table):
            raise ValueError("Can only append column to Table data.")
        new_table = self.payload._append_col(new_col, ser)
        return Data(payload=new_table)
    
    def print(self) -> str:
        if isinstance(self.payload, Table):
            return str(self.payload.df)
        else:
            return str(self.payload)

    @classmethod
    def from_df(cls, df: DataFrame) -> 'Data':
        table = Table._from_df(df)
        return Data(payload=table)
    
    def to_dict(self) -> dict[str, Any]:
        if isinstance(self.payload, Table):
            return {
                "type": "Table",
                "value": self.payload.to_dict()
            }
        elif isinstance(self.payload, File):
            return {
                "type": "File",
                "value": self.payload.to_dict()
            }
        else:
            return {
                "type": type(self.payload).__name__,
                "value": self.payload
            }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'Data':
        """
        Reconstructs a Data object from its dictionary representation.
        """
        payload_type = data["type"]
        payload_value = data["value"]

        payload: Any
        if payload_type == "Table":
            payload = Table.from_dict(payload_value)
        elif payload_type == "File":
            # Assuming your File model also has a from_dict method
            payload = File.from_dict(payload_value)
        elif payload_type == "str":
            payload = str(payload_value)
        elif payload_type == "int":
            payload = int(payload_value)
        elif payload_type == "float":
            payload = float(payload_value)
        elif payload_type == "bool":
            payload = bool(payload_value)
        else:
            raise TypeError(f"Unsupported payload type for deserialization: {payload_type}")
        
        return cls(payload=payload)
