from datetime import datetime

import pandas as pd
import pytest

from server.models.exception import NodeValidationError
from server.models.types import ColType
from tests.nodes.utils import schema_from_coltypes, table_from_dict


def test_fillnan_datetime_const_and_process(node_ctor):
    # const fill for DATETIME column (fill_value passed as ISO string)
    dt_fill = datetime(2020, 1, 2)
    node = node_ctor("FillNaNValueNode", id="fn_dt", subset_cols=["d"], method="const", fill_value=[dt_fill.isoformat()])
    schema = schema_from_coltypes({"d": ColType.DATETIME, "_index": ColType.INT})
    out = node.infer_schema({"table": schema})
    # node.fill_value should be converted to datetime objects
    assert isinstance(node.fill_value[0], datetime)

    # create table with NaT and a valid datetime
    tbl = table_from_dict({"d": [pd.NaT, pd.Timestamp("2020-01-01")]}, col_types={"d": ColType.DATETIME, "_index": ColType.INT})
    res = node.execute({"table": tbl})
    filled_tbl = res["filled_table"].payload
    # first row should be filled with dt_fill
    assert pd.Timestamp(filled_tbl.df.iloc[0]["d"]) == pd.Timestamp(dt_fill)


def test_fillnan_const_type_mismatch_raises(node_ctor):
    # string column but provided numeric fill_value
    node = node_ctor("FillNaNValueNode", id="fn_err", subset_cols=["s"], method="const", fill_value=[123])
    schema = schema_from_coltypes({"s": ColType.STR, "_index": ColType.INT})
    with pytest.raises(NodeValidationError):
        node.infer_schema({"table": schema})


def test_dropnan_and_dropduplicates_variants(node_ctor):
    # DropNaNValueNode with subset removes rows with NaN in subset
    dn = node_ctor("DropNaNValueNode", id="dropn", subset_cols=["a"])
    schema = schema_from_coltypes({"a": ColType.FLOAT, "b": ColType.INT, "_index": ColType.INT})
    dn.infer_schema({"table": schema})
    tbl = table_from_dict({"a": [1.0, None, 3.0], "b": [1, 2, 3]}, col_types={"a": ColType.FLOAT, "b": ColType.INT, "_index": ColType.INT})
    out = dn.execute({"table": tbl})
    assert len(out["cleaned_table"].payload.df) == 2

    # DropDuplicatesNode: empty subset -> drop full duplicate rows
    dd = node_ctor("DropDuplicatesNode", id="dd1", subset_cols=[])
    schema2 = schema_from_coltypes({"x": ColType.INT, "_index": ColType.INT})
    dd.infer_schema({"table": schema2})
    tbl2 = table_from_dict({"x": [1, 1, 2]}, col_types={"x": ColType.INT, "_index": ColType.INT})
    out2 = dd.execute({"table": tbl2})
    # because Table always includes a unique _index column, drop_duplicates without subset
    # will not remove rows (index makes rows unique). Expect unchanged length.
    assert len(out2["deduplicated_table"].payload.df) == 3

    # DropDuplicatesNode with subset_cols provided
    dd2 = node_ctor("DropDuplicatesNode", id="dd2", subset_cols=["x"])
    # inferred schema should include all columns present in the runtime table
    schema_full = schema_from_coltypes({"x": ColType.INT, "y": ColType.INT, "_index": ColType.INT})
    dd2.infer_schema({"table": schema_full})
    tbl3 = table_from_dict({"x": [1, 1, 1], "y": [1, 2, 1]}, col_types={"x": ColType.INT, "y": ColType.INT, "_index": ColType.INT})
    out3 = dd2.execute({"table": tbl3})
    # when subset specified, duplicates dropped by subset (unique x values -> 1 row)
    assert len(out3["deduplicated_table"].payload.df) == 1


def test_filter_hint_infer_and_process(node_ctor):
    # hint should list boolean columns
    n = node_ctor("FilterNode", id="f1", cond_col="flag")
    schema = schema_from_coltypes({"flag": ColType.BOOL, "val": ColType.INT, "_index": ColType.INT})
    hint = n.get_hint("FilterNode", {"table": schema}, {})
    assert "cond_col_choices" in hint and "flag" in hint["cond_col_choices"]

    # infer and process
    n.infer_schema({"table": schema})
    tbl = table_from_dict({"flag": [True, False, True], "val": [1, 2, 3]}, col_types={"flag": ColType.BOOL, "val": ColType.INT, "_index": ColType.INT})
    out = n.execute({"table": tbl})
    assert len(out["true_table"].payload.df) == 2

    # infer should raise if cond_col not present
    n2 = node_ctor("FilterNode", id="f2", cond_col="missing")
    with pytest.raises(NodeValidationError):
        n2.infer_schema({"table": schema})
