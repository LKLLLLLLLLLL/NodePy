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
    node = node_ctor("ColWithNumberBinOpNode", id="cnb1", op="ADD", col="x")
    # static helper to ensure schema creation doesn't error
    schema_from_coltypes({"x": ColType.INT})
    assert node is not None


def test_colwithnumberbinop_construct_accepts_result_col(node_ctor):
    node = node_ctor("ColWithNumberBinOpNode", id="cnb-exp", op="ADD", col="x", result_col="res")
    assert node.result_col == "res"


def test_colwithnumberbinop_construct_rejects_empty_col(node_ctor):
    with pytest.raises(NodeParameterError):
        node_ctor("ColWithNumberBinOpNode", id="cnb-err", op="ADD", col="  ")


def test_colwithnumberbinop_construct_rejects_result_col_conflict(node_ctor):
    with pytest.raises(NodeParameterError):
        node_ctor("ColWithNumberBinOpNode", id="cnb-conf", op="ADD", col="x", result_col="x")


def test_colwithnumberbinop_static_requires_number_cols(node_ctor):
    node = node_ctor("ColWithNumberBinOpNode", id="cnb2", op="ADD", col="a")
    bad_schema = schema_from_coltypes({"a": ColType.STR})
    with pytest.raises(NodeValidationError):
        node.infer_schema({"table": bad_schema, "num": Schema(type=Schema.Type.INT)})


def test_colwithnumberbinop_static_accepts_matching_types(node_ctor):
    node = node_ctor("ColWithNumberBinOpNode", id="cnb-ok", op="ADD", col="x")
    schema = schema_from_coltypes({"x": ColType.INT})
    out = node.infer_schema({"table": schema, "num": Schema(type=Schema.Type.INT)})
    assert "table" in out


def test_colwithnumberbinop_static_rejects_existing_result_col(node_ctor):
    with pytest.raises(NodeParameterError):
        node_ctor("ColWithNumberBinOpNode", id="cnb-exist", op="ADD", col="x", result_col="x")


def test_colwithnumberbinop_execute_per_row(node_ctor):
    node = node_ctor("ColWithNumberBinOpNode", id="cnb3", op="MUL", col="x")
    tbl = table_from_dict({"x": [2, 3]})
    tbl_obj = cast(Table, tbl.payload)
    col_types_map: Dict[str, ColType] = dict(tbl_obj.col_types)
    node._col_types = col_types_map
    node._col_types[node.result_col] = col_types_map["x"]
    out = node.process({"table": tbl, "num": Data(payload=10)})
    assert hasattr(out["table"].payload, "df")


def test_colwithnumberbinop_execute_add_computes_correctly(node_ctor):
    node = node_ctor("ColWithNumberBinOpNode", id="cnb5", op="ADD", col="x")
    tbl = table_from_dict({"x": [1, 2]})
    tbl_obj = cast(Table, tbl.payload)
    col_types_map: Dict[str, ColType] = dict(tbl_obj.col_types)
    node._col_types = col_types_map
    node._col_types[node.result_col] = col_types_map["x"]
    out = node.process({"table": tbl, "num": Data(payload=5)})
    df = out["table"].payload.df
    assert list(df[node.result_col]) == [6, 7]


def test_colwithnumberbinop_execute_error_on_non_number(node_ctor):
    node = node_ctor("ColWithNumberBinOpNode", id="cnb6", op="ADD", col="x")
    bad_tbl = table_from_dict({"x": [1, "nope"]})
    bad_tbl_obj = cast(Table, bad_tbl.payload)
    col_types_map: Dict[str, ColType] = dict(bad_tbl_obj.col_types)
    node._col_types = col_types_map
    node._col_types[node.result_col] = col_types_map["x"]
    with pytest.raises(Exception):
        node.process({"table": bad_tbl, "num": Data(payload=2)})


def test_colwithnumberbinop_execute_div_by_zero(node_ctor):
    node = node_ctor("ColWithNumberBinOpNode", id="cnb7", op="COL_DIV_NUM", col="x")
    tbl = table_from_dict({"x": [1, 2]})
    tbl_obj = cast(Table, tbl.payload)
    col_types_map: Dict[str, ColType] = dict(tbl_obj.col_types)
    node._col_types = col_types_map
    node._col_types[node.result_col] = col_types_map["x"]
    with pytest.raises(NodeExecutionError):
        node.process({"table": tbl, "num": Data(payload=0)})


def test_colwithnumberbinop_execute_error_on_bad_cell(node_ctor):
    node = node_ctor("ColWithNumberBinOpNode", id="cnb4", op="ADD", col="x")
    bad_tbl = table_from_dict({"x": [1, "nope"]})
    bad_tbl_obj = cast(Table, bad_tbl.payload)
    col_types_map: Dict[str, ColType] = dict(bad_tbl_obj.col_types)
    node._col_types = col_types_map
    node._col_types[node.result_col] = col_types_map["x"]
    with pytest.raises(Exception):
        node.process({"table": bad_tbl, "num": Data(payload=2)})
