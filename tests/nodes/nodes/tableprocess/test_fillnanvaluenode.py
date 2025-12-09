
from server.models.types import ColType
from tests.nodes.utils import schema_from_coltypes, table_from_dict


def test_fillnanvalue_and_const(node_ctor):
    node2 = node_ctor("FillNaNValueNode", id="fn1", subset_cols=["v"], method="const", fill_value=[0.0])
    schema = schema_from_coltypes({"v": ColType.FLOAT, "_index": ColType.INT})
    node2.infer_schema({"table": schema})
    tbl = table_from_dict({"v": [1, None, 2]})
    out2 = node2.execute({"table": tbl})
    assert "filled_table" in out2
