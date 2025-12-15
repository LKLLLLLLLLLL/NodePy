import pytest

from server.models.exception import NodeValidationError
from server.models.types import ColType
from tests.nodes.utils import schema_from_coltypes, table_from_dict


def test_sort_infer_error_and_process(node_ctor):
    s = node_ctor("SortNode", id="s1", sort_col="z", ascending=True)
    bad_schema = schema_from_coltypes({"_index": ColType.INT, "a": ColType.INT})
    with pytest.raises(NodeValidationError):
        s.infer_output_schemas({"table": bad_schema})

    # process sort ascending/descending
    s2 = node_ctor("SortNode", id="s2", sort_col="v", ascending=True)
    schema = schema_from_coltypes({"_index": ColType.INT, "v": ColType.INT})
    out_schema = s2.infer_output_schemas({"table": schema})
    data = table_from_dict({"v": [3, 1, 2]}, col_types={"v": ColType.INT, "_index": ColType.INT})
    res = s2.process({"table": data})
    assert list(res["sorted_table"].payload.df["v"]) == [1, 2, 3]

    s3 = node_ctor("SortNode", id="s3", sort_col="v", ascending=False)
    res2 = s3.process({"table": data})
    assert list(res2["sorted_table"].payload.df["v"]) == [3, 2, 1]
