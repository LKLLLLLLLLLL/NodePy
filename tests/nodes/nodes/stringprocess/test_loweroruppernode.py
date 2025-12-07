import pytest

from server.models.exception import (
    NodeExecutionError,
    NodeParameterError,
    NodeValidationError,
)
from server.models.schema import Schema
from tests.nodes.utils import make_data, make_schema


def test_loweroruppernode_construction_and_errors(node_ctor):
    n1 = node_ctor("LowerOrUpperNode", id="lu1", to_case="lower")
    assert n1.to_case == "lower"
    n2 = node_ctor("LowerOrUpperNode", id="lu2", to_case="upper")
    assert n2.to_case == "upper"

    # error: invalid to_case value should be caught by pydantic/validate
    with pytest.raises(Exception):
        node_ctor("LowerOrUpperNode", id="lu_bad", to_case="flip")

    # error: mutated type
    node = node_ctor("LowerOrUpperNode", id="lu_ok", to_case="lower")
    node.type = "NotLowerOrUpper"
    with pytest.raises(NodeParameterError):
        node.validate_parameters()


def test_loweroruppernode_hint_and_infer(node_ctor):
    node = node_ctor("LowerOrUpperNode", id="lu_hint", to_case="lower")
    assert isinstance(node.get_hint("LowerOrUpperNode", {"input": make_schema("str")}, {}), dict)

    # infer returns output string schema
    out = node.infer_schema({"input": make_schema("str")})
    assert out["output"].type == Schema.Type.STR

    # infer missing input -> NodeValidationError
    node2 = node_ctor("LowerOrUpperNode", id="lu_inf_err", to_case="upper")
    with pytest.raises(NodeValidationError):
        node2.infer_schema({})


def test_loweroruppernode_execute_normals_and_errors(node_ctor):
    n = node_ctor("LowerOrUpperNode", id="lu_exec1", to_case="lower")
    n.infer_schema({"input": make_schema("str")})
    out = n.execute({"input": make_data("HeLLo")})
    assert out["output"].payload == "hello"

    n2 = node_ctor("LowerOrUpperNode", id="lu_exec2", to_case="upper")
    n2.infer_schema({"input": make_schema("str")})
    out2 = n2.execute({"input": make_data("HeLLo")})
    assert out2["output"].payload == "HELLO"

    # error: execute before infer
    n3 = node_ctor("LowerOrUpperNode", id="lu_err1", to_case="lower")
    with pytest.raises(NodeExecutionError):
        n3.execute({"input": make_data("a")})

    # error: mismatched input schema
    n4 = node_ctor("LowerOrUpperNode", id="lu_err2", to_case="upper")
    n4.infer_schema({"input": make_schema("str")})
    with pytest.raises(NodeExecutionError):
        n4.execute({"input": make_data(123)})
