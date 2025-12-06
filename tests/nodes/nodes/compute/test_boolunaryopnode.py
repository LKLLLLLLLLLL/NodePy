import pytest
from pydantic import ValidationError

from server.interpreter.nodes.base_node import BaseNode
from server.models.data import Data
from server.models.exception import NodeExecutionError, NodeParameterError
from server.models.schema import Schema


def test_boolunaryop_hint_empty():
    assert BaseNode.get_hint("BoolUnaryOpNode", {}, {}) == {}


def test_boolunaryop_hint_with_input():
    assert BaseNode.get_hint("BoolUnaryOpNode", {"x": Schema(type=Schema.Type.BOOL)}, {}) == {}


def test_boolunaryop_construct_accepts(node_ctor):
    n = node_ctor("BoolUnaryOpNode", id="bu1", op="NOT")
    assert n


def test_boolunaryop_construct_rejects_blank(node_ctor):
    with pytest.raises(NodeParameterError):
        node_ctor("BoolUnaryOpNode", id="   ", op="NOT")


def test_boolunaryop_construct_rejects_invalid_op(node_ctor):
    with pytest.raises(ValidationError):
        node_ctor("BoolUnaryOpNode", id="bu-bad", op="BAD")


def test_boolunaryop_static_accepts_bool(node_ctor):
    node = node_ctor("BoolUnaryOpNode", id="bu-static", op="NOT")
    out = node.infer_schema({"x": Schema(type=Schema.Type.BOOL)})
    assert out and isinstance(out, dict)


def test_boolunaryop_static_rejects_nonbool(node_ctor):
    node = node_ctor("BoolUnaryOpNode", id="bu-static-err", op="NOT")
    with pytest.raises(Exception):
        node.infer_schema({"x": Schema(type=Schema.Type.INT)})


def test_boolunaryop_static_rejects_none(node_ctor):
    node = node_ctor("BoolUnaryOpNode", id="bu-static-none", op="NOT")
    with pytest.raises(AttributeError):
        node.infer_schema(None)  # type: ignore[arg-type]


def test_boolunaryop_execute_not(node_ctor):
    node = node_ctor("BoolUnaryOpNode", id="bu-exec", op="NOT")
    node.infer_schema({"x": Schema(type=Schema.Type.BOOL)})
    out = node.process({"x": Data(payload=False)})
    assert out["result"].payload is True


def test_boolunaryop_execute_requires_infer(node_ctor):
    node = node_ctor("BoolUnaryOpNode", id="bu-noinf", op="NOT")
    with pytest.raises(NodeExecutionError):
        node.execute({})


def test_boolunaryop_execute_runtime_error(node_ctor):
    node = node_ctor("BoolUnaryOpNode", id="bu-runtime", op="NOT")
    node.infer_schema({"x": Schema(type=Schema.Type.BOOL)})
    with pytest.raises(NodeExecutionError):
        node.execute({"x": Data(payload=1)})

