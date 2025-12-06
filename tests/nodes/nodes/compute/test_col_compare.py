import pandas as pd

from server.models.data import Data, Table
from server.models.schema import Schema, TableSchema
from server.models.types import ColType


def test_col_compare_ops(node_ctor):
    node = node_ctor('ColCompareNode', id='cc', op='GT', col1='a', col2='b', result_col='r')
    df = pd.DataFrame({'a': pd.Series([3, 1], dtype='Int64'), 'b': pd.Series([2, 1], dtype='Int64')})
    table = Table(df=df, col_types={'a': ColType.INT, 'b': ColType.INT})
    schema_table = Schema(type=Schema.Type.TABLE, tab=TableSchema(col_types={'a': ColType.INT, 'b': ColType.INT}))
    node.infer_output_schemas({'table': schema_table})
    out = node.process({'table': Data(payload=table)})
    assert list(out['table'].payload.df['r']) == [True, False]


def test_col_compare_all_ops(node_ctor):
    df = pd.DataFrame({'a': pd.Series([1, 2, 3], dtype='Int64'), 'b': pd.Series([1, 1, 4], dtype='Int64')})
    table = Table(df=df, col_types={'a': ColType.INT, 'b': ColType.INT})
    schema_table = Schema(type=Schema.Type.TABLE, tab=TableSchema(col_types={'a': ColType.INT, 'b': ColType.INT}))
    for op, expected in [('EQ', [True, False, False]), ('NEQ', [False, True, True]), ('LT', [False, False, True]), ('LTE', [True, False, True]), ('GTE', [True, True, False])]:
        node = node_ctor('ColCompareNode', id=f'cmp_{op}', op=op, col1='a', col2='b', result_col=f'r_{op}')
        node.infer_output_schemas({'table': schema_table})
        out = node.process({'table': Data(payload=table)})
        assert list(out['table'].payload.df[f'r_{op}']) == expected
