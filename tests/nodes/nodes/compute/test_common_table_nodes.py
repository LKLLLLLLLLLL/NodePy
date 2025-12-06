import pandas as pd
import pytest

from server.models.data import Data, Table
from server.models.schema import Schema, TableSchema
from server.models.types import ColType


def make_table(col_name, values, col_type: ColType):
    df = pd.DataFrame({col_name: pd.Series(values, dtype=col_type.to_ptype()())})
    col_types = {col_name: col_type}
    return Table(df=df, col_types=col_types)


def test_bool_col_with_col_binop_and_sub(node_ctor):
    # kept here because it was small and similar to a few other boolean tests
    node = node_ctor('BoolColWithColBinOpNode', id='bb', op='SUB', col1='p', col2='q', result_col='r')
    df = pd.DataFrame({'p': pd.Series([True, True, False], dtype='boolean'), 'q': pd.Series([True, False, False], dtype='boolean')})
    table = Table(df=df, col_types={'p': ColType.BOOL, 'q': ColType.BOOL})
    schema_table = Schema(type=Schema.Type.TABLE, tab=TableSchema(col_types={'p': ColType.BOOL, 'q': ColType.BOOL}))
    node.infer_output_schemas({'table': schema_table})
    out = node.process({'table': Data(payload=table)})
    assert list(out['table'].payload.df['r']) == [False, True, False]


def test_unsupported_ops_raise(node_ctor):
    base_table = make_table('a', [1, 2], ColType.INT)
    for type_name, params in [
        ('NumberColUnaryOpNode', {'id': 'x1', 'op': 'ABS', 'col': 'a', 'result_col': 'r'}),
        ('BoolColUnaryOpNode', {'id': 'x2', 'op': 'NOT', 'col': 'a', 'result_col': 'r'}),
        ('NumberColWithColBinOpNode', {'id': 'x3', 'op': 'ADD', 'col1': 'a', 'col2': 'a2', 'result_col': 'r'}),
        ('BoolColWithColBinOpNode', {'id': 'x4', 'op': 'AND', 'col1': 'a', 'col2': 'a', 'result_col': 'r'}),
        ('ColCompareNode', {'id': 'x5', 'op': 'EQ', 'col1': 'a', 'col2': 'a', 'result_col': 'r'}),
    ]:
        try:
            node = node_ctor(type_name, **params)
        except Exception:
            continue
        node.__dict__['op'] = 'BAD_OP'
        node.__dict__['_col_types'] = {'a': ColType.INT, 'r': ColType.INT}
        with pytest.raises(Exception):
            node.process({'table': Data(payload=base_table)})


def test_validate_parameter_errors_on_construction(node_ctor):
    with pytest.raises(Exception):
        node_ctor('ColWithNumberBinOpNode', id='v1', op='ADD', col='', result_col='r')
    with pytest.raises(Exception):
        node_ctor('NumberColUnaryOpNode', id='v2', op='ABS', col='', result_col='r')


def test_hint_methods_for_nodes(node_ctor):
    from server.interpreter.nodes.base_node import BaseNode
    schema_table = Schema(type=Schema.Type.TABLE, tab=TableSchema(col_types={'a': ColType.INT, 'b': ColType.BOOL}))
    for name in ['ColWithNumberBinOpNode', 'ColWithBoolBinOpNode', 'NumberColUnaryOpNode', 'BoolColUnaryOpNode', 'NumberColWithColBinOpNode', 'BoolColWithColBinOpNode', 'ColCompareNode']:
        hint = BaseNode.get_hint(name, {'table': schema_table}, {})
        assert isinstance(hint, dict)
