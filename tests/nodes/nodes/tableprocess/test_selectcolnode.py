import pytest

from server.models.exception import NodeParameterError
from server.models.types import ColType
from tests.nodes.utils import make_data, schema_from_coltypes, table_from_dict


def test_selectcol_construct_hint_infer_and_process(node_ctor):
    node = node_ctor("SelectColNode", id="s1", selected_cols=["a"]) 
    schema = schema_from_coltypes({"a": ColType.INT, "b": ColType.FLOAT, "_index": ColType.INT})
    hint = node.get_hint("SelectColNode", {"table": schema}, {})
    assert "selected_col_choices" in hint

    out_schema = node.infer_schema({"table": schema})
    assert "selected_table" in out_schema and "dropped_table" in out_schema

    tbl = table_from_dict({"a": [1,2], "b": [3.0,4.0]})
    out = node.execute({"table": tbl})
    assert "selected_table" in out and "dropped_table" in out
    assert list(out["selected_table"].payload.df.columns).count("a") == 1


def test_selectcol_errors(node_ctor):
    # wrong type check
    node = node_ctor("SelectColNode", id="s_err", selected_cols=["a"]) 
    node.type = "NotSelect"
    with pytest.raises(NodeParameterError):
        node.validate_parameters()

    # infer with missing column should raise
    node2 = node_ctor("SelectColNode", id="s_err2", selected_cols=["missing"]) 
    bad_schema = schema_from_coltypes({"a": ColType.INT, "_index": ColType.INT})
    with pytest.raises(Exception):
        node2.infer_schema({"table": bad_schema})

    # process with wrong payload
    node3 = node_ctor("SelectColNode", id="s_err3", selected_cols=["a"]) 
    with pytest.raises(AssertionError):
        node3.process({"table": make_data(123)})
