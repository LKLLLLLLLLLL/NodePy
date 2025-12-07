import pytest

from server.models.exception import (
    NodeExecutionError,
    NodeParameterError,
    NodeValidationError,
)
from server.models.schema import Schema
from tests.nodes.utils import make_data, make_schema


def test_concatnode_construction_and_errors(node_ctor):
    n = node_ctor("ConcatNode", id="c1")
    assert n is not None

    # error: empty id
    with pytest.raises(NodeParameterError):
        node_ctor("ConcatNode", id="   ")

    # error: mutated type
    node2 = node_ctor("ConcatNode", id="c_ok")
    node2.type = "NotConcat"
    with pytest.raises(NodeParameterError):
        node2.validate_parameters()


def test_concatnode_hint_and_infer(node_ctor):
    n = node_ctor("ConcatNode", id="c_hint")
    assert isinstance(n.get_hint("ConcatNode", {"input": make_schema("str")}, {}), dict)
    out = n.infer_schema({"input1": make_schema("str"), "input2": make_schema("str")})
    assert out["output"].type == Schema.Type.STR

    # error: missing required ports
    n2 = node_ctor("ConcatNode", id="c_inf_err")
    with pytest.raises(NodeValidationError):
        n2.infer_schema({})


def test_concatnode_execute_normals_and_errors(node_ctor):
    n = node_ctor("ConcatNode", id="c_exec")
    n.infer_schema({"input1": make_schema("str"), "input2": make_schema("str")})
    out = n.execute({"input1": make_data("a"), "input2": make_data("b")})
    assert out["output"].payload == "ab"

    # error: execute before infer
    n2 = node_ctor("ConcatNode", id="c_err1")
    with pytest.raises(NodeExecutionError):
        n2.execute({"input1": make_data("x"), "input2": make_data("y")})

    # error: mismatched schema
    n3 = node_ctor("ConcatNode", id="c_err2")
    n3.infer_schema({"input1": make_schema("str"), "input2": make_schema("str")})
    with pytest.raises(NodeExecutionError):
        n3.execute({"input1": make_data(1), "input2": make_data("y")})
