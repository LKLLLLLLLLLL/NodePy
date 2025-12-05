from datetime import datetime, timezone

import pytest

from server.interpreter.nodes.base_node import BaseNode
from server.models.exception import (
    NodeExecutionError,
    NodeParameterError,
)
from server.models.schema import Schema


def test_datetimenode_hint_empty():
    assert BaseNode.get_hint("DateTimeNode", {}, {}) == {}


def test_datetimenode_construct_accepts_iso(node_ctor):
    now = datetime.now(tz=timezone.utc).isoformat()
    node = node_ctor("DateTimeNode", id="dt1", value=now)
    assert node._value is not None


def test_datetimenode_construct_rejects_bad_string(node_ctor):
    with pytest.raises(NodeParameterError):
        node_ctor("DateTimeNode", id="dt-bad", value="not-a-date")


def test_datetimenode_construct_rejects_blank_id(node_ctor):
    now = datetime.now(tz=timezone.utc).isoformat()
    with pytest.raises(NodeParameterError):
        node_ctor("DateTimeNode", id="   ", value=now)


def test_datetimenode_static_infers_datetime(node_ctor):
    now = datetime.now(tz=timezone.utc).isoformat()
    node = node_ctor("DateTimeNode", id="dt-static", value=now)
    out = node.infer_schema({})
    assert out == {"datetime": Schema(type=Schema.Type.DATETIME)}


def test_datetimenode_execute_emits_datetime(node_ctor):
    now = datetime.now(tz=timezone.utc).isoformat()
    node = node_ctor("DateTimeNode", id="dt-exec", value=now)
    node.infer_schema({})
    outputs = node.execute({})
    assert isinstance(outputs["datetime"].payload, datetime)


def test_datetimenode_execute_requires_inferred_schema(node_ctor):
    now = datetime.now(tz=timezone.utc).isoformat()
    node = node_ctor("DateTimeNode", id="dt-no-infer", value=now)
    with pytest.raises(NodeExecutionError):
        node.execute({})
