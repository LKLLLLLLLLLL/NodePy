import networkx as nx
from pydantic import BaseModel, model_validator
from typing import Any, Literal
from .nodes.BaseNode import BaseNode
from .nodes.DataType import Schema, Data
from .nodes.GlobalConfig import GlobalConfig
import json


"""
Graph classes to analyze and execute node graphs.
"""


class GraphError(Exception):
    """ Custom exception for graph-related errors """
    pass

class Node(BaseModel):
    id: str
    type: str
    name: str
    params: dict[str, Any] = {}

class Edge(BaseModel):
    src: str
    src_port: str
    tar: str
    tar_port: str

class GraphRequestModel(BaseModel):
    """
    Data structure representing node graph data from frontend.
    For validation data.
    """

    nodes: list[Node]
    edges: list[Edge]
    
    @model_validator(mode="after")
    def all_nodes_unique(self) -> "GraphRequestModel":
        """ Validate all node ids are unique """
        node_ids = [node.id for node in self.nodes]
        if len(node_ids) != len(set(node_ids)):
            raise GraphError("Node ids must be unique")
        return self

    @model_validator(mode="after")
    def all_edges_valid(self) -> "GraphRequestModel":
        """ Validate all edges connect valid nodes """
        node_ids = {node.id for node in self.nodes}
        for edge in self.edges:
            if edge.src not in node_ids:
                raise GraphError(f"Edge source '{edge.src}' does not exist")
            if edge.tar not in node_ids:
                raise GraphError(f"Edge target '{edge.tar}' does not exist")
        return self
    
    @model_validator(mode="after")
    def no_multiple_edges(self) -> "GraphRequestModel":
        """ Validate no multiple edges between same nodes and ports """
        edge_set = set()
        for edge in self.edges:
            if (edge.src, edge.src_port, edge.tar, edge.tar_port) in edge_set:
                raise GraphError(f"Multiple edges between '{edge.src}' and '{edge.tar}' on ports '{edge.src_port}' and '{edge.tar_port}' are not allowed")
            edge_set.add((edge.src, edge.src_port, edge.tar, edge.tar_port))
        return self
    
    @classmethod
    def from_json(cls, json_str: str) -> "GraphRequestModel":
        """ Create GraphRequest from JSON string """
        try:
            data = json.loads(json_str)
            return GraphRequestModel(**data)
        except json.JSONDecodeError as e:
            raise GraphError(f"Invalid JSON: {e}")
        except Exception as e:
            raise GraphError(f"Error parsing GraphRequest: {e}")

class NodeGraph:
    """
    The class representing the entire graph of nodes and edges.
    """
    _nodes: list[Node]
    _edges: list[Edge]
    _graph: nx.DiGraph
    _node_map: dict[str, Node] # node id -> Node
    _node_objects: dict[str, BaseNode]
    _exec_queue: list[str]
    _stage: Literal["init", "constructed", "static_analyzed", "running", "finished"] = "init"

    def __init__(self, request: GraphRequestModel) -> None:
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
    
    def _get_edge_tar_from_src(self, src: str) -> list[str]:
        """ Get all target node ids from a source node id """
        return [tar for s, tar in self._graph.out_edges(src)]
    
    def _get_edge_src_from_tar(self, tar: str) -> list[str]:
        """ Get all source node ids from a target node id """
        return [src for src, _ in self._graph.in_edges(tar)]
    
    def construct_nodes(self, global_config: GlobalConfig) -> None:
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

            node_object = BaseNode.create_from_type(type=type, global_config=global_config, id=id, name=name, **params)
            if self._node_objects is None:
                raise GraphError("Node objects initialized failed.")
            self._node_objects[id] = node_object
        self._stage = "constructed"
        return
    
    def static_analyse(self) -> None:
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
        self._stage = "static_analyzed"
        return

    def run(self) -> None:
        """ Execute the graph in topological order """
        if self._stage != "static_analyzed":
            raise GraphError(f"Graph is in stage '{self._stage}', cannot run.")
        data_cache : dict[tuple[str, str], Data] = {} # cache for node output data: (node_id, port) -> Data

        for node_id in self._exec_queue:
            node = self._node_objects[node_id]
            in_edges = list(self._graph.in_edges(node_id, data=True))

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
                print(f"Node '{node_id}' output on port '{tar_port}': {data.print()}")
        self._stage = "finished"
        return
