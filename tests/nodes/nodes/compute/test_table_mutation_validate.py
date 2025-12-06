import pytest

from server.models.exception import NodeParameterError


def test_validate_parameters_type_mismatch_mutation(node_ctor):
    node_specs = [
        ('ColWithNumberBinOpNode', dict(id='t1', op='ADD', col='a', result_col='r')),
        ('ColWithBoolBinOpNode', dict(id='t2', op='AND', col='b', result_col='r')),
        ('NumberColUnaryOpNode', dict(id='t3', op='ABS', col='x', result_col='r')),
        ('BoolColUnaryOpNode', dict(id='t4', op='NOT', col='x', result_col='r')),
        ('NumberColWithColBinOpNode', dict(id='t5', op='ADD', col1='a', col2='b', result_col='r')),
        ('BoolColWithColBinOpNode', dict(id='t6', op='AND', col1='p', col2='q', result_col='r')),
        ('ColCompareNode', dict(id='t7', op='EQ', col1='a', col2='b', result_col='r')),
    ]
    for type_name, params in node_specs:
        node = node_ctor(type_name, **params)
        node.__dict__['type'] = 'BAD_TYPE'
        with pytest.raises(NodeParameterError):
            node.validate_parameters()


def test_validate_parameters_result_col_whitespace(node_ctor):
    # create a valid node then set result_col to whitespace
    node = node_ctor('ColWithNumberBinOpNode', id='w1', op='ADD', col='a', result_col='r')
    node.__dict__['result_col'] = '   '
    with pytest.raises(NodeParameterError):
        node.validate_parameters()
