import numpy as np
import pytest

from server.models.exception import NodeValidationError
from server.models.types import ColType
from tests.nodes.utils import schema_from_coltypes, table_from_dict


def test_drop_nan_value_node(node_ctor):
    n = node_ctor("DropNaNValueNode", id="dn1", subset_cols=["a"]) 
    schema = schema_from_coltypes({"a": ColType.FLOAT, "b": ColType.INT, "_index": ColType.INT})
    n.infer_schema({"table": schema})

    tbl = table_from_dict({"a": [1.0, np.nan, 3.0], "b": [1, 2, 3]}, col_types={"a": ColType.FLOAT, "b": ColType.INT, "_index": ColType.INT})
    out = n.execute({"table": tbl})
    res_tbl = out["cleaned_table"].payload
    assert len(res_tbl.df) == 2

    # error: subset col missing
    n2 = node_ctor("DropNaNValueNode", id="dn2", subset_cols=["nope"])
    with pytest.raises(NodeValidationError):
        n2.infer_schema({"table": schema})

def test_dropnanvaluenode(node_ctor):
    node = node_ctor("DropNaNValueNode", id="dn1", subset_cols=["v"]) 
    # use FLOAT because NaN in pandas will coerce column to float
    schema = schema_from_coltypes({"v": ColType.FLOAT, "_index": ColType.INT})
    node.infer_schema({"table": schema})
    tbl = table_from_dict({"v": [1, None, 2]})
    out = node.execute({"table": tbl})
    assert "cleaned_table" in out
