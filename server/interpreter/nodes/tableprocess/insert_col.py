from typing import Dict, Literal, override

from server.models.data import Data, Table
from server.models.exception import (
    NodeExecutionError,
    NodeParameterError,
    NodeValidationError,
)
from server.models.schema import (
    ColType,
    Pattern,
    Schema,
    check_no_illegal_cols,
)

from ..base_node import BaseNode, InPort, OutPort, register_node

"""
This file defines nodes for inserting columns into tables.
"""
@register_node
class InsertConstColNode(BaseNode):
    """
    Insert a constant value column into the input table.
    """
    
    col_name: str
    col_type: ColType

    @override
    def validate_parameters(self) -> None:
        if not self.type == "InsertConstColNode":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="col_type",
                err_msg="Node type and col_type parameter mismatch.",
            )
        if not check_no_illegal_cols([self.col_name]):
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="col_name",
                err_msg="Column name contains illegal characters.",
            )
        return

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [
            InPort(
                name="table",
                description="Input table to insert the new column into.",
                accept=Pattern(
                    types={Schema.Type.TABLE},
                    table_columns={}  # accept any table schema
                )
            ),
            InPort(
                name="const_value",
                description="Constant value to insert into the new column. If not provided, the parameter const_value will be used.",
                optional=False,
                accept=Pattern(
                    types={Schema.Type.BOOL, Schema.Type.INT, Schema.Type.FLOAT, Schema.Type.STR, Schema.Type.DATETIME}
                )
            )
        ], [
            OutPort(
                name="table",
                description="Output table with the new constant column inserted.",
            )
        ]

    @override
    def infer_output_schemas(self, input_schemas: Dict[str, Schema]) -> Dict[str, Schema]:
        const_value_schema = input_schemas["const_value"]
        if const_value_schema.type != self.col_type:
            raise NodeValidationError(
                node_id=self.id,
                err_input="const_value",
                err_msg="Input const_value schema type does not match specified col_type.",
            )
        input_table_schema = input_schemas["table"]
        return {
            "table": input_table_schema.append_col(self.col_name, self.col_type)
        }

    @override
    def process(self, input: Dict[str, Data]) -> Dict[str, Data]:
        import pandas
        
        input_table_data = input["table"]
        input_table = input_table_data.payload
        assert isinstance(input_table, Table)

        const_value_data = input["const_value"]
        const_value = const_value_data.payload

        # create a Series with the constant value
        num_rows = len(input_table.df)
        const_series = pandas.Series([const_value] * num_rows)

        # append the new column to the table
        new_table = input_table._append_col(self.col_name, const_series)

        return {
            "table": Data(payload=new_table)
        }

@register_node
class InsertRangeColNode(BaseNode):
    """
    Insert a range of values as a new column into the input table. No need to specify the end, it will be inferred from the table length.
    
    The range parameters can be specified by inputs.
    """
    
    col_name: str
    col_type: Literal["int", "float", "datetime"]

    @override
    def validate_parameters(self) -> None:
        if not self.type == "InsertRangeColNode":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="col_type",
                err_msg="Node type and col_type parameter mismatch.",
            )
        if not check_no_illegal_cols([self.col_name]):
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="col_name",
                err_msg="Column name contains illegal characters.",
            )
        return

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [
            InPort(
                name="table",
                description="Input table to insert the new column into.",
                accept=Pattern(
                    types={Schema.Type.TABLE},
                    table_columns={}  # accept any table schema
                )
            ),
            InPort(
                name="start",
                description="Start value of the range. If not provided, the parameter start will be used.",
                accept=Pattern(
                    types={Schema.Type.INT, Schema.Type.FLOAT, Schema.Type.DATETIME}
                )
            ),
            InPort(
                name="step",
                description="Optional step value of the range. If not provided, the parameter step will be used. If step is not provided, defaults to 1 for int/float and 1 day for datetime.",
                optional=True,
                accept=Pattern(
                    types={Schema.Type.INT, Schema.Type.FLOAT, Schema.Type.DATETIME}
                )
            )
        ], [
            OutPort(
                name="table",
                description="Output table with the new range column inserted.",
            )
        ]

    @override
    def infer_output_schemas(self, input_schemas: Dict[str, Schema]) -> Dict[str, Schema]:
        start_schema = input_schemas["start"]
        if start_schema.type != self.col_type:
            raise NodeValidationError(
                node_id=self.id,
                err_input="start",
                err_msg="Input start schema type does not match specified col_type.",
            )
        step_schema = input_schemas["step"]
        if step_schema.type != self.col_type:
            raise NodeValidationError(
                node_id=self.id,
                err_input="step",
                err_msg="Input step schema type does not match specified col_type.",
            )
        input_table_schema = input_schemas["table"]
        return {
            "table": input_table_schema.append_col(self.col_name, ColType(self.col_type))
        }

    @override
    def process(self, input: Dict[str, Data]) -> Dict[str, Data]:
        import pandas
        
        input_table_data = input["table"]
        input_table = input_table_data.payload
        assert isinstance(input_table, Table)

        start_data = input["start"]
        start = start_data.payload

        if "step" in input:
            step_data = input["step"]
            step = step_data.payload
        else:
            step = None

        assert start is not None

        num_rows = len(input_table.df)
        data_rows = []
        if self.col_type == "int":
            assert isinstance(start, int)
            if step is None:
                step = 1
            assert isinstance(step, int)
            current = start
            for _ in range(num_rows):
                data_rows.append(current)
                current += step
        elif self.col_type == "float":
            assert isinstance(start, float)
            if step is None:
                step = 1.0
            assert isinstance(step, float)
            current = start
            for _ in range(num_rows):
                data_rows.append(current)
                current += step
        elif self.col_type == "datetime":
            assert isinstance(start, pandas.Timestamp)
            if step is None:
                step = pandas.Timedelta(1, "D")
            assert isinstance(step, pandas.Timedelta)
            current = start
            for _ in range(num_rows):
                data_rows.append(current)
                current += step
        else:
            raise NodeExecutionError(
                node_id=self.id,
                err_msg="Unsupported col_type for InsertRangeColNode.",
            )

        range_series = pandas.Series(data_rows)

        new_table = input_table._append_col(self.col_name, range_series)

        return {
            "table": Data(payload=new_table)
        }

@register_node
class InsertRandomColNode(BaseNode):
    """
    Insert a column with random values into the input table.
    The random values are generated uniformly between min_value and max_value.
    """
    
    col_name: str
    col_type: Literal["int", "float"]

    @override
    def validate_parameters(self) -> None:
        if not self.type == "InsertRandomColNode":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="col_type",
                err_msg="Node type and col_type parameter mismatch.",
            )
        if not check_no_illegal_cols([self.col_name]):
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="col_name",
                err_msg="Column name contains illegal characters.",
            )
        return

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [
            InPort(
                name="table",
                description="Input table to insert the new column into.",
                accept=Pattern(
                    types={Schema.Type.TABLE},
                    table_columns={}  # accept any table schema
                )
            ),
            InPort(
                name="min_value",
                description="Minimum value for random generation. If not provided, the parameter min_value will be used.",
                accept=Pattern(
                    types={Schema.Type.INT, Schema.Type.FLOAT}
                )
            ),
            InPort(
                name="max_value",
                description="Maximum value for random generation. If not provided, the parameter max_value will be used.",
                accept=Pattern(
                    types={Schema.Type.INT, Schema.Type.FLOAT}
                )
            )
        ], [
            OutPort(
                name="table",
                description="Output table with the new random column inserted.",
            )
        ]

    @override
    def infer_output_schemas(self, input_schemas: Dict[str, Schema]) -> Dict[str, Schema]:
        min_value_schema = input_schemas["min_value"]
        if min_value_schema.type != self.col_type:
            raise NodeValidationError(
                node_id=self.id,
                err_input="min_value",
                err_msg="Input min_value schema type does not match specified col_type.",
            )
        max_value_schema = input_schemas["max_value"]
        if max_value_schema.type != self.col_type:
            raise NodeValidationError(
                node_id=self.id,
                err_input="max_value",
                err_msg="Input max_value schema type does not match specified col_type.",
            )
        input_table_schema = input_schemas["table"]
        return {
            "table": input_table_schema.append_col(self.col_name, ColType(self.col_type))
        }

    @override
    def process(self, input: Dict[str, Data]) -> Dict[str, Data]:   
        import numpy as np
        import pandas
        
        input_table_data = input["table"]
        input_table = input_table_data.payload
        assert isinstance(input_table, Table)

        min_value_data = input["min_value"]
        min_value = min_value_data.payload
        assert min_value is not None

        max_value_data = input["max_value"]
        max_value = max_value_data.payload
        assert max_value is not None

        num_rows = len(input_table.df)
        if self.col_type == "int":
            assert isinstance(min_value, int)
            assert isinstance(max_value, int)
            data_rows = pandas.Series(
                np.random.randint(min_value, max_value + 1, size=num_rows)
            )
        elif self.col_type == "float":
            assert isinstance(min_value, float)
            assert isinstance(max_value, float)
            data_rows = pandas.Series(
                np.random.uniform(min_value, max_value, size=num_rows)
            )
        else:
            raise NodeExecutionError(
                node_id=self.id,
                err_msg="Unsupported col_type for InsertRandomColNode.",
            )

        new_table = input_table._append_col(self.col_name, data_rows)

        return {
            "table": Data(payload=new_table)
        }
