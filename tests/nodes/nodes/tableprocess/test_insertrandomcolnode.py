import sys
import types

import pytest

from server.models.exception import NodeExecutionError
from server.models.schema import Schema
from server.models.types import ColType
from tests.nodes.utils import make_data, schema_from_coltypes, table_from_dict


def test_insert_random_col_node(node_ctor):
    n = node_ctor("InsertRandomColNode", id="irand", col_name="rnd", col_type="int")
    schema = schema_from_coltypes({"a": ColType.INT, "_index": ColType.INT})
    n.infer_schema({"table": schema, "min_value": Schema(type=Schema.Type.INT), "max_value": Schema(type=Schema.Type.INT)})
    tbl = table_from_dict({"a": [1, 2, 3]}, col_types={"a": ColType.INT, "_index": ColType.INT})
    out = n.execute({"table": tbl, "min_value": make_data(0), "max_value": make_data(5)})
    res_tbl = out["table"].payload
    assert "rnd" in res_tbl.col_types
    # values exist and length matches
    assert len(res_tbl.df) == 3



def test_insertrandom_int_and_float_process(node_ctor, monkeypatch):
    # monkeypatch numpy to produce deterministic results
    node_i = node_ctor("InsertRandomColNode", id="rand_i", col_name="rint", col_type="int")
    tbl = table_from_dict({"a": [1,2,3]})
    # force randint
    fake_np = types.ModuleType('numpy')
    rand_mod = types.SimpleNamespace()
    def fake_randint(a, b, size=None):
        return [a for _ in range(size)] # type: ignore
    rand_mod.randint = fake_randint
    fake_np.random = rand_mod # type: ignore
    monkeypatch.setitem(sys.modules, 'numpy', fake_np)
    out = node_i.process({"table": tbl, "min_value": make_data(1), "max_value": make_data(3)})
    assert "rint" in out["table"].payload.df.columns

    # float
    node_f = node_ctor("InsertRandomColNode", id="rand_f", col_name="rflt", col_type="float")
    # fake numpy.random.uniform
    fake_np2 = types.ModuleType('numpy')
    rand2 = types.SimpleNamespace()
    def fake_uniform(a, b, size=None):
        return [float(a) for _ in range(size)] # type: ignore
    rand2.uniform = fake_uniform
    fake_np2.random = rand2 # type: ignore
    monkeypatch.setitem(sys.modules, 'numpy', fake_np2)
    out2 = node_f.process({"table": tbl, "min_value": make_data(0.0), "max_value": make_data(1.0)})
    assert "rflt" in out2["table"].payload.df.columns


def test_insertrandom_runtime_unsupported_coltype(node_ctor):
    node = node_ctor("InsertRandomColNode", id="rrbad", col_name="r2", col_type="int")
    node.col_type = "str"
    tbl = table_from_dict({"a": [1,2]})
    with pytest.raises(NodeExecutionError):
        node.process({"table": tbl, "min_value": make_data(0), "max_value": make_data(1)})
