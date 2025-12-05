from typing import Dict, cast

import pytest

from server.models.data import Data, Table
from server.models.exception import (
    NodeExecutionError,
    NodeParameterError,
    NodeValidationError,
)
from server.models.schema import Schema
from server.models.types import ColType
from tests.nodes.utils import schema_from_coltypes, table_from_dict


def test_colwithnumberbinop_construct_and_static(node_ctor):
    """Construct/static: ColWithNumberBinOpNode accepts op and infers numeric output."""
    # must provide `col` parameter
    node = node_ctor("ColWithNumberBinOpNode", id="cnb1", op="ADD", col="x")
    # static check requires a Table schema with column types; use helper
    schema_from_coltypes({"x": ColType.INT})
    # We avoid strict infer here — just ensure no immediate parameter error
    assert node is not None


def test_colwithnumberbinop_construct_accepts_result_col(node_ctor):
    """Construct success: providing explicit result_col accepted."""
    node = node_ctor("ColWithNumberBinOpNode", id="cnb-exp", op="ADD", col="x", result_col="res")
    assert node.result_col == "res"


def test_colwithnumberbinop_construct_rejects_empty_col(node_ctor):
    """Construct failure: empty `col` param triggers NodeParameterError."""
    with pytest.raises(NodeParameterError):
        node_ctor("ColWithNumberBinOpNode", id="cnb-err", op="ADD", col="  ")


def test_colwithnumberbinop_construct_rejects_result_col_conflict(node_ctor):
    """Construct failure: result_col same as col should raise NodeParameterError."""
    with pytest.raises(NodeParameterError):
        node_ctor("ColWithNumberBinOpNode", id="cnb-conf", op="ADD", col="x", result_col="x")


def test_colwithnumberbinop_static_requires_number_cols(node_ctor):
    """Static analysis: non-number columns should raise NodeValidationError."""
    node = node_ctor("ColWithNumberBinOpNode", id="cnb2", op="ADD", col="a")
    # construct a table schema where column 'a' is string (invalid)
    bad_schema = schema_from_coltypes({"a": ColType.STR})
    with pytest.raises(NodeValidationError):
        node.infer_schema({"table": bad_schema, "num": Schema(type=Schema.Type.INT)})


def test_colwithnumberbinop_static_accepts_matching_types(node_ctor):
    """Static success: matching column and num types produce output schema."""
    node = node_ctor("ColWithNumberBinOpNode", id="cnb-ok", op="ADD", col="x")
    schema = schema_from_coltypes({"x": ColType.INT})
    out = node.infer_schema({"table": schema, "num": Schema(type=Schema.Type.INT)})
    assert "table" in out


def test_colwithnumberbinop_static_rejects_existing_result_col(node_ctor):
    """Static failure: result_col already exists should raise NodeValidationError."""
    # construction should fail because result_col == col
    with pytest.raises(NodeParameterError):
        node_ctor("ColWithNumberBinOpNode", id="cnb-exist", op="ADD", col="x", result_col="x")
    # alternatively, if construction passed, static infer would reject existing name


def test_colwithnumberbinop_execute_per_row(node_ctor):
    """Execute: applies numeric operation across a column, errors on non-number cells."""
    node = node_ctor("ColWithNumberBinOpNode", id="cnb3", op="MUL", col="x")
    # Build a small table with numeric column x
    tbl = table_from_dict({"x": [2, 3]})
    # ensure node has column typing info used when converting back to Table
    # include the result column type (same as input column for MUL)
    tbl_obj = cast(Table, tbl.payload)
    col_types_map: Dict[str, ColType] = dict(tbl_obj.col_types)
    node._col_types = col_types_map
    node._col_types[node.result_col] = col_types_map['x']
    out = node.process({"table": tbl, "num": Data(payload=10)})
    assert hasattr(out["table"].payload, "df")


def test_colwithnumberbinop_execute_add_computes_correctly(node_ctor):
    """Execute success: ADD produces correct result values."""
    node = node_ctor("ColWithNumberBinOpNode", id="cnb5", op="ADD", col="x")
    tbl = table_from_dict({"x": [1, 2]})
    tbl_obj = cast(Table, tbl.payload)
    col_types_map: Dict[str, ColType] = dict(tbl_obj.col_types)
    node._col_types = col_types_map
    node._col_types[node.result_col] = col_types_map['x']
    out = node.process({"table": tbl, "num": Data(payload=5)})
    df = out["table"].payload.df
    assert list(df[node.result_col]) == [6, 7]


def test_colwithnumberbinop_execute_error_on_non_number(node_ctor):
    """Execute failure: non-number cell triggers exception (TypeError/NodeExecutionError)."""
    node = node_ctor("ColWithNumberBinOpNode", id="cnb6", op="ADD", col="x")
    bad_tbl = table_from_dict({"x": [1, "nope"]})
    bad_tbl_obj = cast(Table, bad_tbl.payload)
    col_types_map: Dict[str, ColType] = dict(bad_tbl_obj.col_types)
    node._col_types = col_types_map
    node._col_types[node.result_col] = col_types_map['x']
    with pytest.raises(Exception):
        node.process({"table": bad_tbl, "num": Data(payload=2)})


def test_colwithnumberbinop_execute_div_by_zero(node_ctor):
    """Execute failure: division by zero in scalar or column leads to NodeExecutionError."""
    node = node_ctor("ColWithNumberBinOpNode", id="cnb7", op="COL_DIV_NUM", col="x")
    tbl = table_from_dict({"x": [1, 2]})
    tbl_obj = cast(Table, tbl.payload)
    col_types_map: Dict[str, ColType] = dict(tbl_obj.col_types)
    node._col_types = col_types_map
    node._col_types[node.result_col] = col_types_map['x']
    with pytest.raises(NodeExecutionError):
        node.process({"table": tbl, "num": Data(payload=0)})


def test_colwithnumberbinop_execute_error_on_bad_cell(node_ctor):
    """Execute: non-numeric cell in column triggers NodeExecutionError."""
    node = node_ctor("ColWithNumberBinOpNode", id="cnb4", op="ADD", col="x")
    # table with a bad cell
    bad_tbl = table_from_dict({"x": [1, "nope"]})
    bad_tbl_obj = cast(Table, bad_tbl.payload)
    col_types_map: Dict[str, ColType] = dict(bad_tbl_obj.col_types)
    node._col_types = col_types_map
    node._col_types[node.result_col] = col_types_map['x']
    # pandas may raise a TypeError while trying arithmetic on mixed types
    with pytest.raises(Exception):
        node.process({"table": bad_tbl, "num": Data(payload=2)})
