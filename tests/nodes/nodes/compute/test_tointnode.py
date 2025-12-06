from typing import Any

import pytest
from pydantic import ValidationError

from server.models.data import Data
from server.models.exception import NodeExecutionError, NodeParameterError
from server.models.schema import Schema


def _make_single_input_schema(t):
    return {"input": Schema(type=t)}


def test_toint_construct_accepts_integer_like(node_ctor):
    n1 = node_ctor("ToIntNode", id="t1", method="FLOOR")
    assert n1


def test_toint_construct_rejects_invalid(node_ctor):
    with pytest.raises(ValidationError):
        node_ctor("ToIntNode", id="t-bad")


def test_toint_construct_accepts_other_methods(node_ctor):
    node = node_ctor("ToIntNode", id="t2", method="CEIL")
    assert node.method == "CEIL"


def test_toint_construct_rejects_blank_id(node_ctor):
    with pytest.raises(NodeParameterError):
        node_ctor("ToIntNode", id="  ", method="FLOOR")


def test_toint_static_from_float(node_ctor):
    node = node_ctor("ToIntNode", id="t-int", method="FLOOR")
    out = node.infer_schema(_make_single_input_schema(Schema.Type.FLOAT))
    assert out == {"output": Schema(type=Schema.Type.INT)}


def test_toint_static_from_bool(node_ctor):
    node = node_ctor("ToIntNode", id="t-bool", method="FLOOR")
    out = node.infer_schema(_make_single_input_schema(Schema.Type.BOOL))
    assert out == {"output": Schema(type=Schema.Type.INT)}


def test_toint_static_rejects_unrelated_port(node_ctor):
    node = node_ctor("ToIntNode", id="t-err", method="FLOOR")
    with pytest.raises(ValueError):
        node.infer_schema({"input": Schema(type=Schema.Type.STR), "extra": Schema(type=Schema.Type.INT)})


def test_toint_static_rejects_incompatible_type(node_ctor):
    node = node_ctor("ToIntNode", id="t-inc", method="FLOOR")
    with pytest.raises(Exception):
        node.infer_schema({"input": Schema(type=Schema.Type.FILE)})


def test_toint_static_from_string(node_ctor):
    node = node_ctor("ToIntNode", id="t-str", method="ROUND")
    out = node.infer_schema(_make_single_input_schema(Schema.Type.STR))
    assert out == {"output": Schema(type=Schema.Type.INT)}


def test_toint_execute_bad_string(node_ctor):
    node = node_ctor("ToIntNode", id="t-exec", method="FLOOR")
    node.infer_schema(_make_single_input_schema(Schema.Type.STR))
    with pytest.raises(NodeExecutionError):
        node.process({"input": Data(payload="not-a-number")})


def test_toint_execute_valid(node_ctor):
    node = node_ctor("ToIntNode", id="t-good", method="FLOOR")
    node.infer_schema(_make_single_input_schema(Schema.Type.STR))
    out = node.process({"input": Data(payload="42")})
    assert out["output"].payload == 42


def test_toint_execute_bool_to_int(node_ctor):
    node = node_ctor("ToIntNode", id="t-b1", method="FLOOR")
    node.infer_schema(_make_single_input_schema(Schema.Type.BOOL))
    out = node.process({"input": Data(payload=True)})
    assert out["output"].payload == 1


def test_toint_execute_bad_runtime_type(node_ctor):
    node = node_ctor("ToIntNode", id="t-badrt", method="FLOOR")
    node.infer_schema(_make_single_input_schema(Schema.Type.STR))
    bad_payload: Any = object()
    with pytest.raises(ValidationError):
        Data(payload=bad_payload)


def test_toint_invalid_method_raises(node_ctor):
    node = node_ctor("ToIntNode", id="tint-bad", method="FLOOR")
    node.infer_schema({"input": Schema(type=Schema.Type.FLOAT)})
    # force invalid method
    node.method = "BAD"
    with pytest.raises(NodeExecutionError):
        node.process({"input": Data(payload=3.14)})


def test_toint_string_parse_fallback_float(node_ctor):
    node = node_ctor("ToIntNode", id="tint-str", method="FLOOR")
    node.infer_schema({"input": Schema(type=Schema.Type.STR)})
    out = node.process({"input": Data(payload="3.9")})
    assert out["output"].payload == 3
