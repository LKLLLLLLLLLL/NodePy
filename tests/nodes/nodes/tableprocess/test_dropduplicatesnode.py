import pytest

from server.models.exception import NodeValidationError
from server.models.types import ColType
from tests.nodes.utils import schema_from_coltypes, table_from_dict


def test_drop_duplicates_node(node_ctor):
    n = node_ctor("DropDuplicatesNode", id="dd1", subset_cols=["a"])
    schema = schema_from_coltypes({"a": ColType.INT, "b": ColType.INT, "_index": ColType.INT})
    n.infer_schema({"table": schema})

    tbl = table_from_dict({"a": [1, 1, 2], "b": [10, 10, 20]}, col_types={"a": ColType.INT, "b": ColType.INT, "_index": ColType.INT})
    out = n.execute({"table": tbl})
    res_tbl = out["deduplicated_table"].payload
    # one duplicate dropped -> length 2
    assert len(res_tbl.df) == 2

    # error: subset col not in schema
    n2 = node_ctor("DropDuplicatesNode", id="dd2", subset_cols=["nope"])
    with pytest.raises(NodeValidationError):
        n2.infer_schema({"table": schema})


def test_dropduplicatesnode(node_ctor):
    node2 = node_ctor("DropDuplicatesNode", id="d1", subset_cols=["v"]) 
    schema2 = schema_from_coltypes({"v": ColType.INT, "_index": ColType.INT})
    node2.infer_schema({"table": schema2})
    tbl2 = table_from_dict({"v": [1,1,2]})
    out2 = node2.execute({"table": tbl2})
    assert "deduplicated_table" in out2

def test_dropduplicates_with_empty_subset(node_ctor):
    node = node_ctor("DropDuplicatesNode", id="dd0", subset_cols=[])
    tbl = table_from_dict({"a": [1, 1, 2], "b": [3, 3, 4]})
    out = node.process({"table": tbl})
    assert "deduplicated_table" in out
