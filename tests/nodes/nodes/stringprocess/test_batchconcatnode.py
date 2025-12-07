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


def test_batchconcatnode_construction_and_errors(node_ctor):
    # normal
    n1 = node_ctor("BatchConcatNode", id="bc1", col1="a", col2="b")
    assert n1 is not None

    # error: missing columns in constructor
    with pytest.raises(Exception):
        node_ctor("BatchConcatNode", id="bc_bad")

    # error: empty col1/col2
    with pytest.raises(NodeParameterError):
        node_ctor("BatchConcatNode", id="bc_bad2", col1="   ", col2="b")

    node = node_ctor("BatchConcatNode", id="bc_ok", col1="a", col2="b")
    node.type = "NotBatchConcat"
    with pytest.raises(NodeParameterError):
        node.validate_parameters()

    # whitespace result_col should raise for BatchConcatNode (no auto-reset)
    with pytest.raises(NodeParameterError):
        node_ctor("BatchConcatNode", id="bc_bad3", col1="a", col2="b", result_col="   ")

    # illegal result_col starting with '_' should raise
    with pytest.raises(NodeParameterError):
        node_ctor("BatchConcatNode", id="bc_bad4", col1="a", col2="b", result_col="_illegal")


def test_batchconcatnode_hint_and_infer(node_ctor):
    node = node_ctor("BatchConcatNode", id="bc_hint", col1="a", col2="b")
    schema = schema_from_coltypes({"a": ColType.STR, "b": ColType.STR, "c": ColType.INT})
    hint = node.get_hint("BatchConcatNode", {"input": schema}, {})
    assert "col1_choices" in hint and "col2_choices" in hint

    # infer normal
    out = node.infer_schema({"input": schema})
    assert out["output"].tab is not None

    # infer error: missing input
    node2 = node_ctor("BatchConcatNode", id="bc_inf_err", col1="a", col2="b")
    with pytest.raises(NodeValidationError):
        node2.infer_schema({})

    # infer error: input has wrong column types
    bad_schema = schema_from_coltypes({"a": ColType.INT, "b": ColType.STR})
    with pytest.raises(NodeValidationError):
        node.infer_schema({"input": bad_schema})

    # infer error: extra port
    with pytest.raises(ValueError):
        node.infer_schema({"input": schema, "extra": make_schema("str")})


def test_batchconcatnode_execute_normals_and_errors(node_ctor):
    tbl = table_from_dict({"a": ["x", "y"], "b": ["1", "2"], "c": [1, 2]})
    node = node_ctor("BatchConcatNode", id="bc_exec", col1="a", col2="b")
    node.infer_schema({"input": schema_from_coltypes({"a": ColType.STR, "b": ColType.STR, "c": ColType.INT})})
    out = node.execute({"input": tbl})
    df = out["output"].payload.df
    assert node.result_col in df.columns

    # error: execute before infer
    node2 = node_ctor("BatchConcatNode", id="bc_err1", col1="a", col2="b")
    with pytest.raises(NodeExecutionError):
        node2.execute({"input": tbl})

    # error: mismatched input schema
    node3 = node_ctor("BatchConcatNode", id="bc_err2", col1="a", col2="b")
    node3.infer_schema({"input": schema_from_coltypes({"a": ColType.STR, "b": ColType.STR})})
    with pytest.raises(NodeExecutionError):
        node3.execute({"input": make_data(123)})

    # error: runtime input schema doesn't match inferred schema -> execution should fail
    tbl2 = table_from_dict({"a": [1], "b": [2]})
    node4 = node_ctor("BatchConcatNode", id="bc_exec2", col1="a", col2="b")
    # craft schema that claims cols are STR to satisfy infer
    node4.infer_schema({"input": schema_from_coltypes({"a": ColType.STR, "b": ColType.STR})})
    with pytest.raises(NodeExecutionError):
        node4.execute({"input": tbl2})
