
from server.models.types import ColType
from tests.nodes.utils import schema_from_coltypes, table_from_dict


def test_dropduplicatesnode(node_ctor):
    node2 = node_ctor("DropDuplicatesNode", id="d1", subset_cols=["v"]) 
    schema2 = schema_from_coltypes({"v": ColType.INT, "_index": ColType.INT})
    node2.infer_schema({"table": schema2})
    tbl2 = table_from_dict({"v": [1,1,2]})
    out2 = node2.execute({"table": tbl2})
    assert "deduplicated_table" in out2
