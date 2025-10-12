from pydantic import BaseModel, model_validator
from typing_extensions import Self
from enum import Enum
from abc import abstractmethod
from pandas import DataFrame
from typing import Literal

"""
Errors definitions
"""
class NodeValidationError(Exception): 
    """ static validation error"""
    pass

class NodeExecutionError(Exception):
    """ runtime execution error """
    pass


"""
static analyze
"""

class Schema(BaseModel):
    """ schema defined the data type between nodes """
    
    class DataType(str, Enum):
        """ data type of object passed between nodes """
        TABLE = "table" # dataframe
        STR = "str"   # string
        INT = "int"   # integer
    
    type: DataType
    columns: list[str] | None = None  # for TABLE type, list of column names
    
    @model_validator(mode='after')
    def verify(self) -> Self:
        if self.type == Schema.DataType.TABLE and self.columns is None:
            raise NodeValidationError("For TABLE type, columns must be specified.")
        elif self.type != Schema.DataType.TABLE and self.columns is not None:
            raise NodeValidationError("For non-TABLE type, columns must be None.")
        return self
    
    def include(self, other: "Schema") -> bool:
        """ check if self includes other schema """
        if self.type != other.type:
            return False
        if self.type == Schema.DataType.TABLE:
            if self.columns is None or other.columns is None:
                return False
            return all(col in self.columns for col in other.columns)
        return True


class Data(BaseModel):
    """ the data wrapper """
    schem: Schema
    payload: DataFrame | str | int
    
    model_config = {"arbitrary_types_allowed": True} # allow DataFrame type
    
    @model_validator(mode='after')
    def verify(self) -> Self:
        if self.schem.type == Schema.DataType.TABLE:
            if not isinstance(self.payload, DataFrame):
                raise NodeExecutionError("Payload must be a DataFrame for TABLE schema.")
            if self.schem.columns is not None:
                missing_cols = [col for col in self.schem.columns if col not in self.payload.columns]
                if missing_cols:
                    raise NodeExecutionError(f"Payload is missing columns: {missing_cols}")
        elif self.schem.type == Schema.DataType.STR:
            if not isinstance(self.payload, str):
                raise NodeExecutionError("Payload must be a string for STR schema.")
        elif self.schem.type == Schema.DataType.INT:
            if not isinstance(self.payload, int):
                raise NodeExecutionError("Payload must be an integer for INT schema.")
        else:
            raise NodeExecutionError(f"Unsupported schema type: {self.schem.type}")
        return self
  
class InPort(BaseModel):
    name: str
    schem: Schema
    description: str | None = None
    required: bool

class OutPort(BaseModel):
    name: str
    description: str | None = None

"""
BaseNode definition
"""
class BaseNode(BaseModel):
    id: str
    name: str
    type: str


    """
    methods to be implemented by subclasses
    """
    
    @abstractmethod
    def validate_parameters(self) -> None:
        """ validate parameters when constructing the node """
        pass
    
    @abstractmethod
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        """ define input and output port constraint """
        pass

    @abstractmethod
    def validate_input(self, input: dict[str, Data]) -> None:
        """validate input during processing stage"""
        pass
    
    @abstractmethod
    def infer_output_schema(self, input_schema: dict[str, Schema]) -> dict[str, Schema]:
        """ infer output schema based on input schema during static analysis stage """
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
            if not port.schem.include(real_schema):
                raise NodeValidationError(f"Port '{port.name}' schema mismatch. Expected: {port.schem}, Got: {real_schema}")
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

    def infer_schema(self, input: dict[str, Schema]) -> dict[str, Schema]:
        """ unified static schema inference entry point """
        try:
            # 1. validate input schema against port definitions
            self._validate_schem_to_port_def(input)
            # 2. infer output schema
            return self.infer_output_schema(input)
        except Exception as e:
            raise NodeValidationError(f"Error inferring schema for node {self.id} ({self.name}): {str(e)}")
    
    def execute(self, input: dict[str, Data]) -> dict[str, Data]:
        """ unified execution entry point """
        try:
            # 1. static validate input schema against port definitions
            self._validate_schem_to_port_def({k: v.schem for k, v in input.items()})
            # 2. dynamic validate input data
            self.validate_input(input)
            # 3. process input data
            return self.process(input)
        except Exception as e:
            raise NodeExecutionError(f"Error executing node {self.id} ({self.name}): {str(e)}")
