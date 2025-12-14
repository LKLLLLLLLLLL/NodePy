import pandas as pd
import pytest

from server.models.exception import (
    NodeExecutionError,
    NodeParameterError,
    NodeValidationError,
)
from server.models.schema import NO_SPECIFIED_COL, Schema
from server.models.types import ColType
from tests.nodes.utils import schema_from_coltypes, table_from_dict


def test_kline_construction_and_errors(node_ctor):
    # normal construction
    n = node_ctor(
        "KlinePlotNode",
        id="k1",
        title="My Kline",
        x_col="time",
        open_col="o",
        high_col="h",
        low_col="l",
        close_col="c",
        volume_col="v",
        style_mode="CN",
    )
    assert n is not None

    # error: empty id
    with pytest.raises(NodeParameterError):
        node_ctor(
            "KlinePlotNode",
            id="   ",
            title="t",
            x_col="time",
            open_col="o",
            high_col="h",
            low_col="l",
            close_col="c",
            style_mode="CN",
        )

    # error: mutated type
    n2 = node_ctor(
        "KlinePlotNode",
        id="k_ok",
        title="t",
        x_col="time",
        open_col="o",
        high_col="h",
        low_col="l",
        close_col="c",
        style_mode="CN",
    )
    n2.type = "NotKline"
    with pytest.raises(NodeParameterError):
        n2.validate_parameters()


def test_kline_hint_and_infer(node_ctor):
    n = node_ctor(
        "KlinePlotNode",
        id="k_hint",
        title=None,
        x_col="time",
        open_col="o",
        high_col="h",
        low_col="l",
        close_col="c",
        volume_col="v",
        style_mode="CN",
    )

    # build a schema matching expected column types
    col_types = {
        "time": ColType.DATETIME,
        "o": ColType.FLOAT,
        "h": ColType.FLOAT,
        "l": ColType.FLOAT,
        "c": ColType.FLOAT,
        "v": ColType.FLOAT,
    }
    schema = schema_from_coltypes(col_types)

    # hint should be a dict and contain choice lists
    hint = n.get_hint("KlinePlotNode", {"input": schema}, {})
    assert isinstance(hint, dict)
    assert "x_col_choices" in hint

    # infer schema should produce a file output
    out = n.infer_schema({"input": schema})
    assert out.get("kline_plot") is not None
    assert out["kline_plot"].type == Schema.Type.FILE

    # error: missing required ports
    n2 = node_ctor(
        "KlinePlotNode",
        id="k_inf_err",
        title=None,
        x_col="time",
        open_col="o",
        high_col="h",
        low_col="l",
        close_col="c",
        style_mode="CN",
    )
    with pytest.raises(NodeValidationError):
        n2.infer_schema({})

def test_validate_parameter_empty_fields(node_ctor):
    # x_col empty
    with pytest.raises(NodeParameterError):
        node_ctor(
            "KlinePlotNode",
            id="kx",
            title=None,
            x_col="   ",
            open_col="o",
            high_col="h",
            low_col="l",
            close_col="c",
            style_mode="CN",
        )

    # open_col empty
    with pytest.raises(NodeParameterError):
        node_ctor(
            "KlinePlotNode",
            id="ko",
            title=None,
            x_col="time",
            open_col="",
            high_col="h",
            low_col="l",
            close_col="c",
            style_mode="CN",
        )

    # high_col empty
    with pytest.raises(NodeParameterError):
        node_ctor(
            "KlinePlotNode",
            id="kh",
            title=None,
            x_col="time",
            open_col="o",
            high_col="",
            low_col="l",
            close_col="c",
            style_mode="CN",
        )

    # low_col empty
    with pytest.raises(NodeParameterError):
        node_ctor(
            "KlinePlotNode",
            id="kl",
            title=None,
            x_col="time",
            open_col="o",
            high_col="h",
            low_col="",
            close_col="c",
            style_mode="CN",
        )

    # close_col empty
    with pytest.raises(NodeParameterError):
        node_ctor(
            "KlinePlotNode",
            id="kc",
            title=None,
            x_col="time",
            open_col="o",
            high_col="h",
            low_col="l",
            close_col="",
            style_mode="CN",
        )


def test_volume_and_title_normalization_and_port_def(node_ctor):
    # blank volume and blank title should be normalized to None
    n = node_ctor(
        "KlinePlotNode",
        id="k_norm",
        title="   ",
        x_col="time",
        open_col="o",
        high_col="h",
        low_col="l",
        close_col="c",
        volume_col="   ",
        style_mode="CN",
    )
    assert n.title is None
    assert n.volume_col is None

    # NO_SPECIFIED_COL should also normalize to None
    n2 = node_ctor(
        "KlinePlotNode",
        id="k_nospec",
        title=None,
        x_col="time",
        open_col="o",
        high_col="h",
        low_col="l",
        close_col="c",
        volume_col=NO_SPECIFIED_COL,
        style_mode="CN",
    )
    assert n2.volume_col is None

    # port_def should include volume when provided and exclude when None
    n3 = node_ctor(
        "KlinePlotNode",
        id="k_with_v",
        title=None,
        x_col="time",
        open_col="o",
        high_col="h",
        low_col="l",
        close_col="c",
        volume_col="v",
        style_mode="CN",
    )
    in_ports, _ = n3.port_def()
    # extract table_columns mapping
    pc = in_ports[0].accept.table_columns
    assert "v" in pc

    n4 = node_ctor(
        "KlinePlotNode",
        id="k_no_v",
        title=None,
        x_col="time",
        open_col="o",
        high_col="h",
        low_col="l",
        close_col="c",
        volume_col=None,
        style_mode="CN",
    )
    in_ports2, _ = n4.port_def()
    pc2 = in_ports2[0].accept.table_columns
    assert "v" not in pc2


def test_hint_with_non_table_schema(node_ctor):
    # when input schema is present but not a TABLE, hint keys exist but choices empty
    n = node_ctor(
        "KlinePlotNode",
        id="k_hint2",
        title=None,
        x_col="time",
        open_col="o",
        high_col="h",
        low_col="l",
        close_col="c",
        volume_col=None,
        style_mode="CN",
    )
    hint = n.get_hint("KlinePlotNode", {"input": Schema(type=Schema.Type.STR)}, {})
    assert isinstance(hint, dict)
    assert hint.get("x_col_choices") == []
    assert hint.get("volume_col_choices") == [NO_SPECIFIED_COL]


def test_kline_execute_normals_and_errors(node_ctor):
    n = node_ctor(
        "KlinePlotNode",
        id="k_exec",
        title="T",
        x_col="time",
        open_col="o",
        high_col="h",
        low_col="l",
        close_col="c",
        volume_col="v",
        style_mode="US",
    )

    # prepare a small table with proper dtypes
    times = [pd.Timestamp("2021-01-01"), pd.Timestamp("2021-01-02"), pd.Timestamp("2021-01-03")]
    data = {
        "time": times,
        "o": [10.0, 11.0, 10.5],
        "h": [10.5, 11.5, 11.0],
        "l": [9.5, 10.8, 10.2],
        "c": [10.2, 11.2, 10.8],
        "v": [100, 120, 80],
    }

    tbl = table_from_dict(data, col_types={
        "time": ColType.DATETIME,
        "o": ColType.FLOAT,
        "h": ColType.FLOAT,
        "l": ColType.FLOAT,
        "c": ColType.FLOAT,
        "v": ColType.INT,
        "_index": ColType.INT,
    })

    # infer schema and execute
    schema = schema_from_coltypes({
        "time": ColType.DATETIME,
        "o": ColType.FLOAT,
        "h": ColType.FLOAT,
        "l": ColType.FLOAT,
        "c": ColType.FLOAT,
        "v": ColType.INT,
        "_index": ColType.INT,
    })
    n.infer_schema({"input": schema})
    out = n.execute({"input": tbl})
    assert "kline_plot" in out
    file_obj = out["kline_plot"].payload
    assert hasattr(file_obj, "format")
    assert file_obj.format == "png"

    # error: empty input table should raise during execute
    empty_tbl = table_from_dict({"time": [], "o": [], "h": [], "l": [], "c": []}, col_types={
        "time": ColType.DATETIME,
        "o": ColType.FLOAT,
        "h": ColType.FLOAT,
        "l": ColType.FLOAT,
        "c": ColType.FLOAT,
        "_index": ColType.INT,
    })
    n2 = node_ctor(
        "KlinePlotNode",
        id="k_empty",
        title=None,
        x_col="time",
        open_col="o",
        high_col="h",
        low_col="l",
        close_col="c",
        style_mode="CN",
    )
    n2.infer_schema({"input": schema})
    with pytest.raises(NodeExecutionError):
        n2.execute({"input": empty_tbl})
