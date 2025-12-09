from datetime import datetime

from tests.nodes.utils import make_data, table_from_dict


def test_insertrange_datetime_and_steps(node_ctor):
    # Datetime range without step (defaults to 1 day)
    node_dt = node_ctor("InsertRangeColNode", id="rdt", col_name="rng_dt", col_type="Datetime")
    tbl = table_from_dict({"a": [1,2,3]})
    start = datetime(2020,1,1)
    out = node_dt.process({"table": tbl, "start": make_data(start)})
    assert "rng_dt" in out["table"].payload.df.columns

    # int range with step provided
    node_i = node_ctor("InsertRangeColNode", id="ri", col_name="rng_i", col_type="int")
    tbl2 = table_from_dict({"a": [1,2,3,4]})
    out2 = node_i.process({"table": tbl2, "start": make_data(0), "step": make_data(2)})
    assert "rng_i" in out2["table"].payload.df.columns
