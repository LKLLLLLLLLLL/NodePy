import random
from io import StringIO
from typing import Dict, List, Literal, override

import pandas
from pandas import DataFrame
from pydantic import PrivateAttr

from server.models.data import Data, File
from server.models.exception import (
    NodeExecutionError,
    NodeParameterError,
    NodeValidationError,
)
from server.models.schema import (
    ColType,
    Pattern,
    Schema,
    TableSchema,
    check_no_illegal_cols,
)

from ..base_node import BaseNode, InPort, OutPort, register_node

"""
A series of node that generates a table.
Such as generate by user input, generate by range, generate by random, etc.
"""

@register_node
class TableNode(BaseNode):
    """
    A node to generate a table from user provided data.
    Notice: if providing column_names but not providing rows, will throw error, because cannot infer column types.
    
    Parameters (provided at construction time):
      - rows: list[dict[column_name -> value]]
      - column_names: optional list[str] to enforce column order/selection
    """

    rows: List[Dict[str, str | int | float | bool]]
    col_names: List[str]
    _col_types: Dict[str, ColType] | None = PrivateAttr(None)  # cache for column types

    @override
    def validate_parameters(self) -> None:
        if not self.type == "TableNode":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="type",
                err_msg="Node type must be 'TableNode'."
            )
        if len(self.col_names) != 0:
            if len(self.rows) == 0:
                raise NodeParameterError(
                    node_id=self.id,
                    err_param_key="rows",
                    err_msg="Rows cannot be empty. Else cannot refer types of columns."
                )
        # check all rows key equals col_names (compare as list to avoid dict_keys mismatch)
        for row in self.rows:
            if list(row.keys()) != list(self.col_names):
                raise NodeParameterError(
                    node_id=self.id,
                    err_param_key="rows",
                    err_msg=f"All rows must have the same keys as col_names. But got row keys: {list(row.keys())}"
                )
        # check no illegal column names
        if not check_no_illegal_cols(self.col_names):
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="col_names",
                err_msg="Column names contain illegal names (e.g., reserved keywords)."
            )
        # check if all columns has same type
        if len(self.rows) > 0:
            col_types: Dict[str, ColType] = {}
            # traverse first row to initialize types
            first_row = self.rows[0]
            for col in self.col_names:
                val = first_row[col]
                if isinstance(val, str):
                    col_types[col] = ColType.STR
                elif isinstance(val, bool):
                    col_types[col] = ColType.BOOL
                elif isinstance(val, int):
                    col_types[col] = ColType.INT
                elif isinstance(val, float):
                    col_types[col] = ColType.FLOAT
                else:
                    raise NodeParameterError(
                        node_id=self.id,
                        err_param_key="rows",
                        err_msg=f"Unsupported value type {type(val)} in column '{col}'."
                    )
            self._col_types = col_types
            # traverse other rows to check types
            for row in self.rows[1:]:
                for col in self.col_names:
                    val = row[col]
                    if isinstance(val, str):
                        if col_types[col] != ColType.STR:
                            raise NodeParameterError(
                                node_id=self.id,
                                err_param_key="rows",
                                err_msg=f"Column '{col}' has mixed types: {col_types[col]} and STR."
                            )
                    elif isinstance(val, bool):
                        if col_types[col] != ColType.BOOL:
                            raise NodeParameterError(
                                node_id=self.id,
                                err_param_key="rows",
                                err_msg=f"Column '{col}' has mixed types: {col_types[col]} and BOOL."
                            )
                    elif isinstance(val, int):
                        if col_types[col] == ColType.FLOAT:
                            raise NodeParameterError(
                                node_id=self.id,
                                err_param_key="rows",
                                err_msg=f"Column '{col}' has mixed types: FLOAT and INT."
                            )
                        col_types[col] = ColType.INT # INT can be promoted to FLOAT
                    elif isinstance(val, float):
                        col_types[col] = ColType.FLOAT # promote to FLOAT
                    else:
                        raise NodeParameterError(
                            node_id=self.id,
                            err_param_key="rows",
                            err_msg=f"Unsupported value type {type(val)} in column '{col}'."
                        )
        assert self._col_types is not None
        return

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [], [
            OutPort(name="table", description="The generated table.")
        ]

    @override
    def infer_output_schemas(self, input_schemas: Dict[str, Schema]) -> Dict[str, Schema]:
        assert self._col_types is not None
        return {
            "table": Schema(type=Schema.Type.TABLE, tab=TableSchema(col_types=self._col_types))
        }

    @override
    def process(self, input: Dict[str, Data]) -> Dict[str, Data]:
        assert self._col_types is not None
        df = DataFrame(self.rows, columns=self.col_names)
        out_table = Data.from_df(df)
        return {"table": out_table}

@register_node
class TableFromCSVNode(BaseNode):
    """
    A node to generate a table from a CSV file.
    """

    @override
    def validate_parameters(self) -> None:
        if not self.type == "TableFromCSVNode":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="type",
                err_msg="Node type must be 'TableFromCSVNode'."
            )
        return

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [
            InPort(
                name="csv_file",
                description="The input CSV file to generate table from.",
                accept=Pattern(
                    types={Schema.Type.FILE},
                    file_formats={"csv"}
                )
            )
            ], [
            OutPort(name="table", description="The generated table from CSV.")
        ]

    @override
    def infer_output_schemas(self, input_schemas: Dict[str, Schema]) -> Dict[str, Schema]:
        # To get actual schema, need to read CSV file during static analysis stage.
        file_schema = input_schemas["csv_file"].file
        assert file_schema is not None
        assert file_schema.col_types is not None
        return {
            "table": Schema(
                type=Schema.Type.TABLE,
                tab=TableSchema(
                    col_types=file_schema.col_types
                )
            )
        }

    @override
    def process(self, input: Dict[str, Data]) -> Dict[str, Data]:
        csv_file_data = input["csv_file"]
        assert isinstance(csv_file_data.payload, File)
        file_manager = self.global_config.file_manager
        user_id = self.global_config.user_id
        file_content = file_manager.read_sync(csv_file_data.payload, user_id=user_id)
        df = pandas.read_csv(StringIO(file_content.decode('utf-8')))
        out_table = Data.from_df(df)
        return {"table": out_table}

@register_node
class RandomNode(BaseNode):
    """
    Node to generate a table, with a random column of specified type and range.
    
    The row_count and min_value and max_value can be got from inputs.
    If col_type is "str" or "bool", min_value and max_value must be None
    """
    col_name: str
    col_type: Literal["float", "int", "str", "bool"]
    
    @override
    def validate_parameters(self) -> None:
        if not self.type == "RandomNode":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="type",
                err_msg="Node type must be 'RandomNode'."
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
                name="row_count",
                description="Input to specify number of rows to generate.",
                accept=Pattern(
                    types={Schema.Type.INT}
                )
            ),
            InPort(
                name="min_value",
                description="Optional input to specify minimum value for numeric columns.",
                optional=True,
                accept=Pattern(
                    types={Schema.Type.FLOAT, Schema.Type.INT}
                )
            ),
            InPort(
                name="max_value",
                description="Optional input to specify maximum value for numeric columns.",
                optional=True,
                accept=Pattern(
                    types={Schema.Type.FLOAT, Schema.Type.INT}
                )
            )
        ], [
            OutPort(name="table", description="The generated table with random column.")
        ]

    @override
    def infer_output_schemas(self, input_schemas: Dict[str, Schema]) -> Dict[str, Schema]:
        col_type_map = {
            "float": ColType.FLOAT,
            "int": ColType.INT,
            "str": ColType.STR,
            "bool": ColType.BOOL
        }
        # check if input min_value and max_value are compatible
        if self.col_type in ["float", "int"]:
            if input_schemas.get("min_value") is None:
                raise NodeValidationError(
                    node_id=self.id,
                    err_input="min_value",
                    err_msg="min_value must be provided for numeric col_type."
                )
            min_schema = input_schemas["min_value"]
            if not(
                (min_schema.type == Schema.Type.INT and self.col_type == "int") or 
                (min_schema.type == Schema.Type.FLOAT and self.col_type == "float")):
                raise NodeValidationError(
                    node_id=self.id,
                    err_input="min_value",
                    err_msg=f"min_value input type {min_schema.type} incompatible with col_type {self.col_type}."
                )
            if input_schemas.get("max_value") is None:
                raise NodeValidationError(
                    node_id=self.id,
                    err_input="max_value",
                    err_msg="max_value must be provided for numeric col_type."
                )
            max_schema = input_schemas["max_value"]
            if not(
                (max_schema.type == Schema.Type.INT and self.col_type == "int") or 
                (max_schema.type == Schema.Type.FLOAT and self.col_type == "float")):
                raise NodeValidationError(
                    node_id=self.id,
                    err_input="max_value",
                    err_msg=f"max_value input type {max_schema.type} incompatible with col_type {self.col_type}."
                )
        # check if row_count has been set
        if input_schemas.get("row_count") is None:
            raise NodeValidationError(
                node_id=self.id,
                err_input="row_count",
                err_msg="row_count must be provided as input."
            )
        return {
            "table": Schema(
                type=Schema.Type.TABLE,
                tab=TableSchema(
                    col_types={self.col_name: col_type_map[self.col_type]}
                )
            )
        }

    @override
    def process(self, input: Dict[str, Data]) -> Dict[str, Data]:
        min_value = input["min_value"].payload
        max_value = input["max_value"].payload
        row_count = input["row_count"].payload
        assert isinstance(row_count, int)

        data_rows = []
        for _ in range(row_count):
            if self.col_type == "float":
                assert isinstance(min_value, float)
                assert isinstance(max_value, float)
                if min_value is not None and max_value is not None:
                    val = random.uniform(min_value, max_value)
                elif min_value is not None:
                    val = random.uniform(min_value, min_value + 1000.0)
                elif max_value is not None:
                    val = random.uniform(max_value - 1000.0, max_value)
                else:
                    val = random.uniform(0.0, 1000.0)
            elif self.col_type == "int":
                assert isinstance(min_value, int)
                assert isinstance(max_value, int)
                if min_value is not None and max_value is not None:
                    val = random.randint(int(min_value), int(max_value) - 1)
                elif min_value is not None:
                    val = random.randint(int(min_value), int(min_value) + 1000)
                elif max_value is not None:
                    val = random.randint(int(max_value) - 1000, int(max_value) - 1)
                else:
                    val = random.randint(0, 1000)
            elif self.col_type == "str":
                val = ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=8))
            elif self.col_type == "bool":
                val = random.choice([True, False])
            else:
                raise NodeExecutionError(
                    node_id=self.id,
                    err_msg=f"Unsupported col_type: {self.col_type}."
                )
            data_rows.append({self.col_name: val})
        df = DataFrame(data_rows, columns=[self.col_name])
        out_table = Data.from_df(df)
        return {"table": out_table}

@register_node
class RangeNode(BaseNode):
    """
    Node to generate a table, with a range column of specified type and range.
    Parameters start, end, step can be specified by parameters or inputs.
    """
    col_name: str
    col_type: Literal["float", "int", "Datetime"]
    
    @override
    def validate_parameters(self) -> None:
        if not self.type == "RangeNode":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="type",
                err_msg="Node type must be 'RangeNode'."
            )
        if not check_no_illegal_cols([self.col_name]):
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="col_name",
                err_msg="Column name contains illegal names (e.g., reserved keywords)."
            )
        return

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [
            InPort(
                name="start",
                description="Input to specify start value of the range.",
                accept=Pattern(
                    types={Schema.Type.FLOAT, Schema.Type.INT, Schema.Type.DATETIME}
                )
            ),
            InPort(
                name="end",
                description="Input to specify end value of the range.",
                accept=Pattern(
                    types={Schema.Type.FLOAT, Schema.Type.INT, Schema.Type.DATETIME}
                )
            ),
            InPort(
                name="step",
                description="Optional input to specify step value of the range.",
                optional=True,
                accept=Pattern(
                    types={Schema.Type.FLOAT, Schema.Type.INT, Schema.Type.DATETIME}
                )
            )
        ], [
            OutPort(name="table", description="The generated table with range column.")
        ]

    @override
    def infer_output_schemas(self, input_schemas: Dict[str, Schema]) -> Dict[str, Schema]:
        col_type_map = {
            "float": ColType.FLOAT,
            "int": ColType.INT,
            "Datetime": ColType.DATETIME
        }
        # check if input start, end, step are compatible
        if self.col_type == "float":
            start_schema = input_schemas["start"]
            if start_schema.type != Schema.Type.FLOAT:
                raise NodeValidationError(
                    node_id=self.id,
                    err_input="start",
                    err_msg=f"start input type {start_schema.type} incompatible with col_type {self.col_type}."
                )
            end_schema = input_schemas["end"]
            if end_schema.type != Schema.Type.FLOAT:
                raise NodeValidationError(
                    node_id=self.id,
                    err_input="end",
                    err_msg=f"end input type {end_schema.type} incompatible with col_type {self.col_type}."
                )
            step_schema = input_schemas.get("step")
            if step_schema is not None:
                if step_schema.type != Schema.Type.FLOAT:
                    raise NodeValidationError(
                        node_id=self.id,
                        err_input="step",
                        err_msg=f"step input type {step_schema.type} incompatible with col_type {self.col_type}."
                    )
        elif self.col_type == "int":
            start_schema = input_schemas["start"]
            if start_schema.type != Schema.Type.INT:
                raise NodeValidationError(
                    node_id=self.id,
                    err_input="start",
                    err_msg=f"start input type {start_schema.type} incompatible with col_type {self.col_type}."
                )
            end_schema = input_schemas["end"]
            if end_schema.type != Schema.Type.INT:
                raise NodeValidationError(
                    node_id=self.id,
                    err_input="end",
                    err_msg=f"end input type {end_schema.type} incompatible with col_type {self.col_type}."
                )
            step_schema = input_schemas.get("step")
            if step_schema is not None:
                if step_schema.type != Schema.Type.INT:
                    raise NodeValidationError(
                        node_id=self.id,
                        err_input="step",
                        err_msg=f"step input type {step_schema.type} incompatible with col_type {self.col_type}."
                )
        elif self.col_type == "Datetime":
            start_schema = input_schemas["start"]
            if start_schema.type != Schema.Type.DATETIME:
                raise NodeValidationError(
                    node_id=self.id,
                    err_input="start",
                    err_msg=f"start input type {start_schema.type} incompatible with col_type {self.col_type}."
                )
            end_schema = input_schemas["end"]
            if end_schema.type != Schema.Type.DATETIME:
                raise NodeValidationError(
                    node_id=self.id,
                    err_input="end",
                    err_msg=f"end input type {end_schema.type} incompatible with col_type {self.col_type}."
                )
            step_schema = input_schemas.get("step")
            if step_schema is not None:
                if step_schema.type != Schema.Type.DATETIME:
                    raise NodeValidationError(
                        node_id=self.id,
                        err_input="step",
                        err_msg=f"step input type {step_schema.type} incompatible with col_type {self.col_type}."
                )
        return {
            "table": Schema(
                type=Schema.Type.TABLE,
                tab=TableSchema(
                    col_types={self.col_name: col_type_map[self.col_type]}
                )
            )
        }

    @override
    def process(self, input: Dict[str, Data]) -> Dict[str, Data]:
        start = input["start"].payload
        end = input["end"].payload
        if "step" in input:
            step = input["step"].payload
        else:
            step = None
        assert start is not None
        assert end is not None
        data_rows = []
        if self.col_type == "float":
            assert isinstance(start, float)
            assert isinstance(end, float)
            if step is None:
                step = 1.0
            assert isinstance(step, float)
            current = start
            while current < end:
                data_rows.append({self.col_name: current})
                current += step
        elif self.col_type == "int":
            assert isinstance(start, int)
            assert isinstance(end, int)
            if step is None:
                step = 1
            assert isinstance(step, int)
            current = start
            while current < end:
                data_rows.append({self.col_name: current})
                current += step
        elif self.col_type == "Datetime":
            assert isinstance(start, pandas.Timestamp)
            assert isinstance(end, pandas.Timestamp)
            if step is None:
                step = pandas.Timedelta(1, "D")
            assert isinstance(step, pandas.Timedelta)
            current = start
            while current < end:
                data_rows.append({self.col_name: current})
                current += step
        df = DataFrame(data_rows, columns=[self.col_name])
        out_table = Data.from_df(df)
        return {"table": out_table}
