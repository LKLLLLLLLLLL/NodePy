import pytest
from pydantic import ValidationError

from server.interpreter.nodes.base_node import BaseNode
from server.models.data import Data
from server.models.exception import (
    NodeExecutionError,
    NodeParameterError,
    NodeValidationError,
)
from server.models.schema import Schema


def test_boolbinop_hint_empty():
    assert BaseNode.get_hint("BoolBinOpNode", {}, {}) == {}


def test_boolbinop_hint_with_inputs():
    assert BaseNode.get_hint("BoolBinOpNode", {"x": Schema(type=Schema.Type.BOOL), "y": Schema(type=Schema.Type.BOOL)}, {}) == {}


def test_boolbinop_hint_unknown_raises():
    with pytest.raises(ValueError):
        BaseNode.get_hint("NoSuch", {}, {})


def test_boolbinop_construct_accepts_and_rejects(node_ctor):
    n1 = node_ctor("BoolBinOpNode", id="bb1", op="AND")
    assert n1
    with pytest.raises(ValidationError):
        node_ctor("BoolBinOpNode", id="bb-bad", op="UNKNOWN")


def test_boolbinop_construct_rejects_blank_id(node_ctor):
    with pytest.raises(NodeParameterError):
        node_ctor("BoolBinOpNode", id="  ", op="OR")


def test_boolbinop_static_accepts_bool_inputs(node_ctor):
    node = node_ctor("BoolBinOpNode", id="bb-static", op="AND")
    out = node.infer_schema({"x": Schema(type=Schema.Type.BOOL), "y": Schema(type=Schema.Type.BOOL)})
    assert out and isinstance(out, dict)


def test_boolbinop_static_rejects_mismatch(node_ctor):
    node = node_ctor("BoolBinOpNode", id="bb-static-mis", op="AND")
    with pytest.raises(NodeValidationError):
        node.infer_schema({"x": Schema(type=Schema.Type.INT), "y": Schema(type=Schema.Type.BOOL)})


def test_boolbinop_static_rejects_missing(node_ctor):
    node = node_ctor("BoolBinOpNode", id="bb-static-miss", op="AND")
    with pytest.raises(NodeValidationError):
        node.infer_schema({"x": Schema(type=Schema.Type.BOOL)})


def test_boolbinop_execute_and(node_ctor):
    node = node_ctor("BoolBinOpNode", id="bb-exec", op="AND")
    node.infer_schema({"x": Schema(type=Schema.Type.BOOL), "y": Schema(type=Schema.Type.BOOL)})
    out = node.process({"x": Data(payload=True), "y": Data(payload=False)})
    assert out["result"].payload is False


def test_boolbinop_execute_requires_infer(node_ctor):
    node = node_ctor("BoolBinOpNode", id="bb-noinf", op="OR")
    with pytest.raises(NodeExecutionError):
        node.execute({})


def test_boolbinop_execute_runtime_type_error(node_ctor):
    node = node_ctor("BoolBinOpNode", id="bb-runtime", op="AND")
    node.infer_schema({"x": Schema(type=Schema.Type.BOOL), "y": Schema(type=Schema.Type.BOOL)})
    with pytest.raises(NodeExecutionError):
        node.execute({"x": Data(payload=True), "y": Data(payload=1)})


def test_boolbinop_unknown_op_runtime(node_ctor):
    node = node_ctor("BoolBinOpNode", id="bb-runtime-bad", op="AND")
    node.infer_schema({"x": Schema(type=Schema.Type.BOOL), "y": Schema(type=Schema.Type.BOOL)})
    node.op = "UNKNOWN"
    with pytest.raises(NodeExecutionError):
        node.process({"x": Data(payload=True), "y": Data(payload=False)})


def test_boolbinop_other_ops(node_ctor):
    node = node_ctor("BoolBinOpNode", id="bb-or", op="OR")
    node.infer_schema({"x": Schema(type=Schema.Type.BOOL), "y": Schema(type=Schema.Type.BOOL)})
    assert node.process({"x": Data(payload=False), "y": Data(payload=True)})["result"].payload is True
    node.op = "XOR"
    assert node.process({"x": Data(payload=True), "y": Data(payload=False)})["result"].payload is True
    node.op = "SUB"
    assert node.process({"x": Data(payload=True), "y": Data(payload=False)})["result"].payload is True

