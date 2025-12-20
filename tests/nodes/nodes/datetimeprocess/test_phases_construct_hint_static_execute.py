import pytest
from pydantic import ValidationError

from server.interpreter.nodes.base_node import BaseNode
from server.models.data import Data
from server.models.exception import (
    NodeExecutionError,
    NodeParameterError,
    NodeValidationError,
)
from server.models.schema import Schema


def test_get_hint_defaults():
    # Base hint for datetime nodes should be empty (no special hints)
    assert BaseNode.get_hint("ToDatetimeNode", {}, {}) == {}
    assert BaseNode.get_hint("StrToDatetimeNode", {}, {}) == {}


def test_construction_and_param_validation(node_ctor):
    # Missing required literal param 'unit' should raise ValidationError
    with pytest.raises(ValidationError):
        node_ctor("ToDatetimeNode", id="bad1")

    # DatetimePrintNode requires 'format'
    with pytest.raises(ValidationError):
        node_ctor("DatetimePrintNode", id="bad2")

    # Blank id should raise NodeParameterError
    with pytest.raises(NodeParameterError):
        node_ctor("ToDatetimeNode", id="   ", unit="SECONDS")


def test_static_infer_success_and_failure(node_ctor):
    # ToDatetimeNode accepts INT/FLOAT
    node = node_ctor("ToDatetimeNode", id="st1", unit="SECONDS")
    out = node.infer_schema({"value": Schema(type=Schema.Type.INT)})
    assert out == {"datetime": Schema(type=Schema.Type.DATETIME)}

    # wrong input type should raise NodeValidationError
    node = node_ctor("ToDatetimeNode", id="st2", unit="SECONDS")
    with pytest.raises(NodeValidationError):
        node.infer_schema({"value": Schema(type=Schema.Type.STR)})

    # StrToDatetimeNode expects STR
    node = node_ctor("StrToDatetimeNode", id="st3")
    out = node.infer_schema({"value": Schema(type=Schema.Type.STR)})
    assert out == {"datetime": Schema(type=Schema.Type.DATETIME)}

    with pytest.raises(NodeValidationError):
        node.infer_schema({"value": Schema(type=Schema.Type.FLOAT)})

    # DatetimePrintNode expects DATETIME
    node = node_ctor("DatetimePrintNode", id="st4", format="%Y")
    out = node.infer_schema({"datetime": Schema(type=Schema.Type.DATETIME)})
    assert out == {"output": Schema(type=Schema.Type.STR)}

    with pytest.raises(NodeValidationError):
        node.infer_schema({"datetime": Schema(type=Schema.Type.STR)})

    # DatetimeToTimestampNode expects DATETIME
    node = node_ctor("DatetimeToTimestampNode", id="st5", unit="SECONDS")
    out = node.infer_schema({"datetime": Schema(type=Schema.Type.DATETIME)})
    assert out == {"timestamp": Schema(type=Schema.Type.FLOAT)}

    with pytest.raises(NodeValidationError):
        node.infer_schema({"datetime": Schema(type=Schema.Type.INT)})

    # DatetimeComputeNode expects DATETIME and INT/FLOAT
    node = node_ctor("DatetimeComputeNode", id="st6", op="ADD", unit="DAYS")
    out = node.infer_schema({"datetime": Schema(type=Schema.Type.DATETIME), "value": Schema(type=Schema.Type.FLOAT)})
    assert out == {"result": Schema(type=Schema.Type.DATETIME)}

    with pytest.raises(NodeValidationError):
        node.infer_schema({"datetime": Schema(type=Schema.Type.DATETIME), "value": Schema(type=Schema.Type.STR)})

    # DatetimeDiffNode expects two DATETIME inputs
    node = node_ctor("DatetimeDiffNode", id="st7", unit="DAYS")
    out = node.infer_schema({"datetime_x": Schema(type=Schema.Type.DATETIME), "datetime_y": Schema(type=Schema.Type.DATETIME)})
    assert out == {"difference": Schema(type=Schema.Type.FLOAT)}

    with pytest.raises(NodeValidationError):
        node.infer_schema({"datetime_x": Schema(type=Schema.Type.DATETIME)})


def test_execute_success_and_runtime_mismatch(node_ctor):
    # Use infer_schema then execute for proper runtime checking
    node = node_ctor("DatetimeToTimestampNode", id="ex1", unit="SECONDS")
    node.infer_schema({"datetime": Schema(type=Schema.Type.DATETIME)})
    # correct data
    from datetime import datetime
    dt = datetime(1970, 1, 1, tzinfo=None)
    # ensure tzinfo; the node expects aware datetime; create with utc
    import server.config as _cfg
    dt = datetime(1970, 1, 1, tzinfo=_cfg.DEFAULT_TIMEZONE)
    out = node.execute({"datetime": Data(payload=dt)})
    assert "timestamp" in out

    # runtime schema mismatch should raise NodeExecutionError
    node = node_ctor("DatetimeToTimestampNode", id="ex2", unit="SECONDS")
    node.infer_schema({"datetime": Schema(type=Schema.Type.DATETIME)})
    with pytest.raises(NodeExecutionError):
        node.execute({"datetime": Data(payload=123)})
