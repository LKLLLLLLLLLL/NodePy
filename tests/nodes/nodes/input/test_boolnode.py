import pytest
from pydantic import ValidationError

from server.interpreter.nodes.base_node import BaseNode
from server.models.data import Data
from server.models.exception import (
    NodeExecutionError,
    NodeParameterError,
    NodeValidationError,
)
from server.models.schema import Pattern, Schema


def test_boolnode_hint_empty_with_no_inputs():
    """Hint stage: returns empty hints for BoolNode with no inputs or params."""
    assert BaseNode.get_hint("BoolNode", {}, {}) == {}


def test_boolnode_hint_ignores_params_and_inputs():
    """Hint stage: keeps empty hints even when params are prefilled."""
    params = {"value": False}
    schemas = {"ghost": Schema(type=Schema.Type.BOOL)}
    assert BaseNode.get_hint("BoolNode", schemas, params) == {}


def test_boolnode_hint_unknown_type_raises():
    """Hint stage: unknown type names fail registry lookup."""
    with pytest.raises(ValueError):
        BaseNode.get_hint("MissingBool", {}, {})


def test_boolnode_hint_empty_type_raises():
    """Hint stage: empty type names are rejected."""
    with pytest.raises(ValueError):
        BaseNode.get_hint("", {}, {})


def test_boolnode_hint_none_type_raises():
    """Hint stage: None type names are rejected."""
    with pytest.raises(ValueError):
        BaseNode.get_hint(None, {}, {})  # type: ignore[arg-type]


def test_boolnode_construct_accepts_true(node_ctor):
    """Construct stage: accepts boolean True payload."""
    node = node_ctor("BoolNode", id="b-true", value=True)
    assert node.value is True


def test_boolnode_construct_accepts_false(node_ctor):
    """Construct stage: accepts boolean False payload."""
    node = node_ctor("BoolNode", id="b-false", value=False)
    assert node.value is False


def test_boolnode_construct_rejects_missing_value(node_ctor):
    """Construct stage: missing required value triggers validation error."""
    with pytest.raises((NodeParameterError, ValidationError)):
        node_ctor("BoolNode", id="b-missing")


def test_boolnode_construct_rejects_unknown_type(node_ctor):
    """Construct stage: requesting an unregistered node type raises an error."""
    with pytest.raises(ValueError):
        node_ctor("MissingBoolNode", id="b-wrong-type", value=True)  # type: ignore[arg-type]


def test_boolnode_construct_rejects_blank_id(node_ctor):
    """Construct stage: id cannot be blank."""
    with pytest.raises(NodeParameterError):
        node_ctor("BoolNode", id="   ", value=True)


def test_boolnode_static_infers_bool_schema(node_ctor):
    """Static analysis: infers bool output schema."""
    node = node_ctor("BoolNode", id="b-static", value=True)
    out_schemas = node.infer_schema({})
    assert out_schemas == {"const": Schema(type=Schema.Type.BOOL)}


def test_boolnode_static_infers_bool_schema_when_false(node_ctor):
    """Static analysis: inference succeeds regardless of payload truthiness."""
    node = node_ctor("BoolNode", id="b-static-false", value=False)
    out_schemas = node.infer_schema({})
    assert out_schemas == {"const": Schema(type=Schema.Type.BOOL)}


def test_boolnode_static_rejects_extra_inputs(node_ctor):
    """Static analysis: rejects unexpected input schemas for a source node."""
    node = node_ctor("BoolNode", id="b-extra-input", value=True)
    with pytest.raises(ValueError):
        node.infer_schema({"extra": Schema(type=Schema.Type.BOOL)})


def test_boolnode_static_rejects_non_mapping_input(node_ctor):
    """Static analysis: infer_schema requires a mapping input."""
    node = node_ctor("BoolNode", id="b-non-mapping", value=True)
    with pytest.raises(TypeError):
        node.infer_schema(None)  # type: ignore[arg-type]


def test_boolnode_static_requires_required_input_when_port_defined(node_ctor, monkeypatch):
    """Static analysis: missing required input triggers NodeValidationError when ports exist."""
    node = node_ctor("BoolNode", id="b-missing-port", value=True)

    def fake_port_def(_self=None):
        from server.interpreter.nodes.base_node import InPort

        return [InPort(name="input", description="required", accept=Pattern(types={Schema.Type.BOOL}))], []

    monkeypatch.setattr(type(node), "port_def", fake_port_def)
    with pytest.raises(NodeValidationError):
        node.infer_schema({})


def test_boolnode_execute_emits_true(node_ctor):
    """Execute stage: emits True payload matching schema."""
    node = node_ctor("BoolNode", id="b-exec-true", value=True)
    node.infer_schema({})
    outputs = node.execute({})
    assert outputs == {"const": Data(payload=True)}


def test_boolnode_execute_emits_false(node_ctor):
    """Execute stage: emits False payload matching schema."""
    node = node_ctor("BoolNode", id="b-exec-false", value=False)
    node.infer_schema({})
    outputs = node.execute({})
    assert outputs == {"const": Data(payload=False)}


def test_boolnode_execute_requires_inferred_schema(node_ctor):
    """Execute stage: running without prior inference raises an error."""
    node = node_ctor("BoolNode", id="b-no-infer", value=True)
    with pytest.raises(NodeExecutionError):
        node.execute({})


def test_boolnode_execute_rejects_unexpected_input(node_ctor):
    """Execute stage: runtime input mismatches inferred schema."""
    node = node_ctor("BoolNode", id="b-extra-runtime", value=True)
    node.infer_schema({})
    with pytest.raises(NodeExecutionError):
        node.execute({"extra": Data(payload=True)})


def test_boolnode_execute_rejects_mismatched_output_schema(node_ctor):
    """Execute stage: tampered cached schema triggers mismatch error."""
    node = node_ctor("BoolNode", id="b-out-mismatch", value=True)
    node.infer_schema({})
    node._schemas_out = {"const": Schema(type=Schema.Type.INT)}  # type: ignore[attr-defined]
    with pytest.raises(NodeExecutionError):
        node.execute({})
