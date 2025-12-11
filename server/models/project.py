from typing import Any, Literal, Self

from pydantic import BaseModel, model_validator

from server.models.data_view import DataRef
from server.models.project_topology import TopoEdge, TopoNode, WorkflowTopology
from server.models.schema import Schema


class ProjNodeError(BaseModel):
    type: Literal["param", "validation", "execution"]
    params: list[str] | None
    inputs: list[str] | None
    message: list[str] | str
    
    @model_validator(mode="after")
    def check_error_type(self) -> Self:
        # check type consistency
        if self.type == "param":
            if self.params is None:
                raise ValueError("'params' must be provided for 'param' type errors.")
            if not isinstance(self.params, list):
                raise ValueError("'params' must be a list for 'param' type errors.")
            if not isinstance(self.message, list):
                raise ValueError("'message' must be a list for 'param' type errors.")
            if len(self.params) != len(self.message):
                raise ValueError("Length of 'params' and 'message' must be the same for 'param' type errors.")
        elif self.type == "validation":
            if self.inputs is None:
                raise ValueError("'inputs' must be provided for 'validation' type errors.")
            if not isinstance(self.inputs, list):
                raise ValueError("'inputs' must be a list for 'validation' type errors.")
            if not isinstance(self.message, list):
                raise ValueError("'message' must be a list for 'validation' type errors.")
            if len(self.inputs) != len(self.message):
                raise ValueError("Length of 'inputs' and 'message' must be the same for 'validation' type errors.")
        else:  # execution
            if not isinstance(self.message, str):
                raise ValueError("'message' must be a string for 'execution' type errors.")

        return self

class ProjNode(BaseModel):
    """
    Store the node topological state and running results.
    """
    id: str
    type: str
    param: dict[str, Any]
    
    runningtime: float | None = None  # in ms

    schema_out: dict[str, Schema] = {}
    data_out: dict[str, DataRef] = {}

    hint: dict[str, Any] = {}

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

    def apply_patch(self, patch: 'ProjWorkflowPatch') -> None:
        """
        Apply a patch to the workflow.
        """
        workflow_key = patch.key
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

    def generate_del_error_patches(self) -> list["ProjWorkflowPatch"]:
        result = []
        # 1. del error_message
        result.append(ProjWorkflowPatch(key=["error_message"], value=None))
        # 2. del node errors
        for node in self.nodes:
            if node.error is not None:
                result.append(
                    ProjWorkflowPatch(
                        key=[
                            "nodes",
                            self.nodes.index(node),
                            "error",
                        ],
                        value=None,
                    )
                )
        return result

    def generate_del_schema_data_patches(self, include: list[int] = []) -> list["ProjWorkflowPatch"]:
        """
        If node_ids is provided, only delete data_out for those nodes.
        """
        result = []
        for index, node in enumerate(self.nodes):
            if node.schema_out and (index in include):
                result.append(
                    ProjWorkflowPatch(
                        key=[
                            "nodes",
                            self.nodes.index(node),
                            "schema_out",
                        ],
                        value={},
                    )
                )
        return result

    def generate_del_data_patches(self, include: list[int] = []) -> list["ProjWorkflowPatch"]:
        """
        If node_ids is provided, only delete data_out for those nodes.
        """
        result = []
        for index, node in enumerate(self.nodes):
            if node.data_out and (index in include):
                result.append(
                    ProjWorkflowPatch(
                        key=[
                            "nodes",
                            self.nodes.index(node),
                            "data_out",
                        ],
                        value={},
                    )
                )
        return result

    def generate_del_runningtime_patches(self) -> list["ProjWorkflowPatch"]:
        result = []
        for node in self.nodes:
            if node.runningtime is not None:
                result.append(
                    ProjWorkflowPatch(
                        key=[
                            "nodes",
                            self.nodes.index(node),
                            "runningtime",
                        ],
                        value=None,
                    )
                )
        return result

class ProjUIState(BaseModel):
    """
    The UI state of the project, e.g., node positions.
    The index of nodes is correspond to the index in workflow.
    """
    class Position(BaseModel):
        id: str
        x: float
        y: float

    nodes: list[Position]
    
    @classmethod
    def get_empty_ui_state(cls) -> "ProjUIState":
        return cls(
            nodes=[],
        )

class Project(BaseModel):
    """
    A unified data structure for all data for a project.
    """
    model_config = {
        "validate_assignment": True
    }

    project_name: str
    project_id: int
    user_id: int
    updated_at: int # timestamp in milliseconds
    thumb: str | None = None  # base64 encoded thumbnail image
    
    editable: bool = True  # whether the project is editable by the current user. This value is read-only.

    workflow: ProjWorkflow
    ui_state: ProjUIState
    
    @model_validator(mode="after")
    def validate_workflow_vs_ui(self) -> Self:
        workflow_nodes = self.workflow.nodes
        ui_state_nodes = self.ui_state.nodes
        workflow_node_ids = {node.id for node in workflow_nodes}
        ui_state_node_ids = {node.id for node in ui_state_nodes}
        if workflow_node_ids != ui_state_node_ids:
            raise ValueError("Node IDs in workflow and ui_state do not match.")
        return self

    def to_topo(self) -> WorkflowTopology:
        """Convert to WorkflowTopology"""
        return self.workflow.to_topo(project_id=self.project_id)

class ProjWorkflowPatch(BaseModel):
    """
    A data structure for patching project.
    
    example:
    key: ["nodes", 2, "position"]
    value: (100.0, 100.0)
    """
    key: list[str | int]
    value: Any

class ProjectSetting(BaseModel):
    show_to_explore: bool = False  
    # whether the project is shown in explore list to other users
    project_name: str
