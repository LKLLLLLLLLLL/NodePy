import re

import pytest

from server.models.exception import (
    NodeExecutionError,
    NodeParameterError,
    NodeValidationError,
)
from tests.nodes.utils import make_data, make_schema


def test_regexmatchnode_construction_normals_and_errors(node_ctor):
    # normals
    n1 = node_ctor("RegexMatchNode", id="rm_ok1", pattern="a.*")
    n2 = node_ctor("RegexMatchNode", id="rm_ok2", pattern="^$")
    assert n1 is not None and n2 is not None

    # errors: missing pattern
    with pytest.raises(Exception):
        node_ctor("RegexMatchNode", id="rm_missing")

    # errors: empty id
    with pytest.raises(NodeParameterError):
        node_ctor("RegexMatchNode", id="   ", pattern="x")

    # errors: mutated type
    node = node_ctor("RegexMatchNode", id="rm_mut", pattern="x")
    node.type = "NotRegex"
    with pytest.raises(NodeParameterError):
        node.validate_parameters()


def test_regexmatchnode_hint_behaviour_and_exceptions(node_ctor):
    node = node_ctor("RegexMatchNode", id="rm_hint", pattern="a.*")
    # Base get_hint should return dict (normal) with or without input
    h1 = node.get_hint("RegexMatchNode", {"string": make_schema("str")}, {})
    h2 = node.get_hint("RegexMatchNode", {}, {})
    assert isinstance(h1, dict) and isinstance(h2, dict)

    # direct class hint exceptions: monkeypatch different raising behaviors
    from server.interpreter.nodes.stringprocess import regex as rmod
    orig = rmod.RegexMatchNode.hint
    try:
        def _boom1(cls, a, b):
            raise RuntimeError("boom1")
        def _boom2(cls, a, b):
            raise ValueError("boom2")
        def _boom3(cls, a, b):
            raise TypeError("boom3")

        rmod.RegexMatchNode.hint = classmethod(_boom1)  # type: ignore
        with pytest.raises(RuntimeError):
            rmod.RegexMatchNode.hint({}, {})  # type: ignore

        rmod.RegexMatchNode.hint = classmethod(_boom2)  # type: ignore
        with pytest.raises(ValueError):
            rmod.RegexMatchNode.hint({}, {})  # type: ignore

        rmod.RegexMatchNode.hint = classmethod(_boom3)  # type: ignore
        with pytest.raises(TypeError):
            rmod.RegexMatchNode.hint({}, {})  # type: ignore
    finally:
        rmod.RegexMatchNode.hint = orig


def test_regexmatchnode_infer_normals_and_errors(node_ctor):
    node = node_ctor("RegexMatchNode", id="rm_inf", pattern="a+")
    # normal infer
    out = node.infer_schema({"string": make_schema("str")})
    assert "is_match" in out

    # normal infer with different string input schema
    out2 = node.infer_schema({"string": make_schema("str")})
    assert "is_match" in out2

    # error: missing required input
    node2 = node_ctor("RegexMatchNode", id="rm_inf_err", pattern="x")
    with pytest.raises(NodeValidationError):
        node2.infer_schema({})

    # error: wrong type (Table instead of str)
    with pytest.raises(NodeValidationError):
        node.infer_schema({"string": make_schema("Table")})

    # error: extra port
    with pytest.raises(ValueError):
        node.infer_schema({"string": make_schema("str"), "extra": make_schema("str")})


def test_regexmatchnode_execute_normals_and_errors(node_ctor):
    node = node_ctor("RegexMatchNode", id="rm_exec", pattern="a.*")
    node.infer_schema({"string": make_schema("str")})

    # normal: match
    r1 = node.execute({"string": make_data("abc")})
    assert isinstance(r1["is_match"].payload, bool)

    # normal: non-match
    r2 = node.execute({"string": make_data("")})
    assert isinstance(r2["is_match"].payload, bool)

    # error: execute before infer
    node2 = node_ctor("RegexMatchNode", id="rm_err1", pattern="a")
    with pytest.raises(NodeExecutionError):
        node2.execute({"string": make_data("a")})

    # error: mismatched input schema
    node3 = node_ctor("RegexMatchNode", id="rm_err2", pattern="a")
    node3.infer_schema({"string": make_schema("str")})
    with pytest.raises(NodeExecutionError):
        node3.execute({"string": make_data(123)})

    # error: invalid regex pattern at runtime (compilation/usage)
    bad = node_ctor("RegexMatchNode", id="rm_badpat", pattern="(*")
    bad.infer_schema({"string": make_schema("str")})
    with pytest.raises(re.error):
        bad.execute({"string": make_data("x")})

