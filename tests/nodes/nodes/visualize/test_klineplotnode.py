import sys

from server.models.exception import NodeParameterError
from server.models.types import ColType
from tests.nodes.utils import schema_from_coltypes, table_from_dict


def _install_fake_mplfinance(monkeypatch):
    # create a fake mplfinance module with required APIs
    import types

    mod = types.ModuleType("mplfinance")

    def make_marketcolors(*args, **kwargs):
        return {"fake": True}

    def make_mpf_style(*args, **kwargs):
        return {"style": True}

    class _FakeFig:
        pass

    def plot(*args, **kwargs):
        # return a real matplotlib Figure so plt.close(fig) works
        import matplotlib.pyplot as _plt
        fig = _plt.figure(figsize=(10, 6))
        ax = fig.add_subplot(111)
        return (fig, [ax])

    mod.make_marketcolors = make_marketcolors
    mod.make_mpf_style = make_mpf_style
    mod.plot = plot

    monkeypatch.setitem(sys.modules, 'mplfinance', mod)


def test_kline_construct_and_execute(node_ctor, test_file_root, monkeypatch):
    _install_fake_mplfinance(monkeypatch)

    node = node_ctor(
        "KLinePlotNode",
        id="k1",
        title="K",
        x_col="dt",
        open_col="o",
        high_col="h",
        low_col="l",
        close_col="c",
        volume_col="v",
        style_mode="CN",
    )

    tbl = table_from_dict({
        "dt": [
            __import__("pandas").Timestamp("2020-01-01"),
            __import__("pandas").Timestamp("2020-01-02"),
        ],
        "o": [1.0, 2.0],
        "h": [1.5, 2.5],
        "l": [0.8, 1.8],
        "c": [1.2, 2.1],
        "v": [100, 150],
    })
    schema = schema_from_coltypes({
        "dt": ColType.DATETIME,
        "o": ColType.FLOAT,
        "h": ColType.FLOAT,
        "l": ColType.FLOAT,
        "c": ColType.FLOAT,
        "v": ColType.INT,
    })

    out_schema = node.infer_schema({"input": schema})
    assert "plot" in out_schema
    out = node.execute({"input": tbl})
    f = out["plot"].payload
    assert f.format == "png"


def test_kline_parameter_errors(node_ctor):
    import pytest

    # missing required field should raise during construction
    with pytest.raises(NodeParameterError):
        node_ctor("KLinePlotNode", id="k_err", x_col="", open_col="o", high_col="h", low_col="l", close_col="c", style_mode="CN")

    with pytest.raises(NodeParameterError):
        node_ctor("KLinePlotNode", id="k_err2", x_col="dt", open_col="", high_col="h", low_col="l", close_col="c", style_mode="CN")


def test_kline_hint(node_ctor):
    node = node_ctor("KLinePlotNode", id="k_hint", x_col="dt", open_col="o", high_col="h", low_col="l", close_col="c", style_mode="CN")
    schema = schema_from_coltypes({"dt": ColType.DATETIME, "o": ColType.FLOAT, "h": ColType.FLOAT, "l": ColType.FLOAT, "c": ColType.FLOAT})
    hint = node.get_hint("KLinePlotNode", {"input": schema}, {})
    assert isinstance(hint.get("x_col_choices"), list)
    assert isinstance(hint.get("open_col_choices"), list)
