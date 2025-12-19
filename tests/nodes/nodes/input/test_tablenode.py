from datetime import datetime, timedelta, timezone

import pandas as pd
import pytest
from pydantic import ValidationError

from server.config import DEFAULT_TIMEZONE
from server.interpreter.nodes.base_node import BaseNode
from server.models.data import Data
from server.models.exception import (
    NodeExecutionError,
    NodeParameterError,
    NodeValidationError,
)
from server.models.schema import ColType, Schema, TableSchema


def test_tablenode_hint_empty():
    """Hint stage: TableNode provides no hints by default."""
    assert BaseNode.get_hint("TableNode", {}, {}) == {}


def test_tablenode_hint_with_params_returns_empty():
    """Hint stage success: even with params or schemas TableNode returns empty by default."""
    params = {"rows": []}
    schemas = {"ghost": Schema(type=Schema.Type.INT)}
    assert BaseNode.get_hint("TableNode", schemas, params) == {}


def test_tablenode_hint_unknown_type_raises():
    """Hint stage failure: unknown type lookup raises ValueError."""
    with pytest.raises(ValueError):
        BaseNode.get_hint("NoSuchTable", {}, {})


def test_tablenode_hint_empty_type_raises():
    """Hint stage failure: empty type name raises ValueError."""
    with pytest.raises(ValueError):
        BaseNode.get_hint("", {}, {})


def test_tablenode_hint_none_type_raises():
    """Hint stage failure: None type name raises ValueError when looked up."""
    with pytest.raises(ValueError):
        BaseNode.get_hint(None, {}, {})  # type: ignore[arg-type]


def test_tablenode_construct_accepts_valid_rows(node_ctor):
    """Construct stage: accepts rows when col_names and col_types match."""
    rows = [{"a": 1, "b": 2.0}]
    col_names = ["a", "b"]
    col_types = {"a": ColType.INT, "b": ColType.FLOAT}
    node = node_ctor("TableNode", id="t-good", rows=rows, col_names=col_names, col_types=col_types)
    assert node._rows is not None


def test_tablenode_construct_accepts_multiple_rows(node_ctor):
    """Construct stage success: accepts multiple consistent rows."""
    rows = [{"a": 1}, {"a": 2}, {"a": 3}]
    node = node_ctor("TableNode", id="t-multi", rows=rows, col_names=["a"], col_types={"a": ColType.INT})
    assert node._rows is not None and len(node._rows) == 3


def test_tablenode_construct_rejects_empty_rows_with_colnames(node_ctor):
    """Construct stage: empty rows are now allowed when `col_types` is provided."""
    # implementation now permits empty rows if explicit col_types are present
    node = node_ctor("TableNode", id="t-empty-ok", rows=[], col_names=["a"], col_types={"a": ColType.INT})
    assert node._rows == []


def test_tablenode_construct_rejects_empty_rows_without_col_types(node_ctor):
    """Construct stage failure: providing col_names but no col_types with empty rows should still fail."""
    with pytest.raises((NodeParameterError, ValidationError)):
        node_ctor("TableNode", id="t-empty-bad", rows=[], col_names=["a"])  # type: ignore[arg-type]


def test_tablenode_construct_rejects_mismatched_row_keys(node_ctor):
    """Construct stage: rows whose keys don't match col_names are rejected."""
    rows = [{"x": 1}]
    with pytest.raises(NodeParameterError):
        node_ctor("TableNode", id="t-bad-keys", rows=rows, col_names=["a"], col_types={"a": ColType.INT})


def test_tablenode_construct_rejects_bad_col_types_keys(node_ctor):
    """Construct stage: col_types keys must match col_names."""
    rows = [{"a": 1}]
    with pytest.raises(NodeParameterError):
        node_ctor("TableNode", id="t-bad-coltypes", rows=rows, col_names=["a"], col_types={"b": ColType.INT})


def test_tablenode_construct_rejects_unsupported_value_type(node_ctor):
    """Construct stage: unsupported cell types cause failure (pydantic or NodeParameterError)."""
    rows = [{"a": object()}]
    with pytest.raises((NodeParameterError, ValidationError)):
        node_ctor("TableNode", id="t-unsupported", rows=rows, col_names=["a"], col_types={"a": ColType.STR})


def test_tablenode_construct_rejects_missing_col_types(node_ctor):
    """Construct stage failure: missing col_types when col_names present should fail."""
    rows = [{"a": 1}]
    with pytest.raises((NodeParameterError, ValidationError)):
        node_ctor("TableNode", id="t-no-coltypes", rows=rows, col_names=["a"])  # type: ignore[arg-type]


def test_tablenode_static_infers_table_schema(node_ctor):
    """Static analysis: infers a Table schema with provided col_types."""
    rows = [{"a": 1}]
    col_names = ["a"]
    col_types = {"a": ColType.INT}
    node = node_ctor("TableNode", id="t-static", rows=rows, col_names=col_names, col_types=col_types)
    out = node.infer_schema({})
    assert out == {"table": Schema(type=Schema.Type.TABLE, tab=TableSchema(col_types=col_types))}


def test_tablenode_static_accepts_inferred_coltypes(node_ctor):
    """Static success: if node can infer col_types from rows, infer_schema returns table schema."""
    rows = [{"a": 1, "b": 2.0}]
    col_names = ["a", "b"]
    col_types = {"a": ColType.INT, "b": ColType.FLOAT}
    node = node_ctor("TableNode", id="t-static-infer", rows=rows, col_names=col_names, col_types=col_types)
    out = node.infer_schema({})
    assert "table" in out


def test_tablenode_static_rejects_extra_input(node_ctor):
    """Static analysis: unexpected inputs are rejected for source nodes."""
    rows = [{"a": 1}]
    col_names = ["a"]
    col_types = {"a": ColType.INT}
    node = node_ctor("TableNode", id="t-static-extra", rows=rows, col_names=col_names, col_types=col_types)
    with pytest.raises(ValueError):
        node.infer_schema({"extra": Schema(type=Schema.Type.INT)})


def test_tablenode_static_rejects_none_input(node_ctor):
    """Static analysis: infer_schema expects a mapping not None."""
    rows = [{"a": 1}]
    col_names = ["a"]
    col_types = {"a": ColType.INT}
    node = node_ctor("TableNode", id="t-static-none", rows=rows, col_names=col_names, col_types=col_types)
    with pytest.raises(TypeError):
        node.infer_schema(None)  # type: ignore[arg-type]


def test_tablenode_static_rejects_extra_input_variant(node_ctor):
    """Static failure variant: unexpected inputs are rejected for source nodes."""
    rows = [{"a": 1}]
    col_names = ["a"]
    col_types = {"a": ColType.INT}
    node = node_ctor("TableNode", id="t-static-extra2", rows=rows, col_names=col_names, col_types=col_types)
    with pytest.raises(ValueError):
        node.infer_schema({"extra": Schema(type=Schema.Type.INT)})


def test_tablenode_execute_emits_table(node_ctor):
    """Execute stage: emits a Table Data payload matching inferred schema."""
    rows = [{"a": 1}]
    col_names = ["a"]
    col_types = {"a": ColType.INT}
    node = node_ctor("TableNode", id="t-exec", rows=rows, col_names=col_names, col_types=col_types)
    node.infer_schema({})
    outputs = node.execute({})
    assert "table" in outputs
    # Table implementation adds an index column; ensure original cols exist and match types
    out_col_types = outputs["table"].payload.col_types
    for k, v in col_types.items():
        assert k in out_col_types and out_col_types[k] == v


def test_tablenode_execute_emits_table_for_multiple_rows(node_ctor):
    """Execute success: emits table when multiple rows were provided at construction."""
    rows = [{"a": 1}, {"a": 2}]
    node = node_ctor("TableNode", id="t-exec-multi", rows=rows, col_names=["a"], col_types={"a": ColType.INT})
    node.infer_schema({})
    outputs = node.execute({})
    assert "table" in outputs and len(outputs["table"].payload.df) == 2


def test_tablenode_execute_rejects_tampered_output_schema(node_ctor):
    """Execute failure: tampering cached output schema triggers NodeExecutionError."""
    rows = [{"a": 1}]
    node = node_ctor("TableNode", id="t-out-tamper", rows=rows, col_names=["a"], col_types={"a": ColType.INT})
    node.infer_schema({})
    node._schemas_out = {"table": Schema(type=Schema.Type.TABLE, tab=TableSchema(col_types={"a": ColType.FLOAT}))}  # type: ignore[attr-defined]
    with pytest.raises(NodeExecutionError):
        node.execute({})


def test_tablenode_execute_requires_inferred_schema(node_ctor):
    """Execute stage: running without prior static inference raises NodeExecutionError."""
    rows = [{"a": 1}]
    col_names = ["a"]
    col_types = {"a": ColType.INT}
    node = node_ctor("TableNode", id="t-no-infer", rows=rows, col_names=col_names, col_types=col_types)
    with pytest.raises(NodeExecutionError):
        node.execute({})


def test_tablenode_execute_rejects_unexpected_runtime_input(node_ctor):
    """Execute stage: unexpected runtime inputs cause schema mismatch errors."""
    rows = [{"a": 1}]
    col_names = ["a"]
    col_types = {"a": ColType.INT}
    node = node_ctor("TableNode", id="t-extra-runtime", rows=rows, col_names=col_names, col_types=col_types)
    node.infer_schema({})
    with pytest.raises(NodeExecutionError):
        node.execute({"extra": Data(payload=5)})


def test_tablenode_valid_and_process(node_ctor):
    rows = [{"a": 1, "b": 2.0}]
    col_names = ["a", "b"]
    col_types = {"a": ColType.INT, "b": ColType.FLOAT}
    node = node_ctor(
        "TableNode", id="tn1", rows=rows, col_names=col_names, col_types=col_types
    )
    out_schema = node.infer_schema({})
    assert out_schema["table"].type == Schema.Type.TABLE
    res = node.process({})
    assert "table" in res and isinstance(res["table"].payload.df, object)


def test_tablenode_rejects_mismatched_row_keys(node_ctor):
    rows = [{"a": 1, "c": 2}]
    col_names = ["a", "b"]
    col_types = {"a": ColType.INT, "b": ColType.INT}
    with pytest.raises(NodeParameterError):
        node_ctor(
            "TableNode",
            id="tn-bad",
            rows=rows,
            col_names=col_names,
            col_types=col_types,
        )


def test_tablenode_invalid_datetime_string(node_ctor):
    rows = [{"ts": "not-a-date"}]
    col_names = ["ts"]
    col_types = {"ts": ColType.DATETIME}
    with pytest.raises(NodeParameterError):
        node_ctor(
            "TableNode", id="tn-dt", rows=rows, col_names=col_names, col_types=col_types
        )


def test_randomnode_infer_requires_min_max_for_numeric(node_ctor):
    node = node_ctor("RandomNode", id="rn1", col_name="c", col_type="float")
    # missing min_value in input_schemas should raise
    with pytest.raises(NodeValidationError):
        node.infer_schema({"row_count": Schema(type=Schema.Type.INT)})


def test_randomnode_process_row_count_too_large(node_ctor):
    node = node_ctor("RandomNode", id="rn2", col_name="c", col_type="int")
    # provide schemas so infer_schema succeeds
    out = node.infer_schema(
        {
            "row_count": Schema(type=Schema.Type.INT),
            "min_value": Schema(type=Schema.Type.INT),
            "max_value": Schema(type=Schema.Type.INT),
        }
    )
    assert out["table"].type == Schema.Type.TABLE
    # runtime with huge row_count triggers NodeExecutionError
    # patch the module-level constant the node uses (imported at module level)
    import importlib
    mod = importlib.import_module('server.interpreter.nodes.input.table')
    from pytest import MonkeyPatch
    mp = MonkeyPatch()
    mp.setattr(mod, "MAX_GENERATED_TABLE_ROWS", 100000)
    try:
        with pytest.raises(NodeExecutionError):
            node.process(
                {
                    "row_count": Data(payload=100001),
                    "min_value": Data(payload=0),
                    "max_value": Data(payload=10),
                }
            )
    finally:
        mp.undo()


def test_randomnode_min_ge_max_raises(node_ctor):
    node = node_ctor("RandomNode", id="rn3", col_name="c", col_type="int")
    node.infer_schema(
        {
            "row_count": Schema(type=Schema.Type.INT),
            "min_value": Schema(type=Schema.Type.INT),
            "max_value": Schema(type=Schema.Type.INT),
        }
    )
    with pytest.raises(NodeExecutionError):
        node.process(
            {
                "row_count": Data(payload=2),
                "min_value": Data(payload=10),
                "max_value": Data(payload=5),
            }
        )


def test_rangenode_int_infer_and_process(node_ctor):
    node = node_ctor("RangeNode", id="rg1", col_name="r", col_type="int")
    out_schema = node.infer_schema(
        {"start": Schema(type=Schema.Type.INT), "end": Schema(type=Schema.Type.INT)}
    )
    assert out_schema["table"].type == Schema.Type.TABLE
    res = node.process({"start": Data(payload=1), "end": Data(payload=5)})
    # should generate rows for 1,2,3,4 -> length 4
    assert len(res["table"].payload.df) == 4


def test_rangenode_step_type_mismatch_infer(node_ctor):
    node = node_ctor("RangeNode", id="rg2", col_name="r", col_type="int")
    # step provided as float should raise
    with pytest.raises(NodeValidationError):
        node.infer_schema(
            {
                "start": Schema(type=Schema.Type.INT),
                "end": Schema(type=Schema.Type.INT),
                "step": Schema(type=Schema.Type.FLOAT),
            }
        )


def test_rangenode_large_range_raises(node_ctor):
    node = node_ctor("RangeNode", id="rg3", col_name="r", col_type="int")
    node.infer_schema(
        {"start": Schema(type=Schema.Type.INT), "end": Schema(type=Schema.Type.INT)}
    )
    # make a huge range to trigger execution error
    import importlib
    mod = importlib.import_module('server.interpreter.nodes.input.table')
    from pytest import MonkeyPatch
    mp = MonkeyPatch()
    mp.setattr(mod, "MAX_GENERATED_TABLE_ROWS", 100000)
    try:
        with pytest.raises(NodeExecutionError):
            node.process({"start": Data(payload=0), "end": Data(payload=200000)})
    finally:
        mp.undo()


def test_tablenode_mixed_type_int_float_conversion(node_ctor):
    # provide float for FLOAT column to satisfy Table dtype checks
    rows = [{"a": 1, "b": 2.0}]
    col_names = ["a", "b"]
    col_types = {"a": ColType.INT, "b": ColType.FLOAT}
    node = node_ctor(
        "TableNode", id="tn2", rows=rows, col_names=col_names, col_types=col_types
    )
    res = node.process({})
    # b should be converted to float
    assert float(res["table"].payload.df.iloc[0]["b"]) == 2.0


def test_tablenode_illegal_col_name_rejected(node_ctor):
    rows = [{"_a": 1}]
    col_names = ["_a"]
    col_types = {"_a": ColType.INT}
    with pytest.raises(NodeParameterError):
        node_ctor(
            "TableNode",
            id="tn-illegal",
            rows=rows,
            col_names=col_names,
            col_types=col_types,
        )


def test_randomnode_infer_type_mismatch_min_max(node_ctor):
    node = node_ctor("RandomNode", id="rn4", col_name="c", col_type="float")
    # min_value provided as INT while float expected
    with pytest.raises(NodeValidationError):
        node.infer_schema(
            {
                "row_count": Schema(type=Schema.Type.INT),
                "min_value": Schema(type=Schema.Type.INT),
                "max_value": Schema(type=Schema.Type.FLOAT),
            }
        )


def test_randomnode_process_float_and_str_bool(node_ctor):
    # float case
    node = node_ctor("RandomNode", id="rn5", col_name="c", col_type="float")
    node.infer_schema(
        {
            "row_count": Schema(type=Schema.Type.INT),
            "min_value": Schema(type=Schema.Type.FLOAT),
            "max_value": Schema(type=Schema.Type.FLOAT),
        }
    )
    out = node.process(
        {
            "row_count": Data(payload=2),
            "min_value": Data(payload=0.0),
            "max_value": Data(payload=1.0),
        }
    )
    assert len(out["table"].payload.df) == 2
    # str case
    node2 = node_ctor("RandomNode", id="rn6", col_name="s", col_type="str")
    node2.infer_schema({"row_count": Schema(type=Schema.Type.INT)})
    out2 = node2.process({"row_count": Data(payload=3)})
    assert len(out2["table"].payload.df) == 3


def test_rangenode_float_and_datetime(node_ctor):
    # float range
    node = node_ctor("RangeNode", id="rg4", col_name="f", col_type="float")
    node.infer_schema(
        {"start": Schema(type=Schema.Type.FLOAT), "end": Schema(type=Schema.Type.FLOAT)}
    )
    out = node.process({"start": Data(payload=0.0), "end": Data(payload=3.0)})
    assert len(out["table"].payload.df) > 0
    # datetime range
    node_dt = node_ctor("RangeNode", id="rg5", col_name="d", col_type="Datetime")
    node_dt.infer_schema(
        {
            "start": Schema(type=Schema.Type.DATETIME),
            "end": Schema(type=Schema.Type.DATETIME),
        }
    )
    start = datetime(2020, 1, 1, tzinfo=timezone.utc)
    end = datetime(2020, 1, 4, tzinfo=timezone.utc)
    out_dt = node_dt.process({"start": Data(payload=start), "end": Data(payload=end)})
    assert len(out_dt["table"].payload.df) == 3


def test_tablenode_bool_column_accepts_bool(node_ctor):
    rows = [{"b": True}]
    col_names = ["b"]
    col_types = {"b": ColType.BOOL}
    node = node_ctor(
        "TableNode", id="tn-bool", rows=rows, col_names=col_names, col_types=col_types
    )
    out = node.process({})
    assert bool(out["table"].payload.df.iloc[0]["b"]) is True


def test_tablenode_float_in_int_column_rejects(node_ctor):
    rows = [{"a": 1.5}]
    col_names = ["a"]
    col_types = {"a": ColType.INT}
    with pytest.raises(NodeParameterError):
        node_ctor(
            "TableNode",
            id="tn-float-int",
            rows=rows,
            col_names=col_names,
            col_types=col_types,
        )


def test_rangenode_int_negative_step(node_ctor):
    node = node_ctor("RangeNode", id="rg-neg", col_name="n", col_type="int")
    node.infer_schema(
        {
            "start": Schema(type=Schema.Type.INT),
            "end": Schema(type=Schema.Type.INT),
            "step": Schema(type=Schema.Type.INT),
        }
    )
    res = node.process(
        {"start": Data(payload=5), "end": Data(payload=1), "step": Data(payload=-1)}
    )
    # should produce 5,4,3,2
    assert len(res["table"].payload.df) == 4


def test_tablenode_string_column_accepts_str(node_ctor):
    rows = [{"s": "hello"}]
    col_names = ["s"]
    col_types = {"s": ColType.STR}
    node = node_ctor(
        "TableNode", id="tn-str", rows=rows, col_names=col_names, col_types=col_types
    )
    res = node.process({})
    # ensure the stored value is a string/object
    assert str(res["table"].payload.df.iloc[0]["s"]) == "hello"


def test_tablenode_datetime_without_tz_gets_default_timezone(node_ctor):
    # naive ISO datetime string should be parsed and assigned DEFAULT_TIMEZONE
    rows = [{"ts": "2020-01-02T03:04:05"}]
    col_names = ["ts"]
    col_types = {"ts": ColType.DATETIME}
    node = node_ctor(
        "TableNode",
        id="tn-dt-naive",
        rows=rows,
        col_names=col_names,
        col_types=col_types,
    )
    # validate_parameters populates _rows with pandas.Timestamp
    assert node._rows is not None
    ts_val = node._rows[0]["ts"]
    assert isinstance(ts_val, pd.Timestamp)
    # timezone should be set to DEFAULT_TIMEZONE
    assert ts_val.tzinfo == DEFAULT_TIMEZONE


def test_randomnode_unsupported_col_type_runtime(node_ctor):
    node = node_ctor("RandomNode", id="rn-unk", col_name="c", col_type="int")
    # infer first to set internal _col_types, then change col_type to unsupported value
    node.infer_schema(
        {
            "row_count": Schema(type=Schema.Type.INT),
            "min_value": Schema(type=Schema.Type.INT),
            "max_value": Schema(type=Schema.Type.INT),
        }
    )
    node.col_type = "unknown"
    with pytest.raises(NodeExecutionError):
        node.process(
            {
                "row_count": Data(payload=1),
                "min_value": Data(payload=0),
                "max_value": Data(payload=10),
            }
        )


def test_tablenode_unsupported_value_type(node_ctor):
    rows = [{"a": [1, 2, 3]}]
    col_names = ["a"]
    col_types = {"a": ColType.INT}
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        node_ctor(
            "TableNode",
            id="tn-unsupported",
            rows=rows,
            col_names=col_names,
            col_types=col_types,
        )


def test_randomnode_default_col_name_generation(node_ctor):
    node = node_ctor("RandomNode", id="rn-default", col_name=None, col_type="int")
    # infer with required schemas
    node.infer_schema(
        {
            "row_count": Schema(type=Schema.Type.INT),
            "min_value": Schema(type=Schema.Type.INT),
            "max_value": Schema(type=Schema.Type.INT),
        }
    )
    assert node.col_name is not None and node.col_name.startswith("rn-default_")


def test_rangenode_float_negative_step(node_ctor):
    node = node_ctor("RangeNode", id="rgf", col_name="f", col_type="float")
    node.infer_schema(
        {
            "start": Schema(type=Schema.Type.FLOAT),
            "end": Schema(type=Schema.Type.FLOAT),
            "step": Schema(type=Schema.Type.FLOAT),
        }
    )
    res = node.process(
        {
            "start": Data(payload=5.0),
            "end": Data(payload=1.0),
            "step": Data(payload=-1.0),
        }
    )
    assert len(res["table"].payload.df) > 0


def test_rangenode_datetime_negative_step(node_ctor):
    node = node_ctor("RangeNode", id="rg-dt-neg", col_name="d", col_type="Datetime")
    node.infer_schema(
        {
            "start": Schema(type=Schema.Type.DATETIME),
            "end": Schema(type=Schema.Type.DATETIME),
            "step": Schema(type=Schema.Type.DATETIME),
        }
    )
    start = datetime(2020, 1, 4, tzinfo=DEFAULT_TIMEZONE)
    end = datetime(2020, 1, 1, tzinfo=DEFAULT_TIMEZONE)
    step = timedelta(days=-1)
    # Data model does not accept timedelta payloads, so provide a simple object with `.payload`
    StepObj = type("StepObj", (), {})
    step_obj = StepObj()
    step_obj.payload = step # type: ignore
    out = node.process(
        {"start": Data(payload=start), "end": Data(payload=end), "step": step_obj}
    )
    assert len(out["table"].payload.df) > 0

def test_tablenode_rejects_wrong_node_type(node_ctor):
    """Construct stage: wrong node type raises NodeParameterError."""
    # Create a valid node then mutate type to trigger validation error
    node = node_ctor("TableNode", id="t-bad-type", rows=[{"a": 1}], col_names=["a"], col_types={"a": ColType.INT})
    # Directly mutate the type attribute to bypass pydantic validation
    object.__setattr__(node, "type", "WrongType")
    # Now call validate_parameters which should raise
    with pytest.raises(NodeParameterError):
        node.validate_parameters()


def test_tablenode_string_in_non_str_datetime_col_raises(node_ctor):
    """Construct stage: string value in INT column raises error (line 102)."""
    rows = [{"a": "not_a_number"}]
    with pytest.raises(NodeParameterError):
        node_ctor("TableNode", id="t-str-int", rows=rows, col_names=["a"], col_types={"a": ColType.INT})


def test_tablenode_bool_in_non_bool_col_raises(node_ctor):
    """Construct stage: bool value in non-BOOL column raises error (line 111)."""
    rows = [{"a": True}]
    with pytest.raises(NodeParameterError):
        node_ctor("TableNode", id="t-bool-int", rows=rows, col_names=["a"], col_types={"a": ColType.INT})


def test_randomnode_rejects_wrong_node_type(node_ctor):
    """Construct stage: wrong node type raises NodeParameterError (line 185)."""
    node = node_ctor("RandomNode", id="r-bad-type", col_name="c", col_type="int")
    object.__setattr__(node, "type", "WrongType")
    with pytest.raises(NodeParameterError):
        node.validate_parameters()


def test_randomnode_rejects_illegal_col_name(node_ctor):
    """Construct stage: illegal column name raises error (line 193)."""
    with pytest.raises(NodeParameterError):
        node_ctor("RandomNode", id="r-illegal", col_name="_illegal", col_type="int")


def test_randomnode_infer_requires_max_value(node_ctor):
    """Static analysis: missing max_value for numeric col_type raises (line 256)."""
    node = node_ctor("RandomNode", id="r-no-max", col_name="c", col_type="int")
    with pytest.raises(NodeValidationError):
        node.infer_schema({"row_count": Schema(type=Schema.Type.INT), "min_value": Schema(type=Schema.Type.INT)})


def test_randomnode_infer_max_value_type_mismatch(node_ctor):
    """Static analysis: max_value type mismatch raises (line 265, 272)."""
    node = node_ctor("RandomNode", id="r-max-mismatch", col_name="c", col_type="int")
    with pytest.raises(NodeValidationError):
        node.infer_schema({
            "row_count": Schema(type=Schema.Type.INT),
            "min_value": Schema(type=Schema.Type.INT),
            "max_value": Schema(type=Schema.Type.FLOAT)
        })


def test_randomnode_bool_generation(node_ctor):
    """Execute stage: bool column generation (line 331)."""
    node = node_ctor("RandomNode", id="r-bool", col_name="b", col_type="bool")
    node.infer_schema({"row_count": Schema(type=Schema.Type.INT)})
    out = node.process({"row_count": Data(payload=5)})
    assert len(out["table"].payload.df) == 5
    assert out["table"].payload.col_types["b"] == ColType.BOOL


def test_rangenode_rejects_wrong_node_type(node_ctor):
    """Construct stage: wrong node type raises NodeParameterError (line 371)."""
    node = node_ctor("RangeNode", id="rg-bad-type", col_name="r", col_type="int")
    object.__setattr__(node, "type", "WrongType")
    with pytest.raises(NodeParameterError):
        node.validate_parameters()


def test_rangenode_rejects_illegal_col_name(node_ctor):
    """Construct stage: illegal column name raises error (line 379)."""
    with pytest.raises(NodeParameterError):
        node_ctor("RangeNode", id="rg-illegal", col_name="_illegal", col_type="int")


def test_rangenode_float_start_type_mismatch(node_ctor):
    """Static analysis: start type mismatch for float raises (line 426)."""
    node = node_ctor("RangeNode", id="rg-float-start", col_name="r", col_type="float")
    with pytest.raises(NodeValidationError):
        node.infer_schema({"start": Schema(type=Schema.Type.INT), "end": Schema(type=Schema.Type.FLOAT)})


def test_rangenode_float_end_type_mismatch(node_ctor):
    """Static analysis: end type mismatch for float raises (line 433)."""
    node = node_ctor("RangeNode", id="rg-float-end", col_name="r", col_type="float")
    with pytest.raises(NodeValidationError):
        node.infer_schema({"start": Schema(type=Schema.Type.FLOAT), "end": Schema(type=Schema.Type.INT)})


def test_rangenode_float_step_type_mismatch(node_ctor):
    """Static analysis: step type mismatch for float raises (line 441)."""
    node = node_ctor("RangeNode", id="rg-float-step", col_name="r", col_type="float")
    with pytest.raises(NodeValidationError):
        node.infer_schema({
            "start": Schema(type=Schema.Type.FLOAT),
            "end": Schema(type=Schema.Type.FLOAT),
            "step": Schema(type=Schema.Type.INT)
        })


def test_rangenode_int_start_type_mismatch(node_ctor):
    """Static analysis: start type mismatch for int raises (line 449)."""
    node = node_ctor("RangeNode", id="rg-int-start", col_name="r", col_type="int")
    with pytest.raises(NodeValidationError):
        node.infer_schema({"start": Schema(type=Schema.Type.FLOAT), "end": Schema(type=Schema.Type.INT)})


def test_rangenode_int_end_type_mismatch(node_ctor):
    """Static analysis: end type mismatch for int raises (line 456)."""
    node = node_ctor("RangeNode", id="rg-int-end", col_name="r", col_type="int")
    with pytest.raises(NodeValidationError):
        node.infer_schema({"start": Schema(type=Schema.Type.INT), "end": Schema(type=Schema.Type.FLOAT)})


def test_rangenode_datetime_start_type_mismatch(node_ctor):
    """Static analysis: start type mismatch for datetime raises (line 472)."""
    node = node_ctor("RangeNode", id="rg-dt-start", col_name="r", col_type="Datetime")
    with pytest.raises(NodeValidationError):
        node.infer_schema({"start": Schema(type=Schema.Type.INT), "end": Schema(type=Schema.Type.DATETIME)})


def test_rangenode_datetime_end_type_mismatch(node_ctor):
    """Static analysis: end type mismatch for datetime raises (line 479)."""
    node = node_ctor("RangeNode", id="rg-dt-end", col_name="r", col_type="Datetime")
    with pytest.raises(NodeValidationError):
        node.infer_schema({"start": Schema(type=Schema.Type.DATETIME), "end": Schema(type=Schema.Type.INT)})


def test_rangenode_datetime_step_type_mismatch(node_ctor):
    """Static analysis: step type mismatch for datetime raises (line 487)."""
    node = node_ctor("RangeNode", id="rg-dt-step", col_name="r", col_type="Datetime")
    with pytest.raises(NodeValidationError):
        node.infer_schema({
            "start": Schema(type=Schema.Type.DATETIME),
            "end": Schema(type=Schema.Type.DATETIME),
            "step": Schema(type=Schema.Type.INT)
        })


def test_rangenode_float_no_step_uses_default(node_ctor):
    """Execute stage: float range without step uses default 1.0 (line 547)."""
    node = node_ctor("RangeNode", id="rg-float-nostep", col_name="r", col_type="float")
    node.infer_schema({"start": Schema(type=Schema.Type.FLOAT), "end": Schema(type=Schema.Type.FLOAT)})
    out = node.process({"start": Data(payload=0.0), "end": Data(payload=3.0)})
    # should generate 0.0, 1.0, 2.0 -> length 3
    assert len(out["table"].payload.df) == 3


def test_rangenode_int_no_step_uses_default(node_ctor):
    """Execute stage: int range without step uses default 1 (line 562)."""
    node = node_ctor("RangeNode", id="rg-int-nostep", col_name="r", col_type="int")
    node.infer_schema({"start": Schema(type=Schema.Type.INT), "end": Schema(type=Schema.Type.INT)})
    out = node.process({"start": Data(payload=0), "end": Data(payload=3)})
    # should generate 0, 1, 2 -> length 3
    assert len(out["table"].payload.df) == 3


def test_rangenode_datetime_no_step_uses_default(node_ctor):
    """Execute stage: datetime range without step uses default 1 day (line 577)."""
    node = node_ctor("RangeNode", id="rg-dt-nostep", col_name="r", col_type="Datetime")
    node.infer_schema({"start": Schema(type=Schema.Type.DATETIME), "end": Schema(type=Schema.Type.DATETIME)})
    start = datetime(2020, 1, 1, tzinfo=DEFAULT_TIMEZONE)
    end = datetime(2020, 1, 4, tzinfo=DEFAULT_TIMEZONE)
    out = node.process({"start": Data(payload=start), "end": Data(payload=end)})
    # should generate 2020-01-01, 2020-01-02, 2020-01-03 -> length 3
    assert len(out["table"].payload.df) == 3


def test_tablenode_int_in_str_col_raises(node_ctor):
    """Construct stage: int value in STR column raises error (line 119-122)."""
    rows = [{"a": 123}]
    with pytest.raises(NodeParameterError):
        node_ctor("TableNode", id="t-int-str", rows=rows, col_names=["a"], col_types={"a": ColType.STR})


def test_randomnode_infer_missing_row_count(node_ctor):
    """Static analysis: missing row_count raises (line 272)."""
    node = node_ctor("RandomNode", id="r-no-rowcount", col_name="c", col_type="str")
    with pytest.raises(NodeValidationError):
        node.infer_schema({})


def test_rangenode_default_col_name_generation(node_ctor):
    """Construct stage: empty col_name triggers default generation (line 377)."""
    node = node_ctor("RangeNode", id="rg-default", col_name=None, col_type="int")
    # Validate should set a default col_name
    assert node.col_name is not None and node.col_name.startswith("rg-default_")


def test_tablenode_int_in_datetime_col_raises(node_ctor):
    """Construct stage: int value in DATETIME column raises error (line 120)."""
    rows = [{"a": 123}]
    with pytest.raises(NodeParameterError):
        node_ctor("TableNode", id="t-int-dt", rows=rows, col_names=["a"], col_types={"a": ColType.DATETIME})


def test_tablenode_complex_object_in_col_raises(node_ctor):
    """Construct stage: complex object value raises unsupported type error (line 137)."""
    rows = [{"a": {"nested": "dict"}}]
    from pydantic import ValidationError
    with pytest.raises((NodeParameterError, ValidationError)):
        node_ctor("TableNode", id="t-obj", rows=rows, col_names=["a"], col_types={"a": ColType.STR})
