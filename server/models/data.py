from datetime import datetime
from typing import Any, ClassVar, Literal, Union, cast

from pandas import DataFrame, Series
from pydantic import BaseModel, model_validator
from typing_extensions import Self

from server.models.file import File
from server.models.schema import FileSchema, Schema, TableSchema, check_no_illegal_cols
from server.models.types import ColType

"""
Actual runtime data passed between nodes.
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
    def verify(self) -> Self:
        # 1. check if df is aligned with col_types
        if len(self.df) != 0:
            # Check for missing columns
            missing_cols = [col for col in self.col_types if col not in self.df.columns]
            if missing_cols:
                raise TypeError(f"DataFrame is missing columns: {missing_cols}")
            # Check column types
            for col, expected in self.col_types.items():
                ser = self.df[col]
                if not expected == ColType.from_ptype(ser.dtype):
                    raise TypeError(f"Column '{col}' expected type {expected}, got {ser.dtype}")
        else:
            # if the df has zero rows, it cannot infer column types, we need to specify col_types manually
            for col in self.df.columns:
                if col not in self.col_types:
                    raise TypeError(f"DataFrame has zero rows, missing column type for '{col}'")
                ptype = self.col_types[col].to_ptype()
                if callable(ptype):
                    ptype = ptype()
                self.df[col] = self.df[col].astype(ptype)
        # 2. check if index column exists, if not, add it
        if self.INDEX_COL not in self.df.columns:
            self.df[self.INDEX_COL] = range(len(self.df))
            self.col_types[self.INDEX_COL] = ColType.INT
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
    
    @staticmethod
    def col_types_from_df(df: DataFrame) -> dict[str, ColType]:
        col_types = {}
        for col in df.columns:
            col_types[col] = ColType.from_ptype(df[col].dtype)
        return col_types
    
    # def to_dict(self) -> dict[str, Any]:
    #     return {
    #         "data": self.df.to_dict(orient="list"),
    #         "col_types": {k: v.value for k, v in self.col_types.items()}
    #     }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'Table':
        df = DataFrame.from_dict(data["data"])
        col_types = {k: ColType(v) for k, v in data["col_types"].items()}
        return Table(df=df, col_types=col_types)


class Data(BaseModel):
    payload: Union[Table, str, int, bool, float, File, datetime]

    def extract_schema(self) -> Schema:
        if isinstance(self.payload, Table):
            return Schema(
                type=Schema.Type.TABLE,
                tab=self.payload.extract_schema()
            )
        elif isinstance(self.payload, str):
            return Schema(type=Schema.Type.STR)
        elif isinstance(self.payload, bool):
            return Schema(type=Schema.Type.BOOL)
        elif isinstance(self.payload, int):
            return Schema(type=Schema.Type.INT)
        elif isinstance(self.payload, float):
            return Schema(type=Schema.Type.FLOAT)
        elif isinstance(self.payload, File):
            return Schema(type=Schema.Type.FILE, file=FileSchema.from_file(self.payload))
        elif isinstance(self.payload, datetime):
            return Schema(type=Schema.Type.DATETIME)
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

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, Data):
            raise NotImplementedError(f"Cannot compare Data with {type(value)}")
        self_dict = self.to_view().to_dict()
        other_dict = value.to_view().to_dict()
        return self_dict == other_dict

    # @classmethod
    # def from_df(cls, df: DataFrame) -> 'Data':
    #     table = Table._from_df(df)
    #     return Data(payload=table)

    def to_view(self) -> "DataView":
        if isinstance(self.payload, Table):
            # Serialize Table payload
            cols = {}
            for col in self.payload.df.columns:
                # Convert Timestamp objects to ISO format strings
                if self.payload.col_types[col] == ColType.DATETIME:
                    cols[col] = [v.isoformat() if isinstance(v, datetime) else v for v in self.payload.df[col].tolist()]
                else:
                    cols[col] = self.payload.df[col].tolist()
            table_view = DataView.TableView(
                cols=cols,
                col_types={k: v.value for k, v in self.payload.col_types.items()}
            )
            return DataView(
                type="Table",
                value=table_view
            )
        elif isinstance(self.payload, datetime):
            return DataView(
                type="Datetime",
                value=self.payload.isoformat(),
            )
        else:
            # Map Python types to allowed Literal values
            type_map = {
                str: "str",
                int: "int",
                float: "float",
                bool: "bool",
                File: "File"
            }
            payload_type = type_map.get(type(self.payload))
            if payload_type is None:
                raise TypeError(f"Unsupported payload type for DataView: {type(self.payload)}")
            
            value = self.payload
            if isinstance(self.payload, datetime):
                value = self.payload.isoformat()
            return DataView(
                type=cast(
                    Literal["bool", "int", "float", "str", "File"],
                    payload_type,
            ),
                value=value,
            )

    def to_dict(self) -> dict[str, Any]:
        return self.to_view().to_dict()

    @classmethod
    def from_view(cls, data_view: "DataView") -> "Data":
        payload_type = data_view.type
        payload_value = data_view.value

        payload: Any
        if payload_type == "Table":
            assert isinstance(payload_value, DataView.TableView)
            df = DataFrame.from_dict(payload_value.cols)
            col_types = {k: ColType(v) for k, v in payload_value.col_types.items()}
            # Convert datetime columns back to datetime objects
            for col, col_type in col_types.items():
                if col_type == ColType.DATETIME:
                    df[col] = df[col].apply(lambda x: datetime.fromisoformat(x) if isinstance(x, str) else x)
            payload = Table(df=df, col_types=col_types)
        elif payload_type == "File":
            assert isinstance(payload_value, File)
            payload = payload_value
        elif payload_type == "str":
            assert isinstance(payload_value, str)
            payload = payload_value
        elif payload_type == "int":
            assert isinstance(payload_value, int)
            payload = payload_value
        elif payload_type == "float":
            assert isinstance(payload_value, float)
            payload = payload_value
        elif payload_type == "bool":
            assert isinstance(payload_value, bool)
            payload = payload_value
        elif payload_type == "Datetime":
            assert isinstance(payload_value, str)
            payload = datetime.fromisoformat(payload_value)
        else:
            raise TypeError(f"Unsupported payload type for deserialization: {payload_type}")
        
        return cls(payload=payload)

class DataView(BaseModel):
    """
    A dict-like view of data, for transmitting or json serialization.
    """
    class TableView(BaseModel):
        cols: dict[str, list[str | bool | int | float]] # the datetime columns are serialized as ISO format strings
        col_types: dict[str, str]  # col name -> col type
        
        def model_dump(self, **kwargs):
            """Override to handle Timestamp serialization"""
            result = super().model_dump(**kwargs)
            # Convert Timestamp objects to ISO format strings
            for col_name, values in result['cols'].items():
                result['cols'][col_name] = [
                    v.isoformat() if isinstance(v, datetime) else v 
                    for v in values
                ]
            return result

    type: Literal["int", "float", "str", "bool", "Table", "File", "Datetime"]
    value: Union[TableView, str, int, bool, float, File] # datetime is serialized as str

    model_config = {"arbitrary_types_allowed": True}

    def to_dict(self) -> dict[str, Any]:
        return super().model_dump()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DataView":
        return cls.model_validate(data)

class DataRef(BaseModel):
    """
    A lightweight representation of output data from a node port,
    it store only the url of the data object.
    """
    data_id: int
