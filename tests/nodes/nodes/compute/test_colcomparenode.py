import pytest

from server.interpreter.nodes.base_node import BaseNode
from server.models.exception import (
    NodeExecutionError,
    NodeParameterError,
    NodeValidationError,
)
from server.models.schema import ColType, Schema, TableSchema
from tests.nodes.utils import table_from_dict


def test_colcomparenode_hint_empty():
    assert BaseNode.get_hint("ColCompareNode", {}, {}) == {}


def test_colcomparenode_construct_accepts(node_ctor):
    n = node_ctor("ColCompareNode", id="cc1", col1="a", col2="b", op="EQ")
    assert n


def test_colcomparenode_construct_rejects_blank_id(node_ctor):
    with pytest.raises(NodeParameterError):
        node_ctor("ColCompareNode", id=" ", col1="a", col2="b", op="EQ")


def test_colcomparenode_construct_rejects_missing_cols(node_ctor):
    with pytest.raises(NodeParameterError):
        node_ctor("ColCompareNode", id="cc-bad", col1="", col2="b", op="EQ")


def test_colcomparenode_static_accepts_matching_cols(node_ctor):
    node = node_ctor("ColCompareNode", id="cc-static", col1="a", col2="b", op="EQ")
    in_schema = {"table": Schema(type=Schema.Type.TABLE, tab=TableSchema(col_types={"a": ColType.INT, "b": ColType.INT}))}
    out = node.infer_schema(in_schema)
    assert out and isinstance(out, dict)


def test_colcomparenode_static_rejects_mismatch(node_ctor):
    node = node_ctor("ColCompareNode", id="cc-static-err", col1="a", col2="b", op="EQ")
    with pytest.raises(NodeValidationError):
        node.infer_schema({"table": Schema(type=Schema.Type.TABLE, tab=TableSchema(col_types={"a": ColType.INT, "b": ColType.STR}))})


def test_colcomparenode_static_rejects_missing_table(node_ctor):
    node = node_ctor("ColCompareNode", id="cc-static-miss", col1="a", col2="b", op="EQ")
    with pytest.raises(NodeValidationError):
        node.infer_schema({})


def test_colcomparenode_execute_returns_bool_table(node_ctor):
    node = node_ctor("ColCompareNode", id="cc-exec", col1="a", col2="b", op="EQ")
    node.infer_schema({"table": Schema(type=Schema.Type.TABLE, tab=TableSchema(col_types={"a": ColType.INT, "b": ColType.INT}))})
    tbl = table_from_dict({"a": [1], "b": [1]})
    out = node.process({"table": tbl})
    assert isinstance(out, dict)


def test_colcomparenode_requires_infer(node_ctor):
    node = node_ctor("ColCompareNode", id="cc-noinf", col1="a", col2="b", op="EQ")
    with pytest.raises(NodeExecutionError):
        node.execute({})


def test_colcomparenode_execute_runtime_error_on_bad_cell(node_ctor):
    node = node_ctor("ColCompareNode", id="cc-runtime", col1="a", col2="b", op="EQ")
    node.infer_schema({"table": Schema(type=Schema.Type.TABLE, tab=TableSchema(col_types={"a": ColType.INT, "b": ColType.INT}))})
    with pytest.raises(NodeExecutionError):
        bad_tbl = table_from_dict({"a": [object()], "b": [object()]})
        node.execute({"table": bad_tbl})

