from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Generator, Literal

import networkx as nx

from server.lib.utils import safe_hash
from server.models.project_topology import TopoNode

from .nodes.base_node import BaseNode


class ControlStructureManager:
    """
    A helper class to manage control structures in the workflow.
    """

    @dataclass
    class ControlStructure:
        class Type(str, Enum):
            FOR_EACH_ROW = "FOR_EACH_ROW"
            FOR_ROLLING_WINDOW = "FOR_ROLLING_WINDOW"

        type: Type | None
        begin_node_id: str | None
        end_node_id: str | None
        body_node_ids: set[str] | None

    control_structures: dict[int, ControlStructure] | None = None  # pair_id -> ControlStructure

    def __init__(self):
        pass

    def is_body_node(self, node_id: str) -> bool:
        """
        Check if the given node id is a body node of any control structure.
        """
        assert self.control_structures is not None, "Control structures have not been analyzed yet."
        for struc in self.control_structures.values():
            if struc.body_node_ids is not None and node_id in struc.body_node_ids:
                return True
        return False

    def is_begin_node(self, node_id: str) -> bool:
        """
        Check if the given node id is a begin node of any control structure.
        """
        assert self.control_structures is not None, "Control structures have not been analyzed yet."
        for struc in self.control_structures.values():
            if struc.begin_node_id == node_id:
                return True
        return False

    def is_end_node(self, node_id: str) -> bool:
        """
        Check if the given node id is an end node of any control structure.
        """
        assert self.control_structures is not None, "Control structures have not been analyzed yet."
        for struc in self.control_structures.values():
            if struc.end_node_id == node_id:
                return True
        return False

    def get_end_node_id(self, begin_node_id: str) -> str:
        """
        Get the end node id of the control structure by its begin node id.
        """
        assert self.control_structures is not None, "Control structures have not been analyzed yet."
        for struc in self.control_structures.values():
            if struc.begin_node_id == begin_node_id:
                assert struc.end_node_id is not None
                return struc.end_node_id
        raise ValueError(f"Begin node id {begin_node_id} not found in any control structure.")

    def analyze(
        self,
        graph: nx.MultiDiGraph,
        node_objects: dict[str, BaseNode],
        skip: set[str],
        callback: Callable[[str, Literal["success", "error"], dict[str, Any] | Exception], bool],
    ) -> set[str]:
        """
        Analyze the graph to find all control structures.
        Return the set of node ids that are unreachable due to control structure errors.
        """
        unreached_nodes = skip.copy()

        # 1. find out all begin/end pairs
        self.control_structures = {}
        for node_id, node_object in node_objects.items():
            if node_object.is_control_struc():
                control_info = node_object.get_control_info()
                assert control_info is not None
                pair_id, pair_type = control_info
                control_structure: ControlStructureManager.ControlStructure
                if pair_id in self.control_structures:
                    control_structure = self.control_structures[pair_id]
                else:
                    control_structure = ControlStructureManager.ControlStructure(
                        type=None, begin_node_id=None, end_node_id=None, body_node_ids=None
                    )
                    self.control_structures[pair_id] = control_structure
                if pair_type == "BEGIN":
                    if control_structure.begin_node_id is not None:
                        raise ValueError(f"Duplicate begin node for pair id {pair_id}.")
                    if node_object.type == "ForEachRowBeginNode":
                        control_structure.type = ControlStructureManager.ControlStructure.Type.FOR_EACH_ROW
                    elif node_object.type == "ForRollingWindowBeginNode":
                        control_structure.type = ControlStructureManager.ControlStructure.Type.FOR_ROLLING_WINDOW
                    else:
                        assert False, f"Unknown begin node type {node_object.type} for pair id {pair_id}."
                    control_structure.begin_node_id = node_id
                elif pair_type == "END":
                    if control_structure.end_node_id is not None:
                        raise ValueError(f"Duplicate end node for pair id {pair_id}.")
                    control_structure.end_node_id = node_id
                else:
                    assert False, f"Unknown pair type {pair_type} for pair id {pair_id}."

        # 2. exclude skipped nodes
        copy_control_structures = self.control_structures.copy()
        changed = False
        while changed:
            for pair_id, struc in copy_control_structures.items():
                if struc.begin_node_id in unreached_nodes or struc.end_node_id in unreached_nodes:
                    del self.control_structures[pair_id]
                    if struc.begin_node_id is not None:
                        unreached_nodes.add(struc.begin_node_id)
                        unreached_nodes.update(nx.descendants(graph, struc.begin_node_id))
                    if struc.end_node_id is not None:
                        unreached_nodes.add(struc.end_node_id)
                        unreached_nodes.update(nx.descendants(graph, struc.end_node_id))
                    changed = True
            copy_control_structures = self.control_structures.copy()

        # 3. check if begin node can reach end node
        copy_control_structures = self.control_structures.copy()
        for pair_id, struc in copy_control_structures.items():
            if not nx.has_path(graph, struc.begin_node_id, struc.end_node_id):
                error = ValueError(
                    f"Begin node {struc.begin_node_id} cannot reach end node {struc.end_node_id} for pair id {pair_id}."
                )
                assert struc.begin_node_id is not None
                callback(struc.begin_node_id, "error", error)
                unreached_nodes.add(struc.begin_node_id)
                unreached_nodes.update(nx.descendants(graph, struc.begin_node_id))
                del self.control_structures[pair_id]

        # 4. for each pair, find its body nodes
        for pair_id, struc in self.control_structures.items():
            begin_node_id = struc.begin_node_id
            end_node_id = struc.end_node_id
            # body nodes = (begin.descendants - end.descendants) + (end.predecessors - begin.predecessors)
            body_nodes = set()
            begin_descendants = nx.descendants(graph, begin_node_id)
            end_descendants = nx.descendants(graph, end_node_id)
            begin_predecessors = set(nx.ancestors(graph, begin_node_id))
            end_predecessors = set(nx.ancestors(graph, end_node_id))
            body_nodes.update(begin_descendants - end_descendants)
            body_nodes.update(end_predecessors - begin_predecessors)
            # remove begin and end nodes from body nodes if present
            body_nodes.discard(begin_node_id)
            body_nodes.discard(end_node_id)
            struc.body_node_ids = body_nodes

        # 5. remove struc that contains unreached nodes
        copy_control_structures = self.control_structures.copy()
        for pair_id, struc in copy_control_structures.items():
            if struc.body_node_ids is not None:
                if len(struc.body_node_ids.intersection(unreached_nodes)) > 0:
                    assert struc.begin_node_id is not None
                    callback(
                        struc.begin_node_id,
                        "error",
                        ValueError(f"Control structure with pair id {pair_id} contains unreached body nodes."),
                    )
                    unreached_nodes.add(struc.begin_node_id)
                    unreached_nodes.update(nx.descendants(graph, struc.begin_node_id))
                    del self.control_structures[pair_id]

        # 6. check if all control structures are complete
        for pair_id, struc in self.control_structures.items():
            if struc.begin_node_id is None or struc.end_node_id is None:
                raise ValueError(f"Unmatched begin/end node for pair id {pair_id}.")
            if struc.body_node_ids is None:
                raise ValueError(f"Body nodes not found for pair id {pair_id}.")
            if struc.type is None:
                raise ValueError(f"Control structure type not found for pair id {pair_id}.")
        return unreached_nodes

    def iter_control_structure(self, graph: nx.MultiDiGraph, begin_node_id: str) -> Generator[str, Any, None]:
        """
        Iterate the each node id in control structure by its begin node id.
        """
        assert self.control_structures is not None, "Control structures have not been analyzed yet."
        # 1. find pair id by begin node id
        pair_id: int | None = None
        for id, struc in self.control_structures.items():
            if struc.begin_node_id == begin_node_id:
                pair_id = id
                break
        if pair_id is None:
            raise ValueError(f"Begin node id {begin_node_id} not found in any control structure.")

        # 2. get topological order of body nodes
        struc = self.control_structures[pair_id]
        assert struc.body_node_ids is not None
        body_subgraph = graph.subgraph(struc.body_node_ids)
        body_exec_queue = list(nx.topological_sort(body_subgraph))  # type: ignore

        # 3. yield node ids in order
        for node_id in body_exec_queue:
            assert isinstance(node_id, str)
            yield node_id

    def hash_control_structure(self, graph: nx.MultiDiGraph, begin_node_id: str, nodes: dict[str, TopoNode]) -> str:
        """
        Get the hash of the control structure by its begin node id.
        For check if the control structure has changed.
        This method will hash all body nodes parameters and topology.
        """
        assert self.control_structures is not None, "Control structures have not been analyzed yet."
        # 1. find pair id by begin node id
        pair_id: int | None = None
        for id, struc in self.control_structures.items():
            if struc.begin_node_id == begin_node_id:
                pair_id = id
                break
        if pair_id is None:
            raise ValueError(f"Begin node id {begin_node_id} not found in any control structure.")

        # 2. get topological order of body nodes
        struc = self.control_structures[pair_id]
        assert struc.body_node_ids is not None
        body_subgraph = graph.subgraph(struc.body_node_ids)
        body_exec_queue = list(nx.topological_sort(body_subgraph))  # type: ignore

        # 3. collect parameters and topology
        control_structure_info: dict[str, Any] = {}
        for node_id in body_exec_queue:
            node_id = str(node_id)
            control_structure_info[str(node_id)] = {
                "params": nodes[node_id],
                "in_edges": list(graph.in_edges(node_id, data=True)),  # type: ignore
                "out_edges": list(graph.out_edges(node_id, data=True)),
            }

        # 4. hash the info
        return safe_hash(control_structure_info)
