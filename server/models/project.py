from pydantic import BaseModel, model_validator
from typing import Any, Self
from .data import Schema, DataRef
from .project_topology import WorkflowTopology, TopoNode, TopoEdge


class ProjNodeError(BaseModel):
    params: list[str] | None
    inputs: list[str] | None
    message: list[str] | str
    
    @model_validator(mode="after")
    def check_error_type(self) -> Self:
        if isinstance(self.params, list):
            if self.inputs is not None:
                raise ValueError("If 'params' is a list, 'inputs' must be None.")
            if not isinstance(self.message, list):
                raise ValueError("If 'params' is a list, 'message' must be a list.")
            if len(self.params) != len(self.message):
                raise ValueError("Length of 'params' and 'message' must be the same.")
        elif isinstance(self.inputs, list):
            if self.params is not None:
                raise ValueError("If 'inputs' is a list, 'params' must be None.")
            if not isinstance(self.message, list):
                raise ValueError("If 'inputs' is a list, 'message' must be a list.")
            if len(self.inputs) != len(self.message):
                raise ValueError("Length of 'inputs' and 'message' must be the same.")
        else:
            if not isinstance(self.message, str):
                raise ValueError("If neither 'params' nor 'inputs' is a list, 'message' must be a string.")

        return self

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
    
    @classmethod
    def get_empty_workflow(cls) -> "ProjWorkflow":
        return cls(
            nodes=[],
            edges=[],
            error_message=None,
        )

    def to_topo(self, project_id: int) -> WorkflowTopology:
        """Convert to WorkflowTopology"""
        topo_nodes = [TopoNode(id=node.id, type=node.type, params=node.param) for node in self.nodes]
        topo_edges = [TopoEdge(src=edge.src, src_port=edge.src_port, tar=edge.tar, tar_port=edge.tar_port) for edge in self.edges]
        return WorkflowTopology(
            project_id=project_id,
            nodes=topo_nodes,
            edges=topo_edges,
        )

    def cleanse(self) -> "ProjWorkflow":
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

    def merge_run_results_from(self, other: "ProjWorkflow") -> None:
        """
        Merge running results from another workflow instance.
        Matching is done by node id.
        """
        other_node_map = {node.id: node for node in other.nodes}
        for node in self.nodes:
            if node.id in other_node_map:
                other_node = other_node_map[node.id]
                node.schema_out = other_node.schema_out
                node.data_out = other_node.data_out
                node.error = other_node.error
                node.runningtime = other_node.runningtime
        self.error_message = other.error_message

    def apply_patch(self, patch: 'ProjectPatch') -> None:
        """
        Apply a patch to the workflow.
        """
        if patch.key[0] != "workflow":
            return
        workflow_key = patch.key[1:]
        target: Any = self
        for key in workflow_key[:-1]:
            if isinstance(key, int):
                target = target[key]
            else:
                target = getattr(target, key)
        last_key = workflow_key[-1]
        if isinstance(last_key, int):
            target[last_key] = patch.value
        else:
            setattr(target, last_key, patch.value)

    def generate_del_error_patches(self) -> list["ProjectPatch"]:
        result = []
        # 1. del error_message
        result.append(ProjectPatch(key=["workflow", "error_message"], value=None))
        # 2. del node errors
        for node in self.nodes:
            if node.error is not None:
                result.append(
                    ProjectPatch(
                        key=[
                            "workflow",
                            "nodes",
                            self.nodes.index(node),
                            "error",
                        ],
                        value=None,
                    )
                )
        return result

class Project(BaseModel):
    """
    A unified data structure for all data for a project.
    """
    project_name: str
    project_id: int
    user_id: int
    updated_at: int # timestamp in milliseconds

    thumb: str | None = None  # base64 encoded thumbnail image

    workflow: ProjWorkflow
    def to_topo(self) -> WorkflowTopology:
        """Convert to WorkflowTopology"""
        return self.workflow.to_topo(project_id=self.project_id)

    def cleanse(self) -> "Project":
        """
        Remove unreliable data from frontend before saving to database.
        Waiting to be overwritten by backend execution results.
        """
        self.workflow.cleanse()
        return self
    
    def merge_run_results_from(self, other: "Project") -> None:
        """
        Merge running results from another project instance.
        Matching is done by node id.
        """
        self.workflow.merge_run_results_from(other.workflow)

    def apply_patch(self, patch: 'ProjectPatch') -> None:
        """
        Apply a patch to the project.
        """
        if patch.key[0] != "workflow":
            return
        self.workflow.apply_patch(patch)

class ProjectPatch(BaseModel):
    """
    A data structure for patching project.
    
    example:
    key: ["nodes", 2, "position"]
    value: (100.0, 100.0)
    """
    key: list[str | int]
    value: Any
