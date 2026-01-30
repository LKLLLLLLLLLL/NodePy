from typing import Any

from pydantic import BaseModel, model_validator

from .exception import ModelValidationError


class TopoNode(BaseModel):
    id: str
    type: str
    params: dict[str, Any] = {}

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump()


class TopoEdge(BaseModel):
    src: str
    src_port: str
    tar: str
    tar_port: str

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump()

class WorkflowTopology(BaseModel):
    """
    Data structure representing a topo graph from a project.
    This class focuses on validation, analysis, and execution.
    """

    project_id: int
    nodes: list[TopoNode | None]  # None as a placeholder for virtual nodes
    edges: list[TopoEdge]

    @model_validator(mode="after")
    def all_nodes_unique(self) -> "WorkflowTopology":
        """Validate all node ids are unique"""
        node_ids = [node.id for node in self.nodes if node is not None]
        if len(node_ids) != len(set(node_ids)):
            raise ModelValidationError("Node ids must be unique")
        return self

    @model_validator(mode="after")
    def all_edges_valid(self) -> "WorkflowTopology":
        """Validate all edges connect valid nodes"""
        node_ids = {node.id for node in self.nodes if node is not None}
        for edge in self.edges:
            if edge.src not in node_ids:
                raise ModelValidationError(f"Edge source '{edge.src}' does not exist")
            if edge.tar not in node_ids:
                raise ModelValidationError(f"Edge target '{edge.tar}' does not exist")
        return self

    @model_validator(mode="after")
    def no_multiple_edges(self) -> "WorkflowTopology":
        """Validate no multiple edges between same nodes and ports"""
        edge_set = set()
        for edge in self.edges:
            if (edge.src, edge.src_port, edge.tar, edge.tar_port) in edge_set:
                raise ModelValidationError(
                    f"Multiple edges between '{edge.src}' and '{edge.tar}' on ports '{edge.src_port}' and '{edge.tar_port}' are not allowed"
                )
            edge_set.add((edge.src, edge.src_port, edge.tar, edge.tar_port))
        return self

    def get_index_by_node_id(self, node_id: str) -> int | None:
        """Get index of node by its id"""
        for index, node in enumerate(self.nodes):
            if node is not None and node.id == node_id:
                return index
        return None
