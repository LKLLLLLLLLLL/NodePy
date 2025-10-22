from pydantic import BaseModel, model_validator
from typing import Any
from .exception import ModelValidationError
from .data import Schema

class TopoNode(BaseModel):
    id: str
    type: str
    params: dict[str, Any] = {}


class TopoEdge(BaseModel):
    src: str
    src_port: str
    tar: str
    tar_port: str


class GraphTopoModel(BaseModel):
    """
    Data structure representing node graph data from frontend.
    For validation data.
    """

    project_id: int
    nodes: list[TopoNode]
    edges: list[TopoEdge]

    @model_validator(mode="after")
    def all_nodes_unique(self) -> "GraphTopoModel":
        """Validate all node ids are unique"""
        node_ids = [node.id for node in self.nodes]
        if len(node_ids) != len(set(node_ids)):
            raise ModelValidationError("Node ids must be unique")
        return self

    @model_validator(mode="after")
    def all_edges_valid(self) -> "GraphTopoModel":
        """Validate all edges connect valid nodes"""
        node_ids = {node.id for node in self.nodes}
        for edge in self.edges:
            if edge.src not in node_ids:
                raise ModelValidationError(f"Edge source '{edge.src}' does not exist")
            if edge.tar not in node_ids:
                raise ModelValidationError(f"Edge target '{edge.tar}' does not exist")
        return self

    @model_validator(mode="after")
    def no_multiple_edges(self) -> "GraphTopoModel":
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
            if node.id == node_id:
                return index
        return None


class DataZip(BaseModel):
    """
    A lightweight representation of data,
    it store only the url of the data object.
    """
    url: str

class NodeError(BaseModel):
    param: str | None
    input: list[str] | None
    message: str

class Node(BaseModel):
    class Position(BaseModel):
        x: float
        y: float

    id: str
    type: str
    position: Position = Position(x=0.0, y=0.0)
    param: dict[str, Any] = {}
    
    runningtime: float | None = None  # in ms

    schema_out: dict[str, Schema] = {}
    data_out: dict[str, DataZip] = {}
    
    error: NodeError | None = None

class Edge(BaseModel):
    id: str
    src: str
    src_port: str
    tar: str
    tar_port: str

class Graph(BaseModel):
    """
    A unified data structure for all data for a node graph.
    """
    project_name: str
    project_id: int
    user_id: int
    
    error_message: str | None = None # global error
    
    nodes: list[Node]
    edges: list[Edge]
    
    def to_topo(self) -> GraphTopoModel:
        """Convert to GraphTopoModel"""
        topo_nodes = [TopoNode(id=node.id, type=node.type, params=node.param) for node in self.nodes]
        topo_edges = [TopoEdge(src=edge.src, src_port=edge.src_port, tar=edge.tar, tar_port=edge.tar_port) for edge in self.edges]
        return GraphTopoModel(
            project_id=self.project_id,
            nodes=topo_nodes,
            edges=topo_edges,
        )
    
    def cleanse(self) -> "Graph":
        """
        Remove unreliable data from frontend before saving to database.
        Waiting to be overwritten by backend execution results.
        """
        for node in self.nodes:
            node.schema_out = {}
            node.data_out = {}
            node.error = None
            node.runningtime = None
        self.error_message = None
        return self

    def apply_patch(self, patch: 'GraphPatch') -> None:
        """
        Apply a patch to the graph.
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

class GraphPatch(BaseModel):
    """
    A data structure for patching node graph.
    
    example:
    key: ["nodes", 2, "position"]
    value: (100.0, 100.0)
    """
    key: list[str | int]
    value: Any
