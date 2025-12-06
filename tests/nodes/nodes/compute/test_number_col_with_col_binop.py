import pandas as pd
import pytest

from server.models.data import Data, Table
from server.models.exception import NodeExecutionError
from server.models.schema import Schema, TableSchema
from server.models.types import ColType


def test_number_col_with_col_binop_div_zero(node_ctor):
    node = node_ctor('NumberColWithColBinOpNode', id='nc', op='DIV', col1='x', col2='y', result_col='r')
    df = pd.DataFrame({'x': pd.Series([10, 20], dtype='Int64'), 'y': pd.Series([2, 0], dtype='Int64')})
    table = Table(df=df, col_types={'x': ColType.INT, 'y': ColType.INT})
    schema_table = Schema(type=Schema.Type.TABLE, tab=TableSchema(col_types={'x': ColType.INT, 'y': ColType.INT}))
    node.infer_output_schemas({'table': schema_table})
    with pytest.raises(NodeExecutionError):
        node.process({'table': Data(payload=table)})


def test_more_number_and_unary_ops(node_ctor):
    node_add = node_ctor('NumberColWithColBinOpNode', id='nadd', op='ADD', col1='x', col2='y', result_col='rx')
    df = pd.DataFrame({'x': pd.Series([1, 2], dtype='Int64'), 'y': pd.Series([3, 4], dtype='Int64')})
    table = Table(df=df, col_types={'x': ColType.INT, 'y': ColType.INT})
    schema_table = Schema(type=Schema.Type.TABLE, tab=TableSchema(col_types={'x': ColType.INT, 'y': ColType.INT}))
    node_add.infer_output_schemas({'table': schema_table})
    out = node_add.process({'table': Data(payload=table)})
    assert list(out['table'].payload.df['rx']) == [4, 6]

    node_pow = node_ctor('NumberColWithColBinOpNode', id='npow', op='POW', col1='x', col2='y', result_col='rp')
    df_float = pd.DataFrame({'x': pd.Series([1.0, 2.0], dtype='Float64'), 'y': pd.Series([3.0, 4.0], dtype='Float64')})
    table_float = Table(df=df_float, col_types={'x': ColType.FLOAT, 'y': ColType.FLOAT})
    schema_table_float = Schema(type=Schema.Type.TABLE, tab=TableSchema(col_types={'x': ColType.FLOAT, 'y': ColType.FLOAT}))
    node_pow.infer_output_schemas({'table': schema_table_float})
    out2 = node_pow.process({'table': Data(payload=table_float)})
    assert list(out2['table'].payload.df['rp']) == [1.0 ** 3.0, 2.0 ** 4.0]


def test_number_col_with_col_binop_more_ops(node_ctor):
    node_sub = node_ctor('NumberColWithColBinOpNode', id='ns', op='SUB', col1='x', col2='y', result_col='rs')
    df = pd.DataFrame({'x': pd.Series([5, 6], dtype='Int64'), 'y': pd.Series([2, 3], dtype='Int64')})
    table = Table(df=df, col_types={'x': ColType.INT, 'y': ColType.INT})
    schema_table = Schema(type=Schema.Type.TABLE, tab=TableSchema(col_types={'x': ColType.INT, 'y': ColType.INT}))
    node_sub.infer_output_schemas({'table': schema_table})
    out = node_sub.process({'table': Data(payload=table)})
    assert list(out['table'].payload.df['rs']) == [3, 3]

    node_mul = node_ctor('NumberColWithColBinOpNode', id='nm', op='MUL', col1='x', col2='y', result_col='rm')
    node_mul.infer_output_schemas({'table': schema_table})
    outm = node_mul.process({'table': Data(payload=table)})
    assert list(outm['table'].payload.df['rm']) == [10, 18]
