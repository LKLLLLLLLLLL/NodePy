from pydantic import BaseModel, model_validator
from typing_extensions import Self
from abc import abstractmethod
from typing import Literal
from .Utils import NodeValidationError, InPort, OutPort, Data, Schema, Visualization, NodeExecutionError, GlobalConfig

"""
BaseNode definition.
An abstract base class for all nodes.
"""
class BaseNode(BaseModel):
    id: str
    name: str
    type: str
    global_config: GlobalConfig # set by engine

    vis: Visualization | None = None # set by process method

    """
    methods to be implemented by subclasses
    """
    
    @abstractmethod
    def validate_parameters(self) -> None:
        """ 
        validate parameters when constructing the node 
        as a part of stage1 validation
        """
        pass
    
    @abstractmethod
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        """ 
        define input and output port constraint 
        as a part of stage2 validation
        """
        pass

    @abstractmethod
    def validate_input(self, input: dict[str, Data]) -> None:
        """
        validate input during processing stage
        as a part of stage3 validation
        """
        pass
    
    @abstractmethod
    def infer_output_schema(self, input_schema: dict[str, Schema]) -> dict[str, Schema]:
        """ 
        infer output schema based on input schema during static analysis stage 
        will be called during stage2 validation, for output schema inference
        """
        pass
    
    @abstractmethod
    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        """ 
        process input data and return output data.
        
        input: { port_name: data, ... }
        output: { port_name: data, ... }
        """
        pass
    
    
    """
    private methods
    """
    """ Stage1: simple parameter validation after initialization """
    @model_validator(mode='after')
    def _validate_parameters(self) -> Self:
        """ validate parameters """
        # validate BaseNode parameters
        if self.id == "" or self.id.strip() == "":
            raise NodeValidationError("Node id cannot be empty.")
        if self.name == "" or self.name.strip() == "":
            raise NodeValidationError("Node name cannot be empty.")
        if self.type == "" or self.type.strip() == "":
            raise NodeValidationError("Node type cannot be empty.")
        
        # call subclass-specific parameter validation
        self.validate_parameters()
        
        return self

    def _validate_schem_to_port_def(self, input: dict[str, Schema]) -> None:
        in_ports, _ = self.port_def()
        input_copy = input.copy()
        if not isinstance(in_ports, list):
            raise NodeValidationError("port_def must return a list of input ports.")
        for port in in_ports:
            real_schema = input_copy.get(port.name)
            if real_schema is None:
                if port.required:
                    raise NodeValidationError(f"Required port '{port.name}' not found in schema.")
                else:
                    continue
            # Use the accepts() method which handles type and column validation
            if not port.accepts(real_schema):
                expected_types = ", ".join([t.value for t in port.accept_types])
                if port.table_columns is not None:
                    raise NodeValidationError(
                        f"Port '{port.name}' schema mismatch. "
                        f"Expected TABLE with columns {list(port.table_columns.keys())}, "
                        f"Got: {real_schema}"
                    )
                else:
                    raise NodeValidationError(
                        f"Port '{port.name}' type mismatch. "
                        f"Expected one of: [{expected_types}], Got: {real_schema.type.value}"
                    )
            input_copy.pop(port.name)
        if input_copy:
            raise NodeValidationError(f"Extra input ports not defined: {list(input_copy.keys())}")
    
    """
    methods to be called by the engine
    """  
    def get_ports(self) -> dict[Literal["in", "out"], list[InPort] | list[OutPort]]:
        """ get all ports defination of this node """
        in_ports, out_ports = self.port_def()
        return {"in": in_ports, "out": out_ports}

    """ Stage2: static schema inference before execution """
    def infer_schema(self, input: dict[str, Schema]) -> dict[str, Schema]:
        """ unified static schema inference entry point """
        try:
            # 1. validate input schema against port definitions
            self._validate_schem_to_port_def(input)
            # 2. infer output schema
            return self.infer_output_schema(input)
        except Exception as e:
            raise NodeValidationError(f"Error inferring schema for node {self.id} ({self.name}): {e}") from e
    
    """ Stage3: validate during execution """
    def execute(self, input: dict[str, Data]) -> dict[str, Data]:
        """ unified execution entry point """
        try:
            # 1. static validate input schema against port definitions
            self._validate_schem_to_port_def({k: v.sche for k, v in input.items()})
            # 2. dynamic validate input data
            self.validate_input(input)
            # 3. process input data
            return self.process(input)
        except Exception as e:
            raise NodeExecutionError(f"Error executing node {self.id} ({self.name}): {e}") from e
    
    def visualization(self) -> Visualization:
        """ return visualization info for front-end to render """
        if self.vis is None:
            raise NodeExecutionError(f"Node {self.id} ({self.name}) has no visualization info.")
        return self.vis
