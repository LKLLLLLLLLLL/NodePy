import pytest

from server.models.data import Data
from server.models.exception import NodeExecutionError


@pytest.mark.parametrize('method,val,expected', [
    ('FLOOR', 3.7, 3),
    ('CEIL', 3.1, 4),
    ('ROUND', 3.5, round(3.5)),
])
def test_to_int_from_float_methods(node_ctor, method, val, expected):
    node = node_ctor('ToIntNode', id='i1', method=method)
    out = node.process({'input': Data(payload=float(val))})
    assert out['output'].payload == expected


def test_to_int_from_bool_and_int(node_ctor):
    node = node_ctor('ToIntNode', id='i2', method='FLOOR')
    out = node.process({'input': Data(payload=True)})
    assert out['output'].payload == 1
    out = node.process({'input': Data(payload=0.0)})
    assert out['output'].payload == 0


def test_to_int_from_str_integer_and_float(node_ctor):
    node = node_ctor('ToIntNode', id='i3', method='ROUND')
    out = node.process({'input': Data(payload='42')})
    assert out['output'].payload == 42
    out = node.process({'input': Data(payload='2.7')})
    assert out['output'].payload == round(2.7)


def test_to_int_from_bad_str_raises(node_ctor):
    node = node_ctor('ToIntNode', id='i4', method='FLOOR')
    with pytest.raises(NodeExecutionError):
        node.process({'input': Data(payload='not-a-number')})


def test_to_int_invalid_method_raises(node_ctor):
    # Cannot construct invalid Literal directly; construct valid then mutate
    node = node_ctor('ToIntNode', id='i5', method='FLOOR')
    node.__dict__['method'] = 'UNKNOWN'
    with pytest.raises(NodeExecutionError):
        node.process({'input': Data(payload=1.23)})
