import pytest

from server.models.exception import NodeParameterError, NodeValidationError
from server.models.types import ColType
from tests.nodes.utils import schema_from_coltypes, table_from_dict


def test_groupnode_construct_infer_and_process(node_ctor):
    node = node_ctor("GroupNode", id="g1", group_cols=["k"], agg_cols=["v"], agg_func="SUM")
    schema = schema_from_coltypes({"k": ColType.STR, "v": ColType.INT, "_index": ColType.INT})
    hint = node.get_hint("GroupNode", {"table": schema}, {})
    assert "group_col_choices" in hint

    out_schema = node.infer_schema({"table": schema})
    assert "grouped_table" in out_schema

    tbl = table_from_dict({"k": ["a","a","b"], "v": [1,2,3]})
    out = node.execute({"table": tbl})
    assert out["grouped_table"].payload.df.columns.tolist()


def test_groupnode_errors(node_ctor):
    # missing group cols
    with pytest.raises(NodeParameterError):
        node_ctor("GroupNode", id="g_err1", group_cols=[], agg_cols=["v"], agg_func="SUM")

    # missing agg cols
    with pytest.raises(NodeParameterError):
        node_ctor("GroupNode", id="g_err2", group_cols=["k"], agg_cols=[], agg_func="SUM")

    # infer with missing group col
    node = node_ctor("GroupNode", id="g_err3", group_cols=["missing"], agg_cols=["v"], agg_func="SUM")
    bad_schema = schema_from_coltypes({"k": ColType.STR, "v": ColType.INT, "_index": ColType.INT})
    with pytest.raises(NodeValidationError):
        node.infer_schema({"table": bad_schema})


def test_group_count_and_mean(node_ctor):
    g = node_ctor("GroupNode", id="g_count", group_cols=["g"], agg_cols=["v"], agg_func="COUNT")
    schema_g = schema_from_coltypes({"g": ColType.INT, "v": ColType.INT, "_index": ColType.INT})
    g.infer_schema({"table": schema_g})
    tbl_g = table_from_dict({"g": [1, 1, 2], "v": [10, 20, 30]}, col_types={"g": ColType.INT, "v": ColType.INT, "_index": ColType.INT})
    out_g = g.execute({"table": tbl_g})
    assert "grouped_table" in out_g

    g2 = node_ctor("GroupNode", id="g_mean", group_cols=["g"], agg_cols=["v"], agg_func="MEAN")
    g2.infer_schema({"table": schema_g})
    out_g2 = g2.execute({"table": tbl_g})
    assert out_g2["grouped_table"].payload.df["v"].dtype in (float,)
