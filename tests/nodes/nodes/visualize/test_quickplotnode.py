import os

from server.models.exception import NodeParameterError, NodeValidationError
from server.models.schema import Schema
from server.models.types import ColType
from tests.nodes.utils import schema_from_coltypes, table_from_dict


def test_plotnode_construct_and_infer(node_ctor):
    node = node_ctor("QuickPlotNode", id="p_plot", x_col="x", y_col=["y"], plot_type=["scatter"]) 
    schema = schema_from_coltypes({"x": ColType.STR, "y": ColType.INT})
    out = node.infer_schema({"input": schema})
    assert "plot" in out
    assert out["plot"].type == Schema.Type.FILE
    assert out["plot"].file.format == "png"


def test_plotnode_execute_writes_file(node_ctor, test_file_root):
    node = node_ctor("QuickPlotNode", id="p_exec", x_col="x", y_col=["y"], plot_type=["bar"], title="t")
    tbl = table_from_dict({"x": ["a", "b"], "y": [1, 2]})
    schema = schema_from_coltypes({"x": ColType.STR, "y": ColType.INT})
    node.infer_schema({"input": schema})
    out = node.execute({"input": tbl})
    assert "plot" in out
    f = out["plot"].payload
    assert f.format == "png"
    assert f.filename == f"{node.id}.png"
    expected_key = f"{node.id}_{f.filename}"
    expected_path = os.path.join(test_file_root, expected_key)
    assert os.path.exists(expected_path)


def test_plotnode_rejects_empty_cols(node_ctor):
    with __import__("pytest").raises(NodeParameterError):
        node_ctor("QuickPlotNode", id="p_err", x_col="  ", y_col=["y"], plot_type=["line"]) 
    with __import__("pytest").raises(NodeParameterError):
        node_ctor("QuickPlotNode", id="p_err2", x_col="x", y_col=["   "], plot_type=["line"]) 


def test_plotnode_infer_rejects_bad_types(node_ctor):
    # x must be int/float/str and y must be int/float
    node = node_ctor("QuickPlotNode", id="p_val", x_col="x", y_col=["y"], plot_type=["scatter"]) 
    bad_schema = schema_from_coltypes({"x": ColType.BOOL, "y": ColType.STR})
    with __import__("pytest").raises(NodeValidationError):
        node.infer_schema({"input": bad_schema})


def test_plotnode_area_type(node_ctor, test_file_root):
    # area chart uses x as labels and y as numeric; ensure it runs
    node = node_ctor("QuickPlotNode", id="p_area", x_col="lbl", y_col=["val"], plot_type=["area"]) 
    tbl = table_from_dict({"lbl": ["a", "b"], "val": [10, 20]})
    schema = schema_from_coltypes({"lbl": ColType.STR, "val": ColType.INT})
    node.infer_schema({"input": schema})
    out = node.execute({"input": tbl})
    f = out["plot"].payload
    assert f.format == "png"


def test_plotnode_scatter_and_line(node_ctor, test_file_root):
    # scatter with numeric y and string x
    node_s = node_ctor("QuickPlotNode", id="p_sc", x_col="x", y_col=["y"], plot_type=["scatter"]) 
    tbl_s = table_from_dict({"x": ["a", "b"], "y": [1, 2]})
    schema_s = schema_from_coltypes({"x": ColType.STR, "y": ColType.INT})
    node_s.infer_schema({"input": schema_s})
    out_s = node_s.execute({"input": tbl_s})
    assert out_s["plot"].payload.format == "png"

    # line with numeric x and y
    node_l = node_ctor("QuickPlotNode", id="p_line", x_col="x", y_col=["y"], plot_type=["line"]) 
    tbl_l = table_from_dict({"x": [1, 2, 3], "y": [2, 3, 4]})
    schema_l = schema_from_coltypes({"x": ColType.INT, "y": ColType.INT})
    node_l.infer_schema({"input": schema_l})
    out_l = node_l.execute({"input": tbl_l})
    assert out_l["plot"].payload.format == "png"


def test_plotnode_title_trim_and_missing_input(node_ctor):
    # title of only spaces should be normalized to None
    node = node_ctor("QuickPlotNode", id="p_trim", x_col="x", y_col=["y"], plot_type=["bar"], title="   ")
    assert node.title is None

    # missing input port should raise validation error during infer
    from server.models.exception import NodeValidationError
    good_schema = schema_from_coltypes({"x": ColType.INT, "y": ColType.INT})
    with __import__("pytest").raises(NodeValidationError):
        node.infer_schema({})


def test_plotnode_hint(node_ctor):
    node = node_ctor("QuickPlotNode", id="p_hint", x_col="a", y_col=["b"], plot_type=["scatter"]) 
    schema = schema_from_coltypes({"a": ColType.STR, "b": ColType.INT, "c": ColType.FLOAT})
    hint = node.get_hint("QuickPlotNode", {"input": schema}, {})
    assert "x_col_choices" in hint and isinstance(hint["x_col_choices"], list)
    assert "y_col_choices" in hint and isinstance(hint["y_col_choices"], list)


def test_plotnode_validate_wrong_type_raises(node_ctor):
    # mutate the node.type to an incorrect value to exercise the type check
    node = node_ctor("QuickPlotNode", id="p_wrongtype", x_col="x", y_col=["y"], plot_type=["scatter"]) 
    node.type = "NotAPlotNode"
    from server.models.exception import NodeParameterError
    with __import__("pytest").raises(NodeParameterError):
        node.validate_parameters()


def test_plotnode_title_triggers_plt_title(monkeypatch, node_ctor, test_file_root):
    # ensure plt.title is called when title is provided
    called = {}

    def fake_title(val):
        called['title'] = val

    import matplotlib.pyplot as plt
    monkeypatch.setattr(plt, 'title', fake_title)

    node = node_ctor("QuickPlotNode", id="p_tcall", x_col="x", y_col=["y"], plot_type=["bar"], title="MyPlot")
    tbl = table_from_dict({"x": ["a", "b"], "y": [1, 2]})
    schema = schema_from_coltypes({"x": ColType.STR, "y": ColType.INT})
    node.infer_schema({"input": schema})
    out = node.execute({"input": tbl})
    # ensure file was written and title was invoked with provided string
    assert out["plot"].payload.format == "png"
    assert called.get('title') == "MyPlot"


def test_plotnode_construction_two_normal_cases(node_ctor):
    # normal constructions for two different plot types
    n1 = node_ctor("QuickPlotNode", id="p_c1", x_col="a", y_col=["b"], plot_type=["scatter"]) 
    n2 = node_ctor("QuickPlotNode", id="p_c2", x_col="lbl", y_col=["val"], plot_type=["area"]) 
    assert n1 is not None and n2 is not None


def test_plotnode_hint_additional_cases(node_ctor):
    # normal: hint returns expected column lists when schema present
    node = node_ctor("QuickPlotNode", id="p_hint2", x_col="a", y_col=["b"], plot_type=["bar"]) 
    schema = schema_from_coltypes({"a": ColType.STR, "b": ColType.INT, "c": ColType.FLOAT})
    hint = node.get_hint("QuickPlotNode", {"input": schema}, {})
    assert isinstance(hint.get("x_col_choices"), list)
    assert isinstance(hint.get("y_col_choices"), list)


def test_plotnode_hint_error_cases():
    import pytest
    # unknown node type should raise
    with pytest.raises(ValueError):
        from server.interpreter.nodes.base_node import BaseNode
        BaseNode.get_hint("NonExistentNode", {}, {})

    # if hint implementation raises, get_hint should swallow and return {}
    from server.interpreter.nodes.visualize import plot as plot_mod
    orig = plot_mod.QuickPlotNode.hint
    def _bad_hint(*a, **k):
        raise RuntimeError("boom")
    try:
        plot_mod.QuickPlotNode.hint = classmethod(lambda cls, a, b: _bad_hint())  # type: ignore
        res = plot_mod.QuickPlotNode.get_hint("QuickPlotNode", {}, {})
        assert res == {}
    finally:
        plot_mod.QuickPlotNode.hint = orig

    # malformed input schemas should also be handled gracefully by get_hint
    res2 = plot_mod.QuickPlotNode.get_hint("QuickPlotNode", {"input": object()}, {}) # type: ignore
    assert res2 == {}


def test_plotnode_hint_direct_raise(node_ctor):
    # direct call to the class hint should raise if the implementation raises
    from server.interpreter.nodes.visualize import plot as plot_mod
    orig = plot_mod.QuickPlotNode.hint
    try:
        def _raise_hint(cls, schema, params):
            raise RuntimeError("hint direct fail")

        plot_mod.QuickPlotNode.hint = classmethod(_raise_hint)  # type: ignore
        import pytest
        with pytest.raises(RuntimeError):
            # call the classmethod directly (not via get_hint which swallows)
            plot_mod.QuickPlotNode.hint({}, {})  # type: ignore
    finally:
        plot_mod.QuickPlotNode.hint = orig


def test_plotnode_hint_direct_raise_value_error(node_ctor):
    # ensure ValueError propagates when hint raises ValueError directly
    from server.interpreter.nodes.visualize import plot as plot_mod
    orig = plot_mod.QuickPlotNode.hint
    try:
        def _raise_valerr(cls, schema, params):
            raise ValueError("bad hint")

        plot_mod.QuickPlotNode.hint = classmethod(_raise_valerr)  # type: ignore
        import pytest
        with pytest.raises(ValueError):
            plot_mod.QuickPlotNode.hint({}, {})  # type: ignore
    finally:
        plot_mod.QuickPlotNode.hint = orig


def test_plotnode_infer_error_extra_port(node_ctor):
    # providing an extra input port should raise ValueError per base_node logic
    node = node_ctor("QuickPlotNode", id="p_extra", x_col="x", y_col=["y"], plot_type=["bar"]) 
    schema = schema_from_coltypes({"x": ColType.STR, "y": ColType.INT})
    with __import__("pytest").raises(ValueError):
        node.infer_schema({"input": schema, "extra": schema})


def test_plotnode_execute_error_cases(node_ctor, monkeypatch):
    import pytest
    # setup node and schema
    node = node_ctor("QuickPlotNode", id="p_exec_err", x_col="x", y_col=["y"], plot_type=["bar"]) 
    schema = schema_from_coltypes({"x": ColType.STR, "y": ColType.INT})

    # 1) execute before infer -> NodeExecutionError
    with pytest.raises(Exception):
        node.execute({})

    # 2) execute with mismatched input schema -> NodeExecutionError
    node.infer_schema({"input": schema})
    # craft Data with wrong schema by using make_data of a primitive
    from tests.nodes.utils import make_data
    bad = {"input": make_data(123)}
    with pytest.raises(Exception):
        node.execute(bad)

    # 3) process raises runtime error should propagate
    def _bad_process(_):
        raise RuntimeError("process fail")
    node2 = node_ctor("QuickPlotNode", id="p_proc_err", x_col="x", y_col=["y"], plot_type=["bar"]) 
    node2.infer_schema({"input": schema})
    # monkeypatch the class process method so it's restored after test
    def _bad_process_method(self, _input):
        _bad_process(_input)
    monkeypatch.setattr(node2.__class__, 'process', _bad_process_method, raising=True)
    from tests.nodes.utils import table_from_dict
    tbl = table_from_dict({"x": ["a"], "y": [1]})
    with pytest.raises(RuntimeError):
        node2.execute({"input": tbl})


def test_quickplot_grouped_and_mixed(node_ctor, test_file_root):
    # grouped bar plot with two y columns
    node = node_ctor("QuickPlotNode", id="p_group", x_col="x", y_col=["a", "b"], plot_type=["bar", "bar"])
    tbl = table_from_dict({"x": ["g1", "g2", "g3"], "a": [1, 2, 3], "b": [2, 1, 4]})
    schema = schema_from_coltypes({"x": ColType.STR, "a": ColType.INT, "b": ColType.INT})
    node.infer_schema({"input": schema})
    out = node.execute({"input": tbl})
    assert out["plot"].payload.format == "png"

    # mixed types: bar + line
    node2 = node_ctor("QuickPlotNode", id="p_mix", x_col="x", y_col=["a", "b"], plot_type=["bar", "line"])
    tbl2 = table_from_dict({"x": [1, 2, 3], "a": [5, 6, 7], "b": [2, 3, 1]})
    schema2 = schema_from_coltypes({"x": ColType.INT, "a": ColType.INT, "b": ColType.INT})
    node2.infer_schema({"input": schema2})
    out2 = node2.execute({"input": tbl2})
    assert out2["plot"].payload.format == "png"


def test_quickplot_parameter_errors(node_ctor):
    import pytest
    # mismatch lengths between y_col and plot_type
    with pytest.raises(NodeParameterError):
        node_ctor("QuickPlotNode", id="p_len_err", x_col="x", y_col=["a", "b"], plot_type=["line"]) 
    # empty element in y_col
    with pytest.raises(NodeParameterError):
        node_ctor("QuickPlotNode", id="p_empty_y", x_col="x", y_col=["a", "  "], plot_type=["line", "line"]) 


def test_quickplot_area_and_long_x(node_ctor):
    # area + scatter inside grouped context and long x-axis to trigger xticks stepping
    x_vals = [f"v{i}" for i in range(30)]
    node = node_ctor("QuickPlotNode", id="p_area_long", x_col="x", y_col=["a", "b", "c"], plot_type=["bar", "area", "scatter"], title="T")
    tbl = table_from_dict({"x": x_vals, "a": list(range(30)), "b": [i * 2 for i in range(30)], "c": [i % 5 for i in range(30)]})
    schema = schema_from_coltypes({"x": ColType.STR, "a": ColType.INT, "b": ColType.INT, "c": ColType.INT})
    node.infer_schema({"input": schema})
    out = node.execute({"input": tbl})
    assert out["plot"].payload.format == "png"


def test_quickplot_nonbar_multiple_y(node_ctor, test_file_root):
    # no 'bar' types present -> use x values for plotting (area + line)
    node = node_ctor("QuickPlotNode", id="p_nb", x_col="x", y_col=["a", "b"], plot_type=["area", "line"]) 
    tbl = table_from_dict({"x": [1, 2, 3], "a": [2, 3, 4], "b": [1, 0, 2]})
    schema = schema_from_coltypes({"x": ColType.INT, "a": ColType.INT, "b": ColType.INT})
    node.infer_schema({"input": schema})
    out = node.execute({"input": tbl})
    assert out["plot"].payload.format == "png"
