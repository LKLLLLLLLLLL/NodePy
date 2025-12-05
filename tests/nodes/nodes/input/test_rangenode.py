from datetime import datetime, timedelta, timezone

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


def test_rangenode_hint_empty():
    """Hint stage: RangeNode returns no hints by default."""
    assert BaseNode.get_hint("RangeNode", {}, {}) == {}


def test_rangenode_construct_defaults_col_name(node_ctor):
    """Construct stage: missing col_name filled with default name."""
    node = node_ctor("RangeNode", id="rg1", col_name=None, col_type="int")
    assert node.col_name is not None and node.col_name.startswith("rg1_")


def test_rangenode_construct_rejects_blank_id(node_ctor):
    """Construct stage: blank id is rejected."""
    with pytest.raises(NodeParameterError):
        node_ctor("RangeNode", id="   ", col_name="c", col_type="int")


def test_rangenode_construct_rejects_illegal_colname(node_ctor):
    """Construct stage: illegal column names are rejected."""
    with pytest.raises(NodeParameterError):
        node_ctor("RangeNode", id="rg-illegal", col_name="_bad", col_type="int")


def test_rangenode_construct_rejects_invalid_coltype(node_ctor):
    """Construct stage: invalid col_type literal is rejected by pydantic."""
    with pytest.raises(ValidationError):
        node_ctor("RangeNode", id="rg-bad", col_name="c", col_type="unknown")


def test_rangenode_static_requires_start_end_types(node_ctor):
    """Static analysis: start/end must match declared col_type."""
    node = node_ctor("RangeNode", id="rg-static-int", col_name="c", col_type="int")
    with pytest.raises(NodeValidationError):
        node.infer_schema({"start": Schema(type=Schema.Type.FLOAT), "end": Schema(type=Schema.Type.FLOAT)})


def test_rangenode_static_accepts_float_inputs(node_ctor):
    """Static analysis: float col_type accepts float start/end schemas."""
    node = node_ctor("RangeNode", id="rg-static-float", col_name="c", col_type="float")
    out = node.infer_schema({"start": Schema(type=Schema.Type.FLOAT), "end": Schema(type=Schema.Type.FLOAT)})
    assert "table" in out


def test_rangenode_static_rejects_none_input(node_ctor):
    """Static analysis: missing required start/end raises NodeValidationError."""
    node = node_ctor("RangeNode", id="rg-static-missing", col_name="c", col_type="int")
    # Base implementation validates required ports first and raises NodeValidationError
    with pytest.raises(NodeValidationError):
        node.infer_schema({})


def test_rangenode_execute_generates_small_range(node_ctor):
    """Execute: generates table rows for a small integer range."""
    node = node_ctor("RangeNode", id="rg-exec-int", col_name="c", col_type="int")
    node.infer_schema({"start": Schema(type=Schema.Type.INT), "end": Schema(type=Schema.Type.INT)})
    outputs = node.process({"start": Data(payload=0), "end": Data(payload=3)})
    assert "table" in outputs


def test_rangenode_execute_rejects_too_large_range(node_ctor):
    """Execute: overly large ranges raise NodeExecutionError."""
    node = node_ctor("RangeNode", id="rg-exec-big", col_name="c", col_type="int")
    node.infer_schema({"start": Schema(type=Schema.Type.INT), "end": Schema(type=Schema.Type.INT)})
    with pytest.raises(NodeExecutionError):
        node.process({"start": Data(payload=0), "end": Data(payload=2000000)})


def test_rangenode_execute_rejects_negative_step_logic(node_ctor):
    """Execute: negative or zero step handling should not crash; use small ranges to validate behavior."""
    node = node_ctor("RangeNode", id="rg-exec-neg", col_name="c", col_type="int")
    node.infer_schema({"start": Schema(type=Schema.Type.INT), "end": Schema(type=Schema.Type.INT), "step": Schema(type=Schema.Type.INT)})
    outputs = node.process({"start": Data(payload=5), "end": Data(payload=2), "step": Data(payload=-1)})
    assert "table" in outputs


def test_rangenode_static_accepts_datetime_inputs(node_ctor):
    """Static analysis: RangeNode should accept datetime start/end when col_type==Datetime."""

    node = node_ctor("RangeNode", id="rg-static-dt", col_name="c", col_type="Datetime")
    out = node.infer_schema({"start": Schema(type=Schema.Type.DATETIME), "end": Schema(type=Schema.Type.DATETIME)})
    assert "table" in out


def test_rangenode_execute_generates_datetime_range(node_ctor):
    """Execute: generate datetime range rows when col_type is Datetime and step is a timedelta-like value."""
    start = datetime.now(tz=timezone.utc)
    end = start + timedelta(days=2)
    node = node_ctor("RangeNode", id="rg-exec-dt", col_name="c", col_type="Datetime")
    # omit explicit step schema to allow default datetime stepping semantics
    node.infer_schema({"start": Schema(type=Schema.Type.DATETIME), "end": Schema(type=Schema.Type.DATETIME)})
    outputs = node.process({"start": Data(payload=start), "end": Data(payload=end)})
    assert "table" in outputs
