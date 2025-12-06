import pandas as pd

from server.models.data import Data, Table
from server.models.schema import Schema, TableSchema
from server.models.types import ColType


def make_table(col_name, values, col_type: ColType):
    df = pd.DataFrame({col_name: pd.Series(values, dtype=col_type.to_ptype()())})
    col_types = {col_name: col_type}
    return Table(df=df, col_types=col_types)


def test_col_with_bool_binop_and_or_xor(node_ctor):
    node_and = node_ctor('ColWithBoolBinOpNode', id='nb', op='AND', col='b', result_col='r')
    table = make_table('b', [True, False, True], ColType.BOOL)
    schema_table = Schema(type=Schema.Type.TABLE, tab=TableSchema(col_types={'b': ColType.BOOL}))
    node_and.infer_output_schemas({'table': schema_table, 'bool': Schema(type=Schema.Type.BOOL)})
    out = node_and.process({'table': Data(payload=table), 'bool': Data(payload=True)})
    assert list(out['table'].payload.df['r']) == [True, False, True]

    node_xor = node_ctor('ColWithBoolBinOpNode', id='nb2', op='XOR', col='b', result_col='r2')
    node_xor.infer_output_schemas({'table': schema_table, 'bool': Schema(type=Schema.Type.BOOL)})
    out2 = node_xor.process({'table': Data(payload=table), 'bool': Data(payload=True)})
    assert list(out2['table'].payload.df['r2']) == [False, True, False]


def test_col_with_bool_extra_ops(node_ctor):
    node_or = node_ctor('ColWithBoolBinOpNode', id='bb1', op='OR', col='b', result_col='r1')
    table = make_table('b', [True, False], ColType.BOOL)
    schema_table = Schema(type=Schema.Type.TABLE, tab=TableSchema(col_types={'b': ColType.BOOL}))
    node_or.infer_output_schemas({'table': schema_table, 'bool': Schema(type=Schema.Type.BOOL)})
    out = node_or.process({'table': Data(payload=table), 'bool': Data(payload=False)})
    assert list(out['table'].payload.df['r1']) == [True, False]

    node_csub = node_ctor('ColWithBoolBinOpNode', id='bb2', op='COL_SUB_NUM', col='b', result_col='rc')
    node_csub.infer_output_schemas({'table': schema_table, 'bool': Schema(type=Schema.Type.BOOL)})
    out_c = node_csub.process({'table': Data(payload=table), 'bool': Data(payload=True)})
    assert list(out_c['table'].payload.df['rc']) == [False, False]

