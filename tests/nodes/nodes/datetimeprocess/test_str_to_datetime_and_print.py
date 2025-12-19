from datetime import datetime

import pytest

from server.config import DEFAULT_TIMEZONE
from server.models.data import Data
from server.models.exception import NodeExecutionError


def test_str_to_datetime_iso_and_with_tz(node_ctor):
    node = node_ctor('StrToDatetimeNode', id='s1')
    out = node.process({'value': Data(payload='2020-01-02T03:04:05')})
    assert isinstance(out['datetime'].payload, datetime)
    # without tz in string, should get DEFAULT_TIMEZONE
    assert out['datetime'].payload.tzinfo == DEFAULT_TIMEZONE

    node = node_ctor('StrToDatetimeNode', id='s2')
    out = node.process({'value': Data(payload='2020-01-02T03:04:05+00:00')})
    assert out['datetime'].payload.tzinfo is not None


def test_str_to_datetime_bad_string_raises(node_ctor):
    node = node_ctor('StrToDatetimeNode', id='s3')
    with pytest.raises(NodeExecutionError):
        node.process({'value': Data(payload='not-a-date')})


def test_datetime_print_formats(node_ctor):
    dt = datetime(2021, 12, 31, 23, 59, 59, tzinfo=DEFAULT_TIMEZONE)
    node = node_ctor('DatetimePrintNode', id='p1', format='%Y-%m-%d')
    out = node.process({'datetime': Data(payload=dt)})
    assert out['output'].payload == '2021-12-31'

    node = node_ctor('DatetimePrintNode', id='p2', format='%H:%M:%S')
    out = node.process({'datetime': Data(payload=dt)})
    assert out['output'].payload == '23:59:59'


def test_str_to_datetime_non_str_raises(node_ctor):
    node = node_ctor('StrToDatetimeNode', id='s4')
    with pytest.raises(AssertionError):
        node.process({'value': Data(payload=123)})


def test_datetime_print_non_datetime_and_missing_format(node_ctor):
    node = node_ctor('DatetimePrintNode', id='p3', format='%Y')
    with pytest.raises(AssertionError):
        node.process({'datetime': Data(payload='2021')})

    # missing/invalid format should raise (TypeError or similar)
    node = node_ctor('DatetimePrintNode', id='p4', format='%Y')
    node.__dict__['format'] = None
    with pytest.raises(Exception):
        node.process({'datetime': Data(payload=datetime.now(tz=DEFAULT_TIMEZONE))})


def test_str_to_datetime_invalid_month_raises(node_ctor):
    node = node_ctor('StrToDatetimeNode', id='s5')
    # invalid month should cause parsing error
    with pytest.raises(NodeExecutionError):
        node.process({'value': Data(payload='2020-13-01T00:00:00')})


def test_datetime_print_invalid_format_type_raises(node_ctor):
    node = node_ctor('DatetimePrintNode', id='p5', format='%Y')
    # force a non-string format
    node.__dict__['format'] = 123
    with pytest.raises(Exception):
        node.process({'datetime': Data(payload=datetime.now(tz=DEFAULT_TIMEZONE))})
