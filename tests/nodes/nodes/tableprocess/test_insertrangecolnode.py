
from tests.nodes.utils import make_data, table_from_dict


def test_insert_range_int_float_datetime_process(node_ctor):
    # int range
    node_i = node_ctor("InsertRangeColNode", id="rint", col_name="rng_i", col_type="int")
    tbl = table_from_dict({"a": [1,2,3]})
    # call process directly (skip infer which uses strict schema checks)
    out = node_i.process({"table": tbl, "start": make_data(0)}) if 'make_data' in globals() else node_i.process({"table": tbl, "start": None})
    assert "table" in out and "rng_i" in out["table"].payload.df.columns

    # float range
    node_f = node_ctor("InsertRangeColNode", id="rflt", col_name="rng_f", col_type="float")
    tbl2 = table_from_dict({"a": [1,2]})
    out2 = node_f.process({"table": tbl2, "start": make_data(0.5)}) if 'make_data' in globals() else node_f.process({"table": tbl2, "start": None})
    assert "rng_f" in out2["table"].payload.df.columns

    # Datetime range
    import datetime
    start = datetime.datetime(2020,1,1)
    node_d = node_ctor("InsertRangeColNode", id="rdt", col_name="rng_dt", col_type="Datetime")
    tbl3 = table_from_dict({"a": [1,2]})
    out3 = node_d.process({"table": tbl3, "start": make_data(start)}) if 'make_data' in globals() else node_d.process({"table": tbl3, "start": None})
    assert "rng_dt" in out3["table"].payload.df.columns
