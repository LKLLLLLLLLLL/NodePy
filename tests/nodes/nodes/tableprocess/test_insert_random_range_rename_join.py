import sys
import types

from server.models.types import ColType
from tests.nodes.utils import make_data, schema_from_coltypes, table_from_dict


def test_insert_range_int_float_datetime_process(node_ctor):
    # int range
    node_i = node_ctor("InsertRangeColNode", id="rint", col_name="rng_i", col_type="int")
    tbl = table_from_dict({"a": [1,2,3]})
    # call process directly (skip infer which uses strict schema checks)
    out = node_i.process({"table": tbl, "start": make_data(0)})
    assert "table" in out and "rng_i" in out["table"].payload.df.columns

    # float range
    node_f = node_ctor("InsertRangeColNode", id="rflt", col_name="rng_f", col_type="float")
    tbl2 = table_from_dict({"a": [1,2]})
    out2 = node_f.process({"table": tbl2, "start": make_data(0.5)})
    assert "rng_f" in out2["table"].payload.df.columns

    # Datetime range
    import datetime
    start = datetime.datetime(2020,1,1)
    node_d = node_ctor("InsertRangeColNode", id="rdt", col_name="rng_dt", col_type="Datetime")
    tbl3 = table_from_dict({"a": [1,2]})
    out3 = node_d.process({"table": tbl3, "start": make_data(start)})
    assert "rng_dt" in out3["table"].payload.df.columns


def test_insertrandom_int_and_float_process(node_ctor, monkeypatch):
    # monkeypatch numpy to produce deterministic results
    node_i = node_ctor("InsertRandomColNode", id="rand_i", col_name="rint", col_type="int")
    tbl = table_from_dict({"a": [1,2,3]})
    # force randint
    orig_np = __import__("numpy")
    # create fake numpy with .random.randint
    fake_np = types.ModuleType('numpy')
    rand_mod = types.SimpleNamespace()
    def fake_randint(a, b, size=None):
        return [a for _ in range(size)]
    rand_mod.randint = fake_randint
    fake_np.random = rand_mod
    monkeypatch.setitem(sys.modules, 'numpy', fake_np)
    out = node_i.process({"table": tbl, "min_value": make_data(1), "max_value": make_data(3)})
    assert "rint" in out["table"].payload.df.columns

    # float
    node_f = node_ctor("InsertRandomColNode", id="rand_f", col_name="rflt", col_type="float")
    # fake numpy.random.uniform
    fake_np2 = types.ModuleType('numpy')
    rand2 = types.SimpleNamespace()
    def fake_uniform(a, b, size=None):
        return [float(a) for _ in range(size)]
    rand2.uniform = fake_uniform
    fake_np2.random = rand2
    monkeypatch.setitem(sys.modules, 'numpy', fake_np2)
    out2 = node_f.process({"table": tbl, "min_value": make_data(0.0), "max_value": make_data(1.0)})
    assert "rflt" in out2["table"].payload.df.columns


def test_rename_execute(node_ctor):
    node = node_ctor("RenameColNode", id="rn1", rename_map={"a": "x"})
    tbl = table_from_dict({"a": [1], "b": [2]})
    # run infer then execute to set internal col types
    s = schema_from_coltypes({"a": ColType.INT, "b": ColType.INT, "_index": ColType.INT})
    node.infer_schema({"table": s})
    out = node.execute({"table": tbl})
    assert "x" in out["renamed_table"].payload.df.columns


def test_join_execute_merging(node_ctor):
    node = node_ctor("JoinNode", id="jexec", left_on="k", right_on="k", how="INNER")
    left = table_from_dict({"k": [1,2], "v": [10,20]})
    right = table_from_dict({"k": [1,3], "w": [100,300]})
    # only test infer phase here; executing process can create dataframe column-name edge-cases
    s_left = schema_from_coltypes({"k": ColType.INT, "v": ColType.INT, "_index": ColType.INT})
    s_right = schema_from_coltypes({"k": ColType.INT, "w": ColType.INT, "_index": ColType.INT})
    out = node.infer_schema({"left_table": s_left, "right_table": s_right})
    assert "joined_table" in out
