import pytest

from server.models.exception import NodeValidationError
from server.models.types import ColType
from tests.nodes.utils import schema_from_coltypes, table_from_dict


def test_sortnode_infer_and_process(node_ctor):
    node = node_ctor("SortNode", id="so1", sort_col="a", ascending=True)
    s = schema_from_coltypes({"a": ColType.INT, "_index": ColType.INT})
    # infer ok
    node.infer_schema({"table": s})
    tbl = table_from_dict({"a": [3,1,2]})
    out = node.execute({"table": tbl})
    assert "sorted_table" in out


def test_sortnode_errors(node_ctor):
    node = node_ctor("SortNode", id="so_err", sort_col="missing", ascending=True)
    bad = schema_from_coltypes({"a": ColType.INT, "_index": ColType.INT})
    with pytest.raises(NodeValidationError):
        node.infer_schema({"table": bad})
