import pytest

from server.models.exception import NodeValidationError
from server.models.schema import Schema, TableSchema
from server.models.types import ColType


def test_validate_number_col_with_col_binop_parameter_errors(node_ctor):
    # empty col1
    with pytest.raises(Exception):
        node_ctor('NumberColWithColBinOpNode', id='p1', op='ADD', col1='', col2='b', result_col='r')
    # empty col2
    with pytest.raises(Exception):
        node_ctor('NumberColWithColBinOpNode', id='p2', op='ADD', col1='a', col2='', result_col='r')
    # col1 == col2
    with pytest.raises(Exception):
        node_ctor('NumberColWithColBinOpNode', id='p3', op='ADD', col1='a', col2='a', result_col='r')
    # result_col same as input
    with pytest.raises(Exception):
        node_ctor('NumberColWithColBinOpNode', id='p4', op='ADD', col1='a', col2='b', result_col='a')
    # illegal result_col
    with pytest.raises(Exception):
        node_ctor('NumberColWithColBinOpNode', id='p5', op='ADD', col1='a', col2='b', result_col='_bad')


def test_validate_bool_col_with_col_binop_parameter_errors(node_ctor):
    with pytest.raises(Exception):
        node_ctor('BoolColWithColBinOpNode', id='b1', op='AND', col1='', col2='q', result_col='r')
    with pytest.raises(Exception):
        node_ctor('BoolColWithColBinOpNode', id='b2', op='AND', col1='p', col2='', result_col='r')
    with pytest.raises(Exception):
        node_ctor('BoolColWithColBinOpNode', id='b3', op='AND', col1='p', col2='p', result_col='r')
    with pytest.raises(Exception):
        node_ctor('BoolColWithColBinOpNode', id='b4', op='AND', col1='p', col2='q', result_col='p')


def test_col_compare_infer_mismatch(node_ctor):
    node = node_ctor('ColCompareNode', id='cmp1', op='EQ', col1='a', col2='b', result_col='r')
    # mismatch types
    schema = Schema(type=Schema.Type.TABLE, tab=TableSchema(col_types={'a': ColType.INT, 'b': ColType.FLOAT}))
    with pytest.raises(NodeValidationError):
        node.infer_output_schemas({'table': schema})


def test_hints_for_bool_col_with_col_binop(node_ctor):
    from server.interpreter.nodes.compute.table import BoolColWithColBinOpNode
    schema = Schema(type=Schema.Type.TABLE, tab=TableSchema(col_types={'p': ColType.BOOL, 'q': ColType.BOOL}))
    hint = BoolColWithColBinOpNode.hint({'table': schema}, {})
    assert 'col1_choices' in hint and 'col2_choices' in hint


def test_port_def_calls(node_ctor):
    # exercise port_def for a couple of nodes to hit Pattern creation
    n1 = node_ctor('ColWithNumberBinOpNode', id='pd1', op='ADD', col='a', result_col='r')
    n1.port_def()
    n2 = node_ctor('ColWithBoolBinOpNode', id='pd2', op='AND', col='b', result_col='r')
    n2.port_def()
