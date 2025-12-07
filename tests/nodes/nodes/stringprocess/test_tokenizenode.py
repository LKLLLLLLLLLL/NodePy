import pytest

from server.models.exception import (
    NodeExecutionError,
    NodeParameterError,
    NodeValidationError,
)
from tests.nodes.utils import make_data, make_schema


def test_tokenizenode_construction_normals_and_errors(node_ctor):
    # normals: english and chinese
    n1 = node_ctor("TokenizeNode", id="tk_en", language="ENGLISH")
    n2 = node_ctor("TokenizeNode", id="tk_cn", language="CHINESE")
    assert n1 is not None and n2 is not None

    # normal: user-provided result_col is preserved
    n3 = node_ctor("TokenizeNode", id="tk_r", language="ENGLISH", result_col="mycol")
    assert n3.result_col == "mycol"

    # errors: missing required language param -> pydantic
    with pytest.raises(Exception):
        node_ctor("TokenizeNode", id="tk_bad")

    # errors: invalid language value -> pydantic should reject
    with pytest.raises(Exception):
        node_ctor("TokenizeNode", id="tk_bad2", language="SPANISH")

    # errors: empty id
    with pytest.raises(NodeParameterError):
        node_ctor("TokenizeNode", id="   ", language="ENGLISH")

    # error: mutated type
    node = node_ctor("TokenizeNode", id="tk_mut", language="ENGLISH")
    node.type = "NotTokenize"
    with pytest.raises(NodeParameterError):
        node.validate_parameters()


def test_tokenizenode_hint_and_direct_exceptions(node_ctor):
    node = node_ctor("TokenizeNode", id="tk_hint", language="ENGLISH")
    # get_hint via BaseNode should return dict
    h = node.get_hint("TokenizeNode", {"text": make_schema("str")}, {})
    assert isinstance(h, dict)

    # direct class hint exceptions propagate when called directly
    from server.interpreter.nodes.stringprocess import tokenize as tmod
    orig = getattr(tmod.TokenizeNode, "hint", None)
    try:
        def _boom1(cls, a, b):
            raise RuntimeError("h1")
        def _boom2(cls, a, b):
            raise ValueError("h2")
        def _boom3(cls, a, b):
            raise TypeError("h3")

        tmod.TokenizeNode.hint = classmethod(_boom1)  # type: ignore
        with pytest.raises(RuntimeError):
            tmod.TokenizeNode.hint({}, {})  # type: ignore

        tmod.TokenizeNode.hint = classmethod(_boom2)  # type: ignore
        with pytest.raises(ValueError):
            tmod.TokenizeNode.hint({}, {})  # type: ignore

        tmod.TokenizeNode.hint = classmethod(_boom3)  # type: ignore
        with pytest.raises(TypeError):
            tmod.TokenizeNode.hint({}, {})  # type: ignore
    finally:
        if orig is not None:
            tmod.TokenizeNode.hint = orig
        else:
            delattr(tmod.TokenizeNode, "hint")


def test_tokenizenode_infer_normals_and_errors(node_ctor):
    node = node_ctor("TokenizeNode", id="tk_inf", language="ENGLISH")
    # normal infer
    out = node.infer_schema({"text": make_schema("str")})
    from server.models.schema import Schema
    assert "tokens" in out and out["tokens"].type == Schema.Type.TABLE

    # infer normal for CHINESE
    node2 = node_ctor("TokenizeNode", id="tk_inf2", language="CHINESE")
    out2 = node2.infer_schema({"text": make_schema("str")})
    assert "tokens" in out2

    # error: missing input
    node3 = node_ctor("TokenizeNode", id="tk_err1", language="ENGLISH")
    with pytest.raises(NodeValidationError):
        node3.infer_schema({})

    # error: wrong input type
    with pytest.raises(NodeValidationError):
        node.infer_schema({"text": make_schema("Table")})

    # error: extra port
    with pytest.raises(ValueError):
        node.infer_schema({"text": make_schema("str"), "extra": make_schema("str")})


def test_tokenizenode_execute_normals_and_errors(node_ctor, monkeypatch):
    # english normal
    node = node_ctor("TokenizeNode", id="tk_exec_en", language="ENGLISH")
    node.infer_schema({"text": make_schema("str")})
    out = node.execute({"text": make_data("a b c")})
    df = out["tokens"].payload.df
    assert node.result_col in df.columns
    assert list(df[node.result_col]) == ["a", "b", "c"]

    # chinese normal: patch jieba.cut to deterministic result
    node2 = node_ctor("TokenizeNode", id="tk_exec_cn", language="CHINESE")
    node2.infer_schema({"text": make_schema("str")})
    import sys
    fake_mod = type("M", (), {"cut": staticmethod(lambda s: ["中", "文"]) })
    monkeypatch.setitem(sys.modules, "jieba", fake_mod)
    out2 = node2.execute({"text": make_data("中文")})
    df2 = out2["tokens"].payload.df
    assert node2.result_col in df2.columns
    assert list(df2[node2.result_col]) == ["中", "文"]

    # error: execute before infer
    node3 = node_ctor("TokenizeNode", id="tk_err_exec1", language="ENGLISH")
    with pytest.raises(NodeExecutionError):
        node3.execute({"text": make_data("x")})

    # error: mismatched input schema (non-str payload)
    node4 = node_ctor("TokenizeNode", id="tk_err_exec2", language="ENGLISH")
    node4.infer_schema({"text": make_schema("str")})
    with pytest.raises(NodeExecutionError):
        node4.execute({"text": make_data(123)})

    # error: runtime jieba error should propagate
    node5 = node_ctor("TokenizeNode", id="tk_err_exec3", language="CHINESE")
    node5.infer_schema({"text": make_schema("str")})
    fake_err = type("M", (), {"cut": staticmethod(lambda s: (_ for _ in ()).throw(RuntimeError("fail"))) })
    monkeypatch.setitem(sys.modules, "jieba", fake_err)
    with pytest.raises(RuntimeError):
        node5.execute({"text": make_data("中文")})
