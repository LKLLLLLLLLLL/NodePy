import pytest

from server.models.exception import NodeParameterError, NodeValidationError
from server.models.types import ColType
from tests.nodes.utils import schema_from_coltypes, table_from_dict


def test_filter_validate_empty_col(node_ctor):
    with pytest.raises(NodeParameterError):
        node_ctor("FilterNode", id="f_empty", cond_col="   ")


def test_dropduplicates_infer_missing_subset_col(node_ctor):
    dd = node_ctor("DropDuplicatesNode", id="dd_err", subset_cols=["missing"])
    schema = schema_from_coltypes({"a": ColType.INT, "_index": ColType.INT})
    with pytest.raises(NodeValidationError):
        dd.infer_schema({"table": schema})


def test_dropnan_infer_missing_subset_col(node_ctor):
    dn = node_ctor("DropNaNValueNode", id="dn_err", subset_cols=["missing"])
    schema = schema_from_coltypes({"a": ColType.INT, "_index": ColType.INT})
    with pytest.raises(NodeValidationError):
        dn.infer_schema({"table": schema})


def test_fillnan_validate_errors_and_ffill(node_ctor):
    # empty subset -> error
    with pytest.raises(NodeParameterError):
        node_ctor("FillNaNValueNode", id="fn_empty", subset_cols=[], method="const", fill_value=[1])

    # method const but no fill_value -> error
    with pytest.raises(NodeParameterError):
        node_ctor("FillNaNValueNode", id="fn_noval", subset_cols=["a"], method="const")

    # fill_value length mismatch
    with pytest.raises(NodeParameterError):
        node_ctor("FillNaNValueNode", id="fn_len", subset_cols=["a","b"], method="const", fill_value=[1])

    # ffill processing
    fn = node_ctor("FillNaNValueNode", id="fn_ff", subset_cols=["a"], method="ffill")
    schema = schema_from_coltypes({"a": ColType.FLOAT, "_index": ColType.INT})
    fn.infer_schema({"table": schema})
    tbl = table_from_dict({"a": [None, 1.0, None]}, col_types={"a": ColType.FLOAT, "_index": ColType.INT})
    out = fn.execute({"table": tbl})
    # forward fill should propagate last valid forward: result -> [NaN, 1.0, 1.0]
    import pandas as _pd
    assert _pd.isna(out["filled_table"].payload.df.iloc[0]["a"]) is True
    assert out["filled_table"].payload.df.iloc[1]["a"] == 1.0
    assert out["filled_table"].payload.df.iloc[2]["a"] == 1.0
