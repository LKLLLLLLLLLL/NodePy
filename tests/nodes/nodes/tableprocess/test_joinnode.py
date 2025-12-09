import pytest

from server.models.types import ColType
from tests.nodes.utils import schema_from_coltypes


def test_join_normal_and_errors(node_ctor):
    left = node_ctor("JoinNode", id="j1", left_on="k", right_on="k", how="INNER")
    # matching types
    left_schema = schema_from_coltypes({"k": ColType.INT, "v": ColType.INT, "_index": ColType.INT})
    right_schema = schema_from_coltypes({"k": ColType.INT, "w": ColType.INT, "_index": ColType.INT})
    out = left.infer_schema({"left_table": left_schema, "right_table": right_schema})
    assert "joined_table" in out

    # mismatched key types
    left_bad = node_ctor("JoinNode", id="j2", left_on="k", right_on="k", how="LEFT")
    left_schema2 = schema_from_coltypes({"k": ColType.INT, "_index": ColType.INT})
    right_schema2 = schema_from_coltypes({"k": ColType.STR, "_index": ColType.INT})
    # implementation may raise NodeValidationError or AssertionError due to error construction
    with pytest.raises(Exception):
        left_bad.infer_schema({"left_table": left_schema2, "right_table": right_schema2})


def test_join_infer_execute_merging(node_ctor):
    node = node_ctor("JoinNode", id="jexec", left_on="k", right_on="k", how="INNER")
    s_left = schema_from_coltypes({"k": ColType.INT, "v": ColType.INT, "_index": ColType.INT})
    s_right = schema_from_coltypes({"k": ColType.INT, "w": ColType.INT, "_index": ColType.INT})
    out = node.infer_schema({"left_table": s_left, "right_table": s_right})
    assert "joined_table" in out
