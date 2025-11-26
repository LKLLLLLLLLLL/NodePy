from enum import Enum


class ColType(str, Enum):
    INT = "int"  # int64
    FLOAT = "float"  # float64
    STR = "str"  # str
    BOOL = "bool"  # bool
    DATETIME = "Datetime"  # datetime64[ns]

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ColType):
            return self.value == other.value
        elif isinstance(other, str):
            return self.value == other
        return NotImplemented

    def __hash__(self) -> int:
        return super().__hash__()

    def to_ptype(self):
        import pandas

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
        import pandas.api.types as ptypes

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
