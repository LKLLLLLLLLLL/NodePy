import pytest

from server.models.exception import NodeParameterError, NodeValidationError
from server.models.types import ColType
from tests.nodes.utils import schema_from_coltypes, table_from_dict


def test_shift_validate_errors(node_ctor):
    # type mismatch
    node = node_ctor("ShiftNode", id="sh_test1", col="a", periods=1)
    node.type = "NotShift"
    with pytest.raises(NodeParameterError):
        node.validate_parameters()

    # empty col (creation triggers validation)
    with pytest.raises(NodeParameterError):
        node_ctor("ShiftNode", id="sh_test2", col=" ", periods=1)

    # illegal result_col name (starts with reserved '_') (creation triggers validation)
    with pytest.raises(NodeParameterError):
        node_ctor("ShiftNode", id="sh_test3", col="a", periods=1, result_col="_bad")


def test_filter_infer_and_process(node_ctor):
    node = node_ctor("FilterNode", id="fl1", cond_col="flag")
    # infer should raise if cond_col not in schema
    bad_schema = schema_from_coltypes({"_index": ColType.INT, "x": ColType.INT})
    with pytest.raises(NodeValidationError):
        node.infer_output_schemas({"table": bad_schema})

    # process should split true/false tables
    data = table_from_dict({"x": [1, 2, 3], "flag": [True, False, True]})
    out = node.process({"table": data})
    assert out["true_table"].payload.df.shape[0] == 2
    assert out["false_table"].payload.df.shape[0] == 1


def test_dropduplicates_infer_error(node_ctor):
    node = node_ctor("DropDuplicatesNode", id="dd1", subset_cols=["a"]) 
    bad_schema = schema_from_coltypes({"_index": ColType.INT, "b": ColType.INT})
    with pytest.raises(NodeValidationError):
        node.infer_output_schemas({"table": bad_schema})


def test_fillnan_validate_and_infer_and_process(node_ctor):
    # validate: empty subset (creation triggers validation)
    with pytest.raises(NodeParameterError):
        node_ctor("FillNaNValueNode", id="fn_empty", subset_cols=[], method="const", fill_value=None)

    # validate: const requires fill_value (creation triggers validation)
    with pytest.raises(NodeParameterError):
        node_ctor("FillNaNValueNode", id="fn2", subset_cols=["s"], method="const", fill_value=None)

    # infer: type mismatch for const
    node3 = node_ctor("FillNaNValueNode", id="fn3", subset_cols=["s"], method="const", fill_value=[1])
    bad_schema = schema_from_coltypes({"_index": ColType.INT, "s": ColType.STR})
    with pytest.raises(NodeValidationError):
        node3.infer_output_schemas({"table": bad_schema})

    # infer+process: correct const fill for str and float
    node4 = node_ctor("FillNaNValueNode", id="fn4", subset_cols=["s", "f"], method="const", fill_value=["x", 1.5])
    schema = schema_from_coltypes({"_index": ColType.INT, "s": ColType.STR, "f": ColType.FLOAT})
    node4.infer_output_schemas({"table": schema})
    data = table_from_dict({"s": [None, "a"], "f": [None, 2.0]}, col_types={"s": ColType.STR, "f": ColType.FLOAT, "_index": ColType.INT})
    out = node4.process({"table": data})
    df = out["filled_table"].payload.df
    assert df["s"].iloc[0] == "x"
    assert float(df["f"].iloc[0]) == pytest.approx(1.5)

    # process: ffill and bfill behave without error
    node_ff = node_ctor("FillNaNValueNode", id="fn_ff", subset_cols=["f"], method="ffill")
    node_bf = node_ctor("FillNaNValueNode", id="fn_bf", subset_cols=["f"], method="bfill")
    data2 = table_from_dict({"f": [None, 2.0, None]}, col_types={"f": ColType.FLOAT, "_index": ColType.INT})
    out_ff = node_ff.process({"table": data2})
    out_bf = node_bf.process({"table": data2})
    import pandas as pd
    # ffill does not fill leading NaN, but fills subsequent ones
    assert pd.isna(out_ff["filled_table"].payload.df["f"].iloc[0])
    assert out_ff["filled_table"].payload.df["f"].iloc[2] == 2.0
    # bfill fills from next valid value, trailing NaN remains
    assert out_bf["filled_table"].payload.df["f"].iloc[0] == 2.0
    assert pd.isna(out_bf["filled_table"].payload.df["f"].iloc[2])


def test_merge_infer_and_process(node_ctor):
    node = node_ctor("MergeNode", id="merge1")
    schema1 = schema_from_coltypes({"_index": ColType.INT, "a": ColType.INT})
    schema2 = schema_from_coltypes({"_index": ColType.INT, "b": ColType.INT})
    with pytest.raises(NodeParameterError):
        node.infer_output_schemas({"table_1": schema1, "table_2": schema2})

    # process: merge two tables
    data1 = table_from_dict({"a": [1, 2]}, col_types={"a": ColType.INT, "_index": ColType.INT})
    data2 = table_from_dict({"a": [3]}, col_types={"a": ColType.INT, "_index": ColType.INT})
    out = node.process({"table_1": data1, "table_2": data2})
    merged = out["merged_table"].payload.df
    assert merged.shape[0] == 3


def test_tableslice_validate_and_process(node_ctor):
    node = node_ctor("TableSliceNode", id="slice1", begin=1, end=4, step=2)
    # valid parameters
    node.validate_parameters()
    data = table_from_dict({"a": [0, 1, 2, 3, 4]}, col_types={"a": ColType.INT, "_index": ColType.INT})
    out = node.process({"table": data})
    assert out["sliced_table"].payload.df.shape[0] == 2

    # step cannot be zero (creation triggers validation)
    with pytest.raises(NodeParameterError):
        node_ctor("TableSliceNode", id="slice2", step=0)
