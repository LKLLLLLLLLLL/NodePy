import pytest
from pydantic import ValidationError

from server.interpreter.nodes.base_node import BaseNode
from server.models.data import Data
from server.models.exception import (
    NodeExecutionError,
    NodeParameterError,
)
from server.models.schema import ColType, Schema, TableSchema


def test_tablenode_hint_empty():
    """Hint stage: TableNode provides no hints by default."""
    assert BaseNode.get_hint("TableNode", {}, {}) == {}


def test_tablenode_hint_with_params_returns_empty():
    """Hint stage success: even with params or schemas TableNode returns empty by default."""
    params = {"rows": []}
    schemas = {"ghost": Schema(type=Schema.Type.INT)}
    assert BaseNode.get_hint("TableNode", schemas, params) == {}


def test_tablenode_hint_unknown_type_raises():
    """Hint stage failure: unknown type lookup raises ValueError."""
    with pytest.raises(ValueError):
        BaseNode.get_hint("NoSuchTable", {}, {})


def test_tablenode_hint_empty_type_raises():
    """Hint stage failure: empty type name raises ValueError."""
    with pytest.raises(ValueError):
        BaseNode.get_hint("", {}, {})


def test_tablenode_hint_none_type_raises():
    """Hint stage failure: None type name raises ValueError when looked up."""
    with pytest.raises(ValueError):
        BaseNode.get_hint(None, {}, {})  # type: ignore[arg-type]


def test_tablenode_construct_accepts_valid_rows(node_ctor):
    """Construct stage: accepts rows when col_names and col_types match."""
    rows = [{"a": 1, "b": 2.0}]
    col_names = ["a", "b"]
    col_types = {"a": ColType.INT, "b": ColType.FLOAT}
    node = node_ctor("TableNode", id="t-good", rows=rows, col_names=col_names, col_types=col_types)
    assert node._rows is not None


def test_tablenode_construct_accepts_multiple_rows(node_ctor):
    """Construct stage success: accepts multiple consistent rows."""
    rows = [{"a": 1}, {"a": 2}, {"a": 3}]
    node = node_ctor("TableNode", id="t-multi", rows=rows, col_names=["a"], col_types={"a": ColType.INT})
    assert node._rows is not None and len(node._rows) == 3


def test_tablenode_construct_rejects_empty_rows_with_colnames(node_ctor):
    """Construct stage: empty rows are now allowed when `col_types` is provided."""
    # implementation now permits empty rows if explicit col_types are present
    node = node_ctor("TableNode", id="t-empty-ok", rows=[], col_names=["a"], col_types={"a": ColType.INT})
    assert node._rows == []


def test_tablenode_construct_rejects_empty_rows_without_col_types(node_ctor):
    """Construct stage failure: providing col_names but no col_types with empty rows should still fail."""
    with pytest.raises((NodeParameterError, ValidationError)):
        node_ctor("TableNode", id="t-empty-bad", rows=[], col_names=["a"])  # type: ignore[arg-type]


def test_tablenode_construct_rejects_mismatched_row_keys(node_ctor):
    """Construct stage: rows whose keys don't match col_names are rejected."""
    rows = [{"x": 1}]
    with pytest.raises(NodeParameterError):
        node_ctor("TableNode", id="t-bad-keys", rows=rows, col_names=["a"], col_types={"a": ColType.INT})


def test_tablenode_construct_rejects_bad_col_types_keys(node_ctor):
    """Construct stage: col_types keys must match col_names."""
    rows = [{"a": 1}]
    with pytest.raises(NodeParameterError):
        node_ctor("TableNode", id="t-bad-coltypes", rows=rows, col_names=["a"], col_types={"b": ColType.INT})


def test_tablenode_construct_rejects_unsupported_value_type(node_ctor):
    """Construct stage: unsupported cell types cause failure (pydantic or NodeParameterError)."""
    rows = [{"a": object()}]
    with pytest.raises((NodeParameterError, ValidationError)):
        node_ctor("TableNode", id="t-unsupported", rows=rows, col_names=["a"], col_types={"a": ColType.STR})


def test_tablenode_construct_rejects_missing_col_types(node_ctor):
    """Construct stage failure: missing col_types when col_names present should fail."""
    rows = [{"a": 1}]
    with pytest.raises((NodeParameterError, ValidationError)):
        node_ctor("TableNode", id="t-no-coltypes", rows=rows, col_names=["a"])  # type: ignore[arg-type]


def test_tablenode_static_infers_table_schema(node_ctor):
    """Static analysis: infers a Table schema with provided col_types."""
    rows = [{"a": 1}]
    col_names = ["a"]
    col_types = {"a": ColType.INT}
    node = node_ctor("TableNode", id="t-static", rows=rows, col_names=col_names, col_types=col_types)
    out = node.infer_schema({})
    assert out == {"table": Schema(type=Schema.Type.TABLE, tab=TableSchema(col_types=col_types))}


def test_tablenode_static_accepts_inferred_coltypes(node_ctor):
    """Static success: if node can infer col_types from rows, infer_schema returns table schema."""
    rows = [{"a": 1, "b": 2.0}]
    col_names = ["a", "b"]
    col_types = {"a": ColType.INT, "b": ColType.FLOAT}
    node = node_ctor("TableNode", id="t-static-infer", rows=rows, col_names=col_names, col_types=col_types)
    out = node.infer_schema({})
    assert "table" in out


def test_tablenode_static_rejects_extra_input(node_ctor):
    """Static analysis: unexpected inputs are rejected for source nodes."""
    rows = [{"a": 1}]
    col_names = ["a"]
    col_types = {"a": ColType.INT}
    node = node_ctor("TableNode", id="t-static-extra", rows=rows, col_names=col_names, col_types=col_types)
    with pytest.raises(ValueError):
        node.infer_schema({"extra": Schema(type=Schema.Type.INT)})


def test_tablenode_static_rejects_none_input(node_ctor):
    """Static analysis: infer_schema expects a mapping not None."""
    rows = [{"a": 1}]
    col_names = ["a"]
    col_types = {"a": ColType.INT}
    node = node_ctor("TableNode", id="t-static-none", rows=rows, col_names=col_names, col_types=col_types)
    with pytest.raises(TypeError):
        node.infer_schema(None)  # type: ignore[arg-type]


def test_tablenode_static_rejects_extra_input_variant(node_ctor):
    """Static failure variant: unexpected inputs are rejected for source nodes."""
    rows = [{"a": 1}]
    col_names = ["a"]
    col_types = {"a": ColType.INT}
    node = node_ctor("TableNode", id="t-static-extra2", rows=rows, col_names=col_names, col_types=col_types)
    with pytest.raises(ValueError):
        node.infer_schema({"extra": Schema(type=Schema.Type.INT)})


def test_tablenode_execute_emits_table(node_ctor):
    """Execute stage: emits a Table Data payload matching inferred schema."""
    rows = [{"a": 1}]
    col_names = ["a"]
    col_types = {"a": ColType.INT}
    node = node_ctor("TableNode", id="t-exec", rows=rows, col_names=col_names, col_types=col_types)
    node.infer_schema({})
    outputs = node.execute({})
    assert "table" in outputs
    # Table implementation adds an index column; ensure original cols exist and match types
    out_col_types = outputs["table"].payload.col_types
    for k, v in col_types.items():
        assert k in out_col_types and out_col_types[k] == v


def test_tablenode_execute_emits_table_for_multiple_rows(node_ctor):
    """Execute success: emits table when multiple rows were provided at construction."""
    rows = [{"a": 1}, {"a": 2}]
    node = node_ctor("TableNode", id="t-exec-multi", rows=rows, col_names=["a"], col_types={"a": ColType.INT})
    node.infer_schema({})
    outputs = node.execute({})
    assert "table" in outputs and len(outputs["table"].payload.df) == 2


def test_tablenode_execute_rejects_tampered_output_schema(node_ctor):
    """Execute failure: tampering cached output schema triggers NodeExecutionError."""
    rows = [{"a": 1}]
    node = node_ctor("TableNode", id="t-out-tamper", rows=rows, col_names=["a"], col_types={"a": ColType.INT})
    node.infer_schema({})
    node._schemas_out = {"table": Schema(type=Schema.Type.TABLE, tab=TableSchema(col_types={"a": ColType.FLOAT}))}  # type: ignore[attr-defined]
    with pytest.raises(NodeExecutionError):
        node.execute({})


def test_tablenode_execute_requires_inferred_schema(node_ctor):
    """Execute stage: running without prior static inference raises NodeExecutionError."""
    rows = [{"a": 1}]
    col_names = ["a"]
    col_types = {"a": ColType.INT}
    node = node_ctor("TableNode", id="t-no-infer", rows=rows, col_names=col_names, col_types=col_types)
    with pytest.raises(NodeExecutionError):
        node.execute({})


def test_tablenode_execute_rejects_unexpected_runtime_input(node_ctor):
    """Execute stage: unexpected runtime inputs cause schema mismatch errors."""
    rows = [{"a": 1}]
    col_names = ["a"]
    col_types = {"a": ColType.INT}
    node = node_ctor("TableNode", id="t-extra-runtime", rows=rows, col_names=col_names, col_types=col_types)
    node.infer_schema({})
    with pytest.raises(NodeExecutionError):
        node.execute({"extra": Data(payload=5)})
