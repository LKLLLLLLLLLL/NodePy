import pytest

from server.models.data import Data
from server.models.exception import NodeExecutionError
from server.models.schema import Schema


def test_tofloat_execute(node_ctor):
    node = node_ctor("ToFloatNode", id="f1")
    node.infer_schema({"input": Schema(type=Schema.Type.INT)})
    out = node.process({"input": Data(payload=3)})
    assert isinstance(out["output"].payload, float)


def test_tofloat_static_rejects_file(node_ctor):
    node = node_ctor("ToFloatNode", id="f2")
    with pytest.raises(Exception):
        node.infer_schema({"input": Schema(type=Schema.Type.FILE)})


def test_tofloat_execute_bad_string(node_ctor):
    node = node_ctor("ToFloatNode", id="f3")
    node.infer_schema({"input": Schema(type=Schema.Type.STR)})
    with pytest.raises(NodeExecutionError):
        node.process({"input": Data(payload="notfloat")})
