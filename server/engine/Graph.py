import networkx as nx
from server.models.graph import GraphRequestModel, Node, Edge
from typing import Any, Literal, Callable
from .nodes.BaseNode import BaseNode
from ..models.data import Schema, Data
from .nodes.GlobalConfig import GlobalConfig
from server.lib.CacheManager import CacheManager
from server.lib.FileManager import FileManager


"""
Graph classes to analyze and execute node graphs.
"""


class GraphError(Exception):
    """ Custom exception for graph-related errors """
    pass

class NodeGraph:
    """
    The class representing the entire graph of nodes and edges.
    """
    
    file_manager: FileManager
    cache_manager: CacheManager
    _global_config: GlobalConfig
    
    _nodes: list[Node]
    _edges: list[Edge]
    _graph: nx.DiGraph
    _node_map: dict[str, Node] # node id -> Node
    _node_objects: dict[str, BaseNode]
    _exec_queue: list[str]
    _stage: Literal["init", "constructed", "static_analyzed", "running", "finished"] = "init"

    def __init__(self, 
                 request: GraphRequestModel, 
                 file_manager: FileManager, 
                 cache_manager: CacheManager
                ) -> None:
        self._nodes = request.nodes
        self._edges = request.edges
        self._graph = nx.MultiDiGraph()
        self._graph.add_nodes_from([node.id for node in self._nodes]) # add nodes as indices
        for edge in self._edges:
            self._graph.add_edge(edge.src, edge.tar, src_port=edge.src_port, tar_port=edge.tar_port)
        if not nx.is_directed_acyclic_graph(self._graph):
            raise GraphError("The graph must be a Directed Acyclic Graph (DAG)")
        self._node_map = {}
        for node in self._nodes:
            self._node_map[node.id] = node
        self._node_objects = {}
        self._exec_queue = []
        self._stage = "init"
        # construct global config
        self.cache_manager = cache_manager # used only by NodeGraph, no need to pass to nodes
        self._global_config = GlobalConfig(file_manager=file_manager)
    
    def _get_edge_tar_from_src(self, src: str) -> list[str]:
        """ Get all target node ids from a source node id """
        return [tar for s, tar in self._graph.out_edges(src)]
    
    def _get_edge_src_from_tar(self, tar: str) -> list[str]:
        """ Get all source node ids from a target node id """
        return [src for src, _ in self._graph.in_edges(tar)]
    
    def construct_nodes(self) -> None:
        """ Construct node instances from node definitions to test if there are parameter errors """
        if self._stage != "init":
            raise GraphError(f"Graph is already in stage '{self._stage}', cannot construct nodes again.")
        self._exec_queue = list(nx.topological_sort(self._graph))
        
        for node_id in self._exec_queue:
            node = self._node_map[node_id]
            id = node.id
            name = node.name
            type = node.type
            params = node.params

            node_object = BaseNode.create_from_type(type=type, global_config=self._global_config, id=id, name=name, **params)
            if self._node_objects is None:
                raise GraphError("Node objects initialized failed.")
            self._node_objects[id] = node_object
        self._stage = "constructed"
        return
    
    def static_analyse(self, callback: Callable[[str, dict[str, Any]], None]) -> None:
        """ Perform static analysis to infer schemas and validate the graph """
        if self._stage != "constructed":
            raise GraphError(f"Graph is in stage '{self._stage}', cannot perform static analysis.")

        schema_cache : dict[tuple[str, str], Schema] = {} # cache for node output schema: (node_id, port) -> Schema
        for node_id in self._exec_queue:
            node = self._node_objects[node_id]
            in_edges = list(self._graph.in_edges(node_id, data=True))

            # get input schema
            input_schemas : dict[str, Schema] = {}
            for edge in in_edges:
                src_id, _, edge_data = edge
                src_port = edge_data['src_port']
                tar_port = edge_data['tar_port']
                src_schema = schema_cache[(src_id, src_port)]
                input_schemas[tar_port] = src_schema

            # run schema inference
            output_schemas = node.infer_schema(input_schemas)
            for tar_port, schema in output_schemas.items():
                schema_cache[(node_id, tar_port)] = schema

            # call call_back
            callback(node_id, output_schemas)
        self._stage = "static_analyzed"
        return

    def execute(self, callbefore: Callable[[str], None], callafter: Callable[[str, dict[str, Any]], None]) -> None:
        """ Execute the graph in topological order """
        if self._stage != "static_analyzed":
            raise GraphError(f"Graph is in stage '{self._stage}', cannot run.")
        data_cache : dict[tuple[str, str], Data] = {} # cache for node output data: (node_id, port) -> Data

        for node_id in self._exec_queue:
            node = self._node_objects[node_id]
            in_edges = list(self._graph.in_edges(node_id, data=True))

            # call callbefore
            callbefore(node_id)
    
            # get input data
            input_data : dict[str, Data] = {}
            for edge in in_edges:
                src_id, _, edge_data = edge
                src_port = edge_data['src_port']
                tar_port = edge_data['tar_port']
                src_data = data_cache[(src_id, src_port)]
                input_data[tar_port] = src_data
            
            # run node
            output_data = node.execute(input_data)
            for tar_port, data in output_data.items():
                if data_cache.get((node_id, tar_port)) is not None:
                    raise GraphError(f"Node '{node_id}' output on port '{tar_port}' already exists in cache.")
                data_cache[(node_id, tar_port)] = data
                # for debug
                # print(f"Node '{node_id}' output on port '{tar_port}': {data.print()}")
            
            # call callafter
            callafter(node_id, output_data)
        self._stage = "finished"
        return
