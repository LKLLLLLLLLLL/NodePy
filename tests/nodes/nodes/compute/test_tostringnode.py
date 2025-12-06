import pytest
from pydantic import ValidationError

from server.interpreter.nodes.base_node import BaseNode
from server.models.data import Data
from server.models.exception import NodeExecutionError, NodeParameterError
from server.models.schema import Schema


def test_tostringnode_hint_empty():
    assert BaseNode.get_hint("ToStringNode", {}, {}) == {}


def test_tostringnode_hint_with_input():
    hint = BaseNode.get_hint("ToStringNode", {"input": Schema(type=Schema.Type.INT)}, {})
    assert hint == {}


def test_tostringnode_hint_unknown_raises():
    with pytest.raises(ValueError):
        BaseNode.get_hint("NoSuchNode", {}, {})


def test_tostringnode_construct_accepts_default(node_ctor):
    n = node_ctor("ToStringNode", id="ts1")
    assert n


def test_tostringnode_construct_rejects_blank_id(node_ctor):
    with pytest.raises(NodeParameterError):
        node_ctor("ToStringNode", id="   ")


def test_tostringnode_construct_rejects_bad_param(node_ctor):
    with pytest.raises((ValidationError, NodeParameterError)):
        node_ctor("ToStringNode", id="ts-bad", some_param=object())


def test_tostringnode_static_accepts_primitive(node_ctor):
    node = node_ctor("ToStringNode", id="ts-static")
    out = node.infer_schema({"input": Schema(type=Schema.Type.INT)})
    assert out and isinstance(out, dict)


def test_tostringnode_static_rejects_none_input(node_ctor):
    node = node_ctor("ToStringNode", id="ts-static-none")
    with pytest.raises(AttributeError):
        node.infer_schema(None)  # type: ignore[arg-type]


def test_tostringnode_static_rejects_extra_input(node_ctor):
    node = node_ctor("ToStringNode", id="ts-static-extra")
    with pytest.raises(ValueError):
        node.infer_schema({"input": Schema(type=Schema.Type.INT), "extra": Schema(type=Schema.Type.INT)})


def test_tostringnode_execute_converts_int(node_ctor):
    node = node_ctor("ToStringNode", id="ts-exec")
    node.infer_schema({"input": Schema(type=Schema.Type.INT)})
    out = node.process({"input": Data(payload=123)})
    assert out and isinstance(out.get("output").payload, str)


def test_tostringnode_execute_requires_infer(node_ctor):
    node = node_ctor("ToStringNode", id="ts-no-infer")
    with pytest.raises(NodeExecutionError):
        node.execute({})


def test_tostringnode_execute_runtime_type_mismatch(node_ctor):
    node = node_ctor("ToStringNode", id="ts-runtime")
    node.infer_schema({"input": Schema(type=Schema.Type.INT)})
    with pytest.raises(NodeExecutionError):
        node.execute({"input": Data(payload=None)})

