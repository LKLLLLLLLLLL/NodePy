from datetime import datetime, timedelta

import pytest

from server.config import DEFAULT_TIMEZONE
from server.models.data import Data
from server.models.exception import NodeExecutionError


def test_datetime_to_timestamp_seconds_and_hours(node_ctor):
    epoch = datetime(1970, 1, 1, tzinfo=DEFAULT_TIMEZONE)
    dt = epoch + timedelta(seconds=3600)
    node = node_ctor('DatetimeToTimestampNode', id='ts1', unit='SECONDS')
    out = node.process({'datetime': Data(payload=dt)})
    assert out['timestamp'].payload == 3600.0

    node = node_ctor('DatetimeToTimestampNode', id='ts2', unit='HOURS')
    out = node.process({'datetime': Data(payload=dt)})
    assert out['timestamp'].payload == 1.0


def test_datetime_to_timestamp_days_and_minutes(node_ctor):
    epoch = datetime(1970, 1, 1, tzinfo=DEFAULT_TIMEZONE)
    dt = epoch + timedelta(days=2, minutes=30)
    node = node_ctor('DatetimeToTimestampNode', id='ts3', unit='DAYS')
    out = node.process({'datetime': Data(payload=dt)})
    assert out['timestamp'].payload == pytest.approx(2.0208333333333335)

    node = node_ctor('DatetimeToTimestampNode', id='ts4', unit='MINUTES')
    out = node.process({'datetime': Data(payload=dt)})
    assert out['timestamp'].payload == pytest.approx((2 * 24 * 60) + 30)


def test_datetime_to_timestamp_invalid_unit_raises(node_ctor):
    epoch = datetime(1970, 1, 1, tzinfo=DEFAULT_TIMEZONE)
    node = node_ctor('DatetimeToTimestampNode', id='ts5', unit='SECONDS')
    node.__dict__['unit'] = 'UNKNOWN'
    with pytest.raises(NodeExecutionError):
        node.process({'datetime': Data(payload=epoch)})


def test_datetime_to_timestamp_non_datetime_and_naive(node_ctor):
    node = node_ctor('DatetimeToTimestampNode', id='ts6', unit='SECONDS')
    with pytest.raises(AssertionError):
        node.process({'datetime': Data(payload='not-dt')})

    # naive datetime (no tzinfo) should raise when subtracting aware epoch
    naive = datetime(1970, 1, 1)
    node = node_ctor('DatetimeToTimestampNode', id='ts7', unit='SECONDS')
    with pytest.raises(TypeError):
        node.process({'datetime': Data(payload=naive)})
