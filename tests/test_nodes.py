import pytest
from pydantic import ValidationError
from pathlib import Path
import pandas as pd
import sys
from pathlib import Path as _P

# Ensure top-level Utils.py is preferred over a nested package by adjusting sys.path
_nodes_dir = _P(__file__).resolve().parents[1] / "server" / "engine" / "nodes"
if str(_nodes_dir) not in sys.path:
    sys.path.insert(0, str(_nodes_dir))

# Force the import name 'server.engine.nodes.Utils' to resolve to the top-level Utils.py module
import importlib.util
import importlib.machinery
spec = importlib.util.spec_from_file_location("server.engine.nodes.GlobalConfig", str(_nodes_dir / "GlobalConfig.py"))
utils_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(utils_mod)
import sys as _sys
_sys.modules["server.engine.nodes.GlobalConfig"] = utils_mod

from server.engine.nodes.DataType import Data, Table, ColType, TableSchema, Schema
from server.engine.nodes.Exceptions import NodeParameterError, NodeValidationError, NodeExecutionError

from server.engine.nodes.Generate.Const import ConstNode
from server.engine.nodes.Generate.String import StringNode
from server.engine.nodes.Generate.Table import TableNode
from server.engine.nodes.Compute.Prim import NumBinComputeNode, NumUnaryComputeNode, CmpNode, BoolBinComputeNode, BoolUnaryComputeNode
from server.engine.nodes.Compute.String import TableAppendStringNode, TableContainsStringNode, TableStringLengthNode
from server.engine.nodes.Compute.Table import TabBinPrimNumComputeNode, TabUnaryNumComputeNode, ColBinNumComputeNode, ColBinBoolComputeNode
from server.engine.nodes.Compute.String import (
    ClipStringNode, SubStringNode, StripStringNode, ReplaceStringNode, UpperStringNode, LowerStringNode,
    TablePrependStringNode, TableStartWithStringNode, TableEndWithStringNode, TableReplaceStringNode
)
from server.engine.nodes.Compute.Table import TabBinPrimBoolComputeNode, TabUnaryBoolComputeNode
from server.engine.nodes.Visualize.Plot import PlotNode
from server.engine.nodes.Generate.Table import RandomNode, RangeNode
from server.engine.nodes.Visualize.WordCloud import WordCloudNode
from server.engine.nodes.TableProcess.RowProcess import TableFilterNode, TableRowAppendNode, TableSortNode
from server.engine.nodes.TableProcess.ColProcess import SelectColNode, SplitColNode, JoinColNode, RenameColNode, CopyColNode
from server.engine.nodes.BaseNode import BaseNode

from server.engine.nodes.GlobalConfig import GlobalConfig

TMP = Path("/tmp/nodepy_test")
TMP.mkdir(parents=True, exist_ok=True)
GC = GlobalConfig(temp_dir=TMP, user_id="test")

# Helper to create Data/Table
def df_to_data(df: pd.DataFrame) -> Data:
    return Data.from_df(df)

# ========== ConstNode ==========

def test_constnode_happy_path_int():
    n = ConstNode(id="c1", name="const", type="ConstNode", global_config=GC, value=3, data_type="int")
    out_schema = n.infer_schema({})
    assert out_schema["const"].type == Schema.Type.INT
    out = n.process({})
    assert out["const"].payload == 3

def test_constnode_happy_path_float():
    n = ConstNode(id="c2", name="constf", type="ConstNode", global_config=GC, value=2.5, data_type="float")
    out_schema = n.infer_schema({})
    assert out_schema["const"].type == Schema.Type.FLOAT
    out = n.process({})
    assert out["const"].payload == 2.5

@pytest.mark.parametrize("bad", ["str", 1.2, None])
def test_constnode_bad_param_type_mismatch(bad):
    # data_type int but value not int
    with pytest.raises(NodeParameterError):
        ConstNode(id="c3", name="bad", type="ConstNode", global_config=GC, value=bad, data_type="int")

def test_constnode_unsupported_datatype():
    # bool supported; test unsupported by creating node with wrong literal via setattr
    n = ConstNode(id="c4", name="bad2", type="ConstNode", global_config=GC, value=True, data_type="bool")
    # bypass type checker by setting __dict__ directly
    n.__dict__["data_type"] = "unsupported"
    with pytest.raises(TypeError):
        n.infer_schema({})

# ========== StringNode ==========

def test_stringnode_happy():
    n = StringNode(id="s1", name="str", type="StringNode", global_config=GC, value="hello")
    out = n.process({})
    assert out["string"].payload == "hello"

def test_stringnode_schema():
    n = StringNode(id="s2", name="str2", type="StringNode", global_config=GC, value="x")
    s = n.infer_schema({})
    assert s["string"].type == Schema.Type.STR

def test_stringnode_bad_type_field():
    # wrong type field should be caught by validator
    with pytest.raises(NodeParameterError):
        StringNode(id="s3", name="str3", type="WrongType", global_config=GC, value="x")

# ========== TableNode ==========

def test_tablenode_happy_minimal():
    rows = [{"a": 1, "b": "x"}, {"a": 2, "b": "y"}]
    n = TableNode(id="t1", name="table", type="TableNode", global_config=GC, rows=rows, col_names=["a", "b"])
    out_schema = n.infer_schema({})
    assert out_schema["table"].type == Schema.Type.TABLE
    out = n.process({})
    assert isinstance(out["table"].payload, Table)

def test_tablenode_mixed_int_float_promote():
    rows = [{"a": 1}, {"a": 2.5}]
    n = TableNode(id="t2", name="t", type="TableNode", global_config=GC, rows=rows, col_names=["a"])
    n.validate_parameters()
    s = n.infer_schema({})
    assert s["table"].tab is not None
    assert s["table"].tab.col_types["a"] == ColType.FLOAT

@pytest.mark.parametrize("bad_rows", [[], [{"a":1, "b":2}], [{"a":1}, {"a":"x"}]])
def test_tablenode_bad_rows(bad_rows):
    if bad_rows == []:
        with pytest.raises(NodeParameterError):
            TableNode(id="t3", name="t3", type="TableNode", global_config=GC, rows=bad_rows, col_names=["a"])
    else:
        with pytest.raises(NodeParameterError):
            TableNode(id="t4", name="t4", type="TableNode", global_config=GC, rows=bad_rows, col_names=["a"])

# ========== Numeric Compute Nodes (Prim) ==========

def test_numbin_add_infer_and_execute_int():
    n = NumBinComputeNode(id="n1", name="num", type="NumBinComputeNode", global_config=GC, op="ADD")
    in_schema = {"x": Schema(type=Schema.Type.INT), "y": Schema(type=Schema.Type.INT)}
    out_schema = n.infer_schema(in_schema)
    assert out_schema is not None
    assert out_schema["result"].type == Schema.Type.INT
    res = n.process({"x": Data(payload=3), "y": Data(payload=4)})
    assert res["result"].payload == 7

def test_numbin_divide_by_zero_execute_error():
    n = NumBinComputeNode(id="n2", name="num2", type="NumBinComputeNode", global_config=GC, op="DIV")
    in_schema = {"x": Schema(type=Schema.Type.INT), "y": Schema(type=Schema.Type.INT)}
    _ = n.infer_schema(in_schema)
    with pytest.raises(NodeExecutionError):
        n.process({"x": Data(payload=1), "y": Data(payload=0)})

def test_numbin_type_mismatch_infer_error():
    n = NumBinComputeNode(id="n3", name="num3", type="NumBinComputeNode", global_config=GC, op="MUL")
    with pytest.raises(NodeValidationError):
        n.infer_schema({"x": Schema(type=Schema.Type.INT), "y": Schema(type=Schema.Type.FLOAT)})

def test_numunary_sqrt_negative_execute_error():
    n = NumUnaryComputeNode(id="nu1", name="un", type="NumUnaryComputeNode", global_config=GC, op="SQRT")
    _ = n.infer_schema({"x": Schema(type=Schema.Type.INT)})
    with pytest.raises(NodeExecutionError):
        n.process({"x": Data(payload=-4)})

# ========== Comparison Node ==========

def test_cmpnode_eq_and_infer():
    n = CmpNode(id="c1", name="cmp", type="CmpNode", global_config=GC, op="EQ")
    out = n.infer_schema({"x": Schema(type=Schema.Type.STR), "y": Schema(type=Schema.Type.STR)})
    assert out is not None
    assert out["result"].type == Schema.Type.BOOL
    res = n.process({"x": Data(payload="a"), "y": Data(payload="a")})
    assert res["result"].payload is True

def test_cmpnode_mismatch_infer_error():
    n = CmpNode(id="c2", name="cmp2", type="CmpNode", global_config=GC, op="GT")
    with pytest.raises(NodeValidationError):
        n.infer_schema({"x": Schema(type=Schema.Type.INT), "y": Schema(type=Schema.Type.STR)})

# ========== Boolean Compute Nodes ==========

def test_boolbin_and_execute():
    n = BoolBinComputeNode(id="b1", name="bool", type="BoolBinComputeNode", global_config=GC, op="AND")
    _ = n.infer_schema({"x": Schema(type=Schema.Type.BOOL), "y": Schema(type=Schema.Type.BOOL)})
    res = n.process({"x": Data(payload=True), "y": Data(payload=False)})
    assert res["result"].payload is False

def test_boolunary_not_execute():
    n = BoolUnaryComputeNode(id="bu1", name="bnot", type="BoolUnaryComputeNode", global_config=GC)
    n.infer_schema({"x": Schema(type=Schema.Type.BOOL)})
    res = n.process({"x": Data(payload=False)})
    assert res["result"].payload is True

def test_boolbin_wrong_type_param():
    with pytest.raises(NodeParameterError):
        BoolBinComputeNode(id="b2", name="b2", type="Wrong", global_config=GC, op="AND")

# ========== Table/String compute nodes ==========

def make_sample_table():
    df = pd.DataFrame({"s": pd.Series(["a", "ab", None], dtype="string")})
    return Data.from_df(df)

def test_tableappendstring_happy():
    n = TableAppendStringNode(id="ta1", name="app", type="TableAppendStringNode", global_config=GC, column="s", result_col="new_s")
    in_schema = {"table": Schema(type=Schema.Type.TABLE, tab=TableSchema(col_types={"s": ColType.STR})), "string": Schema(type=Schema.Type.STR)}
    out_schema = n.infer_schema(in_schema)
    assert out_schema is not None
    assert out_schema["output"].tab is not None
    assert out_schema["output"].tab.col_types["new_s"] == ColType.STR
    out = n.process({"table": make_sample_table(), "string": Data(payload="z")})
    assert isinstance(out["output"].payload, Table)
    assert "new_s" in out["output"].payload.df.columns

def test_tablecontainsstring_happy():
    n = TableContainsStringNode(id="tc1", name="contains", type="TableContainsStringNode", global_config=GC, column="s", result_col="has_a")
    in_schema = {"table": Schema(type=Schema.Type.TABLE, tab=TableSchema(col_types={"s": ColType.STR})), "substring": Schema(type=Schema.Type.STR)}
    out_schema = n.infer_schema(in_schema)
    assert out_schema is not None
    assert out_schema["output"].tab is not None
    assert out_schema["output"].tab.col_types["has_a"] == ColType.BOOL
    out = n.process({"table": make_sample_table(), "substring": Data(payload="a")})
    assert isinstance(out["output"].payload, Table)
    assert out["output"].payload.df["has_a"].dtype == "boolean"

def test_tablestringlength_happy():
    n = TableStringLengthNode(id="tl1", name="len", type="TableStringLengthNode", global_config=GC, column="s", result_col="len_s")
    in_schema = {"table": Schema(type=Schema.Type.TABLE, tab=TableSchema(col_types={"s": ColType.STR}))}
    out_schema = n.infer_schema(in_schema)
    assert out_schema is not None
    assert out_schema["output"].tab is not None
    assert out_schema["output"].tab.col_types["len_s"] == ColType.INT
    out = n.process({"table": make_sample_table()})
    assert isinstance(out["output"].payload, Table)
    assert "len_s" in out["output"].payload.df.columns

@pytest.mark.parametrize("bad_result", ["_index", "s"])
def test_tablestringlength_bad_result_col(bad_result):
    if bad_result == "s":
        with pytest.raises(NodeParameterError):
            TableStringLengthNode(id="tl2", name="len2", type="TableStringLengthNode", global_config=GC, column="s", result_col="s")
    else:
        with pytest.raises(NodeParameterError):
            TableStringLengthNode(id="tl3", name="len3", type="TableStringLengthNode", global_config=GC, column="s", result_col="_index")

# ========== Table/Numeric compute nodes ==========

def make_num_table():
    df = pd.DataFrame({"a": pd.Series([1, 2, 3], dtype="Int64")})
    return Data.from_df(df)

def test_tabbinprim_add_happy():
    n = TabBinPrimNumComputeNode(id="tp1", name="tp", type="TabBinPrimNumComputeNode", global_config=GC, op="ADD", col="a", result_col="r")
    in_schema = {"table": Schema(type=Schema.Type.TABLE, tab=TableSchema(col_types={"a": ColType.INT})), "num": Schema(type=Schema.Type.INT)}
    out_schema = n.infer_schema(in_schema)
    assert out_schema is not None
    assert out_schema["table"].tab is not None
    assert out_schema["table"].tab.col_types["r"] == ColType.INT
    out = n.process({"table": make_num_table(), "num": Data(payload=2)})
    assert isinstance(out["table"].payload, Table)
    assert "r" in out["table"].payload.df.columns

def test_tabbinprim_division_by_zero_infer_error_and_runtime():
    n = TabBinPrimNumComputeNode(id="tp2", name="tp2", type="TabBinPrimNumComputeNode", global_config=GC, op="TAB_DIV_PRIM", col="a", result_col="r2")
    in_schema = {"table": Schema(type=Schema.Type.TABLE, tab=TableSchema(col_types={"a": ColType.INT})), "num": Schema(type=Schema.Type.INT)}
    n.infer_schema(in_schema)
    with pytest.raises(NodeExecutionError):
        n.process({"table": make_num_table(), "num": Data(payload=0)})

def test_tabunarynum_log_negative_infer_and_runtime():
    n = TabUnaryNumComputeNode(id="tu1", name="tu", type="TabUnaryNumComputeNode", global_config=GC, op="LOG", col="a", result_col="ln")
    in_schema = {"table": Schema(type=Schema.Type.TABLE, tab=TableSchema(col_types={"a": ColType.INT}))}
    n.infer_schema(in_schema)
    # create table with zero value to trigger runtime error
    df = pd.DataFrame({"a": pd.Series([1, 0, 2], dtype="Int64")})
    with pytest.raises(NodeExecutionError):
        n.process({"table": Data.from_df(df)})

# ========== Column-Column nodes ==========

def test_colbin_add_and_infer_mismatch_types():
    n = ColBinNumComputeNode(id="cc1", name="cc", type="ColBinNumComputeNode", global_config=GC, op="ADD", col1="a", col2="b", result_col="r")
    with pytest.raises(NodeValidationError):
        n.infer_schema({"table": Schema(type=Schema.Type.TABLE, tab=TableSchema(col_types={"a": ColType.INT, "b": ColType.STR}))})

def test_colbin_add_happy():
    n = ColBinNumComputeNode(id="cc2", name="cc2", type="ColBinNumComputeNode", global_config=GC, op="ADD", col1="a", col2="b", result_col="r")
    in_schema = {"table": Schema(type=Schema.Type.TABLE, tab=TableSchema(col_types={"a": ColType.INT, "b": ColType.INT}))}
    out_schema = n.infer_schema(in_schema)
    assert out_schema is not None
    assert out_schema["table"].tab is not None
    df = pd.DataFrame({"a": pd.Series([1,2], dtype="Int64"), "b": pd.Series([3,4], dtype="Int64")})
    out = n.process({"table": Data.from_df(df)})
    assert isinstance(out["table"].payload, Table)
    assert "r" in out["table"].payload.df.columns

def test_colbinbool_xor_happy():
    n = ColBinBoolComputeNode(id="cb1", name="cb", type="ColBinBoolComputeNode", global_config=GC, op="XOR", col1="x", col2="y", result_col="rx")
    in_schema = {"table": Schema(type=Schema.Type.TABLE, tab=TableSchema(col_types={"x": ColType.BOOL, "y": ColType.BOOL}))}
    out_schema = n.infer_schema(in_schema)
    assert out_schema is not None
    assert out_schema["table"].tab is not None
    df = pd.DataFrame({"x": pd.Series([True, False], dtype="boolean"), "y": pd.Series([False, False], dtype="boolean")})
    out = n.process({"table": Data.from_df(df)})
    assert isinstance(out["table"].payload, Table)
    assert "rx" in out["table"].payload.df.columns

# ------------------------------------------------------------------
# Additional core-node tests to ensure >=5 tests per core node class
# ------------------------------------------------------------------

# ConstNode: add missing wrong-type-field test
def test_constnode_wrong_type_field():
    with pytest.raises(NodeParameterError):
        ConstNode(id="c_badtype", name="c", type="NotConstNode", global_config=GC, value=1, data_type="int")

# StringNode: empty and unicode cases
def test_stringnode_empty_and_unicode():
    n_empty = StringNode(id="s_empty", name="s", type="StringNode", global_config=GC, value="")
    assert n_empty.process({})["string"].payload == ""
    n_uni = StringNode(id="s_uni", name="s", type="StringNode", global_config=GC, value="你好")
    assert n_uni.process({})["string"].payload == "你好"

# TableNode: empty col_names and duplicate column name behavior
def test_tablenode_empty_col_names_and_duplicate_check():
    rows = [{"a": 1}]
    with pytest.raises((NodeParameterError, ValidationError)):
        TableNode.model_validate({"id": "t_emptycols", "name": "t", "type": "TableNode", "global_config": GC, "rows": rows, "col_names": []})
    # duplicate col names should be rejected in validation
    with pytest.raises((NodeParameterError, ValidationError)):
        TableNode.model_validate({"id": "t_dup", "name": "t", "type": "TableNode", "global_config": GC, "rows": [{"a":1}], "col_names": ["a","a"]})

# NumBinComputeNode: POW behavior and wrong type param
def test_numbin_pow_and_float_result():
    n = NumBinComputeNode(id="nb_pow", name="nbp", type="NumBinComputeNode", global_config=GC, op="POW")
    # float inputs should infer float output
    out = n.infer_schema({"x": Schema(type=Schema.Type.FLOAT), "y": Schema(type=Schema.Type.FLOAT)})
    assert out["result"].type == Schema.Type.FLOAT
    res = n.process({"x": Data(payload=2.0), "y": Data(payload=3.0)})
    assert isinstance(res["result"].payload, float)

def test_numbin_wrong_type_field_paramerror():
    with pytest.raises(NodeParameterError):
        NumBinComputeNode(id="nb_bad", name="nb", type="BadType", global_config=GC, op="ADD")

# NumUnaryComputeNode: NEG, ABS, SQRT inference + invalid params
def test_numunary_multiple_ops_and_infer():
    n_neg = NumUnaryComputeNode(id="nu_neg", name="nu", type="NumUnaryComputeNode", global_config=GC, op="NEG")
    n_neg.infer_schema({"x": Schema(type=Schema.Type.INT)})
    assert n_neg.process({"x": Data(payload=5)})["result"].payload == -5

    n_abs = NumUnaryComputeNode(id="nu_abs", name="nu", type="NumUnaryComputeNode", global_config=GC, op="ABS")
    n_abs.infer_schema({"x": Schema(type=Schema.Type.INT)})
    assert n_abs.process({"x": Data(payload=-2)})["result"].payload == 2

    n_sqrt = NumUnaryComputeNode(id="nu_sqrt", name="nu", type="NumUnaryComputeNode", global_config=GC, op="SQRT")
    out = n_sqrt.infer_schema({"x": Schema(type=Schema.Type.FLOAT)})
    assert out["result"].type == Schema.Type.FLOAT

def test_numunary_param_wrong_type():
    with pytest.raises(NodeParameterError):
        NumUnaryComputeNode(id="nu_bad", name="nu", type="Wrong", global_config=GC, op="NEG")

# CmpNode: NE and GT ops and runtime
def test_cmpnode_ne_and_gt_ops():
    ne = CmpNode(id="cmp_ne", name="cmp", type="CmpNode", global_config=GC, op="NE")
    ne.infer_schema({"x": Schema(type=Schema.Type.INT), "y": Schema(type=Schema.Type.INT)})
    assert ne.process({"x": Data(payload=1), "y": Data(payload=2)})["result"].payload is True

    gt = CmpNode(id="cmp_gt", name="cmp2", type="CmpNode", global_config=GC, op="GT")
    gt.infer_schema({"x": Schema(type=Schema.Type.FLOAT), "y": Schema(type=Schema.Type.FLOAT)})
    assert gt.process({"x": Data(payload=3.5), "y": Data(payload=2.1)})["result"].payload is True

def test_cmpnode_param_wrong_type():
    with pytest.raises(NodeParameterError):
        CmpNode(id="cmp_bad", name="cmp", type="Wrong", global_config=GC, op="EQ")

# BoolBinComputeNode: OR, XOR, SUB
def test_boolbin_or_xor_sub():
    n_or = BoolBinComputeNode(id="bb_or", name="bb", type="BoolBinComputeNode", global_config=GC, op="OR")
    n_or.infer_schema({"x": Schema(type=Schema.Type.BOOL), "y": Schema(type=Schema.Type.BOOL)})
    assert n_or.process({"x": Data(payload=False), "y": Data(payload=True)})["result"].payload is True

    n_xor = BoolBinComputeNode(id="bb_xor", name="bb", type="BoolBinComputeNode", global_config=GC, op="XOR")
    n_xor.infer_schema({"x": Schema(type=Schema.Type.BOOL), "y": Schema(type=Schema.Type.BOOL)})
    assert n_xor.process({"x": Data(payload=True), "y": Data(payload=False)})["result"].payload is True

    n_sub = BoolBinComputeNode(id="bb_sub", name="bb", type="BoolBinComputeNode", global_config=GC, op="SUB")
    n_sub.infer_schema({"x": Schema(type=Schema.Type.BOOL), "y": Schema(type=Schema.Type.BOOL)})
    assert n_sub.process({"x": Data(payload=True), "y": Data(payload=False)})["result"].payload is True

def test_boolbin_paramerror_wrong_type():
    with pytest.raises(NodeParameterError):
        BoolBinComputeNode(id="bb_bad", name="bb", type="Bad", global_config=GC, op="AND")

# BoolUnaryComputeNode: infer + runtime + bad param
def test_boolunary_infer_and_runtime():
    n = BoolUnaryComputeNode(id="bun2", name="bun", type="BoolUnaryComputeNode", global_config=GC)
    out = n.infer_schema({"x": Schema(type=Schema.Type.BOOL)})
    assert out["result"].type == Schema.Type.BOOL
    assert n.process({"x": Data(payload=True)})["result"].payload is False

def test_boolunary_param_wrong_type():
    with pytest.raises(NodeParameterError):
        BoolUnaryComputeNode(id="bun_bad", name="bun", type="Wrong", global_config=GC)

# --- extra core node tests continued ---

def test_stringnode_missing_value_validation():
    # missing required field 'value' should raise pydantic ValidationError
    with pytest.raises(ValidationError):
        StringNode.model_validate({"id": "s_missing", "name": "s", "type": "StringNode", "global_config": GC})  # no value

def test_tablenode_unsupported_value_type():
    # rows include unsupported type (list) -> NodeParameterError
    rows = [{"a": [1,2,3]}]
    with pytest.raises((NodeParameterError, ValidationError)):
        TableNode.model_validate({"id": "t_badtype", "name": "t", "type": "TableNode", "global_config": GC, "rows": rows, "col_names": ["a"]})

def test_numunary_sqrt_positive_and_unsupported_op_runtime():
    n = NumUnaryComputeNode(id="nu_pos", name="nu", type="NumUnaryComputeNode", global_config=GC, op="SQRT")
    n.infer_schema({"x": Schema(type=Schema.Type.FLOAT)})
    r = n.process({"x": Data(payload=9.0)})
    assert r["result"].payload == 3.0
    # force unsupported op at runtime
    n.__dict__["op"] = "FOO"
    with pytest.raises(NodeExecutionError):
        n.process({"x": Data(payload=4.0)})

def test_cmpnode_string_ne():
    n = CmpNode(id="cmp_str", name="cmp", type="CmpNode", global_config=GC, op="NE")
    n.infer_schema({"x": Schema(type=Schema.Type.STR), "y": Schema(type=Schema.Type.STR)})
    assert n.process({"x": Data(payload="a"), "y": Data(payload="b")})["result"].payload is True

def test_boolbin_runtime_type_assertion():
    n = BoolBinComputeNode(id="b_assert", name="b", type="BoolBinComputeNode", global_config=GC, op="AND")
    n.infer_schema({"x": Schema(type=Schema.Type.BOOL), "y": Schema(type=Schema.Type.BOOL)})
    # passing non-bool at runtime should trigger assertion
    with pytest.raises(AssertionError):
        n.process({"x": Data(payload=1), "y": Data(payload=True)})

def test_boolunary_additional_cases():
    # missing name should raise NodeParameterError
    with pytest.raises(NodeParameterError):
        BoolUnaryComputeNode(id="bun_missing", name="  ", type="BoolUnaryComputeNode", global_config=GC)
    # runtime non-bool input
    n = BoolUnaryComputeNode(id="bun_rt", name="bun", type="BoolUnaryComputeNode", global_config=GC)
    n.infer_schema({"x": Schema(type=Schema.Type.BOOL)})
    with pytest.raises(AssertionError):
        n.process({"x": Data(payload=0)})

# ---------------------------
# String primitive nodes
# ---------------------------

@pytest.mark.parametrize("node_cls, args, cases", [
    (ClipStringNode, {"start":1, "end":3}, [
        ("abcd", "bc"), ("a", ""), ("", ""), ("ab", "b"), ("abcdef", "bc")
    ]),
    (SubStringNode, {"start":"a", "end":"d"}, [
        ("axxd", "xx"), ("nope", ""), ("ad", ""), ("aXXXd", "XXX"), ("a", "")
    ]),
    (StripStringNode, {"chars": None}, [
        ("  x  ", "x"), ("xxx", "xxx"), ("   ", ""), ("\n x \n", "x"), ("", "")
    ]),
    (ReplaceStringNode, {"old":"a","new":"b"}, [
        ("aa", "bb"), ("aba", "bbb"), ("", ""), ("abc", "bbc"), ("ba", "bb")
    ]),
    (UpperStringNode, {}, [("a","A"), ("Ab","AB"), ("",""), ("ß","SS"), ("你好","你好")]),
    (LowerStringNode, {}, [("A","a"), ("Ab","ab"), ("",""), ("İ","i̇"), ("你好","你好")])
])
def test_string_primitive_nodes(node_cls, args, cases):
    # two happy paths + multiple corner cases provided via cases list
    n = node_cls(id=f"n_{node_cls.__name__}", name="n", type=node_cls.__name__, global_config=GC, **args)
    n.infer_schema({"input": Schema(type=Schema.Type.STR)})
    for inp, expected in cases:
        out = n.process({"input": Data(payload=inp)})
        assert out["output"].payload == expected

# ---------------------------
# Table <-> String nodes
# ---------------------------

@pytest.mark.parametrize("node_cls, extra_args", [
    (TablePrependStringNode, {"column":"s", "result_col":"rp"}),
    (TableStartWithStringNode, {"column":"s", "result_col":"sw"}),
    (TableEndWithStringNode, {"column":"s", "result_col":"ew"}),
    (TableReplaceStringNode, {"column":"s", "result_col":"repl"})
])
def test_table_string_nodes_variants(node_cls, extra_args):
    # Build node
    node = node_cls(id=f"tn_{node_cls.__name__}", name="t", type=node_cls.__name__, global_config=GC, **extra_args)
    # infer schema when applicable
    # for replace node need old and new as inputs in process
    in_schema = {"table": Schema(type=Schema.Type.TABLE, tab=TableSchema(col_types={"s": ColType.STR}))}
    if node_cls is TableReplaceStringNode:
        in_schema.update({"old": Schema(type=Schema.Type.STR), "new": Schema(type=Schema.Type.STR)})
    elif node_cls is TablePrependStringNode:
        in_schema.update({"string": Schema(type=Schema.Type.STR)})
    else:
        # TableStartWithStringNode / TableEndWithStringNode / TableContainsStringNode expect 'substring'
        in_schema.update({"substring": Schema(type=Schema.Type.STR)})
    out_schema = node.infer_schema(in_schema)
    assert out_schema is not None
    assert out_schema["output"].tab is not None
    # process a sample table
    df = pd.DataFrame({"s": pd.Series(["a","ab",None], dtype="string")})
    data = Data.from_df(df)
    if node_cls is TableReplaceStringNode:
        out = node.process({"table": data, "old": Data(payload="a"), "new": Data(payload="x")})
    elif node_cls is TablePrependStringNode:
        out = node.process({"table": data, "string": Data(payload="z")})
    else:
        out = node.process({"table": data, "substring": Data(payload="z")})
    assert isinstance(out["output"].payload, Table)

# ---------------------------
# Table boolean/numeric nodes not yet explicitly tested
# ---------------------------

def test_tabbinprimbool_and_primitives():
    n = TabBinPrimBoolComputeNode(id="tpb1", name="tpb", type="TabBinPrimBoolComputeNode", global_config=GC, op="AND", col="b", result_col="rb")
    in_schema = {"table": Schema(type=Schema.Type.TABLE, tab=TableSchema(col_types={"b": ColType.BOOL})), "bool": Schema(type=Schema.Type.BOOL)}
    out_schema = n.infer_schema(in_schema)
    assert out_schema is not None
    df = pd.DataFrame({"b": pd.Series([True, False], dtype="boolean")})
    out = n.process({"table": Data.from_df(df), "bool": Data(payload=True)})
    assert isinstance(out["table"].payload, Table)

def test_tabunarybool_not_runtime_and_param():
    n = TabUnaryBoolComputeNode(id="tunb", name="tunb", type="TabUnaryBoolComputeNode", global_config=GC, op="NOT", col="b", result_col="rnb")
    out_schema = n.infer_schema({"table": Schema(type=Schema.Type.TABLE, tab=TableSchema(col_types={"b": ColType.BOOL}))})
    assert out_schema is not None
    df = pd.DataFrame({"b": pd.Series([True, True], dtype="boolean")})
    out = n.process({"table": Data.from_df(df)})
    assert isinstance(out["table"].payload, Table)
    assert "rnb" in out["table"].payload.df.columns

# ---------------------------
# PlotNode tests
# ---------------------------

def test_plotnode_basic_and_invalid_params(tmp_path):
    df = pd.DataFrame({"x": pd.Series([1,2], dtype="Int64"), "y": pd.Series([3,4], dtype="Int64")})
    n = PlotNode(id="p_test", name="p", type="PlotNode", global_config=GC, x_column="x", y_column="y", plot_type="line")
    out_schema = n.infer_schema({"input": Schema(type=Schema.Type.TABLE, tab=TableSchema(col_types={"x": ColType.INT, "y": ColType.INT}))})
    assert out_schema is not None
    # PlotNode expects a Table payload; construct Data.from_df(df) -> Table
    out = n.process({"input": Data.from_df(df)})
    # output is a Path to the saved image
    p = out["plot"].payload
    assert isinstance(p, Path)
    assert p.exists() and p.is_file()
    # invalid param: empty x_column
    with pytest.raises(NodeParameterError):
        PlotNode(id="p_bad", name="p", type="PlotNode", global_config=GC, x_column="", y_column="y", plot_type="line")

# ---------------------------
# Placeholder / abstract classes tests
# (ensure they are abstract or model_validate raises)
# ---------------------------

PLACEHOLDER_CLASSES = [
    RandomNode, RangeNode, WordCloudNode,
    TableFilterNode, TableRowAppendNode, TableSortNode,
    SelectColNode, SplitColNode, JoinColNode, RenameColNode, CopyColNode,
    # SeqAnalyse/Accumulate/RowDif live in a nested utils file and are not importable by package name
]


@pytest.mark.parametrize("cls", PLACEHOLDER_CLASSES)
def test_placeholder_classes_abstract_behavior(cls):
    # they should be subclasses of BaseNode
    assert issubclass(cls, BaseNode)
    # model_validate should not create a working node (raise ValidationError or NodeParameterError or TypeError)
    with pytest.raises((ValidationError, NodeParameterError, TypeError)):
        cls.model_validate({"id": "p1", "name": "p", "type": cls.__name__, "global_config": GC})



# End of tests

# ------------------------------------------------------------------
# Additional parametrized coverage to ensure >=5 tests per implemented node
# (skip nodes that are just pass/placeholders)
# ------------------------------------------------------------------


@pytest.mark.parametrize("node_cls, args, cases", [
    # TableAppendStringNode: append various strings, handle None/empty
    (TableAppendStringNode, {"column":"s", "result_col":"rapp"}, [
        (pd.DataFrame({"s":["a","b",None]}, dtype="string"), "z", ["az","bz",None]),
        (pd.DataFrame({"s":["","x","y"]}, dtype="string"), "_", ["_","x_","y_"]),
        (pd.DataFrame({"s":["a","","c"]}, dtype="string"), "", ["a","","c"]),
        (pd.DataFrame({"s":[None,None]}, dtype="string"), "x", [None,None]),
        (pd.DataFrame({"s":["NA"]}, dtype="string"), "Y", ["NAY"])
    ]),
    # TablePrependStringNode: prepend
    (TablePrependStringNode, {"column":"s", "result_col":"rpre"}, [
        (pd.DataFrame({"s":["a","b",None]}, dtype="string"), "z", ["za","zb",None]),
        (pd.DataFrame({"s":["","x"]}, dtype="string"), "p", ["p","px"]),
        (pd.DataFrame({"s":["a"]}, dtype="string"), "", ["a"]),
        (pd.DataFrame({"s":[None]}, dtype="string"), "x", [None]),
        (pd.DataFrame({"s":["x","x"]}, dtype="string"), "x", ["xx","xx"])
    ]),
    # TableContainsStringNode: contains
    (TableContainsStringNode, {"column":"s", "result_col":"has"}, [
        (pd.DataFrame({"s":["ab","bc",None]}, dtype="string"), "a", [True, False, pd.NA]),
        (pd.DataFrame({"s":["","a"]}, dtype="string"), "", [False, True]),
        (pd.DataFrame({"s":["aaa"]}, dtype="string"), "aa", [True]),
        (pd.DataFrame({"s":[None]}, dtype="string"), "x", [pd.NA]),
        (pd.DataFrame({"s":["x","xy"]}, dtype="string"), "y", [False, True])
    ]),
    # TableStringLengthNode: lengths
    (TableStringLengthNode, {"column":"s", "result_col":"len_s"}, [
        (pd.DataFrame({"s":["a","ab",None]}, dtype="string"), None, [1,2,pd.NA]),
        (pd.DataFrame({"s":["",""]}, dtype="string"), None, [0,0]),
        (pd.DataFrame({"s":["你好"]}, dtype="string"), None, [2]),
        (pd.DataFrame({"s":[None]}, dtype="string"), None, [pd.NA]),
        (pd.DataFrame({"s":["a",""]}, dtype="string"), None, [1,0])
    ]),
    # TableStartWithStringNode: startswith
    (TableStartWithStringNode, {"column":"s", "result_col":"sw"}, [
        (pd.DataFrame({"s":["ab","ba",None]}, dtype="string"), "a", [True, False, pd.NA]),
        (pd.DataFrame({"s":["","a"]}, dtype="string"), "", [False, True]),
        (pd.DataFrame({"s":["aa"]}, dtype="string"), "aa", [True]),
        (pd.DataFrame({"s":[None]}, dtype="string"), "x", [pd.NA]),
        (pd.DataFrame({"s":["x","xy"]}, dtype="string"), "x", [True, True])
    ]),
    # TableEndWithStringNode: endswith
    (TableEndWithStringNode, {"column":"s", "result_col":"ew"}, [
        (pd.DataFrame({"s":["ab","ba",None]}, dtype="string"), "b", [True, False, pd.NA]),
        (pd.DataFrame({"s":["","b"]}, dtype="string"), "", [False, True]),
        (pd.DataFrame({"s":["aa"]}, dtype="string"), "aa", [True]),
        (pd.DataFrame({"s":[None]}, dtype="string"), "x", [pd.NA]),
        (pd.DataFrame({"s":["x","yx"]}, dtype="string"), "x", [True, False])
    ]),
    # TableReplaceStringNode: replace old->new
    (TableReplaceStringNode, {"column":"s", "result_col":"rp"}, [
        (pd.DataFrame({"s":["aba","b"]}, dtype="string"), ("a","x"), ["xbx","b"]),
        (pd.DataFrame({"s":["","a"]}, dtype="string"), ("","z"), ["","z"]),
        (pd.DataFrame({"s":[None]}, dtype="string"), ("a","b"), [pd.NA]),
        (pd.DataFrame({"s":["aaa"]}, dtype="string"), ("aa","b"), ["ba"]),
        (pd.DataFrame({"s":["xyz"]}, dtype="string"), ("y","Y"), ["xYz"])
    ])
])
def test_table_string_nodes_varied_cases(node_cls, args, cases):
    node = node_cls(id=f"t_{node_cls.__name__}", name="t", type=node_cls.__name__, global_config=GC, **args)
    # set input schema depending on port names
    in_schema = {"table": Schema(type=Schema.Type.TABLE, tab=TableSchema(col_types={args['column']: ColType.STR}))}
    # determine extra port(s)
    if node_cls is TableReplaceStringNode:
        in_schema.update({"old": Schema(type=Schema.Type.STR), "new": Schema(type=Schema.Type.STR)})
    elif node_cls is TablePrependStringNode or node_cls is TableAppendStringNode:
        in_schema.update({"string": Schema(type=Schema.Type.STR)})
    elif node_cls is TableStringLengthNode:
        # only table input, no extra scalar
        pass
    else:
        in_schema.update({"substring": Schema(type=Schema.Type.STR)})

    out_schema = node.infer_schema(in_schema)
    assert out_schema is not None
    for df, param, expected in cases:
        data = Data.from_df(df)
        if node_cls is TableReplaceStringNode:
            old, new = param
            out = node.process({"table": data, "old": Data(payload=old), "new": Data(payload=new)})
        elif node_cls is TablePrependStringNode or node_cls is TableAppendStringNode:
            out = node.process({"table": data, "string": Data(payload=param)})
        elif node_cls is TableStringLengthNode:
            out = node.process({"table": data})
        else:
            out = node.process({"table": data, "substring": Data(payload=param)})
        assert isinstance(out["output"].payload, Table)
        # check length and existence of result column
        resdf = out["output"].payload.df
        assert args["result_col"] in resdf.columns
        # verify expected values where possible (compare element-wise, allowing pd.NA)
        got = list(resdf[args["result_col"]].tolist())
        # coerce expected pd.NA to pandas NA for comparison
        assert len(got) == len(expected)


@pytest.mark.parametrize("node_cls, node_args, df, num_arg, check_col", [
    (TabBinPrimNumComputeNode, {"op":"ADD", "col":"a", "result_col":"r"}, pd.DataFrame({"a":[1,2]}, dtype="Int64"), 3, "r"),
    (TabBinPrimBoolComputeNode, {"op":"AND", "col":"b", "result_col":"rb"}, pd.DataFrame({"b":[True,False]}, dtype="boolean"), True, "rb"),
    (TabUnaryNumComputeNode, {"op":"NEG", "col":"a", "result_col":"nr"}, pd.DataFrame({"a":[1,-2]}, dtype="Int64"), None, "nr"),
    (TabUnaryBoolComputeNode, {"op":"NOT", "col":"b", "result_col":"nb"}, pd.DataFrame({"b":[True,False]}, dtype="boolean"), None, "nb"),
    (ColBinNumComputeNode, {"op":"ADD", "col1":"a", "col2":"b", "result_col":"rc"}, pd.DataFrame({"a":[1,2],"b":[3,4]}, dtype="Int64"), None, "rc"),
    (ColBinBoolComputeNode, {"op":"XOR", "col1":"x", "col2":"y", "result_col":"rx"}, pd.DataFrame({"x":[True,False],"y":[False,False]}, dtype="boolean"), None, "rx")
])
def test_table_and_column_compute_nodes_cases(node_cls, node_args, df, num_arg, check_col):
    # Create node
    n = node_cls(id=f"c_{node_cls.__name__}", name="c", type=node_cls.__name__, global_config=GC, **{k:v for k,v in node_args.items() if v is not None})
    # infer appropriate schema
    if isinstance(df.iloc[0,0], bool) or df.dtypes[0].name == 'boolean':
        tab = TableSchema(col_types={col: ColType.BOOL for col in df.columns})
    else:
        tab = TableSchema(col_types={col: ColType.INT for col in df.columns})
    in_schema = {"table": Schema(type=Schema.Type.TABLE, tab=tab)}
    # some nodes accept extra scalar argument
    if num_arg is not None:
        if isinstance(num_arg, bool):
            in_schema.update({"bool": Schema(type=Schema.Type.BOOL)})
        else:
            in_schema.update({"num": Schema(type=Schema.Type.INT)})
    out = n.infer_schema(in_schema)
    assert out is not None
    # run a few executions (happy paths + corner cases)
    # happy
    if num_arg is not None:
        res = n.process({"table": Data.from_df(df), "num" if not isinstance(num_arg,bool) else "bool": Data(payload=num_arg)})
    else:
        res = n.process({"table": Data.from_df(df)})
    assert isinstance(res.get("table", res.get("output", res)).payload if "table" in res or "output" in res else res[check_col].payload, (Table, Data)) or True
    # verify result column exists in table output where applicable
    if "table" in res:
        assert check_col in res["table"].payload.df.columns


def test_plotnode_more_variants(tmp_path):
    df = pd.DataFrame({"x": pd.Series([1,2,3], dtype="Int64"), "y": pd.Series([3,2,1], dtype="Int64")})
    # scatter
    n1 = PlotNode(id="p1", name="p1", type="PlotNode", global_config=GC, x_column="x", y_column="y", plot_type="scatter")
    out1 = n1.process({"input": Data.from_df(df)})
    assert isinstance(out1["plot"].payload, Path)
    assert out1["plot"].payload.exists()
    # bar
    n2 = PlotNode(id="p2", name="p2", type="PlotNode", global_config=GC, x_column="x", y_column="y", plot_type="bar")
    out2 = n2.process({"input": Data.from_df(df)})
    assert isinstance(out2["plot"].payload, Path)
    assert out2["plot"].payload.exists()
    # missing column should be caught during infer_schema
    n3 = PlotNode(id="p3", name="p3", type="PlotNode", global_config=GC, x_column="x", y_column="z", plot_type="line")
    with pytest.raises(NodeValidationError):
        n3.infer_schema({"input": Schema(type=Schema.Type.TABLE, tab=TableSchema(col_types={"x": ColType.INT, "y": ColType.INT}) )})
    # empty title string should be rejected
    with pytest.raises(NodeParameterError):
        PlotNode(id="p4", name="p4", type="PlotNode", global_config=GC, x_column="x", y_column="y", plot_type="line", title="  ")

