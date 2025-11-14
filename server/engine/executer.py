import networkx as nx
from server.models.project import WorkflowTopology, TopoNode, TopoEdge
from typing import Any, Literal, Callable
from .nodes.base_node import BaseNode
from server.models.data import Schema, Data
from .nodes.config import GlobalConfig
from server.lib.CacheManager import CacheManager
from server.lib.FileManager import FileManager
from server.lib.utils import safe_hash
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
        self._graph.add_nodes_from(node.id for node in self._nodes) # add nodes as indices
        for edge in self._edges:
            self._graph.add_edge(edge.src, edge.tar, src_port=edge.src_port, tar_port=edge.tar_port)
        if not nx.is_directed_acyclic_graph(self._graph):
            raise ValueError("The graph must be a Directed Acyclic Graph (DAG)")
        self._node_map: dict[str, TopoNode] = {node.id: node for node in self._nodes}
        self._node_objects: dict[str, BaseNode] = {}
        self._exec_queue: list[str] = []
        self._stage: Literal["init", "constructed", "static_analyzed", "running", "finished"] = "init"
        # construct global config
        self.cache_manager = cache_manager # used only by NodeGraph, no need to pass to nodes
        self._global_config = GlobalConfig(file_manager=file_manager, user_id=user_id, project_id=topology.project_id)
    
    def construct_nodes(self, callback: Callable[[str, Literal["success", "error"], Exception | None], bool]) -> None:
        """ 
        Construct node instances from node definitions to test if there are parameter errors .
        
        The callback function will look like:
        continue_execution = callback(node_id: str, status: Literal["success", "error"], exception: Exception | None) -> bool
        If continue_execution is False, the execution will stop.
        """
        if self._stage != "init":
            raise AssertionError(f"Graph is already in stage '{self._stage}', cannot construct nodes again.")
        self._exec_queue = list(nx.topological_sort(self._graph))

        for node_id in self._exec_queue:
            # during construction, if one nodes fails, it does not affect others
            node = self._node_map[node_id]
            id = node.id
            type = node.type
            params = node.params

            try:
                node_object = BaseNode.create_from_type(type=type, global_config=self._global_config, id=id, **params)
                if self._node_objects is None:
                    raise RuntimeError("Node objects initialized failed.")
                self._node_objects[id] = node_object
            except Exception as e:
                continue_execution = callback(id, "error", e)
                if not continue_execution:
                    return
                else:
                    continue
            else:
                continue_execution = callback(id, "success", None)
                if not continue_execution:
                    return
                else:
                    continue
        self._stage = "constructed"
        return

    def static_analyse(self, callback: Callable[[str, Literal["success", "error"], dict[str, Any] | Exception], bool]) -> None:
        """ 
        Perform static analysis to infer schemas and validate the graph 
        The callback function will look like:
        
        continue_execution = callback(node_id: str, status: Literal["success", "error"], result: dict[str, Any] | Exception) -> bool
        """
        if self._stage != "constructed":
            raise AssertionError(f"Graph is in stage '{self._stage}', cannot perform static analysis.")

        schema_cache : dict[tuple[str, str], Schema] = {} # cache for node output schema: (node_id, port) -> Schema
        unreachable_nodes = set() # the descendants of nodes that failed static analysis
        
        for node_id in self._exec_queue:
            # if one node fails, all its descendants will be skipped for avoiding redundant errors
            if node_id in unreachable_nodes:
                continue
            node = self._node_objects[node_id]
            in_edges = list(self._graph.in_edges(node_id, data=True)) # type: ignore

            # get input schema
            input_schemas : dict[str, Schema] = {}
            for edge in in_edges:
                src_id, _, edge_data = edge
                src_port = edge_data['src_port']
                tar_port = edge_data['tar_port']
                src_schema = schema_cache[(src_id, src_port)]
                input_schemas[tar_port] = src_schema

            # run schema inference
            try:
                input_schemas_hash = safe_hash(input_schemas) # guide to avoid accidental mutation
                output_schemas = node.infer_schema(input_schemas)
                if safe_hash(input_schemas) != input_schemas_hash:
                    raise AssertionError(f"Node {node_id} in type {node.type} input schemas were modified during inference, which is not allowed.")
                # store output schema
                for tar_port, schema in output_schemas.items():
                    schema_cache[(node_id, tar_port)] = schema
            except Exception as e:
                unreachable_nodes.update([node_id, *nx.descendants(self._graph, node_id)])
                continue_execution = callback(node_id, "error", e)
                if not continue_execution:
                    return
                else:
                    continue
            else:
                continue_execution = callback(node_id, "success", output_schemas)
                if not continue_execution:
                    return
                else:
                    continue

        self._stage = "static_analyzed"
        return

    def execute(self, 
                callbefore: Callable[[str], None], 
                callafter: Callable[[str, Literal["success", "error"], dict[str, Any] | Exception, float | None], bool]) -> None:
        """ 
        Execute the graph in topological order.
        
        The callbefore function will look like:
        callbefore(node_id: str) -> None
        The callafter function will look like:
        continue_execution = callafter(node_id: str, status: Literal["success", "error"], result: dict[str, Any] | Exception, running_time(in ms): float | None) -> bool
        """
        if self._stage != "static_analyzed":
            raise AssertionError(f"Graph is in stage '{self._stage}', cannot run.")
        data_cache : dict[tuple[str, str], Data] = {} # cache for node output data: (node_id, port) -> Data
        unreachable_nodes = set() # the descendants of nodes that failed execution

        for node_id in self._exec_queue:
            if node_id in unreachable_nodes:
                continue
            node = self._node_objects[node_id]
            in_edges = list(self._graph.in_edges(node_id, data=True)) # type: ignore
            
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
                node_type=self._node_map[node_id].type,
                params=self._node_map[node_id].params,
                inputs=input_data,
            )

            output_data: dict[str, Data]
            running_time: float
            try:
                # 3. execute node if cache miss
                if cache_data is None:
                    # call callbefore, only when cache miss
                    callbefore(node_id)

                    # run node
                    input_data_hash = safe_hash(input_data)  # guide to avoid accidental mutation
                    start_time = time.perf_counter()
                    output_data = node.execute(input_data)
                    running_time = (time.perf_counter() - start_time) * 1000  # in ms
                    if safe_hash(input_data) != input_data_hash:
                        raise AssertionError(f"Node {node_id} in type {node.type} input data were modified during execution, which is not allowed.")
                else:
                    output_data, running_time = cache_data
            # 4. call callafter
            except Exception as e:
                unreachable_nodes.update([node_id, *nx.descendants(self._graph, node_id)])
                continue_execution = callafter(node_id, "error", e, None)
                if not continue_execution:
                    return
                else:
                    continue
            else:
                continue_execution = callafter(node_id, "success", output_data, running_time)
                if not continue_execution:
                    return
                else:
                    pass

            # 4. store output data to self cache
            for tar_port, data in output_data.items():
                if data_cache.get((node_id, tar_port)) is not None:
                    raise RuntimeError(f"Node '{node_id}' output on port '{tar_port}' already exists in cache.")
                data_cache[(node_id, tar_port)] = data
            
            # 6. store to CacheManager
            if output_data is not None:
                self.cache_manager.set(
                    node_type=self._node_map[node_id].type,
                    params=self._node_map[node_id].params,
                    inputs=input_data,
                    outputs=output_data,
                    running_time=running_time,
                )
        self._stage = "finished"
        return
