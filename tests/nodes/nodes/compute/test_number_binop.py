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


def test_numberbinop_hint_empty():
    """Hint stage: no hints expected for NumberBinOpNode."""
    assert BaseNode.get_hint("NumberBinOpNode", {}, {}) == {}


def test_numberbinop_hint_with_inputs():
    """Hint stage success: still returns empty hint for primitive inputs."""
    hint = BaseNode.get_hint("NumberBinOpNode", {"x": Schema(type=Schema.Type.INT), "y": Schema(type=Schema.Type.INT)}, {})
    assert hint == {}


def test_numberbinop_hint_failure_missing_key():
    """Hint stage failure: assert missing expected key triggers assertion (negative test)."""
    with pytest.raises(AssertionError):
        hint = BaseNode.get_hint("NumberBinOpNode", {"x": Schema(type=Schema.Type.INT), "y": Schema(type=Schema.Type.INT)}, {})
        assert "op_choices" in hint


def test_numberbinop_hint_failure_bad_input_shape():
    """Hint stage failure: wrong input schema shape should not produce expected hint."""
    # pass a valid Schema but unexpected port name; hint should be empty
    hint = BaseNode.get_hint("NumberBinOpNode", {"only": Schema(type=Schema.Type.INT)}, {})
    assert hint == {}


def test_numberbinop_hint_failure_nonexistent_type():
    """Hint stage failure: requesting hint for nonexistent node type raises ValueError."""
    with pytest.raises(ValueError):
        from server.interpreter.nodes.base_node import BaseNode
        BaseNode.get_hint("NoSuchNode", {}, {})


def test_numberbinop_construct_accepts_op(node_ctor):
    """Construct stage: valid op literal allowed."""
    node = node_ctor("NumberBinOpNode", id="nb1", op="ADD")
    assert node.op == "ADD"


def test_numberbinop_construct_accepts_other_op(node_ctor):
    """Construct stage success: another valid op is accepted."""
    node = node_ctor("NumberBinOpNode", id="nb2", op="POW")
    assert node.op == "POW"


def test_numberbinop_construct_rejects_missing_op(node_ctor):
    """Construct stage failure: missing op should raise ValidationError."""
    with pytest.raises(ValidationError):
        node_ctor("NumberBinOpNode", id="nb-missing")


def test_numberbinop_construct_rejects_blank_id(node_ctor):
    """Construct stage failure: blank id triggers NodeParameterError."""
    with pytest.raises(NodeParameterError):
        node_ctor("NumberBinOpNode", id="   ", op="ADD")


def test_numberbinop_construct_rejects_invalid_op_literal(node_ctor):
    """Construct stage failure: invalid literal causes ValidationError."""
    with pytest.raises(ValidationError):
        node_ctor("NumberBinOpNode", id="nb-bad", op="XYZ")


def test_numberbinop_construct_rejects_invalid_op(node_ctor):
    """Construct stage: invalid op literal causes ValidationError."""
    with pytest.raises(ValidationError):
        node_ctor("NumberBinOpNode", id="nb-bad", op="XYZ")



def test_numberbinop_static_infers_int_result(node_ctor):
    """Static analysis: same int types produce int result for non-div/pow ops."""
    node = node_ctor("NumberBinOpNode", id="nb-int", op="ADD")
    out = node.infer_schema({"x": Schema(type=Schema.Type.INT), "y": Schema(type=Schema.Type.INT)})
    assert out == {"result": Schema(type=Schema.Type.INT)}


def test_numberbinop_static_infers_float_for_div(node_ctor):
    """Static analysis success: DIV returns float schema."""
    node = node_ctor("NumberBinOpNode", id="nb-div-schem", op="DIV")
    out = node.infer_schema({"x": Schema(type=Schema.Type.FLOAT), "y": Schema(type=Schema.Type.FLOAT)})
    assert out == {"result": Schema(type=Schema.Type.FLOAT)}


def test_numberbinop_static_rejects_mismatch_types(node_ctor):
    """Static analysis failure: mismatched input types raise NodeValidationError."""
    node = node_ctor("NumberBinOpNode", id="nb-mismatch", op="ADD")
    with pytest.raises(NodeValidationError):
        node.infer_schema({"x": Schema(type=Schema.Type.INT), "y": Schema(type=Schema.Type.FLOAT)})


def test_numberbinop_static_rejects_missing_port(node_ctor):
    """Static analysis failure: missing required port raises NodeValidationError."""
    node = node_ctor("NumberBinOpNode", id="nb-missport", op="ADD")
    with pytest.raises(NodeValidationError):
        node.infer_schema({"x": Schema(type=Schema.Type.INT)})


def test_numberbinop_static_rejects_extra_port(node_ctor):
    """Static analysis failure: extra input port causes ValueError."""
    node = node_ctor("NumberBinOpNode", id="nb-extraport", op="ADD")
    with pytest.raises(ValueError):
        node.infer_schema({"x": Schema(type=Schema.Type.INT), "y": Schema(type=Schema.Type.INT), "z": Schema(type=Schema.Type.INT)})


def test_numberbinop_static_requires_matching_types(node_ctor):
    """Static analysis: mismatched input types raise NodeValidationError."""
    node = node_ctor("NumberBinOpNode", id="nb-mismatch", op="ADD")
    with pytest.raises(NodeValidationError):
        node.infer_schema({"x": Schema(type=Schema.Type.INT), "y": Schema(type=Schema.Type.FLOAT)})


def test_numberbinop_execute_add(node_ctor):
    """Execute stage: performs ADD correctly for ints."""
    node = node_ctor("NumberBinOpNode", id="nb-exec", op="ADD")
    node.infer_schema({"x": Schema(type=Schema.Type.INT), "y": Schema(type=Schema.Type.INT)})
    out = node.process({"x": Data(payload=2), "y": Data(payload=3)})
    assert out == {"result": Data(payload=5)}


def test_numberbinop_execute_mul(node_ctor):
    """Execute success: MUL works for ints."""
    node = node_ctor("NumberBinOpNode", id="nb-mul", op="MUL")
    node.infer_schema({"x": Schema(type=Schema.Type.INT), "y": Schema(type=Schema.Type.INT)})
    out = node.process({"x": Data(payload=4), "y": Data(payload=3)})
    assert out["result"].payload == 12



def test_numberbinop_execute_type_mismatch_runtime(node_ctor):
    """Execute failure: runtime data type mismatch triggers NodeExecutionError via execute()."""
    node = node_ctor("NumberBinOpNode", id="nb-runtime-mismatch", op="ADD")
    node.infer_schema({"x": Schema(type=Schema.Type.INT), "y": Schema(type=Schema.Type.INT)})
    # pass float in Data to mismatch expected INT schema
    with pytest.raises(NodeExecutionError):
        node.execute({"x": Data(payload=1), "y": Data(payload=2.5)})


def test_numberbinop_execute_unsupported_op(node_ctor):
    """Execute failure: unsupported op should raise NodeExecutionError at runtime if reached."""
    # construct via direct creation to force unsupported op
    with pytest.raises(ValidationError):
        node_ctor("NumberBinOpNode", id="nb-unsupported", op="BADOP")


def test_numberbinop_execute_div_by_zero(node_ctor):
    """Execute stage: division by zero raises NodeExecutionError."""
    node = node_ctor("NumberBinOpNode", id="nb-div", op="DIV")
    node.infer_schema({"x": Schema(type=Schema.Type.FLOAT), "y": Schema(type=Schema.Type.FLOAT)})
    with pytest.raises(NodeExecutionError):
        node.process({"x": Data(payload=1.0), "y": Data(payload=0.0)})


def test_numberbinop_execute_pow_returns_float(node_ctor):
    """Execute stage: POW returns float result."""
    node = node_ctor("NumberBinOpNode", id="nb-pow", op="POW")
    node.infer_schema({"x": Schema(type=Schema.Type.INT), "y": Schema(type=Schema.Type.INT)})
    out = node.process({"x": Data(payload=2), "y": Data(payload=3)})
    assert isinstance(out["result"].payload, float)
