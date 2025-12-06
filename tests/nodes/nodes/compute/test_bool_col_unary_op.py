import pandas as pd

from server.models.data import Data, Table
from server.models.schema import Schema, TableSchema
from server.models.types import ColType


def make_table(col_name, values, col_type: ColType):
    df = pd.DataFrame({col_name: pd.Series(values, dtype=col_type.to_ptype()())})
    col_types = {col_name: col_type}
    return Table(df=df, col_types=col_types)


def test_bool_col_unary_not(node_ctor):
    node = node_ctor('BoolColUnaryOpNode', id='bn', op='NOT', col='f', result_col='r')
    table = make_table('f', [True, False], ColType.BOOL)
    schema_table = Schema(type=Schema.Type.TABLE, tab=TableSchema(col_types={'f': ColType.BOOL}))
    node.infer_output_schemas({'table': schema_table})
    out = node.process({'table': Data(payload=table)})
    assert list(out['table'].payload.df['r']) == [False, True]
