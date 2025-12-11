import time
from typing import Any, Callable, Literal

from pydantic import ValidationError

from server import DEBUG, logger
from server.config import TRACING_ENABLED
from server.lib.CacheManager import CacheManager
from server.lib.FileManager import FileManager
from server.lib.FinancialDataManager import FinancialDataManager
from server.lib.utils import safe_hash, time_check
from server.models.data import Data, Schema, Table
from server.models.exception import NodeExecutionError, NodeParameterError
from server.models.project import TopoEdge, TopoNode, WorkflowTopology

from .nodes.base_node import BaseNode
from .nodes.config import GlobalConfig

"""
Graph classes to analyze and execute node graphs.
"""

class ProjectInterpreter:
    """
    The class to interpret and execute a workflow topology.
    """

    def __init__(self, 
                 topology: WorkflowTopology, 
                 file_manager: FileManager, 
                 cache_manager: CacheManager,
                 financial_data_manager: FinancialDataManager,
                 user_id: int,
                ) -> None:
        import networkx as nx

        trace_begin: float | None = None
        if TRACING_ENABLED:
            trace_begin = time.perf_counter()

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
        self._global_config = GlobalConfig(
            file_manager=file_manager, 
            financial_data_manager=financial_data_manager, 
            user_id=user_id, 
            project_id=topology.project_id
        )
        # cache unreached node ids, each period will only process nodes not in this list, and may append more unreached nodes 
        self._unreached_node_ids: set[str] = set()
        
        if TRACING_ENABLED:
            assert trace_begin is not None
            end_time = time.perf_counter()
            logger.debug(f"[Tracing] Initialized ProjectInterpreter in {(end_time - trace_begin) * 1000:.2f} ms.")

    def construct_nodes(self, callback: Callable[[str, Literal["success", "error"], Exception | None], bool]) -> None:
        """ 
        Construct node instances from node definitions to test if there are parameter errors .
        
        The callback function will look like:
        continue_execution = callback(node_id: str, status: Literal["success", "error"], exception: Exception | None) -> bool
        If continue_execution is False, the execution will stop.
        """
        import networkx as nx
        
        trace_begin: float | None = None
        if TRACING_ENABLED:
            trace_begin = time.perf_counter()
        
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
            except ValidationError as e:
                self._unreached_node_ids.update(
                    [node_id, *nx.descendants(self._graph, node_id)]
                )
                # convert pydantic ValidationError to parameter error with more information
                errors = e.errors()
                err_params: list[str] = [str(error['loc'][-1]) for error in errors]
                err_msgs: list[str] = [error['msg'] for error in errors]
                param_error = NodeParameterError(
                    node_id=node_id,
                    err_param_keys=err_params,
                    err_msgs=err_msgs,
                )
                continue_execution = callback(id, "error", param_error)
                if not continue_execution:
                    return
                else:
                    continue
            except Exception as e:
                self._unreached_node_ids.update(
                    [node_id, *nx.descendants(self._graph, node_id)]
                )
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

        # analyze control structures
        self._analyze_control_structures()

        self._stage = "constructed"
        
        if TRACING_ENABLED:
            assert trace_begin is not None
            end_time = time.perf_counter()
            logger.debug(f"[Tracing] Constructed nodes in {(end_time - trace_begin) * 1000:.2f} ms.")

        return

    def static_analyse(self, callback: Callable[[str, Literal["success", "error"], dict[str, Any] | Exception], bool]) -> None:
        """ 
        Perform static analysis to infer schemas and validate the graph 
        The callback function will look like:
        
        continue_execution = callback(node_id: str, status: Literal["success", "error"], result: dict[str, Any] | Exception) -> bool
        """
        import networkx as nx
        
        trace_begin: float | None = None
        if TRACING_ENABLED:
            trace_begin = time.perf_counter()

        if self._stage != "constructed":
            raise AssertionError(f"Graph is in stage '{self._stage}', cannot perform static analysis.")

        schema_cache : dict[tuple[str, str], Schema] = {} # cache for node output schema: (node_id, port) -> Schema
        
        for node_id in self._exec_queue:
            # if one node fails, all its descendants will be skipped for avoiding redundant errors
            if node_id in self._unreached_node_ids:
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
                input_schemas_hash: str = ""
                if DEBUG:
                    input_schemas_hash = safe_hash(input_schemas) # guard to avoid accidental mutation

                output_schemas = node.infer_schema(input_schemas)

                if DEBUG:
                    if safe_hash(input_schemas) != input_schemas_hash:
                        raise AssertionError(f"Node {node_id} in type {node.type} input schemas were modified during inference, which is not allowed.")
                # store output schema
                for tar_port, schema in output_schemas.items():
                    schema_cache[(node_id, tar_port)] = schema
            except Exception as e:
                self._unreached_node_ids.update(
                    [node_id, *nx.descendants(self._graph, node_id)]
                )
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
        
        if TRACING_ENABLED:
            assert trace_begin is not None
            end_time = time.perf_counter()
            logger.debug(f"[Tracing] Static analyzed nodes in {(end_time - trace_begin) * 1000:.2f} ms.")

        return

    def execute(self, 
                callbefore: Callable[[str], None], 
                callafter: Callable[[str, Literal["success", "error"], dict[str, Any] | Exception, float | None], bool],
                periodic_time_check_seconds: float,
                periodic_time_check_callback: Callable[[], bool]
    ) -> None:
        """ 
        Execute the graph in topological order.
        
        The callbefore function will look like:
        callbefore(node_id: str) -> None
        The callafter function will look like:
        continue_execution = callafter(node_id: str, status: Literal["success", "error"], result: dict[str, Any] | Exception, running_time(in ms): float | None) -> bool
        """
        import networkx as nx
        
        trace_begin: float | None = None
        if TRACING_ENABLED:
            trace_begin = time.perf_counter()

        if self._stage != "static_analyzed":
            raise AssertionError(f"Graph is in stage '{self._stage}', cannot run.")
        data_cache : dict[tuple[str, str], Data] = {} # cache for node output data: (node_id, port) -> Data

        body_node_ids = set()
        for pair_info in self._control_structures.values():
            body_node_ids.update(pair_info["body_node_ids"])
        end_node_ids = set()
        for pair_info in self._control_structures.values():
            end_node_ids.add(pair_info["end_node_id"])

        for node_id in self._exec_queue:
            if node_id in self._unreached_node_ids:
                continue
            if node_id in body_node_ids:
                # body nodes are executed in control structure execution
                continue
            if node_id in end_node_ids:
                # end nodes' outputs are set in control structure execution
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
            
            # special handling for control structures
            if node_id in self._control_structures:
                end_node_id = self._control_structures[node_id]["end_node_id"]
                # 3. execute control structure
                try:
                    callbefore(node_id)
                    start_time = time.perf_counter()

                    @time_check(periodic_time_check_seconds, periodic_time_check_callback)
                    def _wrapped_execute(begin_node_id: str, inputs: dict[str, Data]) -> dict[str, Data]:
                        return self._execute_control_structure(begin_node_id, inputs)

                    output_data = _wrapped_execute(node_id, input_data)

                    running_time = (time.perf_counter() - start_time) * 1000  # in ms
                
                # 4. call callafter
                except Exception as e:
                    self._unreached_node_ids.update(
                        [node_id, *nx.descendants(self._graph, node_id)]
                    )
                    continue_execution = callafter(node_id, "error", e, None)
                    if not continue_execution:
                        self._unreached_node_ids.update(
                            [node_id, *nx.descendants(self._graph, node_id)]
                        )
                        return
                    else:
                        continue
                else:
                    continue_execution = callafter(node_id, "success", output_data, running_time)
                    if not continue_execution:
                        return
                    else:
                        pass
                
                # 5. store output data as the output data from end node to self cache
                for tar_port, data in output_data.items():
                    if data_cache.get((end_node_id, tar_port)) is not None:
                        raise RuntimeError(f"Node '{end_node_id}' output on port '{tar_port}' already exists in cache.")
                    data_cache[(end_node_id, tar_port)] = data
                
                # 6. store to CacheManager
                # pass
                continue
            
            try:
                # 3. execute node if cache miss
                if cache_data is None:
                    # call callbefore, only when cache miss
                    callbefore(node_id)

                    # run node
                    start_time = time.perf_counter()
                    input_data_hash: str = ""

                    if DEBUG:
                        input_data_hash = safe_hash(input_data)  # guard to avoid accidental mutation

                    @time_check(periodic_time_check_seconds, periodic_time_check_callback)
                    def _wrapped_execute(node: BaseNode, input_data: dict[str, Data]) -> dict[str, Data]:
                        return node.execute(input_data)

                    output_data = _wrapped_execute(node, input_data)

                    if DEBUG:
                        if safe_hash(input_data) != input_data_hash:
                            raise AssertionError(f"Node {node_id} in type {node.type} input data were modified during execution, which is not allowed.")

                    running_time = (time.perf_counter() - start_time) * 1000  # in ms
                else:
                    output_data, running_time = cache_data
            # 4. call callafter
            except Exception as e:
                self._unreached_node_ids.update(
                    [node_id, *nx.descendants(self._graph, node_id)]
                )
                continue_execution = callafter(node_id, "error", e, None)
                if not continue_execution:
                    self._unreached_node_ids.update(
                        [node_id, *nx.descendants(self._graph, node_id)]
                    )
                    return
                else:
                    continue
            else:
                continue_execution = callafter(node_id, "success", output_data, running_time)
                if not continue_execution:
                    return
                else:
                    pass

            # 5. store output data to self cache
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
        
        if TRACING_ENABLED:
            assert trace_begin is not None
            end_time = time.perf_counter()
            logger.debug(f"[Tracing] Executed nodes in {(end_time - trace_begin) * 1000:.2f} ms.")

        return

    def get_unreached_nodes(self) -> list[int]:
        """ 
        Get the list of node ids that were not reached during the last static analysis or execution.
        """
        # convert node id to the index in the topology nodes list
        unreached_node_indices = []
        for index, node in enumerate(self._nodes):
            if node.id in self._unreached_node_ids:
                unreached_node_indices.append(index)
        return unreached_node_indices

    def get_ui_hint(self, callback: Callable[[str, dict[str, Schema]], bool]) -> None:
        """
        Get UI hints from all nodes.
        For this method, there is no need to clean up unreached nodes, because it traverses all nodes anyway.
        param: 
        The callback function will look like:
        continue_execution = callback(node_id: str, hint: dict[str, Schema]) -> bool
        """
        # Because the hint method may be called before all parameters are set,
        # so it should process all node errors transparently.
        import networkx as nx

        exec_queue = list(nx.topological_sort(self._graph))
        node_objects: dict[str, BaseNode] = {}
        # 1. try to construct nodes
        for node_id in exec_queue:
            topo_node = self._node_map[node_id]
            try:
                node_object = BaseNode.create_from_type(
                    type=topo_node.type, 
                    global_config=self._global_config, 
                    id=topo_node.id, 
                    **topo_node.params
                )
                node_objects[node_id] = node_object
            except Exception:
                continue

        schema_cache : dict[tuple[str, str], Schema] = {} # cache for node output schema: (node_id, port) -> Schema
        for node_id in exec_queue:
            # 2. get as much as schemas as possible
            node = node_objects.get(node_id, None)
            in_edges = list(self._graph.in_edges(node_id, data=True)) # type: ignore

            # get input schema
            input_schemas : dict[str, Schema] = {}
            for edge in in_edges:
                src_id, _, edge_data = edge
                src_port = edge_data['src_port']
                tar_port = edge_data['tar_port']
                if (src_id, src_port) in schema_cache:
                    src_schema = schema_cache[(src_id, src_port)]
                    input_schemas[tar_port] = src_schema
            if node is not None:
                # run schema inference
                try:
                    output_schemas = node.infer_schema(input_schemas)
                    # store output schema
                    for tar_port, schema in output_schemas.items():
                        schema_cache[(node_id, tar_port)] = schema
                except Exception:
                    pass

            # 3. get UI hint for constructed nodes
            topo_node = self._node_map[node_id]
            hint = BaseNode.get_hint(topo_node.type, input_schemas, topo_node.params)
            continue_execution = callback(node_id, hint)
            if not continue_execution:
                break  

    """
    Helper methods to process control structures in the graph.
    """
    def _analyze_control_structures(self) -> None:
        """
        Scan the graph to find all begin/end pairs and their bodies.
        """
        import networkx as nx

        # 1. find out all begin/end pairs
        pair_nodes: dict[int, tuple[str, str]] = {}  # pair_id -> (begin_node_id, end_node_id)
        for node_id, node_object in self._node_objects.items():
            if node_object.is_pair():
                pair_info = node_object.get_pair_info()
                assert pair_info is not None
                pair_id, pair_type = pair_info
                old_begin_node_id, old_end_node_id = pair_nodes.get(pair_id, ("", ""))
                if pair_type == "BEGIN":
                    if old_begin_node_id != "":
                        raise ValueError(f"Duplicate begin node for pair id {pair_id}.")
                    pair_nodes[pair_id] = (node_id, old_end_node_id)
                elif pair_type == "END":
                    if old_end_node_id != "":
                        raise ValueError(f"Duplicate end node for pair id {pair_id}.")
                    pair_nodes[pair_id] = (old_begin_node_id, node_id)
        
        # 2. for each pair, find its body nodes
        body_graphs: dict[int, set[str]] = {}  # pair_id -> set of body node ids
        for pair_id, (begin_node_id, end_node_id) in pair_nodes.items():
            if begin_node_id == "" or end_node_id == "":
                raise ValueError(f"Unmatched begin/end node for pair id {pair_id}.")
            # find all nodes reachable from begin_node_id without passing through end_node_id
            body_nodes = set()
            for node in self._exec_queue[self._exec_queue.index(begin_node_id) + 1: self._exec_queue.index(end_node_id)]:
                if nx.has_path(self._graph, begin_node_id, node) and nx.has_path(self._graph, node, end_node_id):
                    body_nodes.add(node)
            body_graphs[pair_id] = body_nodes

        # 3. get exec_queue for each body
        body_exec_queues: dict[int, list[str]] = {}  # pair_id -> list of body node ids in exec order
        for pair_id, body_nodes in body_graphs.items():
            subgraph = self._graph.subgraph(body_nodes).copy()
            subgraph = nx.MultiDiGraph(subgraph)
            body_exec_queue = list(nx.topological_sort(subgraph))
            body_exec_queues[pair_id] = body_exec_queue

        # 4. store results
        self._control_structures: dict[str, dict] = {}
        for pair_id, (begin_node_id, end_node_id) in pair_nodes.items():
            self._control_structures[begin_node_id] = {
                "end_node_id": end_node_id,
                "body_node_ids": body_graphs[pair_id],
                "body_exec_queue": body_exec_queues[pair_id],
            }

    def _execute_control_structure(self, begin_node_id: str, inputs: dict[str, Data]) -> dict[str, Data]:
        """
        Execute a control structure starting from the given begin node id.
        You can call it like a normal node's execute method.
        """
        import pandas as pd
        if begin_node_id not in self._control_structures:
            raise ValueError(f"Node {begin_node_id} is not a begin node of a control structure.")
        control_info = self._control_structures[begin_node_id]
        control_structure_begin_type = self._node_objects[begin_node_id].type
        
        if control_structure_begin_type == "ForEachRowBeginNode":
            # ForEachRow control structure
            input_table_data = inputs.get("table")
            assert input_table_data is not None
            assert isinstance(input_table_data.payload, Table)
            input_table_df = input_table_data.payload.df
            output_rows: list[Data] = []
            for index in range(0, len(input_table_df)):
                res_cache: dict[tuple[str, str], Data] = {} # local cache for exec result in this iteration: (node_id, port) -> Data

                # set the current row data to the output port of the begin node
                row_data = Data(
                    payload=Table(
                        df=input_table_df.iloc[index: index + 1],
                        col_types=input_table_data.payload.col_types
                    )
                )
                res_cache[(begin_node_id, "row")] = row_data

                # a sample interpreter to execute body nodes
                for node_id in control_info["body_exec_queue"]:
                    node = self._node_objects[node_id]
                    in_edges = list(self._graph.in_edges(node_id, data=True)) # type: ignore

                    # 1. get input data
                    input_data : dict[str, Data] = {}
                    for src_id, _, edge_data in in_edges:
                        src_port = edge_data['src_port']
                        tar_port = edge_data['tar_port']
                        input_data[tar_port] = res_cache[(src_id, src_port)]

                    # 2. search cache in cache manager
                    cache_data = self.cache_manager.get(
                        node.type, 
                        self._node_map[node_id].params, 
                        input_data
                    )

                    output_data: dict[str, Data]
                    if cache_data is not None:
                        output_data, execution_time = cache_data
                    else:
                        # 3. execute node if cache miss
                        start_time = time.perf_counter()
                        output_data = node.execute(input_data)
                        end_time = time.perf_counter()
                        execution_time = (end_time - start_time) * 1000  # in ms

                    # 4. store output data to local cache
                    for tar_port, data in output_data.items():
                        res_cache[(node_id, tar_port)] = data
                    
                    # 5. store to CacheManager
                    if output_data is not None:
                        self.cache_manager.set(
                            node_type=self._node_map[node_id].type,
                            params=self._node_map[node_id].params,
                            inputs=input_data,
                            outputs=output_data,
                            running_time=execution_time,
                        )
                    
                # collect output from the input of the end node
                end_node_id = control_info["end_node_id"]
                end_in_edges = list(self._graph.in_edges(end_node_id, data=True)) # type: ignore
                for src_id, _, edge_data in end_in_edges:
                    src_port = edge_data['src_port']
                    tar_port = edge_data['tar_port']
                    output_rows.append(res_cache[(src_id, src_port)])
            # combine all output rows into a single table
            for row in output_rows:
                assert isinstance(row.payload, Table)
            combined_df = pd.concat([row.payload.df for row in output_rows], ignore_index=True) # type: ignore
            combined_col_types = input_table_data.payload.col_types
            
            # find the output port name of the end node
            end_node_id = control_info["end_node_id"]
            end_node = self._node_objects[end_node_id]
            _, out_ports = end_node.port_def()
            if not out_ports:
                return {} # End node has no output
            output_port_name = out_ports[0].name
            
            return {
                output_port_name: Data(
                    payload=Table(
                        df=combined_df,
                        col_types=combined_col_types
                    )
                )
            }
        elif control_structure_begin_type == "ForRollingWindowBeginNode":
            input_table_data = inputs.get("table")
            assert input_table_data is not None
            input_node = self._node_objects[begin_node_id]
            window_size = getattr(input_node, "window_size", None)
            assert isinstance(window_size, int)
            
            # if windows size is too small, raise error
            assert isinstance(input_table_data.payload, Table)
            assert input_table_data.payload.df is not None
            if window_size > len(input_table_data.payload.df):
                raise NodeExecutionError(
                    node_id=begin_node_id,
                    err_msg=f"Window size {window_size} is larger than the number of rows {len(input_table_data.payload.df)} in the input table.",
                )

            output_rows: list[Data] = []
            for index in range(0, len(input_table_data.payload.df) - window_size + 1):
                res_cache: dict[tuple[str, str], Data] = {} # local cache for exec result in this iteration: (node_id, port) -> Data

                # set the current window data to the output port of the begin node
                window_data = Data(
                    payload=Table(
                        df=input_table_data.payload.df.iloc[index: index + window_size],
                        col_types=input_table_data.payload.col_types
                    )
                )
                res_cache[(begin_node_id, "window")] = window_data

                # a sample interpreter to execute body nodes
                for node_id in control_info["body_exec_queue"]:
                    node = self._node_objects[node_id]
                    in_edges = list(self._graph.in_edges(node_id, data=True)) # type: ignore

                    # 1. get input data
                    input_data : dict[str, Data] = {}
                    for src_id, _, edge_data in in_edges:
                        src_port = edge_data['src_port']
                        tar_port = edge_data['tar_port']
                        input_data[tar_port] = res_cache[(src_id, src_port)]

                    # 2. search cache in cache manager
                    cache_data = self.cache_manager.get(
                        node.type, 
                        self._node_map[node_id].params, 
                        input_data
                    )

                    output_data: dict[str, Data]
                    if cache_data is not None:
                        output_data, execution_time = cache_data
                    else:
                        # 3. execute node if cache miss
                        start_time = time.perf_counter()
                        output_data = node.execute(input_data)
                        end_time = time.perf_counter()
                        execution_time = (end_time - start_time) * 1000  # in ms

                    # 4. store output data to local cache
                    for tar_port, data in output_data.items():
                        res_cache[(node_id, tar_port)] = data
                    
                    # 5. store to CacheManager
                    if output_data is not None:
                        self.cache_manager.set(
                            node_type=self._node_map[node_id].type,
                            params=self._node_map[node_id].params,
                            inputs=input_data,
                            outputs=output_data,
                            running_time=execution_time,
                        )
                    
                # collect output from the input of the end node
                end_node_id = control_info["end_node_id"]
                end_in_edges = list(self._graph.in_edges(end_node_id, data=True)) # type: ignore
                for src_id, _, edge_data in end_in_edges:
                    src_port = edge_data['src_port']
                    tar_port = edge_data['tar_port']
                    output_rows.append(res_cache[(src_id, src_port)])
            # combine all output rows into a single table
            for row in output_rows:
                assert isinstance(row.payload, Table)
            combined_df = pd.concat([row.payload.df for row in output_rows], ignore_index=True) # type: ignore
            combined_col_types = input_table_data.payload.col_types

            # find the output port name of the end node
            end_node_id = control_info["end_node_id"]
            end_node = self._node_objects[end_node_id]
            _, out_ports = end_node.port_def()
            if not out_ports:
                return {} # End node has no output
            output_port_name = out_ports[0].name
            return {
                output_port_name: Data(
                    payload=Table(
                        df=combined_df,
                        col_types=combined_col_types
                    )
                )
            }
            
        else:
            raise NotImplementedError(f"Control structure type '{control_structure_begin_type}' is not implemented yet.")
