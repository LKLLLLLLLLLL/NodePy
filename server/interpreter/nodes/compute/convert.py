import math
from typing import Any, Literal, override

from pydantic import PrivateAttr

from server.models.data import Data, Table
from server.models.exception import (
    NodeExecutionError,
    NodeParameterError,
)
from server.models.schema import Pattern, Schema, check_no_illegal_cols, generate_default_col_name
from server.models.types import ColType

from ..base_node import BaseNode, InPort, OutPort, register_node

"""
This file defines nodes for converting data types.
"""

@register_node()
class ToStringNode(BaseNode):
    """
    Convert input data to string type.
    """

    @override
    def validate_parameters(self) -> None:
        if not self.type == "ToStringNode":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="type",
                err_msg="Type must be 'ToStringNode'",
            )
        return

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [
            InPort(
                name='input',
                description='Input data to be converted to string type.',
                optional=False,
                accept=Pattern(
                    types={Schema.Type.BOOL, Schema.Type.INT, Schema.Type.FLOAT}
                )
            )
        ], [
            OutPort(
                name="output",
                description="Output data converted to string type.",
            )
        ]

    @override
    def infer_output_schemas(self, input_schemas: dict[str, Schema]) -> dict[str, Schema]:
        return {'output': Schema(type=Schema.Type.STR)}

    @override
    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        assert 'input' in input
        input_data = input['input'].payload
        assert isinstance(input_data, (bool, int, float))

        output: str
        output = str(input_data)
        return {'output': Data(payload=output)}

@register_node()
class ToIntNode(BaseNode):
    """
    Convert input data to integer type. Inputs of type float will be rounded down.
    """
    method: Literal['FLOOR', 'CEIL', 'ROUND']

    @override
    def validate_parameters(self) -> None:
        if not self.type == "ToIntNode":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="type",
                err_msg="Type must be 'ToIntNode'",
            )
        return

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [
            InPort(
                name="input",
                description="Input data to be converted to integer type.",
                optional=False,
                accept=Pattern(
                    types={Schema.Type.BOOL, Schema.Type.FLOAT, Schema.Type.STR}
                )
            )
        ], [
            OutPort(
                name='output',
                description='Output data converted to integer type.',
            )
        ]

    @override
    def infer_output_schemas(self, input_schemas: dict[str, Schema]) -> dict[str, Schema]:
        return {'output': Schema(type=Schema.Type.INT)}

    @override
    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        assert 'input' in input
        input_data = input['input'].payload
        assert isinstance(input_data, (bool, float, str))

        def float_to_int(val: float) -> int:
            if self.method == 'FLOOR':
                return math.floor(val)
            elif self.method == 'CEIL':
                return math.ceil(val)
            elif self.method == 'ROUND':
                return round(val)
            else:
                raise NodeExecutionError(
                    node_id=self.id,
                    err_msg=f"Invalid method '{self.method}' for ToIntNode."
                )

        output: int
        if isinstance(input_data, bool):
            output = int(input_data)
        elif isinstance(input_data, float):
            output = float_to_int(input_data)
        elif isinstance(input_data, str):
            try:
                output = int(input_data)
            except ValueError:
                try:
                    float_val = float(input_data)
                    output = float_to_int(float_val)
                except ValueError:
                    raise NodeExecutionError(
                        node_id=self.id,
                        err_msg=f"Cannot convert string '{input_data}' to integer."
                    )
        else:
            raise NodeExecutionError(
                node_id=self.id,
                err_msg=f"Unsupported input type '{type(input_data)}' for ToIntNode."
            )
        return {'output': Data(payload=output)}

@register_node()
class ToFloatNode(BaseNode):
    """
    Convert input data to float type.
    """
    
    @override
    def validate_parameters(self) -> None:
        if not self.type == "ToFloatNode":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="type",
                err_msg="Type must be 'ToFloatNode'",
            )
        return

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [
            InPort(
                name="input",
                description="Input data to be converted to float type.",
                optional=False,
                accept=Pattern(
                    types={Schema.Type.BOOL, Schema.Type.INT, Schema.Type.STR}
                )
            )
        ], [
            OutPort(
                name='output',
                description='Output data converted to float type.',
            )
        ]

    @override
    def infer_output_schemas(self, input_schemas: dict[str, Schema]) -> dict[str, Schema]:
        return {'output': Schema(type=Schema.Type.FLOAT)}

    @override
    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        assert 'input' in input
        input_data = input['input'].payload
        assert isinstance(input_data, (bool, int, str))

        output: float
        if isinstance(input_data, bool):
            output = float(input_data)
        elif isinstance(input_data, int):
            output = float(input_data)
        elif isinstance(input_data, str):
            try:
                output = float(input_data)
            except ValueError:
                raise NodeExecutionError(
                    node_id=self.id,
                    err_msg=f"Cannot convert string '{input_data}' to float."
                )
        else:
            raise NodeExecutionError(
                node_id=self.id,
                err_msg=f"Unsupported input type '{type(input_data)}' for ToFloatNode."
            )
        return {'output': Data(payload=output)}

@register_node()
class ToBoolNode(BaseNode):
    """
    Convert input data to boolean type.
    """
    
    @override
    def validate_parameters(self) -> None:
        if not self.type == "ToBoolNode":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="type",
                err_msg="Type must be 'ToBoolNode'",
            )
        return

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [
            InPort(
                name="input",
                description="Input data to be converted to boolean type.",
                optional=False,
                accept=Pattern(
                    types={Schema.Type.INT, Schema.Type.FLOAT, Schema.Type.STR}
                )
            )
        ], [
            OutPort(
                name='output',
                description='Output data converted to boolean type.',
            )
        ]

    @override
    def infer_output_schemas(self, input_schemas: dict[str, Schema]) -> dict[str, Schema]:
        return {'output': Schema(type=Schema.Type.BOOL)}

    @override
    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        assert 'input' in input
        input_data = input['input'].payload
        assert isinstance(input_data, (int, float, str))

        output: bool
        if isinstance(input_data, int):
            output = bool(input_data)
        elif isinstance(input_data, float):
            output = bool(input_data)
        elif isinstance(input_data, str):
            lowered = input_data.strip().lower()
            if lowered in {'true', '1', 'yes'}:
                output = True
            elif lowered in {'false', '0', 'no'}:
                output = False
            else:
                raise NodeExecutionError(
                    node_id=self.id,
                    err_msg=f"Cannot convert string '{input_data}' to boolean."
                )
        else:
            raise NodeExecutionError(
                node_id=self.id,
                err_msg=f"Unsupported input type '{type(input_data)}' for ToBoolNode."
            )
        return {'output': Data(payload=output)}

@register_node()
class ColToStringNode(BaseNode):
    """
    Convert input column data to string type.
    """
    col: str
    result_col: str | None = None

    _col_types: dict[str, ColType] | None = PrivateAttr(default=None)
    @override
    def validate_parameters(self) -> None:
        if not self.type == "ColToStringNode":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="type",
                err_msg="Type must be 'ColToStringNode'",
            )
        if self.col.strip() == "":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="col",
                err_msg="Column name 'col' must be a non-empty string.",
            )
        if self.result_col is None or self.result_col.strip() == "":
            self.result_col = generate_default_col_name(self.id, "to_string")
        if self.result_col == self.col:
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="result_col",
                err_msg="Result column name 'result_col' must be different from input column name 'col'.",
            )
        if not check_no_illegal_cols([self.result_col]):
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="result_col",
                err_msg=f"Result column name '{self.result_col}' contains illegal characters.",
            )
        return

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [
            InPort(
                name="table",
                description="Input column data to be converted to string type.",
                optional=False,
                accept=Pattern(
                    types={Schema.Type.TABLE},
                    table_columns={
                        self.col: {ColType.BOOL, ColType.INT, ColType.FLOAT}
                    }
                )
            )
        ], [
            OutPort(
                name='table',
                description='Output column data converted to string type.',
            )
        ]
    
    @override
    def infer_output_schemas(self, input_schemas: dict[str, Schema]) -> dict[str, Schema]:
        input_schema = input_schemas["table"]
        assert self.result_col is not None
        output_schema = input_schema.append_col(self.result_col, ColType.STR)
        
        assert output_schema.tab is not None
        self._col_types = output_schema.tab.col_types.copy()
        
        return {'table': output_schema}

    @override
    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        assert isinstance(input["table"].payload, Table)
        table: Table = input['table'].payload
        assert self.result_col is not None
        assert self._col_types is not None

        df = table.df.copy()
        series = df[self.col]
        df[self.result_col] = series.astype(str)

        new_table = Table(df=df, col_types=self._col_types)
        return {'table': Data(payload=new_table)}

    @override
    @classmethod
    def hint(cls, input_schemas: dict[str, Schema], current_params: dict) -> dict[str, Any]:
        hint = {}
        if 'table' in input_schemas:
            table_schema = input_schemas['table']
            if table_schema.tab is not None:
                for col, col_type in table_schema.tab.col_types.items():
                    if col_type in {ColType.BOOL, ColType.INT, ColType.FLOAT}:
                        hint.setdefault('col_choices', []).append(col)
        return hint

@register_node()
class ColToIntNode(BaseNode):
    """
    Convert input column data to integer type. Float values will be rounded down.
    """
    col: str
    result_col: str | None = None
    method: Literal['FLOOR', 'CEIL', 'ROUND']

    _col_types: dict[str, ColType] | None = PrivateAttr(default=None)
    @override
    def validate_parameters(self) -> None:
        if not self.type == "ColToIntNode":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="type",
                err_msg="Type must be 'ColToIntNode'",
            )
        if self.col.strip() == "":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="col",
                err_msg="Column name 'col' must be a non-empty string.",
            )
        if self.result_col is None or self.result_col.strip() == "":
            self.result_col = generate_default_col_name(self.id, "to_int")
        if self.result_col == self.col:
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="result_col",
                err_msg="Result column name 'result_col' must be different from input column name 'col'.",
            )
        if not check_no_illegal_cols([self.result_col]):
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="result_col",
                err_msg=f"Result column name '{self.result_col}' contains illegal characters.",
            )
        return
    
    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [
            InPort(
                name="table",
                description="Input column data to be converted to integer type.",
                optional=False,
                accept=Pattern(
                    types={Schema.Type.TABLE},
                    table_columns={
                        self.col: {ColType.BOOL, ColType.FLOAT, ColType.STR}
                    }
                )
            )
        ], [
            OutPort(
                name='table',
                description='Output column data converted to integer type.',
            )
        ]
    
    @override
    def infer_output_schemas(self, input_schemas: dict[str, Schema]) -> dict[str, Schema]:
        input_schema = input_schemas["table"]
        assert self.result_col is not None
        output_schema = input_schema.append_col(self.result_col, ColType.INT)
        
        assert output_schema.tab is not None
        self._col_types = output_schema.tab.col_types.copy()
        
        return {'table': output_schema}

    @override
    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        assert isinstance(input["table"].payload, Table)
        table: Table = input['table'].payload
        assert self.result_col is not None
        assert self._col_types is not None

        def float_to_int(val: float) -> int:
            if self.method == 'FLOOR':
                return math.floor(val)
            elif self.method == 'CEIL':
                return math.ceil(val)
            elif self.method == 'ROUND':
                return round(val)
            else:
                raise NodeExecutionError(
                    node_id=self.id,
                    err_msg=f"Invalid method '{self.method}' for ColToIntNode."
                )

        df = table.df.copy()
        series = df[self.col]

        def convert_value(val: Any) -> int:
            if isinstance(val, bool):
                return int(val)
            elif isinstance(val, float):
                return float_to_int(val)
            elif isinstance(val, str):
                try:
                    return int(val)
                except ValueError:
                    try:
                        float_val = float(val)
                        return float_to_int(float_val)
                    except ValueError:
                        raise NodeExecutionError(
                            node_id=self.id,
                            err_msg=f"Cannot convert string '{val}' to integer."
                        )
            else:
                raise NodeExecutionError(
                    node_id=self.id,
                    err_msg=f"Unsupported input type '{type(val)}' for ColToIntNode."
                )

        df[self.result_col] = series.apply(convert_value)

        new_table = Table(df=df, col_types=self._col_types)
        return {'table': Data(payload=new_table)}

    @override
    @classmethod
    def hint(cls, input_schemas: dict[str, Schema], current_params: dict) -> dict[str, Any]:
        hint = {}
        if 'table' in input_schemas:
            table_schema = input_schemas['table']
            if table_schema.tab is not None:
                for col, col_type in table_schema.tab.col_types.items():
                    if col_type in {ColType.BOOL, ColType.FLOAT, ColType.STR}:
                        hint.setdefault('col_choices', []).append(col)
        return hint

