import pytest

from server.models.exception import NodeValidationError
from server.models.types import ColType
from tests.nodes.utils import schema_from_coltypes, table_from_dict


def test_renamecol_normal_and_conflict(node_ctor):
    node = node_ctor("RenameColNode", id="r1", rename_map={"a": "x"})
    schema = schema_from_coltypes({"a": ColType.INT, "b": ColType.FLOAT, "_index": ColType.INT})
    out = node.infer_schema({"table": schema})
    assert "renamed_table" in out

    # missing old column
    node2 = node_ctor("RenameColNode", id="r2", rename_map={"missing": "n"})
    with pytest.raises(NodeValidationError):
        node2.infer_schema({"table": schema})

    # conflict after renaming
    node3 = node_ctor("RenameColNode", id="r3", rename_map={"a": "b"})
    with pytest.raises(NodeValidationError):
        node3.infer_schema({"table": schema})


def test_rename_execute(node_ctor):
    node = node_ctor("RenameColNode", id="rn1", rename_map={"a": "x"})
    tbl = table_from_dict({"a": [1], "b": [2]})
    # run infer then execute to set internal col types
    s = schema_from_coltypes({"a": ColType.INT, "b": ColType.INT, "_index": ColType.INT})
    node.infer_schema({"table": s})
    out = node.execute({"table": tbl})
    assert "x" in out["renamed_table"].payload.df.columns
