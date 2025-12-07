import pytest

from server.models.exception import (
    NodeExecutionError,
    NodeParameterError,
    NodeValidationError,
)
from server.models.schema import Schema
from tests.nodes.utils import make_data, make_schema


def test_replacenode_construction_normals_and_errors(node_ctor):
    # normals
    n1 = node_ctor("ReplaceNode", id="r1", old="a", new="b")
    assert n1 is not None
    n2 = node_ctor("ReplaceNode", id="r2")
    assert n2 is not None

    # errors: empty id
    with pytest.raises(NodeParameterError):
        node_ctor("ReplaceNode", id="   ")

    # errors: invalid old param (only spaces) should raise in validate
    with pytest.raises(NodeParameterError):
        node_ctor("ReplaceNode", id="r_bad", old="   ")

    # errors: mutated type
    node = node_ctor("ReplaceNode", id="r_ok")
    node.type = "NotReplace"
    with pytest.raises(NodeParameterError):
        node.validate_parameters()


def test_replacenode_hint_and_edge_cases(node_ctor):
    node = node_ctor("ReplaceNode", id="r_hint")
    # normal: get_hint returns dict
    h = node.get_hint("ReplaceNode", {"input": make_schema("str")}, {})
    assert isinstance(h, dict)

    # malformed input to hint -> {}
    assert node.get_hint("ReplaceNode", {"input": object()}, {}) == {}

    # unknown type raises
    from server.interpreter.nodes.base_node import BaseNode
    with pytest.raises(ValueError):
        BaseNode.get_hint("NoSuch", {}, {})

    # direct hint exceptions propagate
    from server.interpreter.nodes.stringprocess import string as s_mod
    orig = s_mod.ReplaceNode.hint
    try:
        def _boom(cls, a, b):
            raise RuntimeError("hint boom")
        s_mod.ReplaceNode.hint = classmethod(_boom)  # type: ignore
        with pytest.raises(RuntimeError):
            s_mod.ReplaceNode.hint({}, {})  # type: ignore
    finally:
        s_mod.ReplaceNode.hint = orig


def test_replacenode_infer_normals_and_errors(node_ctor):
    # normal: parameters supply old/new
    n1 = node_ctor("ReplaceNode", id="r_inf1", old="a", new="b")
    out = n1.infer_schema({"input": make_schema("str")})
    assert out["output"].type == Schema.Type.STR

    # normal: old/new provided via input schemas
    n2 = node_ctor("ReplaceNode", id="r_inf2")
    out2 = n2.infer_schema({"input": make_schema("str"), "old": make_schema("str"), "new": make_schema("str")})
    assert out2["output"].type == Schema.Type.STR

    # errors: missing old
    n3 = node_ctor("ReplaceNode", id="r_e1")
    with pytest.raises(NodeValidationError):
        n3.infer_schema({"input": make_schema("str"), "new": make_schema("str")})

    # errors: missing new
    n4 = node_ctor("ReplaceNode", id="r_e2")
    with pytest.raises(NodeValidationError):
        n4.infer_schema({"input": make_schema("str"), "old": make_schema("str")})

    # errors: extra port
    n5 = node_ctor("ReplaceNode", id="r_e3")
    with pytest.raises(ValueError):
        n5.infer_schema({"input": make_schema("str"), "old": make_schema("str"), "new": make_schema("str"), "extra": make_schema("str")})


def test_replacenode_execute_normals_and_errors(node_ctor):
    # normal: replace using params
    n1 = node_ctor("ReplaceNode", id="r_exec1", old="x", new="y")
    n1.infer_schema({"input": make_schema("str")})
    out = n1.execute({"input": make_data("xoxo")})
    assert out["output"].payload == "yoyo"

    # normal: replace using input ports
    n2 = node_ctor("ReplaceNode", id="r_exec2")
    n2.infer_schema({"input": make_schema("str"), "old": make_schema("str"), "new": make_schema("str")})
    out2 = n2.execute({"input": make_data("aaabb"), "old": make_data("a"), "new": make_data("z")})
    assert out2["output"].payload == "zzzbb"

    # normal: mix param and input
    n3 = node_ctor("ReplaceNode", id="r_exec3", old="p")
    n3.infer_schema({"input": make_schema("str"), "new": make_schema("str")})
    out3 = n3.execute({"input": make_data("ppq"), "new": make_data("r")})
    assert out3["output"].payload == "rrq"

    # errors: execute before infer
    n4 = node_ctor("ReplaceNode", id="r_err1")
    with pytest.raises(NodeExecutionError):
        n4.execute({"input": make_data("a")})

    # errors: mismatched input schema
    n5 = node_ctor("ReplaceNode", id="r_err2", old="a", new="b")
    n5.infer_schema({"input": make_schema("str")})
    with pytest.raises(NodeExecutionError):
        n5.execute({"input": make_data(123)})

    # errors: old == new triggers NodeExecutionError
    n6 = node_ctor("ReplaceNode", id="r_err3", old="z", new="z")
    n6.infer_schema({"input": make_schema("str")})
    with pytest.raises(NodeExecutionError):
        n6.execute({"input": make_data("zzz")})
