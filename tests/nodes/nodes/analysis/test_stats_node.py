import pandas as pd
import pytest

from server.models.data import Data, Table
from server.models.exception import NodeParameterError, NodeValidationError
from server.models.types import ColType


def make_table(df, col_types):
    return Table(df=df, col_types=col_types)


def test_stats_node_infer_and_execute(node_ctor, context):
    df = pd.DataFrame({"a": [1, 2, 3]})
    table = make_table(df, {"a": ColType.INT})

    node = node_ctor("StatsNode", id="n_stats", col="a")

    out_schema = node.infer_schema({"table": Data(payload=table).extract_schema()})
    # mean and std are float, count is int, sum/min/max same as input (int)
    assert out_schema["mean"].type == out_schema["std"].type == out_schema["quantile_25"].type == out_schema["quantile_50"].type == out_schema["quantile_75"].type
    assert out_schema["count"].type == out_schema["min"].type == out_schema["max"].type == out_schema["sum"].type

    outputs = node.execute({"table": Data(payload=table)})
    assert outputs["mean"].payload == pytest.approx(2.0)
    assert outputs["count"].payload == 3
    assert outputs["sum"].payload == 6


def test_stats_node_construct_invalid_col_raises(node_ctor, context):
    with pytest.raises(NodeParameterError):
        node_ctor("StatsNode", id="n_stats2", col="   ")


def test_stats_node_infer_schema_wrong_type_raises(node_ctor, context):
    df = pd.DataFrame({"a": ["x", "y"]})
    table = make_table(df, {"a": ColType.STR})
    node = node_ctor("StatsNode", id="n_stats3", col="a")
    with pytest.raises(NodeValidationError):
        node.infer_schema({"table": Data(payload=table).extract_schema()})


def test_stats_node_process_bad_payload_asserts(node_ctor, context):
    node = node_ctor("StatsNode", id="n_stats4", col="a")
    # call process directly with non-Table payload should assert
    with pytest.raises(AssertionError):
        node.process({"table": Data(payload=123)})
