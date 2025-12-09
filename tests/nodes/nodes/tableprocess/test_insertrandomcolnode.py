import sys
import types

from tests.nodes.utils import make_data, table_from_dict


def test_insertrandom_int_and_float_process(node_ctor, monkeypatch):
    # monkeypatch numpy to produce deterministic results
    node_i = node_ctor("InsertRandomColNode", id="rand_i", col_name="rint", col_type="int")
    tbl = table_from_dict({"a": [1,2,3]})
    # force randint
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
