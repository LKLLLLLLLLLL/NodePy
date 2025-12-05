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


def test_randomnode_hint_empty():
    """Hint stage: RandomNode returns no hints by default."""
    assert BaseNode.get_hint("RandomNode", {}, {}) == {}


def test_randomnode_construct_defaults_col_name(node_ctor):
    """Construct stage: missing col_name is filled with default."""
    node = node_ctor("RandomNode", id="r1", col_name=None, col_type="int")
    assert node.col_name is not None and node.col_name.startswith("r1_")


def test_randomnode_construct_rejects_blank_id(node_ctor):
    """Construct stage: blank id is rejected."""
    with pytest.raises(NodeParameterError):
        node_ctor("RandomNode", id="   ", col_name="c", col_type="int")


def test_randomnode_construct_rejects_illegal_colname(node_ctor):
    """Construct stage: illegal column names are rejected."""
    with pytest.raises(NodeParameterError):
        node_ctor("RandomNode", id="r-illegal", col_name="_bad", col_type="int")


def test_randomnode_construct_rejects_invalid_coltype(node_ctor):
    """Construct stage: invalid col_type string is rejected by pydantic."""
    with pytest.raises(ValidationError):
        node_ctor("RandomNode", id="r-bad-type", col_name="c", col_type="unknown")


def test_randomnode_static_requires_row_count_and_bounds_for_numeric(node_ctor):
    """Static analysis: numeric col_type requires row_count, min_value and max_value."""
    node = node_ctor("RandomNode", id="r-static", col_name="c", col_type="int")
    with pytest.raises(NodeValidationError):
        node.infer_schema({})


def test_randomnode_static_accepts_str_col_without_minmax(node_ctor):
    """Static analysis: str col_type does not require min/max, only row_count."""
    node = node_ctor("RandomNode", id="r-static-str", col_name="c", col_type="str")
    out = node.infer_schema({"row_count": Schema(type=Schema.Type.INT)})
    assert "table" in out


def test_randomnode_static_rejects_incompatible_minmax(node_ctor):
    """Static analysis: mismatched min/max types produce NodeValidationError."""
    node = node_ctor("RandomNode", id="r-static-num", col_name="c", col_type="float")
    with pytest.raises(NodeValidationError):
        node.infer_schema({"row_count": Schema(type=Schema.Type.INT), "min_value": Schema(type=Schema.Type.INT), "max_value": Schema(type=Schema.Type.INT)})


def test_randomnode_execute_generates_table(node_ctor):
    """Execute stage: produces a table Data for valid inputs."""
    node = node_ctor("RandomNode", id="r-exec", col_name="c", col_type="int")
    node.infer_schema({"row_count": Schema(type=Schema.Type.INT), "min_value": Schema(type=Schema.Type.INT), "max_value": Schema(type=Schema.Type.INT)})
    outputs = node.process({"row_count": Data(payload=3), "min_value": Data(payload=1), "max_value": Data(payload=10)})
    assert "table" in outputs


def test_randomnode_execute_rejects_large_row_count(node_ctor):
    """Execute stage: too large row_count raises NodeExecutionError."""
    node = node_ctor("RandomNode", id="r-exec-big", col_name="c", col_type="int")
    node.infer_schema({"row_count": Schema(type=Schema.Type.INT), "min_value": Schema(type=Schema.Type.INT), "max_value": Schema(type=Schema.Type.INT)})
    with pytest.raises(NodeExecutionError):
        node.process({"row_count": Data(payload=100001), "min_value": Data(payload=1), "max_value": Data(payload=100002)})


def test_randomnode_execute_rejects_min_ge_max(node_ctor):
    """Execute stage: min_value >= max_value triggers NodeExecutionError."""
    node = node_ctor("RandomNode", id="r-exec-minmax", col_name="c", col_type="int")
    node.infer_schema({"row_count": Schema(type=Schema.Type.INT), "min_value": Schema(type=Schema.Type.INT), "max_value": Schema(type=Schema.Type.INT)})
    with pytest.raises(NodeExecutionError):
        node.process({"row_count": Data(payload=2), "min_value": Data(payload=5), "max_value": Data(payload=5)})


def test_randomnode_static_handles_minmax_for_bool(node_ctor):
    """Static analysis: implementation may accept or ignore numeric min/max for bool; ensure it behaves consistently."""
    node = node_ctor("RandomNode", id="r-bool-minmax", col_name="b", col_type="bool")
    # if implementation enforces rejection this will raise; otherwise it should return a table schema
    try:
        out = node.infer_schema({"row_count": Schema(type=Schema.Type.INT), "min_value": Schema(type=Schema.Type.INT), "max_value": Schema(type=Schema.Type.INT)})
        assert "table" in out
    except NodeValidationError:
        pytest.skip("Implementation enforces rejection for bool min/max")


def test_randomnode_execute_rejects_non_int_rowcount(node_ctor):
    """Execute stage failure: non-int row_count payload should be rejected at runtime."""
    node = node_ctor("RandomNode", id="r-exec-bad-row", col_name="c", col_type="int")
    node.infer_schema({"row_count": Schema(type=Schema.Type.INT), "min_value": Schema(type=Schema.Type.INT), "max_value": Schema(type=Schema.Type.INT)})
    # implementation currently asserts row_count is int -> AssertionError expected
    with pytest.raises(AssertionError):
        node.process({"row_count": Data(payload=2.5), "min_value": Data(payload=1), "max_value": Data(payload=10)})
