import pytest

from server.models.exception import (
    NodeExecutionError,
    NodeParameterError,
    NodeValidationError,
)
from server.models.schema import Schema
from tests.nodes.utils import make_data, make_schema


def test_slicenode_construction_normals_and_errors(node_ctor):
    # normal: defaults
    n1 = node_ctor("SliceNode", id="sl1")
    assert n1 is not None
    assert getattr(n1, "start") is None and getattr(n1, "end") is None

    # normal: provide start/end as parameters
    n2 = node_ctor("SliceNode", id="sl2", start=1, end=3)
    assert n2.start == 1 and n2.end == 3

    # error: empty id
    with pytest.raises(NodeParameterError):
        node_ctor("SliceNode", id="   ")

    # error: invalid parameter type for start (pydantic should raise)
    with pytest.raises(Exception):
        node_ctor("SliceNode", id="sl_bad", start="a")

    # error: mutated type triggers validate_parameters
    node = node_ctor("SliceNode", id="sl_ok")
    node.type = "NotSlice"
    with pytest.raises(NodeParameterError):
        node.validate_parameters()


def test_slicenode_hint_behavior(node_ctor):
    node = node_ctor("SliceNode", id="sl_hint")
    # normal: get_hint returns a dict (nodes default to {})
    hint = node.get_hint("SliceNode", {"input": make_schema("str")}, {})
    assert isinstance(hint, dict)

    # malformed input to get_hint returns {}
    res = node.get_hint("SliceNode", {"input": object()}, {})  # type: ignore
    assert res == {}

    # unknown type raises ValueError
    from server.interpreter.nodes.base_node import BaseNode
    with pytest.raises(ValueError):
        BaseNode.get_hint("NoSuch", {}, {})

    # direct class hint should propagate exceptions
    from server.interpreter.nodes.stringprocess import string as s_mod
    orig = s_mod.SliceNode.hint
    try:
        def _boom(cls, a, b):
            raise RuntimeError("hintboom")

        s_mod.SliceNode.hint = classmethod(_boom)  # type: ignore
        with pytest.raises(RuntimeError):
            s_mod.SliceNode.hint({}, {})  # type: ignore
    finally:
        s_mod.SliceNode.hint = orig
    
    # additional error: hint raising ValueError should propagate when called directly
    try:
        def _valerr(cls, a, b):
            raise ValueError("hint bad")

        s_mod.SliceNode.hint = classmethod(_valerr)  # type: ignore
        with pytest.raises(ValueError):
            s_mod.SliceNode.hint({}, {})  # type: ignore
    finally:
        s_mod.SliceNode.hint = orig


def test_slicenode_infer_normals_and_errors(node_ctor):
    node = node_ctor("SliceNode", id="sl_inf")

    # normal: infer with required input
    out = node.infer_schema({"input": make_schema("str")})
    assert "output" in out and out["output"].type == Schema.Type.STR

    # normal: infer when optional start/end provided
    out2 = node.infer_schema({"input": make_schema("str"), "start": make_schema("int"), "end": make_schema("int")})
    assert out2["output"].type == Schema.Type.STR

    # error: missing required input port
    n2 = node_ctor("SliceNode", id="sl_inf_err")
    with pytest.raises(NodeValidationError):
        n2.infer_schema({})

    # error: start provided but wrong type
    with pytest.raises(NodeValidationError):
        node.infer_schema({"input": make_schema("str"), "start": make_schema("str")})

    # error: extra port (provide four ports while only three defined)
    with pytest.raises(ValueError):
        node.infer_schema({"input": make_schema("str"), "start": make_schema("int"), "end": make_schema("int"), "extra": make_schema("str")})


def test_slicenode_execute_normals_and_errors(node_ctor):
    # normal: default behavior returns full string
    n = node_ctor("SliceNode", id="sl_exec1")
    n.infer_schema({"input": make_schema("str")})
    out = n.execute({"input": make_data("hello")})
    assert out["output"].payload == "hello"

    # normal: using constructor params start/end
    n2 = node_ctor("SliceNode", id="sl_exec2", start=1, end=4)
    n2.infer_schema({"input": make_schema("str")})
    out2 = n2.execute({"input": make_data("abcdef")})
    assert out2["output"].payload == "bcd"

    # normal: override start/end via input ports
    n3 = node_ctor("SliceNode", id="sl_exec3")
    n3.infer_schema({"input": make_schema("str"), "start": make_schema("int"), "end": make_schema("int")})
    out3 = n3.execute({"input": make_data("xyz"), "start": make_data(1), "end": make_data(2)})
    assert out3["output"].payload == "y"

    # error: execute before infer
    n4 = node_ctor("SliceNode", id="sl_err1")
    with pytest.raises(NodeExecutionError):
        n4.execute({"input": make_data("a")})

    # error: indices out of range or start> end
    n5 = node_ctor("SliceNode", id="sl_err2")
    n5.infer_schema({"input": make_schema("str")})
    with pytest.raises(NodeExecutionError):
        n5.execute({"input": make_data("ab"), "start": make_data(3), "end": make_data(1)})

    # error: wrong types in execute payload (start not int)
    n6 = node_ctor("SliceNode", id="sl_err3")
    n6.infer_schema({"input": make_schema("str"), "start": make_schema("int")})
    with pytest.raises(Exception):
        n6.execute({"input": make_data("a"), "start": make_data("bad")})
