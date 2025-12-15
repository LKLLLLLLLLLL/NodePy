import pytest

from server.models.exception import NodeParameterError
from server.models.types import ColType
from tests.nodes.utils import schema_from_coltypes, table_from_dict


def test_fill_nan_value_node_const_and_ffill(node_ctor):
    # const method
    n = node_ctor("FillNaNValueNode", id="fn1", subset_cols=["a"], method="const", fill_value=[0])
    schema = schema_from_coltypes({"a": ColType.FLOAT, "b": ColType.INT, "_index": ColType.INT})
    n.infer_schema({"table": schema})
    tbl = table_from_dict({"a": [1.0, None, 3.0], "b": [1, 2, 3]}, col_types={"a": ColType.FLOAT, "b": ColType.INT, "_index": ColType.INT})
    out = n.execute({"table": tbl})
    res = out["filled_table"].payload
    assert res.df.iloc[1]["a"] == 0

    # ffill method
    n2 = node_ctor("FillNaNValueNode", id="fn2", subset_cols=["a"], method="ffill")
    n2.infer_schema({"table": schema})
    tbl2 = table_from_dict({"a": [1.0, None, None], "b": [1, 2, 3]}, col_types={"a": ColType.FLOAT, "b": ColType.INT, "_index": ColType.INT})
    out2 = n2.execute({"table": tbl2})
    assert out2["filled_table"].payload.df.iloc[1]["a"] == 1

    # error: missing subset cols parameter
    with pytest.raises(NodeParameterError):
        node_ctor("FillNaNValueNode", id="fn_err", subset_cols=[], method="const", fill_value=[1])

    # error: fill_value length mismatch
    with pytest.raises(NodeParameterError):
        node_ctor("FillNaNValueNode", id="fn_err2", subset_cols=["a", "b"], method="const", fill_value=[1])



def test_fillnanvalue_and_const(node_ctor):
    node2 = node_ctor("FillNaNValueNode", id="fn1", subset_cols=["v"], method="const", fill_value=[0.0])
    schema = schema_from_coltypes({"v": ColType.FLOAT, "_index": ColType.INT})
    node2.infer_schema({"table": schema})
    tbl = table_from_dict({"v": [1, None, 2]})
    out2 = node2.execute({"table": tbl})
    assert "filled_table" in out2
