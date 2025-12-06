import pandas as pd
import pytest

from server.models.data import Data, Table
from server.models.exception import NodeExecutionError
from server.models.types import ColType


def make_table_with_index(df_dict, col_types):
    df = pd.DataFrame(df_dict)
    # ensure index column present
    return Table(df=df, col_types={**{'_index': ColType.INT}, **col_types})


def test_unsupported_op_process_raises(node_ctor):
    # ColWithNumberBinOpNode
    node = node_ctor('ColWithNumberBinOpNode', id='u1', op='ADD', col='a', result_col='r')
    node.__dict__['_col_types'] = {'_index': ColType.INT, 'a': ColType.INT, 'r': ColType.INT}
    with pytest.raises(NodeExecutionError):
        node.__dict__['op'] = 'BAD'
        node.process({'table': Data(payload=make_table_with_index({'a': pd.Series([1], dtype='Int64')}, {'a': ColType.INT})), 'num': Data(payload=1)})

    # ColWithBoolBinOpNode
    node2 = node_ctor('ColWithBoolBinOpNode', id='u2', op='AND', col='b', result_col='r')
    node2.__dict__['_col_types'] = {'_index': ColType.INT, 'b': ColType.BOOL, 'r': ColType.BOOL}
    with pytest.raises(NodeExecutionError):
        node2.__dict__['op'] = 'BAD'
        node2.process({'table': Data(payload=make_table_with_index({'b': pd.Series([True], dtype='boolean')}, {'b': ColType.BOOL})), 'bool': Data(payload=True)})

    # NumberColUnaryOpNode
    node3 = node_ctor('NumberColUnaryOpNode', id='u3', op='ABS', col='x', result_col='r')
    node3.__dict__['_col_types'] = {'_index': ColType.INT, 'x': ColType.INT, 'r': ColType.INT}
    with pytest.raises(NodeExecutionError):
        node3.__dict__['op'] = 'BAD'
        node3.process({'table': Data(payload=make_table_with_index({'x': pd.Series([1], dtype='Int64')}, {'x': ColType.INT}))})

    # BoolColUnaryOpNode
    node4 = node_ctor('BoolColUnaryOpNode', id='u4', op='NOT', col='x', result_col='r')
    node4.__dict__['_col_types'] = {'_index': ColType.INT, 'x': ColType.BOOL, 'r': ColType.BOOL}
    with pytest.raises(NodeExecutionError):
        node4.__dict__['op'] = 'BAD'
        node4.process({'table': Data(payload=make_table_with_index({'x': pd.Series([True], dtype='boolean')}, {'x': ColType.BOOL}))})

    # NumberColWithColBinOpNode
    node5 = node_ctor('NumberColWithColBinOpNode', id='u5', op='ADD', col1='a', col2='b', result_col='r')
    node5.__dict__['_col_types'] = {'_index': ColType.INT, 'a': ColType.INT, 'b': ColType.INT, 'r': ColType.INT}
    with pytest.raises(NodeExecutionError):
        node5.__dict__['op'] = 'BAD'
        node5.process({'table': Data(payload=make_table_with_index({'a': pd.Series([1], dtype='Int64'), 'b': pd.Series([2], dtype='Int64')}, {'a': ColType.INT, 'b': ColType.INT}))})

    # BoolColWithColBinOpNode
    node6 = node_ctor('BoolColWithColBinOpNode', id='u6', op='AND', col1='p', col2='q', result_col='r')
    node6.__dict__['_col_types'] = {'_index': ColType.INT, 'p': ColType.BOOL, 'q': ColType.BOOL, 'r': ColType.BOOL}
    with pytest.raises(NodeExecutionError):
        node6.__dict__['op'] = 'BAD'
        node6.process({'table': Data(payload=make_table_with_index({'p': pd.Series([True], dtype='boolean'), 'q': pd.Series([False], dtype='boolean')}, {'p': ColType.BOOL, 'q': ColType.BOOL}))})

    # ColCompareNode
    node7 = node_ctor('ColCompareNode', id='u7', op='EQ', col1='a', col2='b', result_col='r')
    node7.__dict__['_col_types'] = {'_index': ColType.INT, 'a': ColType.INT, 'b': ColType.INT, 'r': ColType.BOOL}
    with pytest.raises(NodeExecutionError):
        node7.__dict__['op'] = 'BAD'
        node7.process({'table': Data(payload=make_table_with_index({'a': pd.Series([1], dtype='Int64'), 'b': pd.Series([1], dtype='Int64')}, {'a': ColType.INT, 'b': ColType.INT}))})
