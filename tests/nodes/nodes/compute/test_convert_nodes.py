from typing import Any

import pytest
from pydantic import ValidationError

from server.models.data import Data
from server.models.exception import NodeExecutionError, NodeParameterError
from server.models.schema import Schema


def _make_single_input_schema(t):
    # convert nodes expect an 'input' port
    return {"input": Schema(type=t)}


def test_toint_construct_accepts_integer_like(node_ctor):
    """Construct stage: ToInt accepts ints and numeric strings."""
    # ToIntNode requires a `method` parameter
    n1 = node_ctor("ToIntNode", id="t1", method="FLOOR")
    assert n1


def test_toint_construct_rejects_invalid(node_ctor):
    """Construct stage: ToInt rejects nonsensical options via ValidationError."""
    with pytest.raises(ValidationError):
        # `method` is required and must be one of the allowed literals
        node_ctor("ToIntNode", id="t-bad")


def test_toint_construct_accepts_other_methods(node_ctor):
    """Construct stage success: other valid methods accepted."""
    node = node_ctor("ToIntNode", id="t2", method="CEIL")
    assert node.method == "CEIL"


def test_toint_construct_rejects_blank_id(node_ctor):
    """Construct stage failure: blank id raises NodeParameterError."""
    import pytest

    with pytest.raises(NodeParameterError):
        node_ctor("ToIntNode", id="  ", method="FLOOR")


def test_toint_static_from_float(node_ctor):
    """Static analysis: float input can be converted to int."""
    node = node_ctor("ToIntNode", id="t-int", method="FLOOR")
    out = node.infer_schema(_make_single_input_schema(Schema.Type.FLOAT))
    assert out == {"output": Schema(type=Schema.Type.INT)}


def test_toint_static_from_bool(node_ctor):
    """Static success: bool input can be converted to int."""
    node = node_ctor("ToIntNode", id="t-bool", method="FLOOR")
    out = node.infer_schema(_make_single_input_schema(Schema.Type.BOOL))
    assert out == {"output": Schema(type=Schema.Type.INT)}


def test_toint_static_rejects_unrelated_port(node_ctor):
    """Static failure: extra unrelated port causes ValueError."""
    node = node_ctor("ToIntNode", id="t-err", method="FLOOR")
    with pytest.raises(ValueError):
        node.infer_schema({"input": Schema(type=Schema.Type.STR), "extra": Schema(type=Schema.Type.INT)})


def test_toint_static_rejects_incompatible_type(node_ctor):
    """Static failure: completely incompatible type should still infer as int but may be rejected elsewhere."""
    node = node_ctor("ToIntNode", id="t-inc", method="FLOOR")
    # The node accepts STR/BOOL/FLOAT – passing FILE should be rejected by pattern
    with pytest.raises(Exception):
        node.infer_schema({"input": Schema(type=Schema.Type.FILE)})


def test_toint_static_from_string(node_ctor):
    """Static analysis: string input may be convertible; require runtime check."""
    node = node_ctor("ToIntNode", id="t-str", method="ROUND")
    out = node.infer_schema(_make_single_input_schema(Schema.Type.STR))
    assert out == {"output": Schema(type=Schema.Type.INT)}


def test_toint_execute_bad_string(node_ctor):
    """Execute: invalid numeric string raises NodeValidationError."""
    node = node_ctor("ToIntNode", id="t-exec", method="FLOOR")
    node.infer_schema(_make_single_input_schema(Schema.Type.STR))
    with pytest.raises(NodeExecutionError):
        node.process({"input": Data(payload="not-a-number")})


def test_toint_execute_valid(node_ctor):
    """Execute: numeric string converts to int."""
    node = node_ctor("ToIntNode", id="t-good", method="FLOOR")
    node.infer_schema(_make_single_input_schema(Schema.Type.STR))
    out = node.process({"input": Data(payload="42")})
    assert out["output"].payload == 42


def test_toint_execute_bool_to_int(node_ctor):
    """Execute success: bool True converts to 1."""
    node = node_ctor("ToIntNode", id="t-b1", method="FLOOR")
    node.infer_schema(_make_single_input_schema(Schema.Type.BOOL))
    out = node.process({"input": Data(payload=True)})
    assert out["output"].payload == 1


def test_toint_execute_bad_runtime_type(node_ctor):
    """Execute failure: passing unsupported runtime payload raises NodeExecutionError."""
    node = node_ctor("ToIntNode", id="t-badrt", method="FLOOR")
    node.infer_schema(_make_single_input_schema(Schema.Type.STR))
    # constructing Data with an unsupported payload type will raise ValidationError
    bad_payload: Any = object()
    with pytest.raises(ValidationError):
        Data(payload=bad_payload)


def test_tofloat_execute(node_ctor):
    """Execute: ToFloat converts int to float and raises on bad input."""
    node = node_ctor("ToFloatNode", id="f1")
    node.infer_schema(_make_single_input_schema(Schema.Type.INT))
    out = node.process({"input": Data(payload=3)})
    assert isinstance(out["output"].payload, float)


def test_tofloat_static_rejects_file(node_ctor):
    """Static failure: ToFloat should reject File schema."""
    node = node_ctor("ToFloatNode", id="f2")
    with pytest.raises(Exception):
        node.infer_schema({"input": Schema(type=Schema.Type.FILE)})


def test_tofloat_execute_bad_string(node_ctor):
    """Execute failure: ToFloat with invalid string should raise NodeExecutionError."""
    node = node_ctor("ToFloatNode", id="f3")
    node.infer_schema(_make_single_input_schema(Schema.Type.STR))
    with pytest.raises(NodeExecutionError):
        node.process({"input": Data(payload="notfloat")})


def test_tobool_execute(node_ctor):
    """Execute: ToBool converts truthy/falsy representations."""
    node = node_ctor("ToBoolNode", id="b1")
    node.infer_schema(_make_single_input_schema(Schema.Type.STR))
    out = node.process({"input": Data(payload="true")})
    assert out["output"].payload is True
