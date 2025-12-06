import pandas as pd
import pytest

from server.models.data import Data, Table
from server.models.schema import Schema, TableSchema
from server.models.types import ColType


def test_col_with_number_binop_sub_variants(node_ctor):
    # COL_SUB_NUM
    node = node_ctor('ColWithNumberBinOpNode', id='s1', op='COL_SUB_NUM', col='a', result_col='r')
    df = pd.DataFrame({'a': pd.Series([5, 6], dtype='Int64')})
    table = Table(df=df, col_types={'a': ColType.INT})
    node.__dict__['_col_types'] = {'_index': ColType.INT, 'a': ColType.INT, 'r': ColType.INT}
    out = node.process({'table': Data(payload=table), 'num': Data(payload=2)})
    assert list(out['table'].payload.df['r']) == [3, 4]

    # NUM_SUB_COL
    node2 = node_ctor('ColWithNumberBinOpNode', id='s2', op='NUM_SUB_COL', col='a', result_col='r2')
    node2.__dict__['_col_types'] = {'_index': ColType.INT, 'a': ColType.INT, 'r2': ColType.INT}
    out2 = node2.process({'table': Data(payload=table), 'num': Data(payload=10)})
    assert list(out2['table'].payload.df['r2']) == [5, 4]


def test_number_unary_log_sqrt_success(node_ctor):
    node_log = node_ctor('NumberColUnaryOpNode', id='log_succ', op='LOG', col='x', result_col='r')
    df = pd.DataFrame({'x': pd.Series([1.0, 10.0], dtype='Float64')})
    table = Table(df=df, col_types={'x': ColType.FLOAT})
    schema_table = Schema(type=Schema.Type.TABLE, tab=TableSchema(col_types={'x': ColType.FLOAT}))
    node_log.infer_output_schemas({'table': schema_table})
    out = node_log.process({'table': Data(payload=table)})
    assert list(out['table'].payload.df['r'])[0] == pytest.approx(0.0)

    node_sqrt = node_ctor('NumberColUnaryOpNode', id='sqrt_succ', op='SQRT', col='x', result_col='r2')
    node_sqrt.infer_output_schemas({'table': schema_table})
    out2 = node_sqrt.process({'table': Data(payload=table)})
    assert list(out2['table'].payload.df['r2'])[0] == pytest.approx(1.0)


def test_number_col_with_col_binop_div_success(node_ctor):
    node = node_ctor('NumberColWithColBinOpNode', id='div_ok', op='DIV', col1='a', col2='b', result_col='r')
    df = pd.DataFrame({'a': pd.Series([10, 20], dtype='Int64'), 'b': pd.Series([2, 4], dtype='Int64')})
    table = Table(df=df, col_types={'a': ColType.INT, 'b': ColType.INT})
    schema_table = Schema(type=Schema.Type.TABLE, tab=TableSchema(col_types={'a': ColType.INT, 'b': ColType.INT}))
    node.infer_output_schemas({'table': schema_table})
    out = node.process({'table': Data(payload=table)})
    assert list(out['table'].payload.df['r']) == [5.0, 5.0]


def test_number_col_with_colbinop_hint(node_ctor):
    from server.interpreter.nodes.compute.table import NumberColWithColBinOpNode
    schema_table = Schema(type=Schema.Type.TABLE, tab=TableSchema(col_types={'a': ColType.INT, 'b': ColType.FLOAT, 'c': ColType.BOOL}))
    hint = NumberColWithColBinOpNode.hint({'table': schema_table}, {})
    assert 'col1_choices' in hint and 'col2_choices' in hint
    assert set(hint['col1_choices']).issuperset({'a', 'b'})


def test_validate_parameter_empty_names(node_ctor):
    with pytest.raises(Exception):
        node_ctor('NumberColWithColBinOpNode', id='v1', op='ADD', col1='', col2='b', result_col='r')
    with pytest.raises(Exception):
        node_ctor('NumberColUnaryOpNode', id='v2', op='ABS', col='', result_col='r')
