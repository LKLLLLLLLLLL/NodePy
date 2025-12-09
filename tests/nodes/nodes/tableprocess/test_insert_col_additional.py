import pytest

from server.models.exception import NodeExecutionError
from tests.nodes.utils import make_data, table_from_dict


def test_insertrange_float_step_and_unsupported(node_ctor):
    # float range with explicit step
    node_f = node_ctor("InsertRangeColNode", id="rflt2", col_name="rng_f2", col_type="float")
    tbl = table_from_dict({"a": [1,2,3]})
    out = node_f.process({"table": tbl, "start": make_data(0.5), "step": make_data(0.5)})
    assert "rng_f2" in out["table"].payload.df.columns

    # force unsupported col_type by mutating attribute and expect NodeExecutionError
    node_bad = node_ctor("InsertRangeColNode", id="rbad", col_name="rbad", col_type="int")
    node_bad.col_type = "unsupported_type"
    with pytest.raises(NodeExecutionError):
        node_bad.process({"table": tbl, "start": make_data(0)})


def test_insertrandom_unsupported_coltype(node_ctor):
    node = node_ctor("InsertRandomColNode", id="rrbad", col_name="r2", col_type="int")
    # mutate to unsupported type to trigger NodeExecutionError
    node.col_type = "str"
    tbl = table_from_dict({"a": [1,2]})
    with pytest.raises(NodeExecutionError):
        node.process({"table": tbl, "min_value": make_data(0), "max_value": make_data(1)})
