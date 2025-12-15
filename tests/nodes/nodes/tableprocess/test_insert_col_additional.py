from datetime import datetime

import pytest

from server.models.exception import NodeValidationError
from server.models.types import ColType
from tests.nodes.utils import (
    make_data,
    make_schema,
    schema_from_coltypes,
    table_from_dict,
)


def test_insertconst_infer_mismatch_and_process(node_ctor):
    ic = node_ctor("InsertConstColNode", id="ic1", col_name=None, col_type=ColType.INT)
    # const value schema mismatch (provide float but expecting int)
    tschema = schema_from_coltypes({"_index": ColType.INT, "a": ColType.INT})
    with pytest.raises(NodeValidationError):
        ic.infer_output_schemas({"const_value": make_schema("float"), "table": tschema})

    # process: append string column
    ic2 = node_ctor("InsertConstColNode", id="ic2", col_name="cstr", col_type=ColType.STR)
    tbl = table_from_dict({"a": [1, 2]}, col_types={"a": ColType.INT, "_index": ColType.INT})
    const = make_data("x")
    out = ic2.process({"table": tbl, "const_value": const})
    df = out["table"].payload.df
    assert "cstr" in df.columns and df["cstr"].iloc[0] == "x"


def test_insertrange_infer_errors_and_process(node_ctor):
    # infer mismatch: start schema doesn't match node.col_type
    ir = node_ctor("InsertRangeColNode", id="ir1", col_name=None, col_type="int")
    tschema = schema_from_coltypes({"_index": ColType.INT})
    with pytest.raises(NodeValidationError):
        ir.infer_output_schemas({"start": make_schema("float"), "table": tschema})

    # process int range
    ir2 = node_ctor("InsertRangeColNode", id="ir2", col_name="rint", col_type="int")
    tbl = table_from_dict({"a": [0, 0, 0]}, col_types={"a": ColType.INT, "_index": ColType.INT})
    out = ir2.process({"table": tbl, "start": make_data(5)})
    df = out["table"].payload.df
    assert list(df["rint"]) == [5, 6, 7]

    # process float range with provided step
    ir3 = node_ctor("InsertRangeColNode", id="ir3", col_name="rfloat", col_type="float")
    tbl2 = table_from_dict({"a": [0, 0]}, col_types={"a": ColType.INT, "_index": ColType.INT})
    out2 = ir3.process({"table": tbl2, "start": make_data(1.0), "step": make_data(0.5)})
    assert len(out2["table"].payload.df["rfloat"]) == 2

    # process Datetime range
    ir4 = node_ctor("InsertRangeColNode", id="ir4", col_name="rdt", col_type="Datetime")
    start_dt = datetime(2020, 1, 1)
    tbl3 = table_from_dict({"a": [0, 0, 0]}, col_types={"a": ColType.INT, "_index": ColType.INT})
    out3 = ir4.process({"table": tbl3, "start": make_data(start_dt)})
    assert len(out3["table"].payload.df["rdt"]) == 3


def test_insertrandom_infer_and_process(node_ctor):
    # infer mismatch for min_value
    irand = node_ctor("InsertRandomColNode", id="rand1", col_name=None, col_type="int")
    tschema = schema_from_coltypes({"_index": ColType.INT})
    with pytest.raises(NodeValidationError):
        irand.infer_output_schemas({"min_value": make_schema("float"), "max_value": make_schema("float"), "table": tschema})

    # process int random
    irand2 = node_ctor("InsertRandomColNode", id="rand2", col_name="r", col_type="int")
    tbl = table_from_dict({"a": [0, 0, 0]}, col_types={"a": ColType.INT, "_index": ColType.INT})
    out = irand2.process({"table": tbl, "min_value": make_data(1), "max_value": make_data(3)})
    vals = out["table"].payload.df["r"].tolist()
    assert all(1 <= int(v) <= 3 for v in vals)
