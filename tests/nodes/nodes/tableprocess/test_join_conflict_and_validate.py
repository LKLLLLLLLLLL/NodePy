import pytest

from server.models.exception import NodeParameterError
from server.models.types import ColType
from tests.nodes.utils import schema_from_coltypes, table_from_dict


def test_join_validate_parameters_and_conflict(node_ctor):
    # validate_parameters should reject empty left_on/right_on
    with pytest.raises(NodeParameterError):
        node_ctor("JoinNode", id="jb1", left_on="   ", right_on="k", how="INNER")

    with pytest.raises(NodeParameterError):
        node_ctor("JoinNode", id="jb2", left_on="k", right_on="   ", how="INNER")

    # conflict column name: both tables have column 'v' besides the join key
    node = node_ctor("JoinNode", id="jc1", left_on="k", right_on="k", how="INNER")
    left_schema = schema_from_coltypes({"k": ColType.INT, "v": ColType.INT, "_index": ColType.INT})
    right_schema = schema_from_coltypes({"k": ColType.INT, "v": ColType.FLOAT, "_index": ColType.INT})

    out_schema = node.infer_schema({"left_table": left_schema, "right_table": right_schema})
    assert "joined_table" in out_schema
    # ensure conflict produced a suffixed column
    joined_cols = out_schema["joined_table"].tab.col_types
    assert "v_right" in joined_cols

    # executing process should yield both columns in the dataframe
    left = table_from_dict({"k": [1, 2], "v": [10, 20]})
    right = table_from_dict({"k": [1, 3], "v": [100.0, 300.0]})
    out = node.execute({"left_table": left, "right_table": right})
    df = out["joined_table"].payload.df
    assert "v" in df.columns
    assert "v_right" in df.columns
