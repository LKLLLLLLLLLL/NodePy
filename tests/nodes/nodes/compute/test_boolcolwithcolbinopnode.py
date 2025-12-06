import pytest

from server.interpreter.nodes.base_node import BaseNode
from server.models.exception import (
    NodeExecutionError,
    NodeParameterError,
    NodeValidationError,
)
from server.models.schema import ColType, Schema, TableSchema
from tests.nodes.utils import table_from_dict


def test_boolcolwithcolbinop_hint_empty():
    assert BaseNode.get_hint("BoolColWithColBinOpNode", {}, {}) == {}


def test_boolcolwithcolbinop_construct_accepts(node_ctor):
    n = node_ctor("BoolColWithColBinOpNode", id="bc2", op="AND", col1="a", col2="b", result_col="c")
    assert n


def test_boolcolwithcolbinop_construct_rejects_blank_id(node_ctor):
    with pytest.raises(NodeParameterError):
        node_ctor("BoolColWithColBinOpNode", id="  ", op="AND", col1="a", col2="b", result_col="c")


def test_boolcolwithcolbinop_construct_rejects_missing_cols(node_ctor):
    with pytest.raises(NodeParameterError):
        node_ctor("BoolColWithColBinOpNode", id="bc-bad", op="AND", col1="", col2="b", result_col="c")


def test_boolcolwithcolbinop_static_accepts_matching_bool_cols(node_ctor):
    node = node_ctor("BoolColWithColBinOpNode", id="bc-static", op="AND", col1="a", col2="b", result_col="c")
    in_schema = {"table": Schema(type=Schema.Type.TABLE, tab=TableSchema(col_types={"a": ColType.BOOL, "b": ColType.BOOL}))}
    out = node.infer_schema(in_schema)
    assert out and isinstance(out, dict)


def test_boolcolwithcolbinop_static_rejects_mismatch(node_ctor):
    node = node_ctor("BoolColWithColBinOpNode", id="bc-static-err", op="AND", col1="a", col2="b", result_col="c")
    with pytest.raises(NodeValidationError):
        node.infer_schema({"table": Schema(type=Schema.Type.TABLE, tab=TableSchema(col_types={"a": ColType.BOOL, "b": ColType.INT}))})


def test_boolcolwithcolbinop_static_rejects_missing_table(node_ctor):
    node = node_ctor("BoolColWithColBinOpNode", id="bc-static-miss", op="AND", col1="a", col2="b", result_col="c")
    with pytest.raises(NodeValidationError):
        node.infer_schema({})


def test_boolcolwithcolbinop_execute_computes(node_ctor):
    node = node_ctor("BoolColWithColBinOpNode", id="bc-exec", op="AND", col1="a", col2="b", result_col="c")
    node.infer_schema({"table": Schema(type=Schema.Type.TABLE, tab=TableSchema(col_types={"a": ColType.BOOL, "b": ColType.BOOL}))})
    tbl = table_from_dict({"a": [True], "b": [False]})
    out = node.process({"table": tbl})
    assert isinstance(out, dict)


def test_boolcolwithcolbinop_requires_infer(node_ctor):
    node = node_ctor("BoolColWithColBinOpNode", id="bc-noinf", op="AND", col1="a", col2="b", result_col="c")
    with pytest.raises(NodeExecutionError):
        node.execute({})


def test_boolcolwithcolbinop_execute_runtime_error_on_bad_cell(node_ctor):
    node = node_ctor("BoolColWithColBinOpNode", id="bc-runtime", op="AND", col1="a", col2="b", result_col="c")
    node.infer_schema({"table": Schema(type=Schema.Type.TABLE, tab=TableSchema(col_types={"a": ColType.BOOL, "b": ColType.BOOL}))})
    with pytest.raises(NodeExecutionError):
        bad_tbl = table_from_dict({"a": [object()], "b": [object()]})
        node.execute({"table": bad_tbl})

