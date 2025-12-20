import pandas as pd
import pytest

from server.models.data import Data, Table
from server.models.exception import NodeParameterError, NodeValidationError
from server.models.types import ColType


def make_table(df, col_types):
    return Table(df=df, col_types=col_types)


def test_diff_node_basic(node_ctor, context):
    df = pd.DataFrame({"x": [10.0, 12.0, 15.0]})
    table = make_table(df, {"x": ColType.FLOAT})
    node = node_ctor("DiffNode", id="n_diff", col="x")

    out_schema = node.infer_schema({"table": Data(payload=table).extract_schema()})
    assert "table" in out_schema

    out = node.execute({"table": Data(payload=table)})
    out_table = out["table"].payload
    assert isinstance(out_table, Table)
    # length should be n-1
    assert len(out_table.df) == 2
    # check diff values (floats)
    assert out_table.df.iloc[0]["x_diff"] == pytest.approx(2.0)
    assert out_table.df.iloc[1]["x_diff"] == pytest.approx(3.0)


def test_diff_node_new_col_name_collision(node_ctor, context):
    # if x_diff already exists, infer_output_schemas should pick a different name
    df = pd.DataFrame({"x": [1.0, 2.0], "x_diff": [0.0, 0.0]})
    table = make_table(df, {"x": ColType.FLOAT, "x_diff": ColType.FLOAT})
    node = node_ctor("DiffNode", id="n_diff2", col="x")
    # current implementation will attempt to append 'x_diff' and raise ValueError
    with pytest.raises(ValueError):
        node.infer_schema({"table": Data(payload=table).extract_schema()})


def test_diff_node_infer_missing_col_raises(node_ctor, context):
    df = pd.DataFrame({"y": [1, 2, 3]})
    table = make_table(df, {"y": ColType.INT})
    node = node_ctor("DiffNode", id="n_diff3", col="x")
    with pytest.raises(NodeValidationError):
        node.infer_schema({"table": Data(payload=table).extract_schema()})


def test_diff_process_without_infer_asserts(node_ctor, context):
    df = pd.DataFrame({"x": [1, 2]})
    table = make_table(df, {"x": ColType.INT})
    node = node_ctor("DiffNode", id="n_diff4", col="x")
    with pytest.raises(AssertionError):
        node.process({"table": Data(payload=table)})
