import pytest

from server.models.exception import NodeValidationError
from server.models.types import ColType
from tests.nodes.utils import (
    make_data,
    make_schema,
    schema_from_coltypes,
    table_from_dict,
)


def test_insertconst_and_infer_process(node_ctor):
    node = node_ctor("InsertConstColNode", id="ic1", col_name=None, col_type=ColType.INT)
    # const_value schema mismatch should raise
    with pytest.raises(NodeValidationError):
        # provide a const_value schema that mismatches the declared col_type
        node.infer_schema({"table": schema_from_coltypes({"_index": ColType.INT}), "const_value": make_schema("str")})

    # normal process: append const col
    tbl = table_from_dict({"a": [1,2]})
    # For process we pass const value Data directly via utils
    out = node.process({"table": tbl, "const_value": make_data(5)})
    assert "table" in out
