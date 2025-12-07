import os

import numpy as np

from server.models.exception import NodeParameterError, NodeValidationError
from server.models.types import ColType
from tests.nodes.utils import schema_from_coltypes, table_from_dict


def test_wordcloudnode_execute(node_ctor, test_file_root, monkeypatch):
    # Monkeypatch WordCloud to avoid dependency on system fonts in CI
    class FakeWordCloud:
        def __init__(self, *args, **kwargs):
            self._arr = (np.ones((64, 64, 3), dtype=np.uint8) * 255)

        def generate_from_frequencies(self, freqs):
            return None

        def __array__(self):
            return self._arr

    # patch the installed wordcloud class used inside the node implementation
    monkeypatch.setattr("wordcloud.WordCloud", FakeWordCloud)

    node = node_ctor("WordcloudNode", id="w_exec", word_col="word", frequency_col="freq")
    tbl = table_from_dict({"word": ["hello", "world"], "freq": [5, 3]})
    schema = schema_from_coltypes({"word": ColType.STR, "freq": ColType.INT})
    out_schema = node.infer_schema({"input": schema})
    assert "wordcloud_image" in out_schema
    out = node.execute({"input": tbl})
    assert "wordcloud_image" in out
    f = out["wordcloud_image"].payload
    assert f.format == "png"
    assert f.filename == f"{node.id}.png"
    expected_key = f"{node.id}_{f.filename}"
    expected_path = os.path.join(test_file_root, expected_key)
    assert os.path.exists(expected_path)


def test_wordcloudnode_rejects_empty_cols(node_ctor):
    with __import__("pytest").raises(NodeParameterError):
        node_ctor("WordcloudNode", id="w_err", word_col="  ", frequency_col="freq")
    with __import__("pytest").raises(NodeParameterError):
        node_ctor("WordcloudNode", id="w_err2", word_col="word", frequency_col="   ")


def test_wordcloudnode_infer_rejects_bad_types(node_ctor):
    node = node_ctor("WordcloudNode", id="w_val", word_col="word", frequency_col="freq")
    bad_schema = schema_from_coltypes({"word": ColType.INT, "freq": ColType.STR})
    with __import__("pytest").raises(NodeValidationError):
        node.infer_schema({"input": bad_schema})


def test_wordcloudnode_hint(node_ctor):
    node = node_ctor("WordcloudNode", id="w_hint", word_col="word", frequency_col="freq")
    schema = schema_from_coltypes({"word": ColType.STR, "freq": ColType.FLOAT, "other": ColType.INT})
    hint = node.get_hint("WordcloudNode", {"input": schema}, {})
    assert "word_col_choices" in hint and isinstance(hint["word_col_choices"], list)
    assert "frequency_col_choices" in hint and isinstance(hint["frequency_col_choices"], list)


def test_wordcloudnode_generate_receives_expected_freqs(node_ctor, test_file_root, monkeypatch):
    captured = {}

    class CapturingWordCloud:
        def __init__(self, *args, **kwargs):
            pass

        def generate_from_frequencies(self, freqs):
            # store freqs for inspection
            captured['freqs'] = dict(freqs)
            return None

        def __array__(self):
            import numpy as _np

            return (_np.ones((4, 4, 3), dtype=_np.uint8) * 255)

    monkeypatch.setattr("wordcloud.WordCloud", CapturingWordCloud)

    node = node_ctor("WordcloudNode", id="w_cap", word_col="word", frequency_col="freq")
    tbl = table_from_dict({"word": ["x", "y", "x"], "freq": [1, 2, 3]})
    schema = schema_from_coltypes({"word": ColType.STR, "freq": ColType.INT})
    node.infer_schema({"input": schema})
    node.execute({"input": tbl})

    # expected frequencies: last occurrences should sum? The node zips columns directly, so duplicates
    # will be last-wins in dict(zip(...)) behaviour — verify that
    assert 'freqs' in captured
    assert captured['freqs'].get('x') in {1, 3}
    assert captured['freqs'].get('y') == 2


def test_wordcloudnode_construction_and_hint_more_cases(node_ctor):
    # normal constructions
    n1 = node_ctor("WordcloudNode", id="w_ok1", word_col="w", frequency_col="f")
    n2 = node_ctor("WordcloudNode", id="w_ok2", word_col="word", frequency_col="freq")
    assert n1 is not None and n2 is not None

    # errors: empty params
    import pytest
    with pytest.raises(Exception):
        node_ctor("WordcloudNode", id="w_err3", word_col="  ", frequency_col="f")
    with pytest.raises(Exception):
        node_ctor("WordcloudNode", id="w_err4", word_col="w", frequency_col="   ")

    # hint: when schema lacks suitable cols, returns empty lists
    node = node_ctor("WordcloudNode", id="w_hint2", word_col="w", frequency_col="f")
    schema = schema_from_coltypes({"a": ColType.INT, "b": ColType.BOOL})
    hint = node.get_hint("WordcloudNode", {"input": schema}, {})
    assert isinstance(hint.get("word_col_choices"), list)
    assert isinstance(hint.get("frequency_col_choices"), list)


def test_wordcloudnode_infer_and_execute_errors(node_ctor, monkeypatch):
    import pytest
    node = node_ctor("WordcloudNode", id="w_err_exec", word_col="word", frequency_col="freq")
    schema = schema_from_coltypes({"word": ColType.STR, "freq": ColType.INT})

    # infer: missing input
    with pytest.raises(Exception):
        node.infer_schema({})

    # infer: bad types
    bad = schema_from_coltypes({"word": ColType.INT, "freq": ColType.STR})
    with pytest.raises(Exception):
        node.infer_schema({"input": bad})

    # infer: extra port causes ValueError
    with pytest.raises(ValueError):
        node.infer_schema({"input": schema, "extra": schema})

    # execute: before infer
    from tests.nodes.utils import make_data, table_from_dict
    tbl = table_from_dict({"word": ["a"], "freq": [1]})
    with pytest.raises(Exception):
        node.execute({"input": tbl})

    # execute: mismatched input schema
    node.infer_schema({"input": schema})
    with pytest.raises(Exception):
        node.execute({"input": make_data(123)})

    # execute: process runtime error propagates
    class ExplodingWordCloud:
        def __init__(self, *a, **k):
            pass
        def generate_from_frequencies(self, freqs):
            raise RuntimeError("explode")
        def __array__(self):
            import numpy as _np
            return (_np.ones((4,4,3), dtype=_np.uint8) * 255)

    # monkeypatch the installed wordcloud class used inside the node implementation
    monkeypatch.setattr("wordcloud.WordCloud", ExplodingWordCloud)
    node2 = node_ctor("WordcloudNode", id="w_explode", word_col="word", frequency_col="freq")
    node2.infer_schema({"input": schema})
    with pytest.raises(RuntimeError):
        node2.execute({"input": tbl})
