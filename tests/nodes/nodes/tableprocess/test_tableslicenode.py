import pytest

from server.models.exception import NodeParameterError
from server.models.types import ColType
from tests.nodes.utils import schema_from_coltypes, table_from_dict


def test_tableslicenode_normal_and_errors(node_ctor):
    node4 = node_ctor("TableSliceNode", id="ts1", begin=0, end=1, step=1)
    s4 = schema_from_coltypes({"a": ColType.INT, "_index": ColType.INT})
    node4.infer_schema({"table": s4})
    tbl4 = table_from_dict({"a": [1,2,3]})
    out4 = node4.execute({"table": tbl4})
    assert "sliced_table" in out4

    # TableSlice step zero
    with pytest.raises(NodeParameterError):
        node_ctor("TableSliceNode", id="ts_err", step=0)
