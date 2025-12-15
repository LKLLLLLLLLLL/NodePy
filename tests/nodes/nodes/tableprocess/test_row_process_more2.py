
from server.models.types import ColType
from tests.nodes.utils import schema_from_coltypes, table_from_dict


def test_fillnan_infer_int_and_bool_types(node_ctor):
    # INT and BOOL fill_value type checking in infer_output_schemas
    node = node_ctor("FillNaNValueNode", id="fn_ib", subset_cols=["i", "b"], method="const", fill_value=[1, True])
    schema = schema_from_coltypes({"i": ColType.INT, "b": ColType.BOOL, "_index": ColType.INT})
    node.infer_schema({"table": schema})
    # fill_value should be converted and stored
    assert node.fill_value[0] == 1 and node.fill_value[1] is True


def test_fillnan_hint_fill_value_types(node_ctor):
    node = node_ctor("FillNaNValueNode", id="fn_hint", subset_cols=["a"], method="const", fill_value=["x"])
    schema = schema_from_coltypes({"a": ColType.STR, "_index": ColType.INT})
    hint = node.get_hint("FillNaNValueNode", {"table": schema}, {})
    assert "fill_value_types" in hint and hint["fill_value_types"][0] == ColType.STR.value


def test_tableslice_negative_step(node_ctor):
    ts = node_ctor("TableSliceNode", id="ts_neg", begin=None, end=None, step=-1)
    schema = schema_from_coltypes({"a": ColType.INT, "_index": ColType.INT})
    ts.infer_schema({"table": schema})
    tbl = table_from_dict({"a": [1, 2, 3]}, col_types={"a": ColType.INT, "_index": ColType.INT})
    out = ts.execute({"table": tbl})
    # reversed table should have same length
    assert len(out["sliced_table"].payload.df) == 3


def test_sort_hint_choices(node_ctor):
    sort = node_ctor("SortNode", id="so_hint", sort_col="a", ascending=True)
    schema = schema_from_coltypes({"a": ColType.INT, "b": ColType.FLOAT, "_index": ColType.INT})
    hint = sort.get_hint("SortNode", {"table": schema}, {})
    assert "sort_col_choices" in hint and "a" in hint["sort_col_choices"]
