from server.engine.nodes.RangeNode import RangeNode
from server.engine.nodes.RandomNode import RandomNode

range_node = RangeNode(
    id = "0", 
    name = "Range Node",
    type = "RangeNode",
    start = 0.0,
    end = 10.0,
    step = 0.2,
    column_name = "numbers",
)

random_node = RandomNode(
    id = "1",
    name = "random node",
    type = "RandomNode",
    data_type = "float",
    bottom = 0.0,
    top = 100.0,
    column_name = "randoms",
    seed = None
)

print(range_node.infer_schema({})["output"])
print("--------------")
print(range_node.process(dict())["output"])

print ("\n----------------\n")

print(random_node.infer_schema({})["output"])
print("--------------")
print(random_node.process(dict())["output"])