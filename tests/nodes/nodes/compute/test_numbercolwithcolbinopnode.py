import pytest

from server.interpreter.nodes.base_node import BaseNode
from server.models.exception import (
    NodeExecutionError,
    NodeParameterError,
    NodeValidationError,
)
from server.models.schema import ColType, Schema, TableSchema
from tests.nodes.utils import table_from_dict


def test_numbercolwithcolbinop_hint_empty():
    assert BaseNode.get_hint("NumberColWithColBinOpNode", {}, {}) == {}


def test_numbercolwithcolbinop_construct_accepts(node_ctor):
    n = node_ctor("NumberColWithColBinOpNode", id="nc2", op="ADD", col1="a", col2="b", result_col="c")
    assert n


def test_numbercolwithcolbinop_construct_rejects_blank_id(node_ctor):
    with pytest.raises(NodeParameterError):
        node_ctor("NumberColWithColBinOpNode", id="  ", op="ADD", col1="a", col2="b", result_col="c")


def test_numbercolwithcolbinop_construct_rejects_missing_cols(node_ctor):
    with pytest.raises(NodeParameterError):
        node_ctor("NumberColWithColBinOpNode", id="nc-bad", op="ADD", col1="", col2="b", result_col="c")


def test_numbercolwithcolbinop_static_accepts_matching_number_cols(node_ctor):
    node = node_ctor("NumberColWithColBinOpNode", id="nc-static", op="ADD", col1="a", col2="b", result_col="c")
    in_schema = {"table": Schema(type=Schema.Type.TABLE, tab=TableSchema(col_types={"a": ColType.INT, "b": ColType.INT}))}
    out = node.infer_schema(in_schema)
    assert out and isinstance(out, dict)


def test_numbercolwithcolbinop_static_rejects_mismatch(node_ctor):
    node = node_ctor("NumberColWithColBinOpNode", id="nc-static-err", op="ADD", col1="a", col2="b", result_col="c")
    with pytest.raises(NodeValidationError):
        node.infer_schema({"table": Schema(type=Schema.Type.TABLE, tab=TableSchema(col_types={"a": ColType.INT, "b": ColType.STR}))})


def test_numbercolwithcolbinop_static_rejects_missing_table(node_ctor):
    node = node_ctor("NumberColWithColBinOpNode", id="nc-static-miss", op="ADD", col1="a", col2="b", result_col="c")
    with pytest.raises(NodeValidationError):
        node.infer_schema({})


def test_numbercolwithcolbinop_execute_computes(node_ctor):
    node = node_ctor("NumberColWithColBinOpNode", id="nc-exec", op="ADD", col1="a", col2="b", result_col="c")
    node.infer_schema({"table": Schema(type=Schema.Type.TABLE, tab=TableSchema(col_types={"a": ColType.INT, "b": ColType.INT}))})
    tbl = table_from_dict({"a": [1], "b": [2]})
    out = node.process({"table": tbl})
    assert isinstance(out, dict)


def test_numbercolwithcolbinop_requires_infer(node_ctor):
    node = node_ctor("NumberColWithColBinOpNode", id="nc-noinf", op="ADD", col1="a", col2="b", result_col="c")
    with pytest.raises(NodeExecutionError):
        node.execute({})


def test_numbercolwithcolbinop_execute_runtime_error_on_bad_cell(node_ctor):
    node = node_ctor("NumberColWithColBinOpNode", id="nc-runtime", op="ADD", col1="a", col2="b", result_col="c")
    node.infer_schema({"table": Schema(type=Schema.Type.TABLE, tab=TableSchema(col_types={"a": ColType.INT, "b": ColType.INT}))})
    with pytest.raises(NodeExecutionError):
        bad_tbl = table_from_dict({"a": [object()], "b": [object()]})
        node.execute({"table": bad_tbl})

