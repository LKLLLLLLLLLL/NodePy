import pytest

from server.models.data import Data
from server.models.exception import NodeParameterError


def test_to_string_node_basic(node_ctor):
    node = node_ctor('ToStringNode', id='s1')
    out = node.process({'input': Data(payload=123)})
    assert out['output'].payload == '123'
    out = node.process({'input': Data(payload=3.14)})
    assert out['output'].payload == '3.14'
    out = node.process({'input': Data(payload=True)})
    assert out['output'].payload == 'True'


def test_to_string_validate_parameters_error(node_ctor):
    node = node_ctor('ToStringNode', id='s2')
    node.type = 'Wrong'
    with pytest.raises(NodeParameterError):
        node.validate_parameters()
