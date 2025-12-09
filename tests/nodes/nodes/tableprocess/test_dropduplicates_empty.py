from tests.nodes.utils import table_from_dict


def test_dropduplicates_with_empty_subset(node_ctor):
    node = node_ctor("DropDuplicatesNode", id="dd0", subset_cols=[])
    tbl = table_from_dict({"a": [1,1,2], "b": [3,3,4]})
    out = node.process({"table": tbl})
    assert "deduplicated_table" in out
