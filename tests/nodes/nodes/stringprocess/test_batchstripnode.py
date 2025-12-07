import pytest

from server.models.exception import (
    NodeExecutionError,
    NodeParameterError,
    NodeValidationError,
)
from server.models.types import ColType
from tests.nodes.utils import (
    make_data,
    make_schema,
    schema_from_coltypes,
    table_from_dict,
)


def test_batchstripnode_construction_normals_and_errors(node_ctor):
    # normal: specify col, let result_col be auto-generated
    n1 = node_ctor("BatchStripNode", id="bs1", col="name")
    assert n1 is not None

    # normal: provide strip_chars parameter too
    n2 = node_ctor("BatchStripNode", id="bs2", col="name", strip_chars="x")
    assert n2.strip_chars == "x"

    # error: missing required col (pydantic should raise)
    with pytest.raises(Exception):
        node_ctor("BatchStripNode", id="bs_bad")

    # error: empty col name
    with pytest.raises(NodeParameterError):
        node_ctor("BatchStripNode", id="bs_bad2", col="   ")

    # error: mutated type
    node = node_ctor("BatchStripNode", id="bs_ok", col="c")
    node.type = "NotBatchStrip"
    with pytest.raises(NodeParameterError):
        node.validate_parameters()


def test_batchstripnode_hint_and_edge_cases(node_ctor):
    node = node_ctor("BatchStripNode", id="bs_hint", col="a")
    # normal: when input schema has string cols, hint includes them
    schema = schema_from_coltypes({"a": ColType.STR, "b": ColType.INT})
    hint = node.get_hint("BatchStripNode", {"input": schema}, {})
    assert "col_choices" in hint and isinstance(hint["col_choices"], list)

    # normal: when no input present, hint returns {}
    hint2 = node.get_hint("BatchStripNode", {}, {})
    assert isinstance(hint2, dict)

    # error: unknown node type raises
    from server.interpreter.nodes.base_node import BaseNode
    with pytest.raises(ValueError):
        BaseNode.get_hint("NoSuch", {}, {})

    # direct class hint exceptions propagate
    from server.interpreter.nodes.stringprocess import batch as bmod
    orig = bmod.BatchStripNode.hint
    try:
        def _boom(cls, a, b):
            raise RuntimeError("hintboom")
        bmod.BatchStripNode.hint = classmethod(_boom)  # type: ignore
        with pytest.raises(RuntimeError):
            bmod.BatchStripNode.hint({}, {})  # type: ignore
    finally:
        bmod.BatchStripNode.hint = orig


def test_batchstripnode_infer_normals_and_errors(node_ctor):
    node = node_ctor("BatchStripNode", id="bs_inf", col="name")
    schema = schema_from_coltypes({"name": ColType.STR, "val": ColType.INT})

    # normal: infer produces output schema with appended result_col
    out = node.infer_schema({"input": schema})
    assert "output" in out and out["output"].tab is not None

    # normal: infer when optional strip_chars input provided
    out2 = node.infer_schema({"input": schema, "strip_chars": make_schema("str")})
    assert out2["output"].tab is not None

    # error: missing required input port
    node2 = node_ctor("BatchStripNode", id="bs_inf_err", col="name")
    with pytest.raises(NodeValidationError):
        node2.infer_schema({})

    # error: input table lacks required column type (name not str)
    bad_schema = schema_from_coltypes({"name": ColType.INT})
    with pytest.raises(NodeValidationError):
        node.infer_schema({"input": bad_schema})

    # error: extra port
    with pytest.raises(ValueError):
        node.infer_schema({"input": schema, "strip_chars": make_schema("str"), "extra": make_schema("str")})


def test_batchstripnode_execute_normals_and_errors(node_ctor):
    tbl = table_from_dict({"name": [" a ", " b "], "val": [1, 2]})
    node = node_ctor("BatchStripNode", id="bs_exec", col="name")
    node.infer_schema({"input": schema_from_coltypes({"name": ColType.STR, "val": ColType.INT})})
    out = node.execute({"input": tbl})
    assert "output" in out
    df = out["output"].payload.df
    assert df.columns.str.contains("result").any()

    # normal: using strip_chars param
    node2 = node_ctor("BatchStripNode", id="bs_exec2", col="name", strip_chars=" ")
    node2.infer_schema({"input": schema_from_coltypes({"name": ColType.STR, "val": ColType.INT})})
    out2 = node2.execute({"input": tbl})
    assert out2["output"].payload.df[ node2.result_col ].iloc[0] == "a"

    # normal: override strip_chars via input port
    node3 = node_ctor("BatchStripNode", id="bs_exec3", col="name")
    node3.infer_schema({"input": schema_from_coltypes({"name": ColType.STR, "val": ColType.INT}), "strip_chars": make_schema("str")})
    out3 = node3.execute({"input": tbl, "strip_chars": make_data(" ")})
    assert out3["output"].payload.df[ node3.result_col ].iloc[1] == "b"

    # error: execute before infer
    node4 = node_ctor("BatchStripNode", id="bs_err1", col="name")
    with pytest.raises(NodeExecutionError):
        node4.execute({"input": tbl})

    # error: mismatched input schema (not a table)
    node5 = node_ctor("BatchStripNode", id="bs_err2", col="name")
    node5.infer_schema({"input": schema_from_coltypes({"name": ColType.STR})})
    with pytest.raises(NodeExecutionError):
        node5.execute({"input": make_data(123)})

    # error: strip_chars wrong type in execute
    node6 = node_ctor("BatchStripNode", id="bs_err3", col="name")
    node6.infer_schema({"input": schema_from_coltypes({"name": ColType.STR}) , "strip_chars": make_schema("str")})
    with pytest.raises(Exception):
        node6.execute({"input": tbl, "strip_chars": make_data(42)})


def test_batchstripnode_resultcol_whitespace_and_illegal(node_ctor):
    # if result_col provided as whitespace, it should be reset to a generated default
    node = node_ctor("BatchStripNode", id="bs_ws", col="name", result_col="   ")
    # construction should succeed and result_col becomes default pattern
    assert node.result_col is not None and node.result_col.startswith("bs_ws_")

    # illegal result_col (starts with underscore) should raise NodeParameterError
    with pytest.raises(NodeParameterError):
        node_ctor("BatchStripNode", id="bs_illegal", col="name", result_col="_bad")


def test_batchstripnode_resultcol_cannot_match_col(node_ctor):
    # new behavior: result_col equal to input col should raise NodeParameterError
    with pytest.raises(NodeParameterError):
        node_ctor("BatchStripNode", id="bs_same", col="name", result_col="name")
