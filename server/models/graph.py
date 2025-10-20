from pydantic import BaseModel, model_validator
from typing import Any
from .exception import ModelValidationError

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

    project_id: int
    nodes: list[Node]
    edges: list[Edge]

    @model_validator(mode="after")
    def all_nodes_unique(self) -> "GraphRequestModel":
        """Validate all node ids are unique"""
        node_ids = [node.id for node in self.nodes]
        if len(node_ids) != len(set(node_ids)):
            raise ModelValidationError("Node ids must be unique")
        return self

    @model_validator(mode="after")
    def all_edges_valid(self) -> "GraphRequestModel":
        """Validate all edges connect valid nodes"""
        node_ids = {node.id for node in self.nodes}
        for edge in self.edges:
            if edge.src not in node_ids:
                raise ModelValidationError(f"Edge source '{edge.src}' does not exist")
            if edge.tar not in node_ids:
                raise ModelValidationError(f"Edge target '{edge.tar}' does not exist")
        return self

    @model_validator(mode="after")
    def no_multiple_edges(self) -> "GraphRequestModel":
        """Validate no multiple edges between same nodes and ports"""
        edge_set = set()
        for edge in self.edges:
            if (edge.src, edge.src_port, edge.tar, edge.tar_port) in edge_set:
                raise ModelValidationError(
                    f"Multiple edges between '{edge.src}' and '{edge.tar}' on ports '{edge.src_port}' and '{edge.tar_port}' are not allowed"
                )
            edge_set.add((edge.src, edge.src_port, edge.tar, edge.tar_port))
        return self
