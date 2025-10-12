from server.engine.nodes.RangeNode import RangeNode
from server.engine.nodes.RandomNode import RandomNode
from server.engine.nodes.PlotNode import PlotNode
from .nodes.Utils import GlobalConfig
from pathlib import Path

global_config = GlobalConfig(
    temp_dir=Path("./tmp"),
    user_id="test_user",
)
range_node = RangeNode(
    id = "0", 
    name = "Range Node",
    type = "RangeNode",
    start = 0.0,
    end = 10.0,
    step = 0.2,
    column_name = "numbers",
    global_config=global_config
)

random_node = RandomNode(
    id="1",
    name="random node",
    type="RandomNode",
    data_type="float",
    bottom=0.0,
    top=100.0,
    column_name="randoms",
    seed=10,
    global_config=global_config,
)

print(range_node.infer_schema({})["output"])
print("--------------")
print(range_node.process(dict())["output"])

print ("\n----------------\n")

print(random_node.infer_schema({})["output"])
print("--------------")
print(random_node.process(dict())["output"])

# 创建数据节点
range_node = RangeNode(
    id="1",
    name="Range",
    type="RangeNode",
    start=0,
    end=10,
    step=1,
    column_name="x",
    global_config=global_config,
)
data = range_node.process({})

# 创建可视化节点
plot_node = PlotNode(
    id="2",
    name="Plot",
    type="PlotNode",
    x_column="x",
    y_column="x",
    plot_type="bar",
    title="Line Plot",
    global_config=global_config,
)

# 执行
result = plot_node.execute({"input": data["output"]})
# print(result["output"].payload)  # 输出: my_plot.png