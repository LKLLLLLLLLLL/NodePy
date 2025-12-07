import pytest

from server.models.exception import NodeExecutionError, NodeParameterError
from server.models.types import ColType
from tests.nodes.utils import make_data, schema_from_coltypes, table_from_dict


def test_batchregexmatchnode_construction_and_hint(node_ctor):
    n1 = node_ctor("BatchRegexMatchNode", id="brm1", pattern="^a$", col="a")
    assert n1 is not None

    # missing col -> pydantic/validate should error
    with pytest.raises(Exception):
        node_ctor("BatchRegexMatchNode", id="brm_bad", pattern="a")

    # empty col name -> NodeParameterError
    with pytest.raises(NodeParameterError):
        node_ctor("BatchRegexMatchNode", id="brm_bad2", pattern="a", col="   ")

    # illegal result_col starting with underscore
    with pytest.raises(NodeParameterError):
        node_ctor("BatchRegexMatchNode", id="brm_bad3", pattern="a", col="a", result_col="_bad")

    node = node_ctor("BatchRegexMatchNode", id="brm_hint", pattern="a+", col="a")
    schema = schema_from_coltypes({"a": ColType.STR, "b": ColType.INT})
    hint = node.get_hint("BatchRegexMatchNode", {"input": schema}, {})
    assert "col_choices" in hint

    # additional construction error: whitespace result_col
    with pytest.raises(NodeParameterError):
        node_ctor("BatchRegexMatchNode", id="brm_bad4", pattern="a", col="a", result_col="   ")

    # mutated type error
    badnode = node_ctor("BatchRegexMatchNode", id="brm_mut", pattern="a", col="a")
    badnode.type = "NotBatchRegex"
    with pytest.raises(NodeParameterError):
        badnode.validate_parameters()


def test_batchregexmatchnode_infer_and_process(node_ctor):
    node = node_ctor("BatchRegexMatchNode", id="brm_inf", pattern="^a+$", col="a", result_col="is_a")
    schema = schema_from_coltypes({"a": ColType.STR})

    # normal infer
    out = node.infer_schema({"input": schema})
    assert "output" in out and out["output"].tab is not None

    # infer error: result_col already exists
    node2 = node_ctor("BatchRegexMatchNode", id="brm_inf2", pattern="a", col="a", result_col="a")
    with pytest.raises(NodeParameterError):
        node2.infer_schema({"input": schema})

    # process normal
    tbl = table_from_dict({"a": ["a", "b", "aa"]})
    node.infer_schema({"input": schema})
    out = node.execute({"input": tbl})
    df = out["output"].payload.df
    assert node.result_col in df.columns
    assert df[node.result_col].dtype == bool

    # execute before infer
    node3 = node_ctor("BatchRegexMatchNode", id="brm_err1", pattern="a", col="a")
    with pytest.raises(NodeExecutionError):
        node3.execute({"input": tbl})

    # execute mismatched input type
    node4 = node_ctor("BatchRegexMatchNode", id="brm_err2", pattern="a", col="a")
    node4.infer_schema({"input": schema})
    with pytest.raises(NodeExecutionError):
        node4.execute({"input": make_data(123)})

    # runtime: missing column in table should raise during process (KeyError)
    tbl_bad = table_from_dict({"x": ["a"]})
    node5 = node_ctor("BatchRegexMatchNode", id="brm_err3", pattern="a", col="a")
    node5.infer_schema({"input": schema})
    with pytest.raises(Exception):
        node5.execute({"input": tbl_bad})

    # hint direct exceptions: patch hint to raise different errors and assert
    from server.interpreter.nodes.stringprocess import regex as rmod
    orig = rmod.BatchRegexMatchNode.hint
    try:
        def _boom(cls, a, b):
            raise RuntimeError("hintboom")
        rmod.BatchRegexMatchNode.hint = classmethod(_boom)  # type: ignore
        with pytest.raises(RuntimeError):
            rmod.BatchRegexMatchNode.hint({}, {})  # type: ignore
    finally:
        rmod.BatchRegexMatchNode.hint = orig
