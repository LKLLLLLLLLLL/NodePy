import networkx as nx
from server.models.project import WorkflowTopology, TopoNode, TopoEdge
from typing import Any, Literal, Callable
from .nodes.BaseNode import BaseNode
from server.models.data import Schema, Data
from .nodes.config import GlobalConfig
from server.lib.CacheManager import CacheManager
from server.lib.FileManager import FileManager
import time

"""
Graph classes to analyze and execute node graphs.
"""

class ProjectExecutor:
    """
    The class representing the entire graph of nodes and edges.
    """

    def __init__(self, 
                 topology: WorkflowTopology, 
                 file_manager: FileManager, 
                 cache_manager: CacheManager,
                 user_id: int,
                ) -> None:
        self._topology: WorkflowTopology = topology
        self._nodes: list[TopoNode] = topology.nodes
        self._edges: list[TopoEdge] = topology.edges
        self._graph: nx.MultiDiGraph = nx.MultiDiGraph()
        self._graph.add_nodes_from([node.id for node in self._nodes]) # add nodes as indices
        for edge in self._edges:
            self._graph.add_edge(edge.src, edge.tar, src_port=edge.src_port, tar_port=edge.tar_port)
        if not nx.is_directed_acyclic_graph(self._graph):
            raise ValueError("The graph must be a Directed Acyclic Graph (DAG)")
        self._node_map: dict[str, TopoNode] = {}
        for node in self._nodes:
            self._node_map[node.id] = node
        self._node_objects: dict[str, BaseNode] = {}
        self._exec_queue: list[str] = []
        self._stage: Literal["init", "constructed", "static_analyzed", "running", "finished"] = "init"
        # construct global config
        self.cache_manager = cache_manager # used only by NodeGraph, no need to pass to nodes
        self._global_config = GlobalConfig(file_manager=file_manager, user_id=user_id, project_id=topology.project_id)

    def _get_edge_tar_from_src(self, src: str) -> list[str]:
        """ Get all target node ids from a source node id """
        return [tar for s, tar in self._graph.out_edges(src)]
    
    def _get_edge_src_from_tar(self, tar: str) -> list[str]:
        """ Get all source node ids from a target node id """
        return [src for src, _ in self._graph.in_edges(tar)]
    
    def construct_nodes(self) -> None:
        """ Construct node instances from node definitions to test if there are parameter errors """
        if self._stage != "init":
            raise AssertionError(f"Graph is already in stage '{self._stage}', cannot construct nodes again.")
        self._exec_queue = list(nx.topological_sort(self._graph))
        
        for node_id in self._exec_queue:
            node = self._node_map[node_id]
            id = node.id
            type = node.type
            params = node.params

            node_object = BaseNode.create_from_type(type=type, global_config=self._global_config, id=id, **params)
            if self._node_objects is None:
                raise RuntimeError("Node objects initialized failed.")
            self._node_objects[id] = node_object
        self._stage = "constructed"
        return
    
    def static_analyse(self, callback: Callable[[str, dict[str, Any]], None]) -> None:
        """ Perform static analysis to infer schemas and validate the graph """
        if self._stage != "constructed":
            raise AssertionError(f"Graph is in stage '{self._stage}', cannot perform static analysis.")

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

    def execute(self, callbefore: Callable[[str], None], callafter: Callable[[str, dict[str, Any], float], None]) -> None:
        """ Execute the graph in topological order """
        if self._stage != "static_analyzed":
            raise AssertionError(f"Graph is in stage '{self._stage}', cannot run.")
        data_cache : dict[tuple[str, str], Data] = {} # cache for node output data: (node_id, port) -> Data

        for node_id in self._exec_queue:
            node = self._node_objects[node_id]
            in_edges = list(self._graph.in_edges(node_id, data=True))
            
            # 1. get input data
            input_data : dict[str, Data] = {}
            for edge in in_edges:
                src_id, _, edge_data = edge
                src_port = edge_data['src_port']
                tar_port = edge_data['tar_port']
                src_data = data_cache[(src_id, src_port)]
                input_data[tar_port] = src_data

            # 2. search cache
            cache_data = self.cache_manager.get(
                node_id=node_id,
                params=self._node_map[node_id].params,
                inputs=input_data,
            )

            # 3. execute node if cache miss
            output_data: dict[str, Data]
            running_time: float
            if cache_data is None:
                # call callbefore, only when cache miss
                callbefore(node_id)
                # run node
                start_time = time.perf_counter()
                output_data = node.execute(input_data)
                running_time = (time.perf_counter() - start_time) * 1000  # in ms
            else:
                output_data, running_time = cache_data

            # 4. store output data to self cache
            for tar_port, data in output_data.items():
                if data_cache.get((node_id, tar_port)) is not None:
                    raise RuntimeError(f"Node '{node_id}' output on port '{tar_port}' already exists in cache.")
                data_cache[(node_id, tar_port)] = data

            # 5. call callafter
            callafter(node_id, output_data, running_time)
            
            # 6. store to CacheManager
            if output_data is not None:
                self.cache_manager.set(
                    node_id=node_id,
                    params=self._node_map[node_id].params,
                    inputs=input_data,
                    outputs=output_data,
                    running_time=running_time,
                )
        self._stage = "finished"
        return
