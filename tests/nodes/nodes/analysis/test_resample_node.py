import pandas as pd
import pytest

from server.models.data import Data, Table
from server.models.exception import NodeExecutionError, NodeParameterError, NodeValidationError
from server.models.types import ColType


def make_table(df, col_types):
    return Table(df=df, col_types=col_types)


def test_resample_node_sum(node_ctor, context):
    times = pd.to_datetime(["2020-01-01T00:00:00", "2020-01-01T00:00:30", "2020-01-02T00:00:00"])
    df = pd.DataFrame({"time": times, "v": [1, 2, 3]})
    table = make_table(df, {"time": ColType.DATETIME, "v": ColType.INT})
    node = node_ctor("ResampleNode", id="n_res", col="time", frequency="D", method="sum")

    out_schema = node.infer_schema({"table": Data(payload=table).extract_schema()})
    assert "table" in out_schema

    out = node.execute({"table": Data(payload=table)})
    out_table = out["table"].payload
    # since we resampled by day, expect two rows (2020-01-01 and 2020-01-02)
    assert len(out_table.df) >= 2


def test_resample_node_construct_invalid_col_raises(node_ctor, context):
    with pytest.raises(NodeParameterError):
        node_ctor("ResampleNode", id="n_res2", col="   ", frequency="D", method="sum")


def test_resample_infer_wrong_type_raises(node_ctor, context):
    df = pd.DataFrame({"time": ["a", "b"], "v": [1, 2]})
    table = make_table(df, {"time": ColType.STR, "v": ColType.INT})
    node = node_ctor("ResampleNode", id="n_res3", col="time", frequency="D", method="sum")
    with pytest.raises(NodeValidationError):
        node.infer_schema({"table": Data(payload=table).extract_schema()})


def test_resample_process_unsupported_method_raises(node_ctor, context):
    times = pd.to_datetime(["2020-01-01T00:00:00", "2020-01-01T01:00:00"])
    df = pd.DataFrame({"time": times, "v": [1, 2]})
    table = make_table(df, {"time": ColType.DATETIME, "v": ColType.INT})
    node = node_ctor("ResampleNode", id="n_res4", col="time", frequency="H", method="mean")
    node.method = "unsupported_method"
    with pytest.raises(NodeExecutionError):
        node.process({"table": Data(payload=table)})
