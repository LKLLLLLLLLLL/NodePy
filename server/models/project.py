from pydantic import BaseModel
from typing import Any
from .data import Schema, DataRef
from .project_topology import ProjectTopology, TopoNode, TopoEdge


class ProjNodeError(BaseModel):
    param: str | None
    input: list[str] | None
    message: str

class ProjNode(BaseModel):
    class Position(BaseModel):
        x: float
        y: float

    id: str
    type: str
    position: Position
    param: dict[str, Any]
    
    runningtime: float | None = None  # in ms

    schema_out: dict[str, Schema] = {}
    data_out: dict[str, DataRef] = {}

    error: ProjNodeError | None = None

class ProjEdge(BaseModel):
    id: str
    src: str
    src_port: str
    tar: str
    tar_port: str

class ProjWorkflow(BaseModel):
    error_message: str | None = None # global error

    nodes: list[ProjNode]
    edges: list[ProjEdge]

class Project(BaseModel):
    """
    A unified data structure for all data for a project.
    """
    project_name: str
    project_id: int
    user_id: int

    workflow: ProjWorkflow
    def to_topo(self) -> ProjectTopology:
        """Convert to ProjectTopology"""
        topo_nodes = [TopoNode(id=node.id, type=node.type, params=node.param) for node in self.workflow.nodes]
        topo_edges = [TopoEdge(src=edge.src, src_port=edge.src_port, tar=edge.tar, tar_port=edge.tar_port) for edge in self.workflow.edges]
        return ProjectTopology(
            project_id=self.project_id,
            nodes=topo_nodes,
            edges=topo_edges,
        )

    def cleanse(self) -> "Project":
        """
        Remove unreliable data from frontend before saving to database.
        Waiting to be overwritten by backend execution results.
        """
        for node in self.workflow.nodes:
            node.schema_out = {}
            node.data_out = {}
            node.error = None
            node.runningtime = None
        self.workflow.error_message = None
        return self
    
    def merge_run_results_from(self, other: "Project") -> None:
        """
        Merge running results from another project instance.
        Matching is done by node id.
        """
        other_node_map = {node.id: node for node in other.workflow.nodes}
        for node in self.workflow.nodes:
            if node.id in other_node_map:
                other_node = other_node_map[node.id]
                node.schema_out = other_node.schema_out
                node.data_out = other_node.data_out
                node.error = other_node.error
                node.runningtime = other_node.runningtime
        self.error_message = other.error_message

    def apply_patch(self, patch: 'ProjectPatch') -> None:
        """
        Apply a patch to the project.
        """
        target = self
        for key in patch.key[:-1]:
            if isinstance(key, int):
                target = target[key]  # type: ignore
            else:
                target = getattr(target, key)  # type: ignore
        last_key = patch.key[-1]
        if isinstance(last_key, int):
            target[last_key] = patch.value  # type: ignore
        else:
            setattr(target, last_key, patch.value)  # type: ignore

class ProjectPatch(BaseModel):
    """
    A data structure for patching project.
    
    example:
    key: ["nodes", 2, "position"]
    value: (100.0, 100.0)
    """
    key: list[str | int]
    value: Any
