import pandas as pd
import pytest

from server.models.data import Data, Table
from server.models.exception import NodeParameterError, NodeValidationError
from server.models.types import ColType


def make_table(df, col_types):
    return Table(df=df, col_types=col_types)


def test_pct_change_basic(node_ctor, context):
    df = pd.DataFrame({"v": [10.0, 20.0, 30.0]})
    table = make_table(df, {"v": ColType.FLOAT})
    node = node_ctor("PctChangeNode", id="n_pct", col="v")

    out_schema = node.infer_schema({"table": Data(payload=table).extract_schema()})
    assert out_schema["table"].tab.col_types[node.result_col] == ColType.FLOAT

    out = node.execute({"table": Data(payload=table)})
    out_table = out["table"].payload
    assert node.result_col in out_table.df.columns


def test_pct_change_construct_invalid_col(node_ctor, context):
    with pytest.raises(NodeParameterError):
        node_ctor("PctChangeNode", id="n_pct2", col=" ")


def test_pct_change_infer_missing_col_raises(node_ctor, context):
    df = pd.DataFrame({"x": [1, 2]})
    table = make_table(df, {"x": ColType.INT})
    node = node_ctor("PctChangeNode", id="n_pct3", col="v")
    with pytest.raises(NodeValidationError):
        node.infer_schema({"table": Data(payload=table).extract_schema()})


def test_pct_change_process_without_infer_asserts(node_ctor, context):
    df = pd.DataFrame({"v": [1.0, 2.0]})
    table = make_table(df, {"v": ColType.FLOAT})
    node = node_ctor("PctChangeNode", id="n_pct4", col="v")
    with pytest.raises(AssertionError):
        node.process({"table": Data(payload=table)})
