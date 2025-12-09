import pytest

from server.models.exception import NodeParameterError, NodeValidationError
from server.models.types import ColType
from tests.nodes.utils import schema_from_coltypes, table_from_dict


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
