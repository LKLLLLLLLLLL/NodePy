import pandas as pd

from server.models.data import Data, Table
from server.models.schema import Schema, TableSchema
from server.models.types import ColType


def test_bool_col_with_col_binop_and_sub(node_ctor):
    node = node_ctor('BoolColWithColBinOpNode', id='bb', op='SUB', col1='p', col2='q', result_col='r')
    df = pd.DataFrame({'p': pd.Series([True, True, False], dtype='boolean'), 'q': pd.Series([True, False, False], dtype='boolean')})
    table = Table(df=df, col_types={'p': ColType.BOOL, 'q': ColType.BOOL})
    schema_table = Schema(type=Schema.Type.TABLE, tab=TableSchema(col_types={'p': ColType.BOOL, 'q': ColType.BOOL}))
    node.infer_output_schemas({'table': schema_table})
    out = node.process({'table': Data(payload=table)})
    assert list(out['table'].payload.df['r']) == [False, True, False]


def test_bool_col_with_col_binop_and_or_xor(node_ctor):
    node_and = node_ctor('BoolColWithColBinOpNode', id='bb_and', op='AND', col1='p', col2='q', result_col='r_and')
    df = pd.DataFrame({'p': pd.Series([True, False], dtype='boolean'), 'q': pd.Series([False, False], dtype='boolean')})
    table = Table(df=df, col_types={'p': ColType.BOOL, 'q': ColType.BOOL})
    schema_table = Schema(type=Schema.Type.TABLE, tab=TableSchema(col_types={'p': ColType.BOOL, 'q': ColType.BOOL}))
    node_and.infer_output_schemas({'table': schema_table})
    out = node_and.process({'table': Data(payload=table)})
    assert list(out['table'].payload.df['r_and']) == [False, False]

    node_xor = node_ctor('BoolColWithColBinOpNode', id='bb_xor', op='XOR', col1='p', col2='q', result_col='r_x')
    node_xor.infer_output_schemas({'table': schema_table})
    outx = node_xor.process({'table': Data(payload=table)})
    assert list(outx['table'].payload.df['r_x']) == [True, False]

