
from server.models.data import Data
from server.models.schema import Schema


def test_tobool_execute(node_ctor):
    node = node_ctor("ToBoolNode", id="b1")
    node.infer_schema({"input": Schema(type=Schema.Type.STR)})
    out = node.process({"input": Data(payload="true")})
    assert out["output"].payload is True
