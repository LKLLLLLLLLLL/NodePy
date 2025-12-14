import decimal
import fractions
import itertools
import json
import math
import os
import re
import typing
from typing import Any, Literal, override

from server.lib.utils import timeout
from server.models.data import Data
from server.models.exception import (
    NodeExecutionError,
    NodeParameterError,
)
from server.models.schema import Pattern, Schema

from ..base_node import BaseNode, InPort, OutPort, register_node

AllowedTypes = Literal["str", "int", "float", "bool", "Datetime"]

_TEMPLATE_CACHE = None

@register_node()
class CustomScriptNode(BaseNode):
    """
    This node allows users to define custom Script using Python code.
    The function should take inputs as defined in the input ports and return outputs as defined in the output ports.
    """

    input_ports: dict[str, AllowedTypes]  # port_name -> type
    output_ports: dict[str, AllowedTypes]  # port_name -> type
    script: str  # The user-defined Python script

    @override
    def validate_parameters(self) -> None:
        if not self.type == "CustomScriptNode":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="type",
                err_msg="Type must be 'CustomScriptNode'",
            )
        return

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        in_ports = []
        for name, type_str in self.input_ports.items():
            schema_type = Schema.Type[type_str]
            in_ports.append(
                InPort(
                    name=name,
                    description=f"Input port of type {type_str}",
                    optional=False,
                    accept=Pattern(types={schema_type})
                )
            )
        out_ports = []
        for name, type_str in self.output_ports.items():
            out_ports.append(
                OutPort(
                    name=name,
                    description=f"Output port of type {type_str}",
                )
            )
        return in_ports, out_ports

    @override
    def infer_output_schemas(self, input_schemas: dict[str, Schema]) -> dict[str, Schema]:
        output_schemas = {}
        for name, type_str in self.output_ports:
            schema_type = Schema.Type[type_str]
            output_schemas[name] = Schema(type=schema_type)
        return output_schemas

    @override
    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        import RestrictedPython
        
        kwargs = {name: data.payload for name, data in input.items()}
        # Execute the user-defined script
        try:
            byte_code = RestrictedPython.compile_restricted(
                self.script,
                filename='<inline>',
                mode='exec'
            )
            safe_globals = {
                "__builtins__": RestrictedPython.safe_builtins,
                "_getiter_": iter,
                "_print_": RestrictedPython.PrintCollector,
                "math": math,
                "typing": typing,
                "re": re,
                "json": json,
                "decimal": decimal,
                "fractions": fractions,
                "itertools": itertools,
            }
            local_env = {}
            
            @timeout(5)
            def wrap_exec(code, globals_dict, locals_dict):
                exec(code, globals_dict, locals_dict)

            success, _ = wrap_exec(byte_code, safe_globals, local_env)
            if not success:
                raise NodeExecutionError(
                    node_id=self.id,
                    err_msg="Custom script execution timed out"
                )

            # Call the script function
            if 'script' not in local_env:
                raise NodeExecutionError(
                    node_id=self.id,
                    err_msg="Function 'script' not defined in custom script"
                )
            
            result = local_env['script'](**kwargs)
            
            if not isinstance(result, dict):
                raise NodeExecutionError(
                    node_id=self.id,
                    err_msg=f"Script function must return a dict, got {type(result)}"
                )
                
        except Exception as e:
            raise NodeExecutionError(
                node_id=self.id,
                err_msg=f"Error executing custom script: {str(e)}"
            )

        # Collect outputs
        output_data = {}
        for name, type_str in self.output_ports:
            if name not in local_env:
                raise NodeExecutionError(
                    node_id=self.id,
                    err_msg=f"Output '{name}' not defined in script"
                )
            output_payload = local_env[name]
            output_data[name] = Data(payload=output_payload)

        return output_data

    @classmethod
    @override
    def hint(cls, input_schemas: dict[str, Schema], current_params: dict) -> dict[str, Any]:
        global _TEMPLATE_CACHE
        template_str: str = ""
        if _TEMPLATE_CACHE is None:
            base_path = os.path.dirname(__file__)
            with open(os.path.join(base_path, "_script_template.py")) as f:
                template_str = f.read()
            _TEMPLATE_CACHE = template_str
        else:
            template_str = _TEMPLATE_CACHE
        hint = {
            "script_template": template_str,
        }
        return hint
