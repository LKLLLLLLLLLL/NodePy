import pytest

from server.models.exception import NodeParameterError, NodeValidationError
from server.models.types import ColType
from tests.nodes.utils import schema_from_coltypes, table_from_dict


def test_selectcol_hint_and_process(node_ctor):
    node = node_ctor("SelectColNode", id="sel1", selected_cols=["a"])
    schema = schema_from_coltypes({"_index": ColType.INT, "a": ColType.INT, "b": ColType.FLOAT})
    hint = node.get_hint("SelectColNode", {"table": schema}, {})
    assert "selected_col_choices" in hint
    out_schema = node.infer_output_schemas({"table": schema})
    assert "selected_table" in out_schema and "dropped_table" in out_schema
    data = table_from_dict({"a": [1, 2], "b": [1.0, 2.0]}, col_types={"a": ColType.INT, "b": ColType.FLOAT, "_index": ColType.INT})
    res = node.process({"table": data})
    assert "selected_table" in res and "dropped_table" in res


def test_join_infer_conflict_and_process(node_ctor):
    # mismatched key types -> infer should raise
    j = node_ctor("JoinNode", id="j1", left_on="id", right_on="id", how="INNER")
    left_schema = schema_from_coltypes({"_index": ColType.INT, "id": ColType.INT, "x": ColType.INT})
    right_schema = schema_from_coltypes({"_index": ColType.INT, "id": ColType.STR, "y": ColType.INT})
    with pytest.raises(NodeValidationError):
        j.infer_output_schemas({"left_table": left_schema, "right_table": right_schema})

    # conflict on non-key column should produce _right suffix
    j2 = node_ctor("JoinNode", id="j2", left_on="id", right_on="id", how="LEFT")
    left_schema = schema_from_coltypes({"_index": ColType.INT, "id": ColType.INT, "x": ColType.INT})
    # make z FLOAT to accommodate NaN introduced by join
    right_schema = schema_from_coltypes({"_index": ColType.INT, "id": ColType.INT, "x": ColType.FLOAT, "z": ColType.FLOAT})
    out = j2.infer_output_schemas({"left_table": left_schema, "right_table": right_schema})
    joined_tab = out["joined_table"].tab
    assert "x_right" in joined_tab.col_types

    # process: perform join and check right-suffixed column exists
    left_data = table_from_dict({"id": [1, 2], "x": [10, 20]}, col_types={"id": ColType.INT, "x": ColType.INT, "_index": ColType.INT})
    right_data = table_from_dict({"id": [1], "x": [1.5], "z": [5.0]}, col_types={"id": ColType.INT, "x": ColType.FLOAT, "z": ColType.FLOAT, "_index": ColType.INT})
    res = j2.process({"left_table": left_data, "right_table": right_data})
    df = res["joined_table"].payload.df
    assert "x_right" in df.columns


def test_rename_errors_and_infer(node_ctor):
    # illegal new name triggers parameter error at construction
    with pytest.raises(NodeParameterError):
        node_ctor("RenameColNode", id="rn1", rename_map={"a": "_bad"})

    rn = node_ctor("RenameColNode", id="rn2", rename_map={"a": "x_new"})
    # infer error when old_name not present
    bad_schema = schema_from_coltypes({"_index": ColType.INT, "b": ColType.INT})
    with pytest.raises(NodeValidationError):
        rn.infer_output_schemas({"table": bad_schema})

    # infer error when rename causes conflict
    schema = schema_from_coltypes({"_index": ColType.INT, "a": ColType.INT, "b": ColType.INT})
    rn_conflict = node_ctor("RenameColNode", id="rn3", rename_map={"a": "b"})
    with pytest.raises(NodeValidationError):
        rn_conflict.infer_output_schemas({"table": schema})
