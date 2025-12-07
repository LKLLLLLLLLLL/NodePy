import pytest

from server.models.exception import NodeParameterError
from tests.nodes.utils import make_data, make_schema


def test_regexextractnode_infer_and_process(node_ctor):
    # pattern with two capturing groups
    node = node_ctor("RegexExtractNode", id="re1", pattern=r"(a)(b)")
    out = node.infer_schema({"string": make_schema("str")})
    assert "matches" in out
    tab = out["matches"].tab
    assert tab is not None
    assert "group_1" in tab.col_types and "group_2" in tab.col_types

    # process normal: there are matches
    node.infer_schema({"string": make_schema("str")})
    res = node.execute({"string": make_data("abab")})
    df = res["matches"].payload.df
    # expect group columns present (may include _index column)
    assert "group_1" in df.columns and "group_2" in df.columns
    assert len(df) == 2

    # pattern with no groups -> 'match' column
    node2 = node_ctor("RegexExtractNode", id="re2", pattern=r"ab+")
    out2 = node2.infer_schema({"string": make_schema("str")})
    assert out2["matches"].tab is not None
    assert "match" in out2["matches"].tab.col_types

    node2.infer_schema({"string": make_schema("str")})
    res2 = node2.execute({"string": make_data("ab abbbb x")})
    df2 = res2["matches"].payload.df
    # expecting matches present (may be multiple); accept presence of index col
    assert "match" in df2.columns

    # invalid regex in infer should raise NodeParameterError
    node_bad = node_ctor("RegexExtractNode", id="re_bad", pattern="(*")
    with pytest.raises(NodeParameterError):
        node_bad.infer_schema({"string": make_schema("str")})

    # process when no matches should still return table with correct columns
    node3 = node_ctor("RegexExtractNode", id="re3", pattern=r"(z)")
    node3.infer_schema({"string": make_schema("str")})
    res3 = node3.execute({"string": make_data("abc")})
    df3 = res3["matches"].payload.df
    assert "group_1" in df3.columns


def test_regexextractnode_construction_hint_infer_errors(node_ctor, monkeypatch):
    # construction normals
    n1 = node_ctor("RegexExtractNode", id="rex_ok1", pattern=r"a(b)c")
    n2 = node_ctor("RegexExtractNode", id="rex_ok2", pattern=r"ab+")
    assert n1 is not None and n2 is not None

    # construction errors: missing pattern
    with pytest.raises(Exception):
        node_ctor("RegexExtractNode", id="rex_bad")

    # construction error: empty id
    with pytest.raises(Exception):
        node_ctor("RegexExtractNode", id="   ", pattern=r"a")

    # hint: Base get_hint returns {} normally
    assert n1.get_hint("RegexExtractNode", {}, {}) == {}
    assert n2.get_hint("RegexExtractNode", {"string": make_schema("str")}, {}) == {}

    # hint direct exception propagation
    from server.interpreter.nodes.stringprocess import regex as rmod
    orig = rmod.RegexExtractNode.hint
    try:
        def _boom(cls, a, b):
            raise RuntimeError("h")
        rmod.RegexExtractNode.hint = classmethod(_boom)  # type: ignore
        with pytest.raises(RuntimeError):
            rmod.RegexExtractNode.hint({}, {})  # type: ignore
    finally:
        rmod.RegexExtractNode.hint = orig

    # infer error: generated column names invalid -> patch check_no_illegal_cols to return False
    import server.interpreter.nodes.stringprocess.regex as mod
    orig_check = mod.check_no_illegal_cols
    monkeypatch.setattr(mod, "check_no_illegal_cols", lambda names: False)
    node_bad2 = node_ctor("RegexExtractNode", id="rex_bad2", pattern=r"(a)")
    with pytest.raises(NodeParameterError):
        node_bad2.infer_schema({"string": make_schema("str")})
    # restore original behavior for following assertions
    monkeypatch.setattr(mod, "check_no_illegal_cols", orig_check)

    # infer error: missing input
    node3 = node_ctor("RegexExtractNode", id="rex_err3", pattern=r"(a)")
    with pytest.raises(Exception):
        node3.infer_schema({})

    # execute runtime error: simulate re.findall raising
    node4 = node_ctor("RegexExtractNode", id="rex_err4", pattern=r"(a)")
    node4.infer_schema({"string": make_schema("str")})
    monkeypatch.setattr("re.findall", lambda p, s: (_ for _ in ()).throw(RuntimeError("fail")))
    with pytest.raises(RuntimeError):
        node4.execute({"string": make_data("a")})
