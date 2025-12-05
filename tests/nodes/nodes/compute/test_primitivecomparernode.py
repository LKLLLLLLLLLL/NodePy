import pytest
from pydantic import ValidationError

from server.interpreter.nodes.base_node import BaseNode
from server.models.data import Data
from server.models.exception import NodeExecutionError, NodeValidationError
from server.models.schema import Schema


def test_primitivecompare_equals(node_ctor):
    node = node_ctor("PrimitiveCompareNode", id="pc1", op="EQ")
    node.infer_schema({"x": Schema(type=Schema.Type.INT), "y": Schema(type=Schema.Type.INT)})
    out = node.process({"x": Data(payload=2), "y": Data(payload=2)})
    assert out["result"].payload is True


def test_primitvecompare_type_mismatch(node_ctor):
    node = node_ctor("PrimitiveCompareNode", id="pc2", op="EQ")
    with pytest.raises(NodeValidationError):
        node.infer_schema({"x": Schema(type=Schema.Type.INT), "y": Schema(type=Schema.Type.STR)})


def test_primitivecompare_construct_missing_op(node_ctor):
    with pytest.raises(ValidationError):
        node_ctor("PrimitiveCompareNode", id="pc-miss")


def test_primitivecompare_static_success_bool(node_ctor):
    node = node_ctor("PrimitiveCompareNode", id="pc3", op="EQ")
    out = node.infer_schema({"x": Schema(type=Schema.Type.BOOL), "y": Schema(type=Schema.Type.BOOL)})
    assert out == {"result": Schema(type=Schema.Type.BOOL)}


def test_primitivecompare_execute_type_mismatch_runtime(node_ctor):
    node = node_ctor("PrimitiveCompareNode", id="pc4", op="EQ")
    node.infer_schema({"x": Schema(type=Schema.Type.INT), "y": Schema(type=Schema.Type.INT)})
    with pytest.raises(NodeExecutionError):
        node.execute({"x": Data(payload=1), "y": Data(payload="1")})


def test_primitivecompare_hint_negative(node_ctor):
    with pytest.raises(AssertionError):
        hint = BaseNode.get_hint("PrimitiveCompareNode", {"x": Schema(type=Schema.Type.INT), "y": Schema(type=Schema.Type.INT)}, {})
        assert hint
