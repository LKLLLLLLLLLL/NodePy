import pandas as pd
import pytest

from server.models.data import Data, Table
from server.models.exception import NodeParameterError, NodeValidationError
from server.models.types import ColType


def make_table(df, col_types):
    return Table(df=df, col_types=col_types)


def test_rolling_node_mean(node_ctor, context):
    df = pd.DataFrame({"v": [1.0, 2.0, 3.0, 4.0]})
    table = make_table(df, {"v": ColType.FLOAT})
    node = node_ctor("RollingNode", id="n_roll", col="v", window_size=2, method="mean")

    out_schema = node.infer_schema({"table": Data(payload=table).extract_schema()})
    # mean should produce float
    assert out_schema["table"].tab.col_types[node.result_col] == ColType.FLOAT

    out = node.execute({"table": Data(payload=table)})
    out_table = out["table"].payload
    assert node.result_col in out_table.df.columns


def test_rolling_node_window_invalid_raises(node_ctor, context):
    with pytest.raises(NodeParameterError):
        node_ctor("RollingNode", id="n_roll2", col="v", window_size=0, method="mean")


def test_rolling_node_infer_schema_wrong_type(node_ctor, context):
    df = pd.DataFrame({"v": ["a", "b"]})
    table = make_table(df, {"v": ColType.STR})
    node = node_ctor("RollingNode", id="n_roll3", col="v", window_size=2, method="sum")
    with pytest.raises(NodeValidationError):
        node.infer_schema({"table": Data(payload=table).extract_schema()})


def test_rolling_process_without_infer_asserts(node_ctor, context):
    df = pd.DataFrame({"v": [1, 2, 3]})
    table = make_table(df, {"v": ColType.INT})
    node = node_ctor("RollingNode", id="n_roll4", col="v", window_size=2, method="sum")
    with pytest.raises(AssertionError):
        node.process({"table": Data(payload=table)})
