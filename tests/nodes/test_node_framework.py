def test_registry_has_nodes(node_registry):
    """Basic sanity: node registry should not be empty and values subclass BaseNode."""
    assert isinstance(node_registry, dict)
    assert len(node_registry) > 0

    # spot-check: every value should be a class
    for k, v in list(node_registry.items())[:10]:
        assert isinstance(k, str)
        assert isinstance(v, type)


def test_const_node_smoke(node_ctor):
    """Construct, infer schema, and execute a simple ConstNode."""
    from server.models.data import Data
    from server.models.schema import Schema

    # construct node
    node = node_ctor("ConstNode", id="c1", value=42, data_type="int")

    # infer schemas (no inputs)
    out_schemas = node.infer_schema({})
    assert isinstance(out_schemas, dict)
    assert out_schemas.get("const") == Schema(type=Schema.Type.INT)

    # execute (no inputs)
    outputs = node.execute({})
    assert isinstance(outputs, dict)
    assert "const" in outputs
    assert isinstance(outputs["const"], Data)
    assert outputs["const"].payload == 42
