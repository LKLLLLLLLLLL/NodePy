import pytest

from server.models.exception import NodeExecutionError
from server.models.schema import Schema
from server.models.types import ColType
from tests.nodes.utils import make_data, schema_from_coltypes, table_from_dict


def test_insert_range_col_node_int_and_float(node_ctor):
    # int range
    n = node_ctor("InsertRangeColNode", id="ir1", col_name="r", col_type="int")
    schema = schema_from_coltypes({"a": ColType.INT, "_index": ColType.INT})
    n.infer_schema({"table": schema, "start": Schema(type=Schema.Type.INT)})
    tbl = table_from_dict({"a": [1, 2, 3]}, col_types={"a": ColType.INT, "_index": ColType.INT})
    n.infer_schema({"table": schema, "start": Schema(type=Schema.Type.INT)})
    out = n.execute({"table": tbl, "start": make_data(10)})
    res_tbl = out["table"].payload
    assert "r" in res_tbl.col_types

    # float range
    n2 = node_ctor("InsertRangeColNode", id="ir2", col_name="rf", col_type="float")
    schema2 = schema_from_coltypes({"a": ColType.FLOAT, "_index": ColType.INT})
    n2.infer_schema({"table": schema2, "start": Schema(type=Schema.Type.FLOAT)})
    tbl2 = table_from_dict({"a": [1.0, 2.0]}, col_types={"a": ColType.FLOAT, "_index": ColType.INT})
    out2 = n2.execute({"table": tbl2, "start": make_data(0.5)})
    assert "rf" in out2["table"].payload.col_types



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


def test_insertrange_unsupported_coltype_runtime_error(node_ctor):
    # mutate node.col_type to unsupported to trigger NodeExecutionError
    node = node_ctor("InsertRangeColNode", id="rbad", col_name="rbad", col_type="int")
    node.col_type = "unsupported_type"
    tbl = table_from_dict({"a": [1,2,3]})
    with pytest.raises(NodeExecutionError):
        node.process({"table": tbl, "start": make_data(0)})
