from typing import Any, Dict, Iterable, List

import pandas as pd

from server.models.data import Data, Table
from server.models.schema import Schema, TableSchema
from server.models.types import ColType


def table_from_dict(data: Dict[str, list], col_types: Dict[str, ColType] | None = None) -> Data:
    """Create a `Data` object wrapping a `Table` from a plain dict of columns.

    - Automatically adds `_index` column required by `Table`.
    - If `col_types` not provided, attempts to infer using `ColType.from_ptype`.

    Example:
        d = table_from_dict({"a": [1,2], "b": [3.0,4.0]})
    """
    df = pd.DataFrame(data)

    # reset index and add explicit index column if absent
    df = df.reset_index(drop=True)
    if Table.INDEX_COL not in df.columns:
        df[Table.INDEX_COL] = list(range(len(df)))

    if col_types is None:
        inferred: Dict[str, ColType] = {}
        for col in df.columns:
            if col == Table.INDEX_COL:
                continue
            inferred[col] = ColType.from_ptype(df[col].dtype)
        # ensure index column has a declared type
        inferred[Table.INDEX_COL] = ColType.INT
        col_types = inferred

    table = Table(df=df, col_types=col_types)
    return Data(payload=table)


def schema_from_coltypes(col_types: Dict[str, ColType]) -> Schema:
    """Construct a `Schema` of type TABLE from a `col_types` mapping."""
    return Schema(type=Schema.Type.TABLE, tab=TableSchema(col_types=col_types))


def make_schema(typ: str) -> Schema:
    """Make a primitive `Schema` given a string: 'int','float','str','bool','Datetime','Table','File'."""
    mapping = {
        "int": Schema.Type.INT,
        "float": Schema.Type.FLOAT,
        "str": Schema.Type.STR,
        "bool": Schema.Type.BOOL,
        "Datetime": Schema.Type.DATETIME,
        "Table": Schema.Type.TABLE,
        "File": Schema.Type.FILE,
    }
    t = mapping.get(typ)
    if t is None:
        raise ValueError(f"Unknown schema type: {typ}")
    if t == Schema.Type.TABLE:
        # empty table schema
        return Schema(type=t, tab=TableSchema(col_types={}))
    return Schema(type=t)


def make_data(payload: Any) -> Data:
    """Wrap a raw payload into `Data` object (helper for tests)."""
    return Data(payload=payload)


def table_from_records(records: Iterable[Dict[str, Any]]) -> Data:
    """Create a `Table` Data from an iterable of row dicts (records)."""
    recs: List[Dict[str, Any]] = list(records)
    if not recs:
        return table_from_dict({})
    # construct column-wise dict
    cols: Dict[str, List[Any]] = {}
    for k in recs[0].keys():
        cols[k] = [r.get(k) for r in recs]
    return table_from_dict(cols)
