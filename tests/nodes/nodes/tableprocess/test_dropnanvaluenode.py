
from server.models.types import ColType
from tests.nodes.utils import schema_from_coltypes, table_from_dict


def test_dropnanvaluenode(node_ctor):
    node = node_ctor("DropNaNValueNode", id="dn1", subset_cols=["v"]) 
    # use FLOAT because NaN in pandas will coerce column to float
    schema = schema_from_coltypes({"v": ColType.FLOAT, "_index": ColType.INT})
    node.infer_schema({"table": schema})
    tbl = table_from_dict({"v": [1, None, 2]})
    out = node.execute({"table": tbl})
    assert "cleaned_table" in out
