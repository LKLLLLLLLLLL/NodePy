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


def test_number_col_unary_log_sqrt_errors(node_ctor):
    node_log = node_ctor('NumberColUnaryOpNode', id='un1', op='LOG', col='a', result_col='r')
    table = make_table('a', [1, -1, 3], ColType.INT)
    schema_table = Schema(type=Schema.Type.TABLE, tab=TableSchema(col_types={'a': ColType.INT}))
    node_log.infer_output_schemas({'table': schema_table})
    with pytest.raises(NodeExecutionError):
        node_log.process({'table': Data(payload=table)})

    node_sqrt = node_ctor('NumberColUnaryOpNode', id='un2', op='SQRT', col='a', result_col='r2')
    table2 = make_table('a', [4, -9], ColType.INT)
    schema_table2 = Schema(type=Schema.Type.TABLE, tab=TableSchema(col_types={'a': ColType.INT}))
    node_sqrt.infer_output_schemas({'table': schema_table2})
    with pytest.raises(NodeExecutionError):
        node_sqrt.process({'table': Data(payload=table2)})


def test_unary_exp_and_hint_methods(node_ctor):
    node = node_ctor('NumberColUnaryOpNode', id='u3', op='EXP', col='v', result_col='rv')
    df = pd.DataFrame({'v': pd.Series([0.0, 1.0], dtype='Float64')})
    table = Table(df=df, col_types={'v': ColType.FLOAT})
    schema_table = Schema(type=Schema.Type.TABLE, tab=TableSchema(col_types={'v': ColType.FLOAT}))
    node.infer_output_schemas({'table': schema_table})
    out = node.process({'table': Data(payload=table)})
    import numpy as np
    assert pytest.approx(list(out['table'].payload.df['rv'])) == [1.0, pytest.approx(float(np.exp(1.0)))]
