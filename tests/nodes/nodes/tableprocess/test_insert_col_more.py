import pytest

from server.models.exception import (
    NodeExecutionError,
    NodeParameterError,
    NodeValidationError,
)
from server.models.schema import Schema
from server.models.types import ColType
from tests.nodes.utils import make_data, schema_from_coltypes, table_from_dict


def test_insert_const_parameter_and_infer_errors(node_ctor):
    # blank col_name -> default generated
    n = node_ctor("InsertConstColNode", id="ic_def", col_name="   ", col_type=ColType.INT)
    # validate_parameters called during creation; it should generate a default non-empty name
    assert n.col_name is not None and n.col_name.endswith("_const")

    # illegal column name (starts with '_') should raise on creation
    with pytest.raises(NodeParameterError):
        node_ctor("InsertConstColNode", id="ic_bad", col_name="_bad", col_type=ColType.INT)

    # infer should raise when const_value schema mismatches declared col_type
    n2 = node_ctor("InsertConstColNode", id="ic2", col_name="c", col_type=ColType.INT)
    with pytest.raises(NodeValidationError):
        n2.infer_schema({"table": schema_from_coltypes({"a": ColType.INT, "_index": ColType.INT}), "const_value": Schema(type=Schema.Type.FLOAT)})


def test_insert_range_infer_and_process_variants(node_ctor):
    # start type mismatch in infer
    nr = node_ctor("InsertRangeColNode", id="ir1", col_name="r", col_type="int")
    with pytest.raises(NodeValidationError):
        nr.infer_schema({"table": schema_from_coltypes({"a": ColType.INT, "_index": ColType.INT}), "start": Schema(type=Schema.Type.FLOAT)})

    # step type mismatch when provided
    nr2 = node_ctor("InsertRangeColNode", id="ir2", col_name="r2", col_type="float")
    with pytest.raises(NodeValidationError):
        nr2.infer_schema({"table": schema_from_coltypes({"a": ColType.FLOAT, "_index": ColType.INT}), "start": Schema(type=Schema.Type.FLOAT), "step": Schema(type=Schema.Type.INT)})

    # process int/float/Datetime flows (call process directly to avoid strict infer)
    n_int = node_ctor("InsertRangeColNode", id="ir_int", col_name="ri", col_type="int")
    tbl = table_from_dict({"a": [1,2,3]})
    out = n_int.process({"table": tbl, "start": make_data(0)})
    assert "ri" in out["table"].payload.df.columns

    n_float = node_ctor("InsertRangeColNode", id="ir_f", col_name="rf", col_type="float")
    out2 = n_float.process({"table": tbl, "start": make_data(0.5)})
    assert "rf" in out2["table"].payload.df.columns

    import datetime as _dt
    n_dt = node_ctor("InsertRangeColNode", id="ir_dt", col_name="rdt", col_type="Datetime")
    start = _dt.datetime(2021,1,1)
    out3 = n_dt.process({"table": tbl, "start": make_data(start)})
    assert "rdt" in out3["table"].payload.df.columns

    # runtime unsupported col_type
    n_bad = node_ctor("InsertRangeColNode", id="ir_bad", col_name="rbad", col_type="int")
    n_bad.col_type = "unsupported"
    with pytest.raises(NodeExecutionError):
        n_bad.process({"table": tbl, "start": make_data(0)})


def test_insert_random_infer_errors_and_runtime(node_ctor, monkeypatch):
    # infer mismatch for min_value
    nr = node_ctor("InsertRandomColNode", id="rnd1", col_name="rr", col_type="int")
    with pytest.raises(NodeValidationError):
        nr.infer_schema({"table": schema_from_coltypes({"a": ColType.INT, "_index": ColType.INT}), "min_value": Schema(type=Schema.Type.FLOAT), "max_value": Schema(type=Schema.Type.INT)})

    # infer mismatch for max_value
    nr2 = node_ctor("InsertRandomColNode", id="rnd2", col_name="rr2", col_type="float")
    with pytest.raises(NodeValidationError):
        nr2.infer_schema({"table": schema_from_coltypes({"a": ColType.FLOAT, "_index": ColType.INT}), "min_value": Schema(type=Schema.Type.FLOAT), "max_value": Schema(type=Schema.Type.INT)})

    # runtime int branch with monkeypatched numpy
    import sys
    import types
    fake_np = types.ModuleType('numpy')
    rand = types.SimpleNamespace()
    def fake_randint(a, b, size=None):
        return [a for _ in range(size)]
    rand.randint = fake_randint
    fake_np.random = rand
    monkeypatch.setitem(sys.modules, 'numpy', fake_np)

    nproc = node_ctor("InsertRandomColNode", id="rnd_proc", col_name="rint", col_type="int")
    tbl = table_from_dict({"a": [1,2,3]})
    out = nproc.process({"table": tbl, "min_value": make_data(1), "max_value": make_data(3)})
    assert "rint" in out["table"].payload.df.columns

    # runtime unsupported col_type
    nproc2 = node_ctor("InsertRandomColNode", id="rnd_bad", col_name="rb", col_type="int")
    nproc2.col_type = "str"
    with pytest.raises(NodeExecutionError):
        nproc2.process({"table": tbl, "min_value": make_data(0), "max_value": make_data(1)})
