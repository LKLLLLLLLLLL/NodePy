import pandas as pd
import pytest

from server.models.exception import NodeValidationError
from server.models.types import ColType
from tests.nodes.utils import schema_from_coltypes, table_from_dict


def test_fillnan_datetime_infer_and_process(node_ctor):
    # success: DATETIME fill_value provided as ISO string
    fn = node_ctor("FillNaNValueNode", id="fn_dt_ok", subset_cols=["t"], method="const", fill_value=["2020-01-01T00:00:00"])
    schema = schema_from_coltypes({"_index": ColType.INT, "t": ColType.DATETIME})
    out = fn.infer_output_schemas({"table": schema})
    assert "filled_table" in out

    data = table_from_dict({"t": [pd.NaT, pd.Timestamp("2020-01-01")]}, col_types={"t": ColType.DATETIME, "_index": ColType.INT})
    res = fn.process({"table": data})
    filled = res["filled_table"].payload.df
    assert pd.Timestamp(filled["t"].iloc[0]) == pd.Timestamp("2020-01-01T00:00:00")


def test_fillnan_datetime_infer_error(node_ctor):
    # invalid: DATETIME expecting string but provided non-string -> infer should raise
    fn_bad = node_ctor("FillNaNValueNode", id="fn_dt_bad", subset_cols=["t"], method="const", fill_value=[123])
    schema = schema_from_coltypes({"_index": ColType.INT, "t": ColType.DATETIME})
    with pytest.raises(NodeValidationError):
        fn_bad.infer_output_schemas({"table": schema})


def test_dropduplicates_empty_subset_process(node_ctor):
    dd = node_ctor("DropDuplicatesNode", id="dd_empty", subset_cols=[])
    tbl = table_from_dict({"a": [1, 1, 2], "b": [9, 9, 8]}, col_types={"a": ColType.INT, "b": ColType.INT, "_index": ColType.INT})
    out = dd.process({"table": tbl})
    # When subset_cols == [], drop_duplicates considers all columns (including _index)
    # so duplicates won't be removed because _index is unique per row.
    assert out["deduplicated_table"].payload.df.shape[0] == 3

    # If user specifies subset_cols, dedup should remove duplicates based on subset
    dd2 = node_ctor("DropDuplicatesNode", id="dd_by_a", subset_cols=["a"])
    out2 = dd2.process({"table": tbl})
    assert out2["deduplicated_table"].payload.df.shape[0] == 2


def test_dropnan_infer_and_process(node_ctor):
    dn = node_ctor("DropNaNValueNode", id="dn1", subset_cols=["a"]) 
    # infer should raise if subset missing
    bad_schema = schema_from_coltypes({"_index": ColType.INT, "b": ColType.INT})
    with pytest.raises(NodeValidationError):
        dn.infer_output_schemas({"table": bad_schema})

    # process should drop rows with NaN in subset
    tbl = table_from_dict({"a": [1, None, 2], "b": [1, 2, 3]}, col_types={"a": ColType.FLOAT, "b": ColType.INT, "_index": ColType.INT})
    out = dn.process({"table": tbl})
    assert out["cleaned_table"].payload.df.shape[0] == 2


def test_hints_cover_fillna_and_filter(node_ctor):
    # Filter hint
    f = node_ctor("FilterNode", id="f_hint", cond_col="flag")
    schema = schema_from_coltypes({"_index": ColType.INT, "flag": ColType.BOOL, "x": ColType.INT})
    hint = f.get_hint("FilterNode", {"table": schema}, {})
    assert "cond_col_choices" in hint and "flag" in hint["cond_col_choices"]

    # FillNaN hint returns fill_value_types
    fn = node_ctor("FillNaNValueNode", id="fn_hint", subset_cols=["a", "b"], method="const", fill_value=[1, "x"])
    schema2 = schema_from_coltypes({"_index": ColType.INT, "a": ColType.INT, "b": ColType.STR})
    hh = fn.get_hint("FillNaNValueNode", {"table": schema2}, {})
    assert "fill_value_types" in hh and set(hh["fill_value_types"]) == {"int", "str"}


def test_filter_validate_empty(node_ctor):
    # empty cond_col triggers validation on construction
    import pytest
    with pytest.raises(Exception):
        node_ctor("FilterNode", id="f_err2", cond_col=" ")


def test_fillnan_length_mismatch_and_type_errors(node_ctor):
    import pytest
    # length mismatch triggers parameter error on creation
    with pytest.raises(Exception):
        node_ctor("FillNaNValueNode", id="fn_len", subset_cols=["a", "b"], method="const", fill_value=[1])

    # INT column but provided float -> infer should raise
    fn_int = node_ctor("FillNaNValueNode", id="fn_int", subset_cols=["a"], method="const", fill_value=[1.2])
    bad_schema = schema_from_coltypes({"_index": ColType.INT, "a": ColType.INT})
    with pytest.raises(NodeValidationError):
        fn_int.infer_output_schemas({"table": bad_schema})

    # BOOL success and mismatch
    fn_bool_ok = node_ctor("FillNaNValueNode", id="fn_b_ok", subset_cols=["b"], method="const", fill_value=[True])
    bool_schema = schema_from_coltypes({"_index": ColType.INT, "b": ColType.BOOL})
    out = fn_bool_ok.infer_output_schemas({"table": bool_schema})
    assert "filled_table" in out

    fn_bool_bad = node_ctor("FillNaNValueNode", id="fn_b_bad", subset_cols=["b"], method="const", fill_value=[1])
    with pytest.raises(NodeValidationError):
        fn_bool_bad.infer_output_schemas({"table": bool_schema})


def test_fillnan_int_and_float_accepts_int(node_ctor):
    # INT success
    fn_i = node_ctor("FillNaNValueNode", id="fn_i", subset_cols=["a"], method="const", fill_value=[5])
    schema_i = schema_from_coltypes({"_index": ColType.INT, "a": ColType.INT})
    out = fn_i.infer_output_schemas({"table": schema_i})
    assert "filled_table" in out
    # cannot construct a Table with NaN and ColType.INT (pandas upcasts to float),
    # so we only assert infer behavior for INT fill_value here.

    # FLOAT accepts int and casts to float
    fn_f = node_ctor("FillNaNValueNode", id="fn_f", subset_cols=["f"], method="const", fill_value=[1])
    schema_f = schema_from_coltypes({"_index": ColType.INT, "f": ColType.FLOAT})
    out2 = fn_f.infer_output_schemas({"table": schema_f})
    assert "filled_table" in out2
    tbl2 = table_from_dict({"f": [None, 2.0]}, col_types={"f": ColType.FLOAT, "_index": ColType.INT})
    res2 = fn_f.process({"table": tbl2})
    assert float(res2["filled_table"].payload.df["f"].iloc[0]) == pytest.approx(1.0)


def test_filter_validate_type_mismatch(node_ctor):
    node = node_ctor("FilterNode", id="f_tm", cond_col="flag")
    node.type = "NotFilter"
    with pytest.raises(Exception):
        node.validate_parameters()


def test_dropnodes_hints_and_validate(node_ctor):
    # DropDuplicates hint
    dd = node_ctor("DropDuplicatesNode", id="dd_h", subset_cols=["a"]) 
    schema = schema_from_coltypes({"_index": ColType.INT, "a": ColType.INT, "b": ColType.INT})
    hint = dd.get_hint("DropDuplicatesNode", {"table": schema}, {})
    assert "subset_col_choices" in hint and "a" in hint["subset_col_choices"]
    # validate type mismatch when altered after construction
    dd.type = "NotDrop"
    with pytest.raises(Exception):
        dd.validate_parameters()

    # DropNaN hint
    dn = node_ctor("DropNaNValueNode", id="dn_h", subset_cols=["a"]) 
    hint2 = dn.get_hint("DropNaNValueNode", {"table": schema}, {})
    assert "subset_col_choices" in hint2 and "b" in hint2["subset_col_choices"]
    dn.type = "NotDropNaN"
    with pytest.raises(Exception):
        dn.validate_parameters()


def test_fillna_ffill_bfill_extra_cases(node_ctor):
    # ffill with middle valid should fill following only
    fn_ff = node_ctor("FillNaNValueNode", id="fn_ff2", subset_cols=["f"], method="ffill")
    tbl = table_from_dict({"f": [None, 1.0, None, 2.0]}, col_types={"f": ColType.FLOAT, "_index": ColType.INT})
    out = fn_ff.process({"table": tbl})
    vals = out["filled_table"].payload.df["f"].tolist()
    assert vals[1] == 1.0 and vals[2] == 1.0

    # bfill with only trailing valid fills earlier NAs
    fn_bf = node_ctor("FillNaNValueNode", id="fn_bf2", subset_cols=["f"], method="bfill")
    tbl2 = table_from_dict({"f": [None, None, 3.0]}, col_types={"f": ColType.FLOAT, "_index": ColType.INT})
    out2 = fn_bf.process({"table": tbl2})
    vals2 = out2["filled_table"].payload.df["f"].tolist()
    assert vals2[0] == 3.0 and vals2[1] == 3.0
