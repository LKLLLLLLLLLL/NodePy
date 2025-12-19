from datetime import datetime, timedelta

import pytest
from pydantic import ValidationError

from server.config import DEFAULT_TIMEZONE
from server.models.data import Data
from server.models.exception import NodeExecutionError


def test_to_datetime_seconds_and_hours(node_ctor):
    node = node_ctor('ToDatetimeNode', id='t1', unit='SECONDS')
    out = node.process({'value': Data(payload=10)})
    expected = datetime(1970, 1, 1, tzinfo=DEFAULT_TIMEZONE) + timedelta(seconds=10)
    assert out['datetime'].payload == expected

    node = node_ctor('ToDatetimeNode', id='t2', unit='HOURS')
    out = node.process({'value': Data(payload=1)})
    expected = datetime(1970, 1, 1, tzinfo=DEFAULT_TIMEZONE) + timedelta(hours=1)
    assert out['datetime'].payload == expected


def test_to_datetime_days_and_minutes_float(node_ctor):
    node = node_ctor('ToDatetimeNode', id='t3', unit='DAYS')
    out = node.process({'value': Data(payload=1.5)})
    expected = datetime(1970, 1, 1, tzinfo=DEFAULT_TIMEZONE) + timedelta(days=1.5)
    assert out['datetime'].payload == expected

    node = node_ctor('ToDatetimeNode', id='t4', unit='MINUTES')
    out = node.process({'value': Data(payload=30)})
    expected = datetime(1970, 1, 1, tzinfo=DEFAULT_TIMEZONE) + timedelta(minutes=30)
    assert out['datetime'].payload == expected


def test_to_datetime_invalid_unit_raises(node_ctor):
    node = node_ctor('ToDatetimeNode', id='t5', unit='SECONDS')
    node.__dict__['unit'] = 'UNKNOWN'
    with pytest.raises(NodeExecutionError):
        node.process({'value': Data(payload=1)})


def test_to_datetime_non_numeric_raises(node_ctor):
    node = node_ctor('ToDatetimeNode', id='t6', unit='SECONDS')
    with pytest.raises(AssertionError):
        node.process({'value': Data(payload='not-a-number')})

    with pytest.raises(ValidationError):
        node.process({'value': Data(payload=None)})
