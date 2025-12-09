import pytest

from server.models.types import ColType
from tests.nodes.utils import schema_from_coltypes, table_from_dict


def test_quickplot_nonbar_multiple_y(node_ctor, test_file_root):
    # no 'bar' types present -> use x values for plotting (area + line)
    node = node_ctor("QuickPlotNode", id="p_nb", x_col="x", y_col=["a", "b"], plot_type=["area", "line"]) 
    tbl = table_from_dict({"x": [1, 2, 3], "a": [2, 3, 4], "b": [1, 0, 2]})
    schema = schema_from_coltypes({"x": ColType.INT, "a": ColType.INT, "b": ColType.INT})
    node.infer_schema({"input": schema})
    out = node.execute({"input": tbl})
    assert out["plot"].payload.format == "png"


def test_dualaxis_hint_accepts_table_key(node_ctor):
    # DualAxisPlotNode.hint looks for key 'table' in some code paths
    from server.interpreter.nodes.visualize import plot as plot_mod
    node = node_ctor("DualAxisPlotNode", id="d_hint_table", x_col="x", left_y_col="l", left_plot_type="line", right_y_col="r", right_plot_type="bar")
    schema = schema_from_coltypes({"x": ColType.INT, "l": ColType.INT, "r": ColType.INT})
    hint = plot_mod.DualAxisPlotNode.get_hint("DualAxisPlotNode", {"table": schema}, {})
    assert "x_col_choices" in hint
    assert "left_y_col_choices" in hint
    assert "right_y_col_choices" in hint


def test_statisticalplot_hint_hist_omits_y(node_ctor):
    # when plot_type is 'hist', y_col_choices should be omitted per implementation
    node = node_ctor("StatisticalPlotNode", id="sp_hist_hint", x_col="x", plot_type="hist")
    schema = schema_from_coltypes({"x": ColType.STR, "y": ColType.INT, "h": ColType.STR})
    hint = node.get_hint("StatisticalPlotNode", {"input": schema}, {"plot_type": "hist"})
    assert "x_col_choices" in hint
    assert "hue_col_choices" in hint
    assert "y_col_choices" not in hint
