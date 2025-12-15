import pytest

from server.models.exception import (
    NodeExecutionError,
    NodeParameterError,
    NodeValidationError,
)
from server.models.schema import Schema
from tests.nodes.utils import make_data, make_schema


def test_stripnode_construction_normals_and_trim(node_ctor):
    # normal: default construction (no strip_chars)
    n1 = node_ctor("StripNode", id="s1")
    assert n1 is not None
    assert getattr(n1, "strip_chars") is None

    # normal: explicit strip_chars
    n2 = node_ctor("StripNode", id="s2", strip_chars="x")
    assert n2.strip_chars == "x"

    # trim-only strip_chars (only spaces) should normalize to None
    n3 = node_ctor("StripNode", id="s3", strip_chars="   ")
    assert n3.strip_chars is None


def test_stripnode_construction_error_cases(node_ctor):
    # 1) empty id should raise NodeParameterError
    with pytest.raises(NodeParameterError):
        node_ctor("StripNode", id="   ")

    # 2) mutated type should raise when validating parameters
    node = node_ctor("StripNode", id="s_ok")
    node.type = "NotStrip"
    with pytest.raises(NodeParameterError):
        node.validate_parameters()

    # 3) creating unknown node type raises ValueError (framework-level)
    from server.interpreter.nodes.base_node import BaseNode
    with pytest.raises(ValueError):
        BaseNode.create_from_type(node.context, "NoSuchNode", id="x")


def test_stripnode_hint_normals_and_errors(node_ctor):
    node = node_ctor("StripNode", id="s_hint")
    # normal: get_hint returns a dict (most nodes return {} by default)
    hint = node.get_hint("StripNode", {"input": make_schema("str")}, {})
    assert isinstance(hint, dict)

    # normal: malformed input to hint should be handled and return {}
    res = node.get_hint("StripNode", {"input": object()}, {})  # type: ignore
    assert res == {}

    # error: unknown node type in get_hint should raise ValueError
    from server.interpreter.nodes.base_node import BaseNode
    with pytest.raises(ValueError):
        BaseNode.get_hint("NoSuch", {}, {})

    # direct hint invocation should propagate exceptions (class hint)
    from server.interpreter.nodes.stringprocess import string as s_mod
    orig = s_mod.StripNode.hint
    try:
        def _bad_hint(cls, a, b):
            raise RuntimeError("boom")

        s_mod.StripNode.hint = classmethod(_bad_hint)  # type: ignore
        with pytest.raises(RuntimeError):
            s_mod.StripNode.hint({}, {})  # type: ignore
    finally:
        s_mod.StripNode.hint = orig
    
    # additional error: hint raising ValueError should propagate when called directly
    try:
        def _valerr(cls, a, b):
            raise ValueError("bad hint")

        s_mod.StripNode.hint = classmethod(_valerr)  # type: ignore
        with pytest.raises(ValueError):
            s_mod.StripNode.hint({}, {})  # type: ignore
    finally:
        s_mod.StripNode.hint = orig


def test_stripnode_infer_normals_and_errors(node_ctor):
    node = node_ctor("StripNode", id="s_inf")

    # normal: infer with required input present
    out = node.infer_schema({"input": make_schema("str")})
    assert "output" in out and out["output"].type == Schema.Type.STR

    # normal: infer when optional strip_chars input is provided
    out2 = node.infer_schema({"input": make_schema("str"), "strip_chars": make_schema("str")})
    assert out2["output"].type == Schema.Type.STR

    # error: missing required input port
    node2 = node_ctor("StripNode", id="s_inf_err")
    with pytest.raises(NodeValidationError):
        node2.infer_schema({})

    # error: strip_chars provided but wrong type
    with pytest.raises(NodeValidationError):
        node.infer_schema({"input": make_schema("str"), "strip_chars": make_schema("int")})

    # error: extra port should raise ValueError (provide three ports while only two defined)
    with pytest.raises(ValueError):
        node.infer_schema({"input": make_schema("str"), "strip_chars": make_schema("str"), "extra": make_schema("str")})


def test_stripnode_execute_normals_and_errors(node_ctor):

    # normal: strip whitespace when no strip_chars provided
    n = node_ctor("StripNode", id="s_exec1")
    n.infer_schema({"input": make_schema("str")})
    out = n.execute({"input": make_data("  hello  ")})
    assert out["output"].payload == "hello"

    # normal: use parameter strip_chars to strip specific chars
    n2 = node_ctor("StripNode", id="s_exec2", strip_chars="x")
    n2.infer_schema({"input": make_schema("str")})
    out2 = n2.execute({"input": make_data("xxheyxx")})
    assert out2["output"].payload == "hey"

    # normal: override strip_chars via input port
    n3 = node_ctor("StripNode", id="s_exec3", strip_chars="z")
    n3.infer_schema({"input": make_schema("str"), "strip_chars": make_schema("str")})
    out3 = n3.execute({"input": make_data("--val--"), "strip_chars": make_data("-")})
    assert out3["output"].payload == "val"

    # error: execute before infer
    n4 = node_ctor("StripNode", id="s_err1")
    with pytest.raises(NodeExecutionError):
        n4.execute({"input": make_data("a")})

    # error: mismatched input schema
    n5 = node_ctor("StripNode", id="s_err2")
    n5.infer_schema({"input": make_schema("str")})
    with pytest.raises(NodeExecutionError):
        n5.execute({"input": make_data(123)})

    # error: strip_chars payload wrong type triggers assertion in process
    n6 = node_ctor("StripNode", id="s_err3")
    n6.infer_schema({"input": make_schema("str"), "strip_chars": make_schema("str")})
    with pytest.raises(Exception):
        n6.execute({"input": make_data("a"), "strip_chars": make_data(42)})
