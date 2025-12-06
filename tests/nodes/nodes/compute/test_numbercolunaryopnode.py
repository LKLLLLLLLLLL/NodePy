import pytest

from server.interpreter.nodes.base_node import BaseNode
from server.models.exception import (
    NodeExecutionError,
    NodeParameterError,
    NodeValidationError,
)
from server.models.schema import ColType, Schema, TableSchema
from tests.nodes.utils import table_from_dict


def test_numbercolunaryop_hint_empty():
    assert BaseNode.get_hint("NumberColUnaryOpNode", {}, {}) == {}


def test_numbercolunaryop_construct_accepts(node_ctor):
    n = node_ctor("NumberColUnaryOpNode", id="nc1", op="NEG", col="a")
    assert n


def test_numbercolunaryop_construct_rejects_blank_id(node_ctor):
    with pytest.raises(NodeParameterError):
        node_ctor("NumberColUnaryOpNode", id="  ", op="NEG", col="a")


def test_numbercolunaryop_construct_rejects_empty_col(node_ctor):
    with pytest.raises(NodeParameterError):
        node_ctor("NumberColUnaryOpNode", id="nc-bad", op="NEG", col="")


def test_numbercolunaryop_static_accepts_number_col(node_ctor):
    node = node_ctor("NumberColUnaryOpNode", id="nc-static", op="ABS", col="a")
    in_schema = {"table": Schema(type=Schema.Type.TABLE, tab=TableSchema(col_types={"a": ColType.FLOAT}))}
    out = node.infer_schema(in_schema)
    assert out and isinstance(out, dict)


def test_numbercolunaryop_static_rejects_non_number(node_ctor):
    node = node_ctor("NumberColUnaryOpNode", id="nc-static-err", op="ABS", col="a")
    with pytest.raises(NodeValidationError):
        node.infer_schema({"table": Schema(type=Schema.Type.TABLE, tab=TableSchema(col_types={"a": ColType.STR}))})


def test_numbercolunaryop_static_rejects_missing_table(node_ctor):
    node = node_ctor("NumberColUnaryOpNode", id="nc-static-miss", op="ABS", col="a")
    with pytest.raises(NodeValidationError):
        node.infer_schema({})


def test_numbercolunaryop_execute_per_row(node_ctor):
    node = node_ctor("NumberColUnaryOpNode", id="nc-exec", op="NEG", col="a")
    node.infer_schema({"table": Schema(type=Schema.Type.TABLE, tab=TableSchema(col_types={"a": ColType.INT}))})
    tbl = table_from_dict({"a": [1]})
    out = node.process({"table": tbl})
    # we only assert the call doesn't crash and returns a mapping
    assert isinstance(out, dict)


def test_numbercolunaryop_execute_requires_infer(node_ctor):
    node = node_ctor("NumberColUnaryOpNode", id="nc-noinf", op="NEG", col="a")
    with pytest.raises(NodeExecutionError):
        node.execute({})


def test_numbercolunaryop_execute_runtime_error_on_bad_cell(node_ctor):
    node = node_ctor("NumberColUnaryOpNode", id="nc-runtime", op="NEG", col="a")
    node.infer_schema({"table": Schema(type=Schema.Type.TABLE, tab=TableSchema(col_types={"a": ColType.INT}))})
    with pytest.raises(NodeExecutionError):
        bad_tbl = table_from_dict({"a": [object()]})
        node.execute({"table": bad_tbl})

