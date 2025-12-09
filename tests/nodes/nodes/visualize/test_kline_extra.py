import sys

from server.models.exception import NodeParameterError
from server.models.types import ColType
from tests.nodes.utils import schema_from_coltypes, table_from_dict


def _install_fake_mplfinance_capture(monkeypatch, record: dict):
    import types

    mod = types.ModuleType("mplfinance")

    def make_marketcolors(up=None, down=None, **kwargs):
        record['up'] = up
        record['down'] = down
        return {"fake": True}

    def make_mpf_style(*args, **kwargs):
        return {"style": True}

    def plot(*args, **kwargs):
        # capture title kwarg
        record['title'] = kwargs.get('title')
        import matplotlib.pyplot as _plt
        fig = _plt.figure(figsize=(8, 4))
        ax = fig.add_subplot(111)
        return (fig, [ax])

    mod.make_marketcolors = make_marketcolors
    mod.make_mpf_style = make_mpf_style
    mod.plot = plot

    monkeypatch.setitem(sys.modules, 'mplfinance', mod)


def test_kline_validate_type_mismatch(node_ctor):
    node = node_ctor("KLinePlotNode", id="k_tm", x_col="dt", open_col="o", high_col="h", low_col="l", close_col="c", style_mode="CN")
    node.type = "NotKLine"
    with __import__("pytest").raises(NodeParameterError):
        node.validate_parameters()


def test_kline_volume_whitespace_normalizes(node_ctor):
    # volume_col of only spaces should normalize to None during construction
    node = node_ctor("KLinePlotNode", id="k_vol", x_col="dt", open_col="o", high_col="h", low_col="l", close_col="c", volume_col="   ", style_mode="CN")
    assert node.volume_col is None


def test_kline_default_title_and_style_colors(node_ctor, test_file_root, monkeypatch):
    record = {}
    _install_fake_mplfinance_capture(monkeypatch, record)

    node = node_ctor("KLinePlotNode", id="k_def", x_col="dt", open_col="o", high_col="h", low_col="l", close_col="c", style_mode="EN")

    tbl = table_from_dict({
        "dt": [__import__("pandas").Timestamp("2021-01-01")],
        "o": [1.0],
        "h": [1.2],
        "l": [0.9],
        "c": [1.1],
    })

    schema = schema_from_coltypes({
        "dt": ColType.DATETIME,
        "o": ColType.FLOAT,
        "h": ColType.FLOAT,
        "l": ColType.FLOAT,
        "c": ColType.FLOAT,
    })

    node.infer_schema({"input": schema})
    out = node.execute({"input": tbl})
    assert out["plot"].payload.format == "png"

    # default title should be used when title is None
    assert record.get('title') == "K-Line Plot"
    # for EN style: up should be green (#26a69a) and down red (#ef5350)
    assert record.get('up') == "#26a69a"
    assert record.get('down') == "#ef5350"
