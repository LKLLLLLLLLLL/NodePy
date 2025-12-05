import pytest
from pydantic import ValidationError

from server.interpreter.nodes.base_node import BaseNode
from server.models.data import Data
from server.models.exception import NodeExecutionError, NodeValidationError
from server.models.schema import Schema


def test_numberunaryop_negate(node_ctor):
    """Construct/execute: unary negate flips sign for numbers."""
    node = node_ctor("NumberUnaryOpNode", id="nu1", op="NEG")
    node.infer_schema({"x": Schema(type=Schema.Type.INT)})
    out = node.process({"x": Data(payload=5)})
    assert out["result"].payload == -5


def test_numberunaryop_abs(node_ctor):
    """Execute success: ABS returns absolute value."""
    node = node_ctor("NumberUnaryOpNode", id="nu3", op="ABS")
    node.infer_schema({"x": Schema(type=Schema.Type.INT)})
    out = node.process({"x": Data(payload=-7)})
    assert out["result"].payload == 7


def test_numberunaryop_construct_reject_missing_op(node_ctor):
    """Construct failure: missing op raises ValidationError."""
    with pytest.raises(ValidationError):
        node_ctor("NumberUnaryOpNode", id="nu-miss")


def test_numberunaryop_static_rejects_string(node_ctor):
    """Static failure: string input should raise NodeValidationError."""
    node = node_ctor("NumberUnaryOpNode", id="nu4", op="NEG")
    with pytest.raises(NodeValidationError):
        node.infer_schema({"x": Schema(type=Schema.Type.STR)})


def test_numberunaryop_execute_sqrt_negative(node_ctor):
    """Execute failure: SQRT of negative raises NodeExecutionError."""
    node = node_ctor("NumberUnaryOpNode", id="nu5", op="SQRT")
    node.infer_schema({"x": Schema(type=Schema.Type.INT)})
    with pytest.raises(NodeExecutionError):
        node.process({"x": Data(payload=-4)})


def test_numberunaryop_rejects_non_number_static(node_ctor):
    """Static: Non-number input raises NodeValidationError."""
    node = node_ctor("NumberUnaryOpNode", id="nu2", op="NEG")
    with pytest.raises(NodeValidationError):
        node.infer_schema({"x": Schema(type=Schema.Type.STR)})


def test_primitivecompare_equals(node_ctor):
    """Execute: primitive compare returns boolean for equality."""
    node = node_ctor("PrimitiveCompareNode", id="pc1", op="EQ")
    node.infer_schema({"x": Schema(type=Schema.Type.INT), "y": Schema(type=Schema.Type.INT)})
    out = node.process({"x": Data(payload=2), "y": Data(payload=2)})
    assert out["result"].payload is True


def test_primitvecompare_type_mismatch(node_ctor):
    """Static: comparing different types raises NodeValidationError."""
    node = node_ctor("PrimitiveCompareNode", id="pc2", op="EQ")
    with pytest.raises(NodeValidationError):
        node.infer_schema({"x": Schema(type=Schema.Type.INT), "y": Schema(type=Schema.Type.STR)})


def test_primitivecompare_construct_missing_op(node_ctor):
    """Construct failure: missing op raises ValidationError."""
    with pytest.raises(ValidationError):
        node_ctor("PrimitiveCompareNode", id="pc-miss")


def test_primitivecompare_static_success_bool(node_ctor):
    """Static success: bool compare returns bool schema."""
    node = node_ctor("PrimitiveCompareNode", id="pc3", op="EQ")
    out = node.infer_schema({"x": Schema(type=Schema.Type.BOOL), "y": Schema(type=Schema.Type.BOOL)})
    assert out == {"result": Schema(type=Schema.Type.BOOL)}


def test_primitivecompare_execute_type_mismatch_runtime(node_ctor):
    """Execute failure: runtime mismatch triggers NodeExecutionError."""
    node = node_ctor("PrimitiveCompareNode", id="pc4", op="EQ")
    node.infer_schema({"x": Schema(type=Schema.Type.INT), "y": Schema(type=Schema.Type.INT)})
    with pytest.raises(NodeExecutionError):
        node.execute({"x": Data(payload=1), "y": Data(payload="1")})


def test_primitivecompare_hint_negative(node_ctor):
    """Hint stage negative: request hint expecting non-empty when implementation returns {}."""
    with pytest.raises(AssertionError):
        hint = BaseNode.get_hint("PrimitiveCompareNode", {"x": Schema(type=Schema.Type.INT), "y": Schema(type=Schema.Type.INT)}, {})
        assert hint
