from datetime import datetime, timedelta, timezone

import pytest
from pandas import DataFrame
from pydantic import ValidationError

from server.models.data import Table
from server.models.exception import (
    NodeExecutionError,
    NodeParameterError,
    NodeValidationError,
)
from server.models.schema import ColType, Schema


def test_klinenode_construct_rejects_blank_symbol(node_ctor):
    with pytest.raises(NodeParameterError):
        node_ctor("KlineNode", id="k1", data_type="stock", symbol="   ")


def test_klinenode_construct_accepts_iso_times(node_ctor):
    start = (datetime.now(tz=timezone.utc) - timedelta(days=1)).isoformat()
    end = datetime.now(tz=timezone.utc).isoformat()
    node = node_ctor("KlineNode", id="k2", data_type="stock", symbol="A", start_time=start, end_time=end)
    assert node._start_time_dt is not None and node._end_time_dt is not None


def test_klinenode_static_requires_start_and_end_via_inputs(node_ctor):
    node = node_ctor("KlineNode", id="k3", data_type="stock", symbol="A")
    with pytest.raises(NodeValidationError):
        node.infer_schema({})


def test_klinenode_static_accepts_inputs(node_ctor):
    node = node_ctor("KlineNode", id="k4", data_type="stock", symbol="A")
    out = node.infer_schema({"start_time": Schema(type=Schema.Type.DATETIME), "end_time": Schema(type=Schema.Type.DATETIME)})
    assert "kline_data" in out


def test_klinenode_execute_calls_financial_manager(node_ctor, monkeypatch):
    node = node_ctor("KlineNode", id="k5", data_type="stock", symbol="A")
    node._start_time_dt = datetime.now(tz=timezone.utc)
    node._end_time_dt = node._start_time_dt + timedelta(minutes=2)

    def fake_get_data(symbol, data_type, start_time, end_time, interval):
        df = DataFrame([{"Open Time": start_time, "Open": 1.0, "High": 1.0, "Low": 1.0, "Close": 1.0, "Volume": 0.0}])
        return Table(df=df, col_types={"Open Time": ColType.DATETIME, "Open": ColType.FLOAT, "High": ColType.FLOAT, "Low": ColType.FLOAT, "Close": ColType.FLOAT, "Volume": ColType.FLOAT})

    monkeypatch.setattr(node.global_config, "financial_data_manager", node.global_config.financial_data_manager)
    setattr(node.global_config.financial_data_manager, "get_data", fake_get_data)

    out = node.process({})
    assert "kline_data" in out


def test_klinenode_execute_rejects_start_after_end(node_ctor):
    node = node_ctor("KlineNode", id="k6", data_type="stock", symbol="A")
    node._start_time_dt = datetime.now(tz=timezone.utc)
    node._end_time_dt = node._start_time_dt - timedelta(minutes=1)
    with pytest.raises(NodeExecutionError):
        node.process({})


def test_klinenode_construct_rejects_invalid_interval(node_ctor):
    with pytest.raises((NodeParameterError, ValidationError)):
        node_ctor("KlineNode", id="k-interval-bad", data_type="stock", symbol="A", interval="5s")


def test_klinenode_execute_malformed_table_from_manager_raises(node_ctor, monkeypatch):
    node = node_ctor("KlineNode", id="k7", data_type="stock", symbol="A")
    node._start_time_dt = datetime.now(tz=timezone.utc)
    node._end_time_dt = node._start_time_dt + timedelta(minutes=1)

    def fake_get_data_bad(symbol, data_type, start_time, end_time, interval):
        df = DataFrame([{"Open": 1.0}])
        return Table(df=df, col_types={})

    monkeypatch.setattr(node.global_config, "financial_data_manager", node.global_config.financial_data_manager)
    setattr(node.global_config.financial_data_manager, "get_data", fake_get_data_bad)

    with pytest.raises(NodeExecutionError):
        node.process({})
