import pytest

from server.models.exception import NodeParameterError
from server.models.types import ColType
from tests.nodes.utils import schema_from_coltypes


def test_advanceplotnode_requires_y_col(node_ctor):
    # For most plot types (e.g. scatter) y_col is required — omission should raise
    with pytest.raises(NodeParameterError):
        node_ctor("StatisticalPlotNode", id="ap_no_y", x_col="x", plot_type="scatter")


def test_advanceplotnode_allows_no_y_for_count(node_ctor):
    # plot_type 'count' may allow y_col to be None
    node = node_ctor("StatisticalPlotNode", id="ap_count", x_col="x", plot_type="count")
    # Should not raise in construction
    assert node is not None


def test_advanceplotnode_hint_respects_plot_type(node_ctor):
    node_cls = node_ctor("StatisticalPlotNode", id="ap_hint", x_col="x", plot_type="count")
    # prepare schema with various column types
    schema = schema_from_coltypes({"a": ColType.STR, "b": ColType.INT, "c": ColType.BOOL})
    # when current_params plot_type is 'count', y_col_choices should be omitted from hint
    hint = node_cls.get_hint("StatisticalPlotNode", {"input": schema}, {"plot_type": "count"})
    assert "x_col_choices" in hint
    assert "hue_col_choices" in hint
    # y_col_choices should not be present for 'count'
    assert "y_col_choices" not in hint


def test_advanceplotnode_process_various_types(node_ctor, test_file_root, monkeypatch):
    # monkeypatch seaborn plotting functions to no-op to exercise process branches

    for fn in [
        "scatterplot",
        "lineplot",
        "barplot",
        "countplot",
        "stripplot",
        "swarmplot",
        "boxplot",
        "violinplot",
        "histplot",
    ]:
        monkeypatch.setattr(f"seaborn.{fn}", lambda *a, **k: None)

    # create a table with numeric and categorical columns
    from tests.nodes.utils import table_from_dict
    tbl = table_from_dict({"x": ["a", "b", "a"], "y": [1, 2, 3], "h": ["g1", "g2", "g1"]})

    # test each plot type
    types = ["scatter", "bar", "count", "strip", "swarm", "box", "violin", "hist"]
    for t in types:
        # for count/hist y may be optional
        if t in {"count"}:
            node = node_ctor("StatisticalPlotNode", id=f"ap_{t}", x_col="x", plot_type=t)
            schema = schema_from_coltypes({"x": ColType.STR, "y": ColType.INT, "h": ColType.STR})
        else:
            node = node_ctor("StatisticalPlotNode", id=f"ap_{t}", x_col="x", y_col="y", hue_col="h", plot_type=t)
            schema = schema_from_coltypes({"x": ColType.STR, "y": ColType.INT, "h": ColType.STR})
        node.infer_schema({"input": schema})
        out = node.execute({"input": tbl})
        assert out["plot"].payload.format == "png"


def test_statisticalplot_line_and_hint(node_ctor):
    # placeholder: previously attempted to test an unsupported plot_type
    # StatisticalPlotNode does not accept 'line' as a plot_type literal.
    pass


def test_advanceplotnode_construction_normals_and_errors(node_ctor):
    # normals
    n1 = node_ctor("StatisticalPlotNode", id="ap_ok1", x_col="x", y_col="y", plot_type="scatter")
    n2 = node_ctor("StatisticalPlotNode", id="ap_ok2", x_col="x", plot_type="count")
    assert n1 is not None and n2 is not None

    # errors: missing/empty x_col
    import pytest
    with pytest.raises(Exception):
        node_ctor("StatisticalPlotNode", id="ap_err1", x_col="  ", y_col="y", plot_type="scatter")

    # errors: y_col None for non-count plot type
    with pytest.raises(Exception):
        node_ctor("StatisticalPlotNode", id="ap_err2", x_col="x", plot_type="scatter")

    # errors: validate parameters type mismatch when type attribute altered
    node = node_ctor("StatisticalPlotNode", id="ap_err3", x_col="x", y_col="y", plot_type="bar")
    node.type = "NotAdvance"
    from server.models.exception import NodeParameterError
    with pytest.raises(NodeParameterError):
        node.validate_parameters()


def test_advanceplotnode_hint_error_paths():
    import pytest

    from server.interpreter.nodes.base_node import BaseNode
    # unknown node type
    with pytest.raises(ValueError):
        BaseNode.get_hint("NoSuch", {}, {})

    # if hint raises, get_hint returns {}
    from server.interpreter.nodes.visualize import plot as viz_mod
    orig = viz_mod.StatisticalPlotNode.hint
    try:
        viz_mod.StatisticalPlotNode.hint = classmethod(lambda cls, a, b: (_ for _ in ()).throw(RuntimeError("boom"))) # type: ignore
        res = viz_mod.StatisticalPlotNode.get_hint("StatisticalPlotNode", {}, {})
        assert res == {}
    finally:
        viz_mod.StatisticalPlotNode.hint = orig


def test_advanceplotnode_hint_additional_normal(node_ctor):
    # when plot_type is not 'count' the hint should include y_col_choices
    node = node_ctor("StatisticalPlotNode", id="ap_hint2", x_col="x", y_col="y", plot_type="scatter")
    schema = schema_from_coltypes({"a": ColType.STR, "b": ColType.INT})
    hint = node.get_hint("StatisticalPlotNode", {"input": schema}, {"plot_type": "scatter"})
    assert "x_col_choices" in hint
    assert "y_col_choices" in hint
    assert "hue_col_choices" in hint


def test_advanceplotnode_infer_and_execute_error_cases(node_ctor):
    import pytest
    node = node_ctor("StatisticalPlotNode", id="ap_exec_err", x_col="x", y_col="y", plot_type="scatter")
    schema = schema_from_coltypes({"x": ColType.STR, "y": ColType.INT})

    # infer missing input port
    with pytest.raises(Exception):
        node.infer_schema({})

    # infer with bad types
    bad = schema_from_coltypes({"x": ColType.BOOL, "y": ColType.STR})
    with pytest.raises(Exception):
        node.infer_schema({"input": bad})

    # infer: extra input port should raise ValueError
    with pytest.raises(ValueError):
        node.infer_schema({"input": schema, "extra": schema})

    # execute before infer
    from tests.nodes.utils import table_from_dict
    tbl = table_from_dict({"x": ["a"], "y": [1]})
    with pytest.raises(Exception):
        node.execute({"input": tbl})

    # execute with mismatched input schema
    node.infer_schema({"input": schema})
    from tests.nodes.utils import make_data
    with pytest.raises(Exception):
        node.execute({"input": make_data(42)})


def test_statisticalplot_force_line_branch(node_ctor, monkeypatch):
    # create a valid StatisticalPlotNode then force-assign an unsupported 'line' plot_type
    from tests.nodes.utils import table_from_dict

    node = node_ctor("StatisticalPlotNode", id="sp_force", x_col="x", y_col="y", hue_col="h", plot_type="scatter")
    # bypass pydantic validation by setting attribute directly
    object.__setattr__(node, 'plot_type', 'line')

    # monkeypatch seaborn.lineplot to ensure branch executes without rendering
    monkeypatch.setattr('seaborn.lineplot', lambda *a, **k: None)

    schema = schema_from_coltypes({"x": ColType.INT, "y": ColType.INT, "h": ColType.STR})
    tbl = table_from_dict({"x": [1, 2, 3], "y": [2, 3, 4], "h": ["a", "b", "a"]})
    node.infer_schema({"input": schema})
    out = node.execute({"input": tbl})
    assert out["plot"].payload.format == "png"


def test_statisticalplot_hue_normalization(node_ctor):
    # when hue_col is NO_SPECIFIED_COL it should be normalized to None
    from server.models.schema import NO_SPECIFIED_COL
    node = node_ctor("StatisticalPlotNode", id="sp_hue", x_col="x", y_col="y", hue_col=NO_SPECIFIED_COL, plot_type="scatter")
    # validate_parameters runs during construction; hue_col should be normalized
    assert node.hue_col is None


def test_statisticalplot_hint_hist_omits_y(node_ctor):
    # when plot_type is 'hist', y_col_choices should be omitted per implementation
    node = node_ctor("StatisticalPlotNode", id="sp_hist_hint", x_col="x", plot_type="hist")
    schema = schema_from_coltypes({"x": ColType.STR, "y": ColType.INT, "h": ColType.STR})
    hint = node.get_hint("StatisticalPlotNode", {"input": schema}, {"plot_type": "hist"})
    assert "x_col_choices" in hint
    assert "hue_col_choices" in hint
    assert "y_col_choices" not in hint

