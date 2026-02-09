import time
from typing import Any, Callable, Literal

import networkx as nx
from pydantic import ValidationError

from server import DEBUG, logger
from server.config import TRACING_ENABLED
from server.interpreter.nodes.control.loop.for_base_node import (
    ForBaseBeginNode,
    ForBaseEndNode,
)
from server.lib.CacheManager import CacheManager
from server.lib.FileManager import FileManager
from server.lib.FinancialDataManager import FinancialDataManager
from server.lib.utils import safe_hash
from server.models.data import Data, Schema
from server.models.exception import NodeParameterError
from server.models.project import TopoEdge, TopoNode, WorkflowTopology

from .control_structure import ControlStructureManager
from .nodes.base_node import BaseNode
from .nodes.context import NodeContext


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
        trace_begin: float | None = None
        if TRACING_ENABLED:
            trace_begin = time.perf_counter()

        self._nodes: list[TopoNode | None] = topology.nodes
        self._edges: list[TopoEdge] = topology.edges
        self._graph: nx.MultiDiGraph = nx.MultiDiGraph()
        self._graph.add_nodes_from(node.id for node in self._nodes if node is not None) # add nodes as indices
        for edge in self._edges:
            self._graph.add_edge(edge.src, edge.tar, src_port=edge.src_port, tar_port=edge.tar_port)
        if not nx.is_directed_acyclic_graph(self._graph):
            raise ValueError("The graph must be a Directed Acyclic Graph (DAG)")
        self._node_map: dict[str, TopoNode] = {node.id: node for node in self._nodes if node is not None}
        self._node_objects: dict[str, BaseNode] = {}
        self._exec_queue: list[str] = []
        self._stage: Literal["init", "constructed", "static_analyzed", "running", "finished"] = "init"
        # construct global config
        self._cache_manager = cache_manager # used only by Interpreter itself, no need to pass to nodes
        self._context = NodeContext(
            file_manager=file_manager, 
            financial_data_manager=financial_data_manager, 
            user_id=user_id, 
            project_id=topology.project_id
        )
        # cache unreached node ids, each period will only process nodes not in this list, and may append more unreached nodes 
        self._unreached_node_ids: set[str] = set()
        self._control_structure_manager: ControlStructureManager | None = None

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
                node_object = BaseNode.create_from_type(type=type, context=self._context, id=id, **params)
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

        # analyze control structures
        self._control_structure_manager = ControlStructureManager()
        unreached = self._control_structure_manager.analyze(self._graph, self._node_objects, self._unreached_node_ids, callback)
        self._unreached_node_ids.update(unreached)

        self._stage = "static_analyzed"
        
        if TRACING_ENABLED:
            assert trace_begin is not None
            end_time = time.perf_counter()
            logger.debug(f"[Tracing] Static analyzed nodes in {(end_time - trace_begin) * 1000:.2f} ms.")

        return

    def execute(self, 
                callbefore: Callable[[str], None], 
                callafter: Callable[[str, Literal["success", "error"], dict[str, Any] | Exception, float | None], bool],
    ) -> None:
        """ 
        Execute the graph in topological order.
        
        The callbefore function will look like:
        callbefore(node_id: str) -> None
        The callafter function will look like:
        continue_execution = callafter(node_id: str, status: Literal["success", "error"], result: dict[str, Any] | Exception, running_time(in ms): float | None) -> bool
        """
        trace_begin: float | None = None
        if TRACING_ENABLED:
            trace_begin = time.perf_counter()

        if self._stage != "static_analyzed":
            raise AssertionError(f"Graph is in stage '{self._stage}', cannot run.")
        assert self._control_structure_manager is not None, "Control structure manager is not initialized."

        data_cache : dict[tuple[str, str], Data] = {} # cache for node output data: (node_id, port) -> Data
        for node_id in self._exec_queue:
            if node_id in self._unreached_node_ids:
                continue
            if self._control_structure_manager.is_body_node(node_id):
                # body nodes are executed in control structure execution
                continue
            if self._control_structure_manager.is_end_node(node_id):
                # end nodes' outputs are set in control structure execution
                continue
            in_edges = list(self._graph.in_edges(node_id, data=True)) # type: ignore

            # 1. get input data
            input_data : dict[str, Data] = {}
            for edge in in_edges:
                src_id, _, edge_data = edge
                src_port = edge_data['src_port']
                tar_port = edge_data['tar_port']
                src_data = data_cache[(src_id, src_port)]
                input_data[tar_port] = src_data

            output_data: dict[str, Data]
            running_time: float

            is_control_structure = self._control_structure_manager.is_begin_node(node_id)

            # 2. execute normal node
            if is_control_structure:
                res = self._execute_control_structure(
                    begin_node_id=node_id,
                    inputs=input_data,
                    callbefore=callbefore,
                    callafter=callafter,
                )
                if res is None:
                    # execution was stopped in control structure
                    return
                else:
                    output_data, running_time = res
                # 3. call callafter for the begin node
                # call callafter for end node
                end_node_id = self._control_structure_manager.get_end_node_id(node_id)
                continue_execution = callafter(end_node_id, "success", output_data, running_time)
                if not continue_execution:
                    return
            else:
                try:
                    output_data, running_time = self._execute_single_node(
                        node_id, 
                        input_data, 
                        callbefore,
                        use_cache=True
                    )
                # 3. call callafter
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
                    callafter_node_id = node_id if not is_control_structure else self._control_structure_manager.get_end_node_id(node_id)
                    continue_execution = callafter(callafter_node_id, "success", output_data, running_time)
                    if not continue_execution:
                        return

            # 4. store output data to self cache
            if is_control_structure:
                # for control structures, save outputs to the end node only
                end_node_id = self._control_structure_manager.get_end_node_id(node_id)
                for tar_port, data in output_data.items():
                    logger.debug(f"Storing output data for control structure end node {end_node_id} port {tar_port}")
                    if data_cache.get((end_node_id, tar_port)) is not None:
                        raise RuntimeError(f"Node '{end_node_id}' output on port '{tar_port}' already exists in cache.")
                    data_cache[(end_node_id, tar_port)] = data
            else:
                for tar_port, data in output_data.items():
                    if data_cache.get((node_id, tar_port)) is not None:
                        raise RuntimeError(f"Node '{node_id}' output on port '{tar_port}' already exists in cache.")
                    data_cache[(node_id, tar_port)] = data

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
            if node is not None and node.id in self._unreached_node_ids:
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
        exec_queue = list(nx.topological_sort(self._graph))
        node_objects: dict[str, BaseNode] = {}
        # 1. try to construct nodes
        for node_id in exec_queue:
            topo_node = self._node_map[node_id]
            try:
                node_object = BaseNode.create_from_type(
                    type=topo_node.type, 
                    context=self._context, 
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

    def _execute_single_node(
        self, 
        node_id: str, 
        input_data: dict[str, Data],
        callbefore: Callable[[str], None], 
        use_cache: bool
    ) -> tuple[dict[str, Data], float]:
        """
        Execute a single node by its id with given inputs.
        """
        node = self._node_objects.get(node_id, None)
        if node is None:
            raise ValueError(f"Node {node_id} is not constructed.")

        output_data: dict[str, Data]
        running_time: float
        # 1. search cache
        cache_data = None
        if use_cache:
            cache_data = self._cache_manager.get(
                node_type=self._node_map[node_id].type,
                params=self._node_map[node_id].params,
                inputs=input_data,
            )    
        
        if cache_data is None:
            # 2. execute node if cache miss
            # call callbefore, only when cache miss
            callbefore(node_id)

            # run node
            start_time = time.perf_counter()
            input_data_hash: str = ""

            if DEBUG:
                input_data_hash = safe_hash(input_data)  # guard to avoid accidental mutation

            output_data = node.execute(input_data)

            if DEBUG:
                if safe_hash(input_data) != input_data_hash:
                    raise AssertionError(f"Node {node_id} in type {node.type} input data were modified during execution, which is not allowed.")

            running_time = (time.perf_counter() - start_time) * 1000  # in ms
        else:
            assert isinstance(cache_data[1], float), "Cached running time should be a float for single nodes."
            output_data, running_time, _ = cache_data # type: ignore
        # 3. store to CacheManager
        if output_data is not None and use_cache:
            self._cache_manager.set(
                node_type=self._node_map[node_id].type,
                params=self._node_map[node_id].params,
                inputs=input_data,
                outputs=output_data,
                running_time=running_time,
            )
        return output_data, running_time

    def _execute_control_structure(
        self, 
        begin_node_id: str, 
        inputs: dict[str, Data],
        callbefore: Callable[[str], None],
        callafter: Callable[[str, Literal["success", "error"], dict[str, Any] | Exception, float | None], bool],
    ) -> tuple[dict[str, Data], float] | None:
        """
        Execute a control structure starting from the given begin node id.
        You can call it like a normal node's execute method.
        """
        assert self._control_structure_manager is not None, "Control structure manager is not initialized."
        if not self._control_structure_manager.is_begin_node(begin_node_id):
            raise ValueError(f"Node {begin_node_id} is not a begin node of a control structure.")
        end_node_id = self._control_structure_manager.get_end_node_id(begin_node_id)
        begin_node = self._node_objects[begin_node_id]
        end_node = self._node_objects[end_node_id]
        begin_time = time.perf_counter()
        if begin_node_id in self._unreached_node_ids:
            return None
        if isinstance(begin_node, ForBaseBeginNode):
            assert isinstance(end_node, ForBaseEndNode), "Begin node and end node types do not match."
            # send strat message (by callbefore) for begin node and all body nodes
            callbefore(begin_node_id)
            # hash control structure
            control_structure_hash = self._control_structure_manager.hash_control_structure(self._graph, begin_node_id, self._node_map)
            # check cache
            cache_data = self._cache_manager.get(
                node_type=self._node_map[end_node_id].type,
                params={"control_structure_hash": control_structure_hash}, # set control structure hash as params
                inputs=inputs,
            )
            if cache_data is not None:
                # cache hit
                outputs, total_running_time, extra = cache_data
                # call callafter for begin node and body nodes
                callafter(begin_node_id, "success", outputs, total_running_time)
                assert extra is not None, "Cache extra data should not be None for control structure nodes."
                running_times = extra.get("running_times")
                last_iter_result = extra.get("last_iter_result") # type: ignore
                assert running_times is not None and isinstance(running_times, dict), "Cached running time should be a dict for control structure nodes."
                for node_id in self._control_structure_manager.iter_control_structure(self._graph, begin_node_id):
                    callafter(node_id, "success", last_iter_result.get(node_id, {}), running_times[node_id])
                return outputs, total_running_time
            # cache miss, execute loop
            running_times = {}
            for node_id in self._control_structure_manager.iter_control_structure(self._graph, begin_node_id):
                callbefore(node_id)
                running_times[node_id] = 0.0
            last_iter_result: dict[str, dict[str, Data]] = {} # to store last iteration's output data for each node
            for input_datas in begin_node.iter_loop(inputs):
                res_cache: dict[tuple[str, str], Data] = {} # local cache for exec result in this iteration: (node_id, port) -> Data
                last_iter_result[begin_node_id] = input_datas

                # collect inputs for begin node
                for input_port, data in input_datas.items():
                    res_cache[(begin_node_id, input_port)] = data

                # execute body nodes
                for node_id in self._control_structure_manager.iter_control_structure(self._graph, begin_node_id):
                    if node_id in self._unreached_node_ids:
                        return None
                    in_edges = list(self._graph.in_edges(node_id, data=True)) # type: ignore

                    # 1. get input data
                    input_data : dict[str, Data] = {}
                    for src_id, _, edge_data in in_edges:
                        src_port = edge_data['src_port']
                        tar_port = edge_data['tar_port']
                        input_data[tar_port] = res_cache[(src_id, src_port)]

                    # 2. execute node
                    try:
                        output_data, running_time = self._execute_single_node(
                            node_id, 
                            input_data, 
                            lambda nid: None,
                            use_cache=False,
                        ) # callbefore is a no-op for body nodes
                    # 3. call callafter
                    except Exception as e:
                        self._unreached_node_ids.update(
                            [node_id, *nx.descendants(self._graph, node_id)]
                        )
                        continue_execution = callafter(node_id, "error", e, None)
                        if not continue_execution:
                            self._unreached_node_ids.update(
                                [node_id, *nx.descendants(self._graph, node_id)]
                            )
                            return None
                        else:
                            continue
                    else:
                        # for body nodes, do not call callafter
                        running_times[node_id] += running_time
                    # 4. store output data to local cache
                    for tar_port, data in output_data.items():
                        res_cache[(node_id, tar_port)] = data
                    last_iter_result[node_id] = output_data

                # collect output in this iteration for end node
                if end_node_id in self._unreached_node_ids:
                    return None
                end_in_edges = list(self._graph.in_edges(end_node_id, data=True)) # type: ignore
                end_node_inputs: dict[str, Data] = {}
                for src_id, _, edge_data in end_in_edges:
                    src_port = edge_data['src_port']
                    tar_port = edge_data['tar_port']
                    end_node_inputs[tar_port] = res_cache[(src_id, src_port)]
                end_node.end_iter_loop(end_node_inputs)
            # combine outputs
            outputs = end_node.finalize_loop()
            total_running_time = (time.perf_counter() - begin_time) * 1000  # in ms
            # cache outputs for end node
            self._cache_manager.set(
                node_type=self._node_map[end_node_id].type,
                params={"control_structure_hash": control_structure_hash}, # set control structure hash as params
                inputs=inputs,
                outputs=outputs,
                running_time=total_running_time,
                extra={
                    "running_times": running_times,
                    "last_iter_result": last_iter_result,
                },
            )
            # call callback for begin node and body nodes
            callafter(begin_node_id, "success", last_iter_result.get(begin_node_id, {}), total_running_time)
            for node_id in self._control_structure_manager.iter_control_structure(self._graph, begin_node_id):
                callafter(node_id, "success", last_iter_result.get(node_id, {}), running_times[node_id])
            return outputs, total_running_time # execute method will call callafter for end node
        else:
            assert False, f"Unknown control structure begin node type {begin_node.type}."
