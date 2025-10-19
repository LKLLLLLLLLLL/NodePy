from server.models.data import Schema, Data, Pattern
from pydantic import BaseModel, model_validator, PrivateAttr
from abc import abstractmethod
from typing_extensions import Self
from server.models.exception import NodeParameterError, NodeValidationError, NodeExecutionError
from .GlobalConfig import GlobalConfig

"""
This file defines the base class for all nodes.
"""

class InPort(BaseModel):
    name: str
    description: str
    optional: bool = False # default is False, means this port must be connected
    accept: Pattern
    
    def accept_schema(self, schema: Schema) -> bool:
        assert isinstance(schema, Schema)
        return schema in self.accept

class OutPort(BaseModel):
    name: str
    description: str

class BaseNode(BaseModel):
    id: str
    name: str
    type: str
    global_config: GlobalConfig
    
    _schemas_in: dict[str, Schema] | None = PrivateAttr(None) # cache for input schema
    _schemas_out: dict[str, Schema] | None = PrivateAttr(None) # cache for output schema

    """
    methods to be implemented by subclasses
    """
    @abstractmethod
    def validate_parameters(self) -> None:
        """ 
        Validate parameters when constructing the node,
        as a part of stage1 validation(param validation).
        """
        pass

    @abstractmethod
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        """ 
        Define input and output port constraint.
        The in port "accept" will be validate during stage2 validation(static analysis).
        """
        pass

    @abstractmethod
    def infer_output_schemas(self, input_schemas: dict[str, Schema]) -> dict[str, Schema]:
        """ 
        Infer output schema based on input schema during static analysis stage.
        will be called during stage2 validation.
        """
        pass

    @abstractmethod
    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        """ 
        process input data and return output data.
        
        input: { port_name: data, ... }
        output: { port_name: data, ... }
        
        Running as stage3 validation while process.
        """
        pass
    
    """
    Private methods
    """
    @model_validator(mode='after')
    def _validate_parameters(self) -> Self:
        """ validate parameters when constructing """
        if self.id.strip() == "":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="id",
                err_msg="Node id cannot be empty."
            )
        if self.name.strip() == "":
            raise NodeParameterError(
                node_id = self.id,
                err_param_key = "name",
                err_msg = "Node name cannot be empty."
            )
        if self.type.strip() == "":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="type",
                err_msg="Node type cannot be empty."
            )
        self.validate_parameters()
        return self
    
    def _validate_schema_to_port_def(self, input_schema: dict[str, Schema]) -> None:
        in_ports, _ = self.port_def()
        for port in in_ports:
            port_name = port.name
            sche = input_schema.get(port_name)
            if sche is None:
                if not port.optional:
                    raise NodeValidationError(
                        node_id=self.id,
                        err_input=[port_name],
                        err_msg=f"Input port '{port_name}' is required but not provided."
                    )
                else:
                    continue # optional port, can be None
            if sche not in port.accept:
                raise NodeValidationError(
                    node_id=self.id,
                    err_input=[port_name],
                    err_msg=f"Input port '{port_name}' schema {sche} not in accepted schemas {port.accept}."
                )
        if len(input_schema) > len(in_ports):
            raise ValueError("Input schema has more ports than defined in port_def.")
        return
        
    """
    methods to be called by outside
    """
    @classmethod
    def create_from_type(cls, global_config: GlobalConfig, type: str, **data) -> "BaseNode":
        node_type = _NODE_REGISTRY.get(type)
        if node_type is None:
            raise ValueError(f"Node type '{type}' is not registered.")
        return node_type(type=type, **data, global_config=global_config)
    
    def get_port(self):
        """ get all ports definition """
        in_ports, out_ports = self.port_def()
        return {
            "input": in_ports,
            "output": out_ports
        }
    
    def infer_schema(self, input: dict[str, Schema]) -> dict[str, Schema]:
        """ static analysis  """
        self._schemas_in = input
        # 1. validate input schema against port definitions
        self._validate_schema_to_port_def(input)
        # 2. infer output schema
        self._schemas_out = self.infer_output_schemas(input)
        return self._schemas_out
    
    def execute(self, input: dict[str, Data]) -> dict[str, Data]:
        """ run time execution """
        # 1. check if schema is inferred
        if self._schemas_in is None or self._schemas_out is None:
            raise NodeExecutionError(
                node_id=self.id,
                err_msg="Node schema not inferred before execution."
            )
        # 2. check if input data matches input schema
        input_schemas = {k : v.extract_schema() for k, v in input.items()}
        if input_schemas != self._schemas_in:
            raise NodeExecutionError(
                node_id=self.id,
                err_msg=f"Input data schema {input_schemas} does not match inferred schema {self._schemas_in}."
            )
        # 3. check if output data matches output schema
        output = self.process(input)
        output_schema = {k : v.extract_schema() for k, v in output.items()}
        if output_schema != self._schemas_out:
            raise NodeExecutionError(
                node_id=self.id,
                err_msg=f"Output data schema {output_schema} does not match inferred schema {self._schemas_out}."
            )
        return output

_NODE_REGISTRY: dict[str, type[BaseNode]] = {}

def register_node(cls):
    """ Decorator to register node classes by their type name """
    def _wrap(cls: type[BaseNode]) -> type[BaseNode]:
        if not issubclass(cls, BaseNode):
            raise TypeError("Can only register subclasses of BaseNode.")
        _NODE_REGISTRY[cls.__name__] = cls
        return cls
    return _wrap(cls)
