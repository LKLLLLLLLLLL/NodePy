import base64
import hashlib
import io
import json
from datetime import datetime
from math import isinf, isnan
from typing import Any, ClassVar, Literal, Union, cast

import joblib
from pandas import DataFrame, Series, isna
from pydantic import BaseModel, model_validator
from sklearn.base import BaseEstimator
from typing_extensions import Self

from server.models.data_view import DataView, ModelView, TableView
from server.models.file import File
from server.models.schema import (
    FileSchema,
    ModelSchema,
    Schema,
    TableSchema,
    check_no_illegal_cols,
)
from server.models.types import ColType

"""
Runtime data passed between nodes.
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
        # 1. align index column
        if self.INDEX_COL not in self.df.columns:
            self.df[self.INDEX_COL] = range(len(self.df))
            self.col_types[self.INDEX_COL] = ColType.INT
        # 2. check if df is aligned with col_types
        if len(self.df) != 0:
            # Check for missing columns
            df_missing_cols = [col for col in self.col_types if col not in self.df.columns]
            if df_missing_cols:
                raise TypeError(f"DataFrame is missing columns: {df_missing_cols}")
            col_types_missing_cols = [col for col in self.df.columns if col not in self.col_types]
            if col_types_missing_cols:
                raise TypeError(f"Column types missing for columns: {col_types_missing_cols}")
            # Check column types
            for col, expected in self.col_types.items():
                ser = self.df[col]
                if not expected == ColType.from_ptype(ser.dtype):
                    raise TypeError(f"Column '{col}' expected type {expected}, got {ser.dtype}")
        else:
            # if the df has zero rows, it cannot infer column types, we need to specify col and col_types manually
            for col in self.col_types:
                if col not in self.df.columns:
                    # append col to dataframe
                    self.df[col] = Series(dtype=self.col_types[col].to_ptype())
            for col in self.df.columns:
                if col not in self.col_types:
                    raise TypeError(f"DataFrame has zero rows, missing column type for '{col}'")
                ptype = self.col_types[col].to_ptype()
                if callable(ptype):
                    ptype = ptype()
                self.df[col] = self.df[col].astype(ptype)
        # 3. check if the colnames is not illegal
        if check_no_illegal_cols(list(self.col_types.keys()), allow_index=True) is False:
            raise ValueError(f"Column names cannot start with reserved prefix '_' or be whitespace only: {list(self.col_types.keys())}")
        return self

    def extract_schema(self) -> TableSchema:
        return TableSchema(
            col_types=self.col_types
        )

    def regenerate_index(self) -> 'Table':
        new_df = self.df.copy()
        new_df[self.INDEX_COL] = range(len(new_df))
        self.col_types[self.INDEX_COL] = ColType.INT
        return Table(df=new_df, col_types=self.col_types)

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

    def fast_hash(self) -> str:
        from pandas.util import hash_pandas_object
        col_types_hash = hashlib.md5(json.dumps(
            {k: v.value for k, v in self.col_types.items()},
            sort_keys=True
        ).encode("utf-8")).hexdigest()
        data_hash = hashlib.md5(hash_pandas_object(self.df, index=True).values.tobytes()).hexdigest() # type: ignore
        return hashlib.md5((col_types_hash + data_hash).encode("utf-8")).hexdigest()

    @staticmethod
    def col_types_from_df(df: DataFrame) -> dict[str, ColType]:
        col_types = {}
        for col in df.columns:
            col_types[col] = ColType.from_ptype(df[col].dtype)
        return col_types

    def to_view(self) -> TableView:
        cols = {}
        for col in self.df.columns:
            # Convert Timestamp objects to ISO format strings
            if self.col_types[col] == ColType.DATETIME:
                cols[col] = [
                    v.isoformat() if isinstance(v, datetime) else v
                    for v in self.df[col].tolist()
                ]
            else:
                normalized = []
                for v in self.df[col].tolist():
                    # convert nan/NA to None
                    if isna(v):
                        normalized.append(None)
                        continue
                    # convert +/-Infinity and NaN to string markers so JSON can carry them
                    try:
                        if isinf(v):
                            normalized.append("Infinity" if v > 0 else "-Infinity")
                            continue
                        if isnan(v):
                            normalized.append("NaN")
                            continue
                    except TypeError:
                        # non-numeric types will raise TypeError for isinf/isnan, ignore
                        pass
                    normalized.append(v)
                cols[col] = normalized
        table_view = TableView(
            cols=cols,
            col_types={k: v.value for k, v in self.col_types.items()},
        )
        return table_view

    @classmethod
    def from_view(cls, data: TableView) -> 'Table':
        df = DataFrame.from_dict(data.cols)
        col_types = {k: ColType(v) for k, v in data.col_types.items()}
        for col, col_type in col_types.items():
            if len(df) == 0:
                continue

            if col_type == ColType.DATETIME:
                # convert ISO format strings to datetime
                df[col] = df[col].apply(
                    lambda x: datetime.fromisoformat(x) if isinstance(x, str) else x
                )
            else:
                # convert null to nullable types
                # make None to pd.NA/NaN
                ptype = col_type.to_ptype()
                if callable(ptype):
                    ptype = ptype()
                # If float column, convert special string markers back to float values
                if col_type == ColType.FLOAT:
                    def _convert_special(x):
                        if isinstance(x, str):
                            if x == "Infinity":
                                return float("inf")
                            if x == "-Infinity":
                                return float("-inf")
                            if x == "NaN":
                                return float("nan")
                        return x
                    df[col] = df[col].apply(_convert_special)
                df[col] = df[col].astype(ptype) # type: ignore
        return Table(df=df, col_types=col_types)

    # @classmethod
    # def from_dict(cls, data: dict[str, Any]) -> 'Table':
    #     df = DataFrame.from_dict(data["data"])
    #     col_types = {k: ColType(v) for k, v in data["col_types"].items()}
    #     return Table(df=df, col_types=col_types)


class Model(BaseModel):
    """
    The Model data.
    Wrapping the sklearn BaseEstimator.
    """
    # allow arbitrary types like sklearn BaseEstimator
    model_config = {"arbitrary_types_allowed": True}

    model: BaseEstimator
    metadata: ModelSchema

    def extract_schema(self) -> Schema:
        return Schema(
            type=Schema.Type.MODEL,
            model=self.metadata
        )

    def fast_hash(self) -> str:
        # hash the serialized model bytes
        buf = io.BytesIO()
        joblib.dump(self.model, buf)
        buf.seek(0)
        model_bytes = buf.read()
        return hashlib.md5(model_bytes).hexdigest()

    def to_view(self) -> ModelView:
        # serialize the sklearn model using joblib
        buf = io.BytesIO()
        joblib.dump(self.model, buf)
        buf.seek(0)
        model_bytes = buf.read()
        model_b64 = base64.b64encode(model_bytes).decode("ascii")
        return ModelView.model_validate(
            {
                "model": model_b64,
                "metadata": self.metadata,
            }
        )

    @classmethod
    def from_view(cls, data: ModelView) -> 'Model':
        model_b64 = data.model
        model_bytes = base64.b64decode(model_b64)
        buf = io.BytesIO(model_bytes)
        model = joblib.load(buf)
        metadata = data.metadata
        return Model(model=model, metadata=metadata)


class Data(BaseModel):
    payload: Union[Table, str, int, bool, float, File, datetime, Model]

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
        elif isinstance(self.payload, Model):
            return self.payload.extract_schema()
        else:
            raise TypeError(f"Unsupported data payload type: {type(self.payload)}")

    def append_col(self, new_col: str, ser: Series) -> 'Data':
        if not isinstance(self.payload, Table):
            raise ValueError("Can only append column to Table data.")
        new_table = self.payload._append_col(new_col, ser)
        return Data(payload=new_table)
    
    # def print(self) -> str:
    #     if isinstance(self.payload, Table):
    #         return str(self.payload.df)
    #     else:
    #         return str(self.payload)

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, Data):
            return NotImplemented
        self_dict = self.to_view().to_dict()
        other_dict = value.to_view().to_dict()
        return self_dict == other_dict

    def fast_hash(self) -> str:
        if isinstance(self.payload, Table):
            return self.payload.fast_hash()
        elif isinstance(self.payload, Model):
            return self.payload.fast_hash()
        else:
            return hashlib.md5(repr(self.payload).encode("utf-8")).hexdigest()

    def to_view(self) -> "DataView":
        if isinstance(self.payload, Table):
            table_view = self.payload.to_view()
            return DataView(type="Table", value=table_view)
        elif isinstance(self.payload, datetime):
            return DataView(
                type="Datetime",
                value=self.payload.isoformat(),
            )
        elif isinstance(self.payload, Model):
            return DataView(
                type="Model",
                value=self.payload.to_view(),
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

    # def to_dict(self) -> dict[str, Any]:
    #     return self.to_view().to_dict()

    @classmethod
    def from_view(cls, data_view: "DataView") -> "Data":
        payload_type = data_view.type
        payload_value = data_view.value

        payload: Any
        if payload_type == "Table":
            assert isinstance(payload_value, TableView)
            payload = Table.from_view(payload_value)
        elif payload_type == "Model":
            assert isinstance(payload_value, ModelView)
            payload = Model.from_view(payload_value)
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
