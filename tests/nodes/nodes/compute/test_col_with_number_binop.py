import pandas as pd
import pytest

from server.models.data import Data, Table
from server.models.exception import NodeExecutionError
from server.models.schema import Schema, TableSchema
from server.models.types import ColType


def make_table(col_name, values, col_type: ColType):
    df = pd.DataFrame({col_name: pd.Series(values, dtype=col_type.to_ptype()())})
    col_types = {col_name: col_type}
    return Table(df=df, col_types=col_types)


def test_col_with_number_binop_add_and_div_zero(node_ctor):
    node = node_ctor('ColWithNumberBinOpNode', id='n_add', op='ADD', col='a', result_col='res')

    table = make_table('a', [1, 2, 3], ColType.INT)
    schema_table = Schema(type=Schema.Type.TABLE, tab=TableSchema(col_types={'a': ColType.INT}))
    out_schema = node.infer_output_schemas({'table': schema_table, 'num': Schema(type=Schema.Type.INT)})
    assert 'table' in out_schema

    out = node.process({'table': Data(payload=table), 'num': Data(payload=5)})
    assert isinstance(out['table'].payload, Table)
    assert list(out['table'].payload.df['res']) == [6, 7, 8]

    # division by zero for COL_DIV_NUM
    node2 = node_ctor('ColWithNumberBinOpNode', id='n_div', op='COL_DIV_NUM', col='a', result_col='res2')
    node2.infer_output_schemas({'table': schema_table, 'num': Schema(type=Schema.Type.INT)})
    with pytest.raises(NodeExecutionError):
        node2.process({'table': Data(payload=table), 'num': Data(payload=0)})


def test_col_with_number_binop_infer_errors(node_ctor):
    node = node_ctor('ColWithNumberBinOpNode', id='err1', op='ADD', col='a', result_col='res')
    schema_table = Schema(type=Schema.Type.TABLE, tab=TableSchema(col_types={'a': ColType.INT, 'res': ColType.INT}))
    with pytest.raises(Exception):
        node.infer_output_schemas({'table': schema_table, 'num': Schema(type=Schema.Type.INT)})


def test_col_with_number_pow_ops_and_unsupported(node_ctor):
    # COL_POW_NUM
    node = node_ctor('ColWithNumberBinOpNode', id='p1', op='COL_POW_NUM', col='a', result_col='r')
    table = make_table('a', [2, 3], ColType.INT)
    schema_table = Schema(type=Schema.Type.TABLE, tab=TableSchema(col_types={'a': ColType.INT}))
    node.infer_output_schemas({'table': schema_table, 'num': Schema(type=Schema.Type.INT)})
    out = node.process({'table': Data(payload=table), 'num': Data(payload=2)})
    assert list(out['table'].payload.df['r']) == [4.0, 9.0]

    # NUM_POW_COL
    node2 = node_ctor('ColWithNumberBinOpNode', id='p2', op='NUM_POW_COL', col='a', result_col='r2')
    df_float = pd.DataFrame({'a': pd.Series([1.0, 2.0], dtype='Float64')})
    table2 = Table(df=df_float, col_types={'a': ColType.FLOAT})
    schema_table2 = Schema(type=Schema.Type.TABLE, tab=TableSchema(col_types={'a': ColType.FLOAT}))
    node2.infer_output_schemas({'table': schema_table2, 'num': Schema(type=Schema.Type.FLOAT)})
    out2 = node2.process({'table': Data(payload=table2), 'num': Data(payload=3.0)})
    assert list(out2['table'].payload.df['r2']) == [3.0 ** 1.0, 3.0 ** 2.0]

    # unsupported operation path (mutate op)
    node3 = node_ctor('ColWithNumberBinOpNode', id='p3', op='ADD', col='a', result_col='rx')
    node3.__dict__['op'] = 'BAD_OP'
    node3.__dict__['_col_types'] = {'a': ColType.INT, 'rx': ColType.INT}
    with pytest.raises(Exception):
        node3.process({'table': Data(payload=table), 'num': Data(payload=1)})


def test_more_number_binop_successes(node_ctor):
    node = node_ctor('ColWithNumberBinOpNode', id='d1', op='COL_DIV_NUM', col='a', result_col='rd')
    table = make_table('a', [10, 20], ColType.INT)
    schema_table = Schema(type=Schema.Type.TABLE, tab=TableSchema(col_types={'a': ColType.INT}))
    node.infer_output_schemas({'table': schema_table, 'num': Schema(type=Schema.Type.INT)})
    out = node.process({'table': Data(payload=table), 'num': Data(payload=2)})
    assert list(out['table'].payload.df['rd']) == [5.0, 10.0]

    node2 = node_ctor('ColWithNumberBinOpNode', id='d2', op='NUM_DIV_COL', col='a', result_col='r2')
    t2 = make_table('a', [2, 4], ColType.INT)
    node2.infer_output_schemas({'table': schema_table, 'num': Schema(type=Schema.Type.INT)})
    out2 = node2.process({'table': Data(payload=t2), 'num': Data(payload=8)})
    assert list(out2['table'].payload.df['r2']) == [4.0, 2.0]

