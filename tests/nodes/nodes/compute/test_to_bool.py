import pytest

from server.models.data import Data
from server.models.exception import NodeExecutionError


@pytest.mark.parametrize('text,expected', [
    ('true', True), ('1', True), ('yes', True),
    ('false', False), ('0', False), ('no', False),
    (' TRUE ', True), (' No ', False),
])
def test_to_bool_strings(node_ctor, text, expected):
    node = node_ctor('ToBoolNode', id='b1')
    out = node.process({'input': Data(payload=text)})
    assert out['output'].payload == expected


def test_to_bool_numbers(node_ctor):
    node = node_ctor('ToBoolNode', id='b2')
    out = node.process({'input': Data(payload=0)})
    assert out['output'].payload is False
    out = node.process({'input': Data(payload=2.3)})
    assert out['output'].payload is True


def test_to_bool_bad_string_raises(node_ctor):
    node = node_ctor('ToBoolNode', id='b3')
    with pytest.raises(NodeExecutionError):
        node.process({'input': Data(payload='maybe')})
