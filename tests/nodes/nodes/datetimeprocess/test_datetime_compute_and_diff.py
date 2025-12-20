from datetime import datetime, timedelta

import pytest
from pydantic import ValidationError

from server.config import DEFAULT_TIMEZONE
from server.models.data import Data
from server.models.exception import NodeExecutionError


def test_datetime_compute_add_and_sub(node_ctor):
    base = datetime(2022, 1, 1, 0, 0, 0, tzinfo=DEFAULT_TIMEZONE)
    node = node_ctor('DatetimeComputeNode', id='c1', op='ADD', unit='DAYS')
    out = node.process({'datetime': Data(payload=base), 'value': Data(payload=2)})
    assert out['result'].payload == base + timedelta(days=2)

    node = node_ctor('DatetimeComputeNode', id='c2', op='SUB', unit='HOURS')
    out = node.process({'datetime': Data(payload=base), 'value': Data(payload=3)})
    assert out['result'].payload == base - timedelta(hours=3)


def test_datetime_compute_invalid_op_or_unit_raises(node_ctor):
    base = datetime(2022, 1, 1, tzinfo=DEFAULT_TIMEZONE)
    node = node_ctor('DatetimeComputeNode', id='c3', op='ADD', unit='SECONDS')
    node.__dict__['op'] = 'UNKNOWN'
    with pytest.raises(NodeExecutionError):
        node.process({'datetime': Data(payload=base), 'value': Data(payload=1)})

    node = node_ctor('DatetimeComputeNode', id='c4', op='ADD', unit='SECONDS')
    node.__dict__['unit'] = 'UNKNOWN'
    with pytest.raises(NodeExecutionError):
        node.process({'datetime': Data(payload=base), 'value': Data(payload=1)})


def test_datetime_diff_days_hours_minutes_seconds(node_ctor):
    a = datetime(2022, 1, 3, 12, 0, 0, tzinfo=DEFAULT_TIMEZONE)
    b = datetime(2022, 1, 1, 12, 0, 0, tzinfo=DEFAULT_TIMEZONE)
    node = node_ctor('DatetimeDiffNode', id='d1', unit='DAYS')
    out = node.process({'datetime_x': Data(payload=a), 'datetime_y': Data(payload=b)})
    assert out['difference'].payload == 2.0

    node = node_ctor('DatetimeDiffNode', id='d2', unit='HOURS')
    out = node.process({'datetime_x': Data(payload=a), 'datetime_y': Data(payload=b)})
    assert out['difference'].payload == pytest.approx(48.0)

    node = node_ctor('DatetimeDiffNode', id='d3', unit='MINUTES')
    out = node.process({'datetime_x': Data(payload=a), 'datetime_y': Data(payload=b)})
    assert out['difference'].payload == pytest.approx(48.0 * 60)

    node = node_ctor('DatetimeDiffNode', id='d4', unit='SECONDS')
    out = node.process({'datetime_x': Data(payload=a), 'datetime_y': Data(payload=b)})
    assert out['difference'].payload == pytest.approx(48.0 * 3600)


def test_datetime_diff_invalid_unit_raises(node_ctor):
    a = datetime(2022, 1, 2, tzinfo=DEFAULT_TIMEZONE)
    b = datetime(2022, 1, 1, tzinfo=DEFAULT_TIMEZONE)
    node = node_ctor('DatetimeDiffNode', id='d5', unit='DAYS')
    node.__dict__['unit'] = 'UNKNOWN'
    with pytest.raises(NodeExecutionError):
        node.process({'datetime_x': Data(payload=a), 'datetime_y': Data(payload=b)})


def test_datetime_compute_non_datetime_or_non_numeric(node_ctor):
    node = node_ctor('DatetimeComputeNode', id='c5', op='ADD', unit='DAYS')
    with pytest.raises(AssertionError):
        node.process({'datetime': Data(payload='not-dt'), 'value': Data(payload=1)})

    with pytest.raises(AssertionError):
        node.process({'datetime': Data(payload=datetime.now(tz=DEFAULT_TIMEZONE)), 'value': Data(payload='x')})


def test_datetime_diff_non_datetime_inputs(node_ctor):
    node = node_ctor('DatetimeDiffNode', id='d6', unit='DAYS')
    with pytest.raises(AssertionError):
        node.process({'datetime_x': Data(payload='x'), 'datetime_y': Data(payload=datetime.now(tz=DEFAULT_TIMEZONE))})

    with pytest.raises(ValidationError):
        node.process({'datetime_x': Data(payload=datetime.now(tz=DEFAULT_TIMEZONE)), 'datetime_y': Data(payload=None)})
