import pytest

from server.models.exception import NodeParameterError
from server.models.types import ColType
from tests.nodes.utils import schema_from_coltypes


def test_rename_illegal_new_name_raises(node_ctor):
    # new name starts with '_' is illegal
    with pytest.raises(NodeParameterError):
        node_ctor("RenameColNode", id="rn_bad", rename_map={"a": "_bad"})


def test_join_hint_choices(node_ctor):
    n = node_ctor("JoinNode", id="jh", left_on="k", right_on="k", how="INNER")
    s_left = schema_from_coltypes({"k": ColType.INT, "v": ColType.INT, "_index": ColType.INT})
    s_right = schema_from_coltypes({"k": ColType.INT, "w": ColType.INT, "_index": ColType.INT})
    hint = n.get_hint("JoinNode", {"left_table": s_left, "right_table": s_right}, {})
    assert "left_on_choices" in hint and "k" in hint["left_on_choices"]
    assert "right_on_choices" in hint and "k" in hint["right_on_choices"]


def test_merge_infer_schema_mismatch_raises(node_ctor):
    m = node_ctor("MergeNode", id="m1")
    s1 = schema_from_coltypes({"a": ColType.INT, "_index": ColType.INT})
    s2 = schema_from_coltypes({"a": ColType.FLOAT, "_index": ColType.INT})
    with pytest.raises(Exception):
        m.infer_schema({"table_1": s1, "table_2": s2})


def test_selectcol_missing_column_raises(node_ctor):
    sel = node_ctor("SelectColNode", id="s1", selected_cols=["z"])
    s = schema_from_coltypes({"a": ColType.INT, "_index": ColType.INT})
    # infer should fail when selected column not present
    with pytest.raises(Exception):
        sel.infer_schema({"table": s})
