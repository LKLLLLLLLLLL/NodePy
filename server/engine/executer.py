from .graph import GraphRequestModel, NodeGraph
from .nodes.GlobalConfig import GlobalConfig

"""
Excecuter to run the graph.
"""
def executer(request: str, global_config: GlobalConfig) -> None:
    graph_request = GraphRequestModel.from_json(request)
    graph = NodeGraph(graph_request)
    graph.construct_nodes(global_config=global_config)
    graph.static_analyse()
    graph.run()
    # for debug
    print("running finished!")
