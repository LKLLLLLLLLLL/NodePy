import pandas as pd
import pytest

from server.models.exception import NodeParameterError, NodeValidationError
from server.models.types import ColType
from tests.nodes.utils import schema_from_coltypes, table_from_dict


def test_filter_validate_empty_cond_raises(node_ctor):
    with pytest.raises(NodeParameterError):
        node_ctor("FilterNode", id="f_empty", cond_col="   ")


def test_dropduplicates_infer_missing_col_raises(node_ctor):
    n = node_ctor("DropDuplicatesNode", id="dd_err", subset_cols=["z"])
    schema = schema_from_coltypes({"a": ColType.INT, "_index": ColType.INT})
    with pytest.raises(NodeValidationError):
        n.infer_schema({"table": schema})


def test_dropnan_infer_missing_col_raises(node_ctor):
    n = node_ctor("DropNaNValueNode", id="dn_err", subset_cols=["z"])
    schema = schema_from_coltypes({"a": ColType.FLOAT, "_index": ColType.INT})
    with pytest.raises(NodeValidationError):
        n.infer_schema({"table": schema})


def test_fillnan_validate_errors_for_const(node_ctor):
    # empty subset_cols should raise
    with pytest.raises(NodeParameterError):
        node_ctor("FillNaNValueNode", id="fn_e", subset_cols=[], method="const", fill_value=[1])

    # mismatch length of fill_value
    with pytest.raises(NodeParameterError):
        node_ctor("FillNaNValueNode", id="fn_len", subset_cols=["a", "b"], method="const", fill_value=[1])


def test_fillnan_infer_float_conversion_and_ffill(node_ctor):
    # float column accepts int fill_value which will be converted to float
    n = node_ctor("FillNaNValueNode", id="fn_f", subset_cols=["f"], method="const", fill_value=[1])
    schema = schema_from_coltypes({"f": ColType.FLOAT, "_index": ColType.INT})
    n.infer_schema({"table": schema})
    assert isinstance(n.fill_value[0], float)

    # ffill processing: forward fill should propagate previous non-null values
    nf = node_ctor("FillNaNValueNode", id="fn_ff", subset_cols=["a"], method="ffill")
    schema2 = schema_from_coltypes({"a": ColType.FLOAT, "_index": ColType.INT})
    nf.infer_schema({"table": schema2})
    tbl = table_from_dict({"a": [None, 2.0, None]}, col_types={"a": ColType.FLOAT, "_index": ColType.INT})
    out = nf.execute({"table": tbl})
    res = out["filled_table"].payload.df
    # after ffill, the last row should be filled with 2.0
    assert pd.isna(res.iloc[0]["a"]) or res.iloc[0]["a"] is None
    assert res.iloc[2]["a"] == 2.0
