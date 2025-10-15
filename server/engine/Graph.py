from .nodes.BaseNode import BaseNode
import networkx as nx

class NodeGraph:
    """
    The class representing the entire graph of nodes and edges.
    """
    nodes: list[BaseNode]
    graph: nx.DiGraph
    
    def __init__(
        self, 
        nodes: list[BaseNode], 
        edges: list[tuple[str, str]] # for [(node_id1, node_id2), ...], an edge from node1 to node2
    ) -> None:
        self.nodes = nodes
        self.graph = nx.DiGraph()
        self.graph.add_edges_from(edges)
