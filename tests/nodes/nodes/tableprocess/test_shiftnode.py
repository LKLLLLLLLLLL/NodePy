import pytest

from server.models.exception import NodeParameterError
from server.models.types import ColType
from tests.nodes.utils import schema_from_coltypes, table_from_dict


def test_shiftnode_validate_hint_and_process(node_ctor):
    node = node_ctor("ShiftNode", id="sh1", col="v", periods=1, result_col=None)
    # use FLOAT so that shift which introduces NaN keeps float dtype
    schema = schema_from_coltypes({"v": ColType.FLOAT, "_index": ColType.INT})
    hint = node.get_hint("ShiftNode", {"table": schema}, {})
    assert "col_choices" in hint
    out = node.infer_schema({"table": schema})
    assert "table" in out
    tbl = table_from_dict({"v": [1.0,2.0,3.0]})
    res = node.execute({"table": tbl})
    assert "table" in res


def test_shiftnode_errors(node_ctor):
    # empty col name
    with pytest.raises(NodeParameterError):
        node_ctor("ShiftNode", id="sh_err", col="   ", periods=1)
