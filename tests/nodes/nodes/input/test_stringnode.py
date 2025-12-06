import pytest
from pydantic import ValidationError

from server.interpreter.nodes.base_node import BaseNode, InPort
from server.models.data import Data
from server.models.exception import (
    NodeExecutionError,
    NodeParameterError,
    NodeValidationError,
)
from server.models.schema import Pattern, Schema


def test_stringnode_hint_empty_with_no_inputs():
    """Hint stage: returns empty hints for StringNode with no inputs."""
    assert BaseNode.get_hint("StringNode", {}, {}) == {}


def test_stringnode_hint_ignores_params_and_inputs():
    """Hint stage: still empty when params are prefilled or stray inputs exist."""
    params = {"value": "abc"}
    schemas = {"ghost": Schema(type=Schema.Type.STR)}
    assert BaseNode.get_hint("StringNode", schemas, params) == {}


def test_stringnode_hint_unknown_type_raises():
    """Hint stage: unknown type names are rejected."""
    with pytest.raises(ValueError):
        BaseNode.get_hint("MissingString", {}, {})


def test_stringnode_hint_empty_type_raises():
    """Hint stage: empty type names trigger registry errors."""
    with pytest.raises(ValueError):
        BaseNode.get_hint("", {}, {})


def test_stringnode_hint_none_type_raises():
    """Hint stage: None type names are rejected."""
    with pytest.raises(ValueError):
        BaseNode.get_hint(None, {}, {})  # type: ignore[arg-type]


def test_stringnode_construct_accepts_basic(node_ctor):
    """Construct stage: accepts basic string payloads."""
    node = node_ctor("StringNode", id="s-basic", value="hello")
    assert node.value == "hello"


def test_stringnode_construct_accepts_empty(node_ctor):
    """Construct stage: accepts empty strings."""
    node = node_ctor("StringNode", id="s-empty", value="")
    assert node.value == ""


def test_stringnode_construct_rejects_missing_value(node_ctor):
    """Construct stage: missing required value triggers validation error."""
    with pytest.raises((NodeParameterError, ValidationError)):
        node_ctor("StringNode", id="s-missing")


def test_stringnode_construct_rejects_unknown_type(node_ctor):
    """Construct stage: requesting an unregistered node type raises an error."""
    with pytest.raises(ValueError):
        node_ctor("MissingStringNode", id="s-wrong-type", value="hi")  # type: ignore[arg-type]


def test_stringnode_construct_rejects_blank_id(node_ctor):
    """Construct stage: id must be non-empty."""
    with pytest.raises(NodeParameterError):
        node_ctor("StringNode", id="   ", value="hi")


def test_stringnode_static_infers_string_schema(node_ctor):
    """Static analysis: infers string output schema."""
    node = node_ctor("StringNode", id="s-static", value="hello")
    out_schemas = node.infer_schema({})
    assert out_schemas == {"string": Schema(type=Schema.Type.STR)}


def test_stringnode_static_infers_string_schema_for_empty(node_ctor):
    """Static analysis: inference succeeds for empty strings."""
    node = node_ctor("StringNode", id="s-static-empty", value="")
    out_schemas = node.infer_schema({})
    assert out_schemas == {"string": Schema(type=Schema.Type.STR)}


def test_stringnode_static_rejects_extra_inputs(node_ctor):
    """Static analysis: rejects unexpected input schemas."""
    node = node_ctor("StringNode", id="s-extra-input", value="abc")
    with pytest.raises(ValueError):
        node.infer_schema({"extra": Schema(type=Schema.Type.STR)})


def test_stringnode_static_rejects_non_mapping_input(node_ctor):
    """Static analysis: infer_schema requires mapping inputs."""
    node = node_ctor("StringNode", id="s-non-mapping", value="abc")
    with pytest.raises(TypeError):
        node.infer_schema(None)  # type: ignore[arg-type]


def test_stringnode_static_requires_required_input_when_port_defined(node_ctor, monkeypatch):
    """Static analysis: missing required inputs trigger validation when ports demand them."""
    node = node_ctor("StringNode", id="s-missing-port", value="abc")

    def fake_port_def(_self=None):
        return [InPort(name="input", description="required", accept=Pattern(types={Schema.Type.STR}))], []

    monkeypatch.setattr(type(node), "port_def", fake_port_def)
    with pytest.raises(NodeValidationError):
        node.infer_schema({})


def test_stringnode_execute_emits_string(node_ctor):
    """Execute stage: emits provided string payload."""
    node = node_ctor("StringNode", id="s-exec", value="hi")
    node.infer_schema({})
    outputs = node.execute({})
    assert outputs == {"string": Data(payload="hi")}


def test_stringnode_execute_emits_empty(node_ctor):
    """Execute stage: emits empty string payload."""
    node = node_ctor("StringNode", id="s-exec-empty", value="")
    node.infer_schema({})
    outputs = node.execute({})
    assert outputs == {"string": Data(payload="")}


def test_stringnode_execute_requires_inferred_schema(node_ctor):
    """Execute stage: running without schema inference raises an error."""
    node = node_ctor("StringNode", id="s-no-infer", value="hi")
    with pytest.raises(NodeExecutionError):
        node.execute({})


def test_stringnode_execute_rejects_unexpected_input(node_ctor):
    """Execute stage: extra runtime inputs cause schema mismatches."""
    node = node_ctor("StringNode", id="s-extra-runtime", value="hi")
    node.infer_schema({})
    with pytest.raises(NodeExecutionError):
        node.execute({"extra": Data(payload="unused")})


def test_stringnode_execute_rejects_mismatched_output_schema(node_ctor):
    """Execute stage: tampered cached schema triggers mismatch error."""
    node = node_ctor("StringNode", id="s-out-mismatch", value="hi")
    node.infer_schema({})
    node._schemas_out = {"string": Schema(type=Schema.Type.FLOAT)}  # type: ignore[attr-defined]
    with pytest.raises(NodeExecutionError):
        node.execute({})

def test_stringnode_construct_and_process(node_ctor):
    node = node_ctor("StringNode", id="s1", value="hello")
    out = node.infer_schema({})
    assert out == {"string": Schema(type=Schema.Type.STR)}
    res = node.process({})
    assert res["string"].payload == "hello"
