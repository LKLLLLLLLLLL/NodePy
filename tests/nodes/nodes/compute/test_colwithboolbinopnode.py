import pytest

from server.interpreter.nodes.base_node import BaseNode
from server.models.data import Data
from server.models.exception import (
    NodeExecutionError,
    NodeParameterError,
    NodeValidationError,
)
from server.models.schema import ColType, Schema, TableSchema
from tests.nodes.utils import table_from_dict


def test_colwithboolbinop_hint_empty():
    assert BaseNode.get_hint("ColWithBoolBinOpNode", {}, {}) == {}


def test_colwithboolbinop_construct_accepts(node_ctor):
    n = node_ctor("ColWithBoolBinOpNode", id="cb1", op="AND", col="a")
    assert n


def test_colwithboolbinop_construct_rejects_blank_id(node_ctor):
    with pytest.raises(NodeParameterError):
        node_ctor("ColWithBoolBinOpNode", id="  ", op="AND", col="a")


def test_colwithboolbinop_construct_rejects_bad_col(node_ctor):
    with pytest.raises(NodeParameterError):
        node_ctor("ColWithBoolBinOpNode", id="cb-bad", op="AND", col="")


def test_colwithboolbinop_static_accepts_bool_col(node_ctor):
    node = node_ctor("ColWithBoolBinOpNode", id="cb-static", op="AND", col="a")
    in_schema = {"table": Schema(type=Schema.Type.TABLE, tab=TableSchema(col_types={"a": ColType.BOOL})), "bool": Schema(type=Schema.Type.BOOL)}
    out = node.infer_schema(in_schema)
    assert out and isinstance(out, dict)


def test_colwithboolbinop_static_rejects_nonbool(node_ctor):
    node = node_ctor("ColWithBoolBinOpNode", id="cb-static-err", op="AND", col="a")
    with pytest.raises(NodeValidationError):
        node.infer_schema({"table": Schema(type=Schema.Type.TABLE, tab=TableSchema(col_types={"a": ColType.INT})), "bool": Schema(type=Schema.Type.BOOL)})


def test_colwithboolbinop_static_rejects_missing_table(node_ctor):
    node = node_ctor("ColWithBoolBinOpNode", id="cb-static-miss", op="AND", col="a")
    with pytest.raises(NodeValidationError):
        node.infer_schema({})


def test_colwithboolbinop_execute_computes(node_ctor):
    node = node_ctor("ColWithBoolBinOpNode", id="cb-exec", op="AND", col="a")
    node.infer_schema({"table": Schema(type=Schema.Type.TABLE, tab=TableSchema(col_types={"a": ColType.BOOL})), "bool": Schema(type=Schema.Type.BOOL)})
    tbl = table_from_dict({"a": [True]})
    out = node.process({"table": tbl, "bool": Data(payload=True)})
    assert isinstance(out, dict)


def test_colwithboolbinop_requires_infer(node_ctor):
    node = node_ctor("ColWithBoolBinOpNode", id="cb-noinf", op="AND", col="a")
    with pytest.raises(NodeExecutionError):
        node.execute({})


def test_colwithboolbinop_execute_runtime_error_on_bad_cell(node_ctor):
    node = node_ctor("ColWithBoolBinOpNode", id="cb-runtime", op="AND", col="a")
    node.infer_schema({"table": Schema(type=Schema.Type.TABLE, tab=TableSchema(col_types={"a": ColType.BOOL})), "bool": Schema(type=Schema.Type.BOOL)})
    with pytest.raises(NodeExecutionError):
        bad_tbl = table_from_dict({"a": [object()]})
        node.execute({"table": bad_tbl, "bool": Data(payload=True)})

