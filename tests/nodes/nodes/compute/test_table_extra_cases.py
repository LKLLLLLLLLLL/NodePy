import pandas as pd
import pytest

from server.models.data import Data, Table
from server.models.exception import NodeExecutionError, NodeValidationError
from server.models.schema import Schema, TableSchema
from server.models.types import ColType


def test_col_with_number_binop_infer_mismatch_types(node_ctor):
    node = node_ctor('ColWithNumberBinOpNode', id='m1', op='ADD', col='a', result_col='r')
    schema_table = Schema(type=Schema.Type.TABLE, tab=TableSchema(col_types={'a': ColType.INT}))
    # provide num schema as float to mismatch
    with pytest.raises(NodeValidationError):
        node.infer_output_schemas({'table': schema_table, 'num': Schema(type=Schema.Type.FLOAT)})


def test_col_with_number_binop_validate_param_errors(node_ctor):
    # result_col same as col
    with pytest.raises(Exception):
        node_ctor('ColWithNumberBinOpNode', id='p1', op='ADD', col='a', result_col='a')
    # illegal result col starting with underscore
    with pytest.raises(Exception):
        node_ctor('ColWithNumberBinOpNode', id='p2', op='ADD', col='a', result_col='_bad')


def test_col_with_bool_binop_infer_non_bool(node_ctor):
    node = node_ctor('ColWithBoolBinOpNode', id='b1', op='AND', col='x', result_col='r')
    # table col not boolean
    schema_table = Schema(type=Schema.Type.TABLE, tab=TableSchema(col_types={'x': ColType.INT}))
    with pytest.raises(NodeValidationError):
        node.infer_output_schemas({'table': schema_table, 'bool': Schema(type=Schema.Type.BOOL)})


def test_col_with_bool_binop_num_sub_col(node_ctor):
    node = node_ctor('ColWithBoolBinOpNode', id='b2', op='NUM_SUB_COL', col='x', result_col='r')
    df = pd.DataFrame({'x': pd.Series([True, False, True], dtype='boolean')})
    table = Table(df=df, col_types={'x': ColType.BOOL})
    schema_table = Schema(type=Schema.Type.TABLE, tab=TableSchema(col_types={'x': ColType.BOOL}))
    node.infer_output_schemas({'table': schema_table, 'bool': Schema(type=Schema.Type.BOOL)})
    out = node.process({'table': Data(payload=table), 'bool': Data(payload=True)})
    assert list(out['table'].payload.df['r']) == [False, True, False]


def test_number_unary_unsupported_mutation(node_ctor):
    node = node_ctor('NumberColUnaryOpNode', id='u_bad', op='ABS', col='x', result_col='r')
    # prepare table and _col_types
    df = pd.DataFrame({'x': pd.Series([1, 2], dtype='Int64')})
    node.__dict__['_col_types'] = {'x': ColType.INT, 'r': ColType.INT}
    # mutate op to unsupported
    node.__dict__['op'] = 'BAD'
    with pytest.raises(NodeExecutionError):
        node.process({'table': Data(payload=Table(df=df, col_types={'x': ColType.INT}))})


def test_bool_unary_unsupported_mutation(node_ctor):
    node = node_ctor('BoolColUnaryOpNode', id='b_bad', op='NOT', col='x', result_col='r')
    df = pd.DataFrame({'x': pd.Series([True, False], dtype='boolean')})
    node.__dict__['_col_types'] = {'x': ColType.BOOL, 'r': ColType.BOOL}
    node.__dict__['op'] = 'BAD'
    with pytest.raises(NodeExecutionError):
        node.process({'table': Data(payload=Table(df=df, col_types={'x': ColType.BOOL}))})


def test_number_col_with_col_infer_mismatch(node_ctor):
    node = node_ctor('NumberColWithColBinOpNode', id='n_mis', op='ADD', col1='a', col2='b', result_col='r')
    schema_table = Schema(type=Schema.Type.TABLE, tab=TableSchema(col_types={'a': ColType.INT, 'b': ColType.FLOAT}))
    with pytest.raises(NodeValidationError):
        node.infer_output_schemas({'table': schema_table})


def test_hint_no_numeric_choices(node_ctor):
    from server.interpreter.nodes.compute.table import NumberColWithColBinOpNode
    # schema with only boolean columns
    schema_table = Schema(type=Schema.Type.TABLE, tab=TableSchema(col_types={'p': ColType.BOOL}))
    hint = NumberColWithColBinOpNode.hint({'table': schema_table}, {})
    # hint may include internal '_index' column; ensure there are no numeric column choices
    col1 = hint.get('col1_choices', [])
    col2 = hint.get('col2_choices', [])
    assert all(name == '_index' for name in col1)
    assert all(name == '_index' for name in col2)
