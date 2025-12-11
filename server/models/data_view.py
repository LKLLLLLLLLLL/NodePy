from datetime import datetime
from typing import Any, Literal, Union

from pandas import isna
from pydantic import BaseModel, model_validator
from typing_extensions import Self

from server.models.file import File
from server.models.schema import (
    ModelSchema,
)

"""
The exchange format for Data, suitable for transmission or JSON serialization.
"""


class TableView(BaseModel):
    cols: dict[str, list[str | bool | int | float | None]]
    # the datetime columns are serialized as ISO format strings
    # the nan values are serialized as None
    col_types: dict[str, str]  # col name -> col type

    def model_dump(self, **kwargs):
        """Override to handle Timestamp serialization"""
        result = super().model_dump(**kwargs)
        # Normalize values: datetimes -> ISO string, NaN/pandas.NA -> None
        for col_name, values in result["cols"].items():
            normalized = []
            for v in values:
                if isinstance(v, datetime):
                    normalized.append(v.isoformat())
                else:
                    # pandas.isna covers: numpy.nan, pandas.NA, None, etc.
                    if isna(v):
                        normalized.append(None)
                    else:
                        normalized.append(v)
            result["cols"][col_name] = normalized
        return result

class ModelView(BaseModel):
    model: str  # base64 encoded model bytes
    metadata: ModelSchema

class DataView(BaseModel):
    """
    A dict-like view of data, for transmitting or json serialization.
    """

    type: Literal["int", "float", "str", "bool", "Table", "File", "Datetime", "Model"]
    value: Union[
        TableView, str, int, bool, float, File, ModelView
    ]  # datetime is serialized as str

    model_config = {"arbitrary_types_allowed": True}

    @model_validator(mode="after")
    def convert(self) -> Self:
        if self.type == "File":
            if not isinstance(self.value, File):
                self.value = File.model_validate(self.value)
        return self

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
