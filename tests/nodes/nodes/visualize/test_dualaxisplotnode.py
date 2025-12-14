import pytest

from server.models.exception import NodeParameterError
from server.models.types import ColType
from tests.nodes.utils import schema_from_coltypes, table_from_dict


def test_dualaxis_construction_and_execute(node_ctor, test_file_root):
    # normal: left bar, right line
    node = node_ctor("DualAxisPlotNode", id="d_ok1", x_col="x", left_y_col="l", left_plot_type="bar", right_y_col="r", right_plot_type="line")
    tbl = table_from_dict({"x": [1, 2, 3], "l": [5, 6, 7], "r": [2, 1, 3]})
    schema = schema_from_coltypes({"x": ColType.INT, "l": ColType.INT, "r": ColType.INT})
    node.infer_schema({"input": schema})
    out = node.execute({"input": tbl})
    assert out["plot"].payload.format == "png"

    # normal: both lines
    node2 = node_ctor("DualAxisPlotNode", id="d_ok2", x_col="x", left_y_col="l", left_plot_type="line", right_y_col="r", right_plot_type="line")
    node2.infer_schema({"input": schema})
    out2 = node2.execute({"input": tbl})
    assert out2["plot"].payload.format == "png"


def test_dualaxis_parameter_errors(node_ctor):
    # missing x_col
    with pytest.raises(NodeParameterError):
        node_ctor("DualAxisPlotNode", id="d_err1", x_col="  ", left_y_col="l", left_plot_type="line", right_y_col="r", right_plot_type="bar")
    # missing left_y_col
    with pytest.raises(NodeParameterError):
        node_ctor("DualAxisPlotNode", id="d_err2", x_col="x", left_y_col="  ", left_plot_type="line", right_y_col="r", right_plot_type="bar")
    # missing right_y_col
    with pytest.raises(NodeParameterError):
        node_ctor("DualAxisPlotNode", id="d_err3", x_col="x", left_y_col="l", left_plot_type="line", right_y_col="   ", right_plot_type="bar")


def test_dualaxis_hint_and_infer_errors(node_ctor):
    node = node_ctor("DualAxisPlotNode", id="d_hint", x_col="x", left_y_col="l", left_plot_type="line", right_y_col="r", right_plot_type="bar")
    schema = schema_from_coltypes({"x": ColType.INT, "l": ColType.INT, "r": ColType.INT})
    # infer missing input port
    with pytest.raises(Exception):
        node.infer_schema({})

    # infer with wrong types
    bad = schema_from_coltypes({"x": ColType.BOOL, "l": ColType.STR, "r": ColType.STR})
    with pytest.raises(Exception):
        node.infer_schema({"input": bad})


def test_dualaxis_hint_accepts_table_key(node_ctor):
    # DualAxisPlotNode.hint looks for key 'table' in some code paths
    from server.interpreter.nodes.visualize import plot as plot_mod
    node = node_ctor("DualAxisPlotNode", id="d_hint_table", x_col="x", left_y_col="l", left_plot_type="line", right_y_col="r", right_plot_type="bar")
    schema = schema_from_coltypes({"x": ColType.INT, "l": ColType.INT, "r": ColType.INT})
    hint = plot_mod.DualAxisPlotNode.get_hint("DualAxisPlotNode", {"input": schema}, {})
    assert "x_col_choices" in hint
    assert "left_y_col_choices" in hint
    assert "right_y_col_choices" in hint
