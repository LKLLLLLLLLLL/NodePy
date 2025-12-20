import pandas as pd
import pytest

from server.models.data import Data, Table
from server.models.exception import NodeParameterError, NodeValidationError
from server.models.types import ColType


def make_table(df, col_types):
    return Table(df=df, col_types=col_types)


def test_cumulative_cumsum(node_ctor, context):
    df = pd.DataFrame({"v": [1.0, 2.0, 3.0]})
    table = make_table(df, {"v": ColType.FLOAT})
    node = node_ctor("CumulativeNode", id="n_cum", col="v", method="cumsum")

    out_schema = node.infer_schema({"table": Data(payload=table).extract_schema()})
    assert node.result_col in out_schema["table"].tab.col_types

    out = node.execute({"table": Data(payload=table)})
    out_table = out["table"].payload
    assert out_table.df[node.result_col].tolist() == [1.0, 3.0, 6.0]


def test_cumulative_construct_invalid_col(node_ctor, context):
    with pytest.raises(NodeParameterError):
        node_ctor("CumulativeNode", id="n_cum2", col="  ", method="cumsum")


def test_cumulative_infer_wrong_type(node_ctor, context):
    df = pd.DataFrame({"v": ["a", "b"]})
    table = make_table(df, {"v": ColType.STR})
    node = node_ctor("CumulativeNode", id="n_cum3", col="v", method="cumprod")
    with pytest.raises(NodeValidationError):
        node.infer_schema({"table": Data(payload=table).extract_schema()})


def test_cumulative_process_without_infer_asserts(node_ctor, context):
    df = pd.DataFrame({"v": [1, 2]})
    table = make_table(df, {"v": ColType.INT})
    node = node_ctor("CumulativeNode", id="n_cum4", col="v", method="cummin")
    with pytest.raises(AssertionError):
        node.process({"table": Data(payload=table)})
