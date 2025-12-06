import pytest
from pydantic import ValidationError

from server.models.data import Data
from server.models.exception import NodeExecutionError, NodeValidationError
from server.models.schema import Schema


def test_numberunaryop_negate(node_ctor):
    node = node_ctor("NumberUnaryOpNode", id="nu1", op="NEG")
    node.infer_schema({"x": Schema(type=Schema.Type.INT)})
    out = node.process({"x": Data(payload=5)})
    assert out["result"].payload == -5


def test_numberunaryop_abs(node_ctor):
    node = node_ctor("NumberUnaryOpNode", id="nu3", op="ABS")
    node.infer_schema({"x": Schema(type=Schema.Type.INT)})
    out = node.process({"x": Data(payload=-7)})
    assert out["result"].payload == 7


def test_numberunaryop_construct_reject_missing_op(node_ctor):
    with pytest.raises(ValidationError):
        node_ctor("NumberUnaryOpNode", id="nu-miss")


def test_numberunaryop_static_rejects_string(node_ctor):
    node = node_ctor("NumberUnaryOpNode", id="nu4", op="NEG")
    with pytest.raises(NodeValidationError):
        node.infer_schema({"x": Schema(type=Schema.Type.STR)})


def test_numberunaryop_execute_sqrt_negative(node_ctor):
    node = node_ctor("NumberUnaryOpNode", id="nu5", op="SQRT")
    node.infer_schema({"x": Schema(type=Schema.Type.INT)})
    with pytest.raises(NodeExecutionError):
        node.process({"x": Data(payload=-4)})


def test_numberunaryop_rejects_non_number_static(node_ctor):
    node = node_ctor("NumberUnaryOpNode", id="nu2", op="NEG")
    with pytest.raises(NodeValidationError):
        node.infer_schema({"x": Schema(type=Schema.Type.STR)})


def test_numberunary_unknown_op_runtime(node_ctor):
    node = node_ctor("NumberUnaryOpNode", id="nu-runtime-bad", op="NEG")
    node.infer_schema({"x": Schema(type=Schema.Type.INT)})
    node.op = "BAD"
    with pytest.raises(NodeExecutionError):
        node.process({"x": Data(payload=3)})
