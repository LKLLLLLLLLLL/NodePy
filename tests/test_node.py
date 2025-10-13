"""
合并后的单一测试文件：按节点类型分组，包含正常路径与边界测试。
"""

import pytest
from pandas import DataFrame
from pathlib import Path

from server.engine.nodes.ComputeNode import (
    BinNumComputeNode,
    UnaryNumComputeNode,
    BoolBinComputeNode,
    BoolNotNode,
    CmpNode,
)
from server.engine.nodes.GenNode import ConstNode
from server.engine.nodes.PlotNode import PlotNode
from server.engine.nodes.TableGenNode import RandomNode, RangeNode, TableNode
from server.engine.nodes.TableColNode import SelectColNode, SplitNode
from server.engine.nodes.StringComputeNode import (
    ClipStringNode,
    StripStringNode,
    ReplaceStringNode,
    SplitStringNode,
    UpperStringNode,
    LowerStringNode,
)
from server.engine.nodes.TableComputeNode import (
    TableBinNumComputeNode,
    TableUnaryNumComputeNode,
    TableBoolBinComputeNode,
)
from server.engine.nodes.TableComputeNode import TableCmpNode
from server.engine.nodes.Utils import (
    Schema,
    Data,
    GlobalConfig,
    NodeValidationError,
    NodeExecutionError,
    INDEX_COLUMN_NAME,
)

# Shared helpers
def make_table_payload(col, values):
    df = DataFrame({col: values})
    df.insert(0, INDEX_COLUMN_NAME, range(len(df)))
    return df

GLOBAL_CFG = GlobalConfig(temp_dir=Path('.'), user_id='test')

############################################
# 1) Compute primitives
############################################

def test_binnum_add_and_div_and_infer_type():
    node = BinNumComputeNode(id="bn", name="bn", type="BinNumComputeNode", op="ADD", global_config=GLOBAL_CFG)
    out = node.execute({
        "left": Data(sche=Schema(type=Schema.DataType.INT), payload=2),
        "right": Data(sche=Schema(type=Schema.DataType.INT), payload=3),
    })
    payload = out["output"].payload
    assert isinstance(payload, int)
    assert payload == 5

    node_div = BinNumComputeNode(id="bd", name="bd", type="BinNumComputeNode", op="DIV", global_config=GLOBAL_CFG)
    schema = node_div.infer_output_schema({"left": Schema(type=Schema.DataType.INT), "right": Schema(type=Schema.DataType.INT)})
    assert schema["output"].type == Schema.DataType.FLOAT

    with pytest.raises(Exception):
        node_div.execute({
            "left": Data(sche=Schema(type=Schema.DataType.INT), payload=1),
            "right": Data(sche=Schema(type=Schema.DataType.INT), payload=0),
        })


def test_unary_sqrt_negative_and_infer():
    node = UnaryNumComputeNode(id="un", name="un", type="UnaryNumComputeNode", op="SQRT", global_config=GLOBAL_CFG)
    s = node.infer_output_schema({"input": Schema(type=Schema.DataType.INT)})
    assert s["output"].type == Schema.DataType.FLOAT
    with pytest.raises(NodeExecutionError):
        node.execute({"input": Data(sche=Schema(type=Schema.DataType.INT), payload=-9)})


def test_bool_ops_and_not():
    node = BoolBinComputeNode(id="bb", name="bb", type="BoolBinComputeNode", op="XOR", global_config=GLOBAL_CFG)
    out = node.execute({
        "left": Data(sche=Schema(type=Schema.DataType.BOOL), payload=True),
        "right": Data(sche=Schema(type=Schema.DataType.BOOL), payload=False),
    })
    assert out["output"].payload is True

    not_node = BoolNotNode(id="bn", name="bn", type="BoolNotNode", global_config=GLOBAL_CFG)
    out2 = not_node.execute({"input": Data(sche=Schema(type=Schema.DataType.BOOL), payload=True)})
    assert out2["output"].payload is False

############################################
# 2) Compare nodes
############################################

def test_cmpnode_static_type_mismatch_and_runtime_equal():
    node = CmpNode(id="cmp1", name="cmp1", type="CmpNode", op="EQ", global_config=GLOBAL_CFG)
    with pytest.raises(NodeValidationError):
        node.infer_output_schema({
            "input1": Schema(type=Schema.DataType.INT),
            "input2": Schema(type=Schema.DataType.STR),
        })
    out = node.execute({
        "input1": Data(sche=Schema(type=Schema.DataType.INT), payload=5),
        "input2": Data(sche=Schema(type=Schema.DataType.INT), payload=5),
    })
    assert out["output"].payload is True


def test_cmpnode_runtime_type_mismatch_raises_execute_error():
    node = CmpNode(id="cmp2", name="cmp2", type="CmpNode", op="GT", global_config=GLOBAL_CFG)
    with pytest.raises(NodeExecutionError):
        node.execute({
            "input1": Data(sche=Schema(type=Schema.DataType.INT), payload=1),
            "input2": Data(sche=Schema(type=Schema.DataType.STR), payload="x"),
        })


def test_tablecmp_node_and_empty_table_exec_error():
    df = make_table_payload("val", [1,2,3])
    tcmp = TableCmpNode(id="tc", name="tc", type="TableCmpNode", op="EQ", column="val", result_col="eq", global_config=GLOBAL_CFG)
    out = tcmp.execute({
        "table_input": Data(sche=Schema(type=Schema.DataType.TABLE, columns={INDEX_COLUMN_NAME:{Schema.ColumnType.INT}, "val":{Schema.ColumnType.INT}}), payload=df),
        "value_input": Data(sche=Schema(type=Schema.DataType.INT), payload=2),
    })
    payload = out["output"].payload
    assert isinstance(payload, DataFrame)
    assert list(payload["eq"]) == [False, True, False]

    tcmp_empty = TableCmpNode(id="tce", name="tce", type="TableCmpNode", op="EQ", column="val", result_col="eq", global_config=GLOBAL_CFG)
    empty = DataFrame({"val": []})
    empty.insert(0, INDEX_COLUMN_NAME, [])
    with pytest.raises(NodeExecutionError):
        tcmp_empty.execute({
            "table_input": Data(sche=Schema(type=Schema.DataType.TABLE, columns={INDEX_COLUMN_NAME:{Schema.ColumnType.INT}, "val":{Schema.ColumnType.INT}}), payload=empty),
            "value_input": Data(sche=Schema(type=Schema.DataType.INT), payload=1),
        })

############################################
# 3) Const & String nodes
############################################

def test_constnode_type_validation_and_values():
    n1 = ConstNode(id="c1", name="c1", type="ConstNode", value="hi", data_type="str", global_config=GLOBAL_CFG)
    payload = n1.execute({})["output"].payload
    assert isinstance(payload, str)
    assert payload == "hi"
    with pytest.raises(NodeValidationError):
        ConstNode(id="c2", name="c2", type="ConstNode", value=1, data_type="str", global_config=GLOBAL_CFG)


def test_string_nodes_basic_and_bounds():
    sn = ConstNode(id="s", name="s", type="ConstNode", data_type = "str", value="hello", global_config=GLOBAL_CFG)
    p = sn.execute({})["output"].payload
    assert isinstance(p, str)
    assert p == "hello"

    clip = ClipStringNode(id="cs", name="cs", type="ClipStringNode", start=1, end=3, global_config=GLOBAL_CFG)
    out = clip.execute({"input": Data(sche=Schema(type=Schema.DataType.STR), payload="abcd")})
    p2 = out["output"].payload
    assert isinstance(p2, str)
    assert p2 == "bc"

    rep = ReplaceStringNode(id="rs", name="rs", type="ReplaceStringNode", old="a", new="z", global_config=GLOBAL_CFG)
    out2 = rep.execute({"input": Data(sche=Schema(type=Schema.DataType.STR), payload="aba")})
    p3 = out2["output"].payload
    assert isinstance(p3, str)
    assert p3 == "zbz"

    sp = SplitStringNode(id="ss", name="ss", type="SplitStringNode", delimiter=",", column_name="val", global_config=GLOBAL_CFG)
    out3 = sp.execute({"input": Data(sche=Schema(type=Schema.DataType.STR), payload="x,y" )})
    assert isinstance(out3["output"].payload, DataFrame)

    up = UpperStringNode(id="up", name="up", type="UpperStringNode", global_config=GLOBAL_CFG)
    p_up = up.execute({"input": Data(sche=Schema(type=Schema.DataType.STR), payload="Te")})["output"].payload
    assert isinstance(p_up, str)
    assert p_up == "TE"
    low = LowerStringNode(id="low", name="low", type="LowerStringNode", global_config=GLOBAL_CFG)
    p_low = low.execute({"input": Data(sche=Schema(type=Schema.DataType.STR), payload="Te")})["output"].payload
    assert isinstance(p_low, str)
    assert p_low == "te"
    st = StripStringNode(id="st", name="st", type="StripStringNode", chars="x", global_config=GLOBAL_CFG)
    p_st = st.execute({"input": Data(sche=Schema(type=Schema.DataType.STR), payload="xhellox")})["output"].payload
    assert isinstance(p_st, str)
    assert p_st == "hello"

############################################
# 4) Table generation / select / split
############################################

def test_rangenode_and_invalid_params():
    rn = RangeNode(id="r1", name="r1", type="RangeNode", start=0, end=5, step=2, column_name="a", global_config=GLOBAL_CFG)
    out = rn.execute({})
    df = out["output"].payload
    assert isinstance(df, DataFrame)
    assert list(df["a"]) == [0, 2, 4]

    with pytest.raises(NodeValidationError):
        RangeNode(id="r2", name="r2", type="RangeNode", start=5, end=1, step=1, column_name="a", global_config=GLOBAL_CFG)


def test_randomnode_seed_and_invalid_range():
    r1 = RandomNode(id="r1", name="r1", type="RandomNode", data_type="int", top=10, bottom=0, seed=7, column_name="x", global_config=GLOBAL_CFG)
    out = r1.execute({})
    payload = out["output"].payload
    assert isinstance(payload, DataFrame)
    assert len(payload) == 100

    with pytest.raises(NodeValidationError):
        RandomNode(id="rbad", name="rbad", type="RandomNode", data_type="int", top=1, bottom=1, seed=None, column_name="x", global_config=GLOBAL_CFG)


def test_tablenode_inconsistent_and_none_value_error():
    rows = [{"a": 1, "b": 2}, {"a": 3, "b": 4}]
    tn = TableNode(id="t1", name="t1", type="TableNode", rows=rows, column_names=["a", "b"], global_config=GLOBAL_CFG)
    out = tn.execute({})
    df = out["output"].payload
    assert isinstance(df, DataFrame)
    assert INDEX_COLUMN_NAME in df.columns

    bad_rows = [{"a": 1}, {"b": 2}]
    with pytest.raises(NodeValidationError):
        TableNode(id="tbad", name="tbad", type="TableNode", rows=bad_rows, column_names=["a","b"], global_config=GLOBAL_CFG)

    with pytest.raises(NodeValidationError):
        TableNode(id="tnone", name="tnone", type="TableNode", rows=[{"a": None}], column_names=["a"], global_config=GLOBAL_CFG)


def test_select_and_split_node_behaviour_and_infer():
    node = SelectColNode(id="sc", name="sc", type="SelectColNode", selected_columns=["val"], global_config=GLOBAL_CFG)
    df = make_table_payload("val", [1,2])
    out = node.execute({"input": Data(sche=Schema(type=Schema.DataType.TABLE, columns={INDEX_COLUMN_NAME: {Schema.ColumnType.INT}, "val": {Schema.ColumnType.INT}}), payload=df)})
    res = out["output"].payload
    assert isinstance(res, DataFrame)
    assert list(res["val"]) == [1,2]

    out_schema = node.infer_output_schema({"input": Schema(type=Schema.DataType.TABLE, columns=None)})
    assert out_schema["output"].columns is None

    df2 = make_table_payload("other", [1])
    with pytest.raises(NodeExecutionError):
        node.execute({"input": Data(sche=Schema(type=Schema.DataType.TABLE, columns=None), payload=df2)})

    sp = SplitNode(id="sp", name="sp", type="SplitNode", split_column="k", split_values=["a","b"], reserved_columns=None, global_config=GLOBAL_CFG)
    df3 = DataFrame({"k": ["a","b","a"]})
    df3.insert(0, INDEX_COLUMN_NAME, range(len(df3)))
    outsp = sp.execute({"input": Data(sche=Schema(type=Schema.DataType.TABLE, columns={INDEX_COLUMN_NAME:{Schema.ColumnType.INT}, "k":{Schema.ColumnType.STR}}), payload=df3)})
    assert "out_0" in outsp and "out_1" in outsp

############################################
# 5) Table compute nodes
############################################

def test_table_binnum_with_value_and_table_right_and_infer_errors():
    df = make_table_payload("x", [1,2,3])
    node = TableBinNumComputeNode(id="tbv", name="tbv", type="TableBinNumComputeNode", left_col="x", right_col=None, result_col="r", op="ADD", global_config=GLOBAL_CFG)
    out = node.execute({
        "table": Data(sche=Schema(type=Schema.DataType.TABLE, columns={INDEX_COLUMN_NAME:{Schema.ColumnType.INT}, "x":{Schema.ColumnType.INT}}), payload=df),
        "value": Data(sche=Schema(type=Schema.DataType.INT), payload=10),
    })
    res = out["output"].payload
    assert isinstance(res, DataFrame)
    assert list(res["r"]) == [11,12,13]

    with pytest.raises(NodeValidationError):
        node.infer_output_schema({"table": Schema(type=Schema.DataType.TABLE, columns=None)})


def test_table_unary_and_bool_ops_and_type_inference():
    df = make_table_payload("a", [4.0,9.0])
    node = TableUnaryNumComputeNode(id="tu", name="tu", type="TableUnaryNumComputeNode", column="a", result_col="b", op="SQRT", global_config=GLOBAL_CFG)
    out = node.execute({"table": Data(sche=Schema(type=Schema.DataType.TABLE, columns={INDEX_COLUMN_NAME:{Schema.ColumnType.INT}, "a":{Schema.ColumnType.FLOAT}}), payload=df)})
    res = out["output"].payload
    assert isinstance(res, DataFrame)
    assert pytest.approx(list(res["b"])) == [2.0,3.0]

    dfb = make_table_payload("f", [True, False])
    dfg = make_table_payload("g", [True, True])
    nodeb = TableBoolBinComputeNode(id="tb", name="tb", type="TableBoolBinComputeNode", left_col="f", right_col="g", result_col="r", op="AND", global_config=GLOBAL_CFG)
    outb = nodeb.execute({
        "table": Data(sche=Schema(type=Schema.DataType.TABLE, columns={INDEX_COLUMN_NAME:{Schema.ColumnType.INT}, "f":{Schema.ColumnType.BOOL}}), payload=dfb),
        "table_right": Data(sche=Schema(type=Schema.DataType.TABLE, columns={INDEX_COLUMN_NAME:{Schema.ColumnType.INT}, "g":{Schema.ColumnType.BOOL}}), payload=dfg),
    })
    outb_payload = outb["output"].payload
    assert isinstance(outb_payload, DataFrame)
    assert list(outb_payload["r"]) == [True, False]

############################################
# 6) Plot node / side effects
############################################

def test_plotnode_writes_file(tmp_path):
    cfg = GlobalConfig(temp_dir=tmp_path, user_id='u1')
    df = DataFrame({"x": [1,2,3], "y": [4,5,6]})
    df.insert(0, INDEX_COLUMN_NAME, range(len(df)))
    pnode = PlotNode(id="p1", name="p1", type="PlotNode", x_column="x", y_column="y", plot_type="scatter", title="t", global_config=cfg)
    pnode.execute({"input": Data(sche=Schema(type=Schema.DataType.TABLE, columns={INDEX_COLUMN_NAME:{Schema.ColumnType.INT}, "x":{Schema.ColumnType.INT}, "y":{Schema.ColumnType.INT}}), payload=df)})
    files = list(tmp_path.iterdir())
    assert any("plot_" in f.name for f in files)

############################################
# 7) Extra edge tests from previous files
############################################

def test_randomnode_seed_determinism():
    r1 = RandomNode(id="r1", name="r1", type="RandomNode", data_type="int", top=100, bottom=0, seed=123, column_name="x", global_config=GLOBAL_CFG)
    out1 = r1.execute({})
    payload1 = out1["output"].payload
    assert isinstance(payload1, DataFrame)
    arr1 = payload1["x"].tolist()

    r2 = RandomNode(id="r2", name="r2", type="RandomNode", data_type="int", top=100, bottom=0, seed=123, column_name="x", global_config=GLOBAL_CFG)
    out2 = r2.execute({})
    payload2 = out2["output"].payload
    assert isinstance(payload2, DataFrame)
    arr2 = payload2["x"].tolist()

    assert len(arr1) == 100
    assert arr1 == arr2


def test_table_binnum_result_type_float_left():
    node = TableBinNumComputeNode(id="tb_e", name="tb_e", type="TableBinNumComputeNode", left_col="x", right_col=None, result_col="r", op="ADD", global_config=GLOBAL_CFG)
    sch = {"table": Schema(type=Schema.DataType.TABLE, columns={INDEX_COLUMN_NAME:{Schema.ColumnType.INT}, "x":{Schema.ColumnType.FLOAT}}), "value": Schema(type=Schema.DataType.INT)}
    out_s = node.infer_output_schema(sch)["output"]
    assert out_s.columns is not None
    assert Schema.ColumnType.FLOAT in out_s.columns["r"]


def test_table_bool_sub_xor_behavior():
    df = make_table_payload("f", [True, True, False])
    df2 = make_table_payload("g", [True, False, False])

    node_sub = TableBoolBinComputeNode(id="tbs", name="tbs", type="TableBoolBinComputeNode", left_col="f", right_col="g", result_col="r", op="SUB", global_config=GLOBAL_CFG)
    out = node_sub.execute({
        "table": Data(sche=Schema(type=Schema.DataType.TABLE, columns={INDEX_COLUMN_NAME:{Schema.ColumnType.INT}, "f":{Schema.ColumnType.BOOL}}), payload=df),
        "table_right": Data(sche=Schema(type=Schema.DataType.TABLE, columns={INDEX_COLUMN_NAME:{Schema.ColumnType.INT}, "g":{Schema.ColumnType.BOOL}}), payload=df2),
    })
    res = out["output"].payload
    assert isinstance(res, DataFrame)
    assert list(res["r"]) == [False, True, False]

    node_xor = TableBoolBinComputeNode(id="tbx", name="tbx", type="TableBoolBinComputeNode", left_col="f", right_col="g", result_col="rx", op="XOR", global_config=GLOBAL_CFG)
    outx = node_xor.execute({
        "table": Data(sche=Schema(type=Schema.DataType.TABLE, columns={INDEX_COLUMN_NAME:{Schema.ColumnType.INT}, "f":{Schema.ColumnType.BOOL}}), payload=df),
        "table_right": Data(sche=Schema(type=Schema.DataType.TABLE, columns={INDEX_COLUMN_NAME:{Schema.ColumnType.INT}, "g":{Schema.ColumnType.BOOL}}), payload=df2),
    })
    resx = outx["output"].payload
    assert isinstance(resx, DataFrame)
    assert list(resx["rx"]) == [False, True, False]


def test_selectcol_infer_unknown_columns_returns_none():
    node = SelectColNode(id="sc_e", name="sc_e", type="SelectColNode", selected_columns=["a"], global_config=GLOBAL_CFG)
    out = node.infer_output_schema({"input": Schema(type=Schema.DataType.TABLE, columns=None)})
    assert out["output"].columns is None


def test_plotnode_raises_on_empty_columns():
    cfg = GlobalConfig(temp_dir=Path('.'), user_id='plot')
    p = PlotNode(id="p_e", name="p_e", type="PlotNode", x_column="x", y_column="y", plot_type="line", global_config=cfg)
    df = DataFrame({"x": [], "y": []})
    df.insert(0, INDEX_COLUMN_NAME, [])
    with pytest.raises(NodeExecutionError):
        p.execute({"input": Data(sche=Schema(type=Schema.DataType.TABLE, columns={INDEX_COLUMN_NAME:{Schema.ColumnType.INT}, "x":{Schema.ColumnType.INT}, "y":{Schema.ColumnType.INT}}), payload=df)})

if __name__ == '__main__':
    pytest.main()
