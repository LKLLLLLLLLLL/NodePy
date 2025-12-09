from datetime import datetime

import pytest

from server.models.exception import NodeValidationError
from server.models.types import ColType
from tests.nodes.utils import schema_from_coltypes, table_from_dict


def test_fillnan_const_type_checks_and_conversion(node_ctor):
    # INT: wrong type should raise
    node_int = node_ctor("FillNaNValueNode", id="fn_int", subset_cols=["a"], method="const", fill_value=["x"])
    s_int = schema_from_coltypes({"a": ColType.INT, "_index": ColType.INT})
    with pytest.raises(NodeValidationError):
        node_int.infer_schema({"table": s_int})

    # FLOAT: int is acceptable and should be converted to float
    node_f = node_ctor("FillNaNValueNode", id="fn_f", subset_cols=["a"], method="const", fill_value=[0])
    s_f = schema_from_coltypes({"a": ColType.FLOAT, "_index": ColType.INT})
    out = node_f.infer_schema({"table": s_f})
    assert "filled_table" in out

    # STR: wrong type should raise
    node_s = node_ctor("FillNaNValueNode", id="fn_s", subset_cols=["a"], method="const", fill_value=[1])
    s_s = schema_from_coltypes({"a": ColType.STR, "_index": ColType.INT})
    with pytest.raises(NodeValidationError):
        node_s.infer_schema({"table": s_s})

    # BOOL: wrong type should raise
    node_b = node_ctor("FillNaNValueNode", id="fn_b", subset_cols=["a"], method="const", fill_value=[1])
    s_b = schema_from_coltypes({"a": ColType.BOOL, "_index": ColType.INT})
    with pytest.raises(NodeValidationError):
        node_b.infer_schema({"table": s_b})

    # DATETIME: requires isoformat string and converts to datetime
    node_dt = node_ctor("FillNaNValueNode", id="fn_dt", subset_cols=["a"], method="const", fill_value=["2020-01-01T00:00:00"])
    s_dt = schema_from_coltypes({"a": ColType.DATETIME, "_index": ColType.INT})
    node_dt.infer_schema({"table": s_dt})
    # after infer, fill_value should be converted to datetime
    assert isinstance(node_dt.fill_value[0], datetime)


def test_fillnan_process_ffill_bfill(node_ctor):
    # prepare a table with NaNs
    tbl = table_from_dict({"a": [1, None, None, 4]})
    s = schema_from_coltypes({"a": ColType.FLOAT, "_index": ColType.INT})

    # ffill
    node_ff = node_ctor("FillNaNValueNode", id="ff", subset_cols=["a"], method="ffill")
    node_ff.infer_schema({"table": s})
    out_ff = node_ff.execute({"table": tbl})
    assert "filled_table" in out_ff

    # bfill
    node_bf = node_ctor("FillNaNValueNode", id="bf", subset_cols=["a"], method="bfill")
    node_bf.infer_schema({"table": s})
    out_bf = node_bf.execute({"table": tbl})
    assert "filled_table" in out_bf

    # method const path: fill with provided values
    node_const = node_ctor("FillNaNValueNode", id="c1", subset_cols=["a"], method="const", fill_value=[0])
    node_const.infer_schema({"table": s})
    out_c = node_const.execute({"table": tbl})
    assert "filled_table" in out_c
