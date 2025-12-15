import pytest

from server.models.exception import NodeParameterError, NodeValidationError
from server.models.types import ColType
from tests.nodes.utils import schema_from_coltypes, table_from_dict


def test_filter_node(node_ctor):
    n = node_ctor("FilterNode", id="f1", cond_col="flag")
    schema = schema_from_coltypes({"flag": ColType.BOOL, "val": ColType.INT, "_index": ColType.INT})
    out = n.infer_schema({"table": schema})
    assert "true_table" in out and "false_table" in out

    tbl = table_from_dict({"flag": [True, False, True], "val": [1, 2, 3]}, col_types={"flag": ColType.BOOL, "val": ColType.INT, "_index": ColType.INT})
    n.infer_schema({"table": schema})
    res = n.execute({"table": tbl})
    assert len(res["true_table"].payload.df) == 2
    assert len(res["false_table"].payload.df) == 1

    # error: cond_col missing in schema
    n2 = node_ctor("FilterNode", id="f2", cond_col="nope")
    with pytest.raises(NodeValidationError):
        n2.infer_schema({"table": schema})



def test_filternode_normal_and_errors(node_ctor):
    # FilterNode normal
    node = node_ctor("FilterNode", id="f1", cond_col="c")
    schema = schema_from_coltypes({"c": ColType.BOOL, "v": ColType.INT, "_index": ColType.INT})
    node.infer_schema({"table": schema})
    tbl = table_from_dict({"c": [True, False, True], "v": [1,2,3]})
    out = node.execute({"table": tbl})
    assert "true_table" in out and "false_table" in out

    # empty cond_col should raise
    with pytest.raises(NodeParameterError):
        node_ctor("FilterNode", id="f_err", cond_col="   ")

    # infer missing cond_col
    node = node_ctor("FilterNode", id="f2", cond_col="missing")
    bad_schema = schema_from_coltypes({"c": ColType.BOOL, "_index": ColType.INT})
    with pytest.raises(NodeValidationError):
        node.infer_schema({"table": bad_schema})
