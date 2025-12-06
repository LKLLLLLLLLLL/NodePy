import pytest

from server.interpreter.nodes.base_node import BaseNode
from server.models.exception import (
    NodeExecutionError,
    NodeParameterError,
    NodeValidationError,
)
from server.models.schema import ColType, Schema, TableSchema
from tests.nodes.utils import table_from_dict


def test_boolcolunaryop_hint_empty():
    assert BaseNode.get_hint("BoolColUnaryOpNode", {}, {}) == {}


def test_boolcolunaryop_construct_accepts(node_ctor):
    n = node_ctor("BoolColUnaryOpNode", id="bc1", op="NOT", col="flag")
    assert n


def test_boolcolunaryop_construct_rejects_blank_id(node_ctor):
    with pytest.raises(NodeParameterError):
        node_ctor("BoolColUnaryOpNode", id=" ", op="NOT", col="flag")


def test_boolcolunaryop_construct_rejects_empty_col(node_ctor):
    with pytest.raises(NodeParameterError):
        node_ctor("BoolColUnaryOpNode", id="bc-bad", op="NOT", col="")


def test_boolcolunaryop_static_accepts_bool_col(node_ctor):
    node = node_ctor("BoolColUnaryOpNode", id="bc-static", op="NOT", col="flag")
    in_schema = {"table": Schema(type=Schema.Type.TABLE, tab=TableSchema(col_types={"flag": ColType.BOOL}))}
    out = node.infer_schema(in_schema)
    assert out and isinstance(out, dict)


def test_boolcolunaryop_static_rejects_nonbool(node_ctor):
    node = node_ctor("BoolColUnaryOpNode", id="bc-static-err", op="NOT", col="flag")
    with pytest.raises(NodeValidationError):
        node.infer_schema({"table": Schema(type=Schema.Type.TABLE, tab=TableSchema(col_types={"flag": ColType.INT}))})


def test_boolcolunaryop_static_rejects_missing_table(node_ctor):
    node = node_ctor("BoolColUnaryOpNode", id="bc-static-miss", op="NOT", col="flag")
    with pytest.raises(NodeValidationError):
        node.infer_schema({})


def test_boolcolunaryop_execute_negate(node_ctor):
    node = node_ctor("BoolColUnaryOpNode", id="bc-exec", op="NOT", col="flag")
    node.infer_schema({"table": Schema(type=Schema.Type.TABLE, tab=TableSchema(col_types={"flag": ColType.BOOL}))})
    tbl = table_from_dict({"flag": [True]})
    out = node.process({"table": tbl})
    assert isinstance(out, dict)


def test_boolcolunaryop_execute_requires_infer(node_ctor):
    node = node_ctor("BoolColUnaryOpNode", id="bc-noinf", op="NOT", col="flag")
    with pytest.raises(NodeExecutionError):
        node.execute({})


def test_boolcolunaryop_execute_runtime_error_on_bad_cell(node_ctor):
    node = node_ctor("BoolColUnaryOpNode", id="bc-runtime", op="NOT", col="flag")
    node.infer_schema({"table": Schema(type=Schema.Type.TABLE, tab=TableSchema(col_types={"flag": ColType.BOOL}))})
    with pytest.raises(NodeExecutionError):
        bad_tbl = table_from_dict({"flag": [object()]})
        node.execute({"table": bad_tbl})

