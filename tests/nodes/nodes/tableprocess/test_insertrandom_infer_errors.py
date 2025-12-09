import pytest

from server.models.exception import NodeValidationError
from server.models.types import ColType
from tests.nodes.utils import schema_from_coltypes


def test_insertrandom_infer_type_mismatch(node_ctor):
    node = node_ctor("InsertRandomColNode", id="rand_inf", col_name="r1", col_type="int")
    # supply min_value as FLOAT schema to trigger validation error
    bad_min = schema_from_coltypes({"a": ColType.FLOAT, "_index": ColType.INT})
    good_table = schema_from_coltypes({"a": ColType.INT, "_index": ColType.INT})
    with pytest.raises(NodeValidationError):
        node.infer_schema({"table": good_table, "min_value": bad_min, "max_value": bad_min})
