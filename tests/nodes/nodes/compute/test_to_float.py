import pytest

from server.models.data import Data
from server.models.exception import NodeExecutionError, NodeParameterError


def test_to_float_basic_and_errors(node_ctor):
    node = node_ctor('ToFloatNode', id='f1')
    out = node.process({'input': Data(payload=True)})
    assert out['output'].payload == 1.0
    out = node.process({'input': Data(payload=2)})
    assert out['output'].payload == 2.0
    out = node.process({'input': Data(payload="3.5")})
    assert out['output'].payload == 3.5
    with pytest.raises(NodeExecutionError):
        node.process({'input': Data(payload='bad-float')})


def test_validate_parameters_errors_for_other_nodes(node_ctor):
    node = node_ctor('ToFloatNode', id='f2')
    node.type = 'Bad'
    with pytest.raises(NodeParameterError):
        node.validate_parameters()
