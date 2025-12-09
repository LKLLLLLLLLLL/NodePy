import pytest

from server.models.types import ColType
from tests.nodes.utils import schema_from_coltypes, table_from_dict


def test_mergenode_normal_and_error(node_ctor):
    node3 = node_ctor("MergeNode", id="m1")
    t1 = table_from_dict({"a": [1], "b": [2]})
    t2 = table_from_dict({"a": [3], "b": [4]})
    s = schema_from_coltypes({"a": ColType.INT, "b": ColType.INT, "_index": ColType.INT})
    node3.infer_schema({"table_1": s, "table_2": s})
    out3 = node3.execute({"table_1": t1, "table_2": t2})
    assert "merged_table" in out3

    # Merge infer mismatch
    node = node_ctor("MergeNode", id="m_err")
    s1 = schema_from_coltypes({"a": ColType.INT, "_index": ColType.INT})
    s2 = schema_from_coltypes({"a": ColType.FLOAT, "_index": ColType.INT})
    with pytest.raises(Exception):
        node.infer_schema({"table_1": s1, "table_2": s2})
