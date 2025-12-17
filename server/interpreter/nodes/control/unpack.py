from copy import deepcopy
from typing import Any, Dict, override

from pandas import DataFrame
from pydantic import PrivateAttr

from server.models.data import Data, Table, TableSchema
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
    generate_default_col_name,
)

from ..base_node import BaseNode, InPort, OutPort, register_node


@register_node()
class UnpackNode(BaseNode):
    """
    A node to unpack a row into multiple columns of primitive values.
    """
    cols: list[str]

    @override
    def validate_parameters(self) -> None:
        if not self.type == "UnpackNode":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="type",
                err_msg="Node type parameter mismatch.",
            )
        if not self.cols:
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="cols",
                err_msg="At least one column to unpack must be specified.",
            )
        return

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        out_ports = [
            OutPort(
                name="unpacked_row",
                description="The unpacked row.",
            )
        ]
        for col in self.cols:
            out_ports.append(
                OutPort(
                    name=col,
                    description=f"Unpacked column '{col}'.",
                )
            )
        return [
            InPort(
                name="row",
                description="Input row to be unpacked.",
                accept=Pattern(
                    types={Schema.Type.TABLE},
                    table_columns={col: set() for col in self.cols},
                )
            )
        ], out_ports

    @override
    def infer_output_schemas(self, input_schemas: Dict[str, Schema]) -> Dict[str, Schema]:
        input_schema = input_schemas["row"]
        assert input_schema.tab is not None
        output_schemas: Dict[str, Schema] = {}
        output_schemas["unpacked_row"] = input_schema
        for col in self.cols:
            if col not in input_schema.tab.col_types:
                raise NodeValidationError(
                    node_id=self.id,
                    err_input="row",
                    err_msg=f"Column '{col}' does not exist in the input table.",
                )
            type_of_col = input_schema.tab.col_types[col]
            output_schemas[col] = Schema.from_coltype(type_of_col)

        return output_schemas

    @override
    def process(self, input: Dict[str, Data]) -> Dict[str, Data]:
        input_row = input["row"]
        assert isinstance(input_row.payload, Table)
        df = input_row.payload.df
        if len(df) != 1:
            raise NodeExecutionError(
                node_id=self.id,
                err_msg=f"Input row must contain exactly one row, got {len(df)} rows.",
            )
        output: Dict[str, Data] = {}
        output["unpacked_row"] = input_row
        for col in self.cols:
            if col not in df.columns:
                raise NodeExecutionError(
                    node_id=self.id,
                    err_msg=f"Column '{col}' does not exist in the input row.",
                )
            value = df.iloc[0][col]
            col_value = Data(payload=value)
            output[col] = col_value
        return output

    @override
    @classmethod
    def hint(cls, input_schemas: Dict[str, Schema], current_params: Dict) -> Dict[str, Any]:
        hint = {}
        if "cols" in current_params:
            outputs = ["unpacked_row"]
            outputs.extend(current_params["cols"])
            hint["outputs"] = outputs
            if "row" in input_schemas:
                col_choices = []
                if input_schemas["row"].tab is not None:
                    for col in input_schemas["row"].tab.col_types.keys():
                        col_choices.append(col)
                hint["cols_choices"] = col_choices
        return hint

@register_node()
class PackNode(BaseNode):
    """
    Pack multiple primitive values into a single row.
    If not specified column names, use default names.
    """
    cols: list[str | None]

    _col_types: Dict[str, ColType] | None = PrivateAttr(default=None)

    @override
    def validate_parameters(self) -> None:
        if not self.type == "PackNode":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="type",
                err_msg="Node type parameter mismatch.",
            )
        if not self.cols:
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="cols",
                err_msg="At least one column to pack must be specified.",
            )
        for index, col in enumerate(self.cols):
            if col is not None and not col.strip():
                self.cols[index] = None
            if col is None:
                self.cols[index] = generate_default_col_name(self.id, f"col{index+1}")
        assert all(isinstance(col, str) for col in self.cols)
        if check_no_illegal_cols(self.cols) is False: # type: ignore
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="cols",
                err_msg=f"Column names cannot start with reserved prefix '_' or be whitespace only: {self.cols}",
            )
        return

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        in_ports = []
        in_ports.append(
            InPort(
                name="base_row",
                description="Input row to be packed.",
                optional=True,
                accept=Pattern(
                    types={Schema.Type.TABLE},
                )
            )
        )
        for col in self.cols:
            assert col is not None
            in_ports.append(
                InPort(
                    name=col,
                    description=f"Column '{col}' to be packed.",
                    accept=Pattern(
                        types={Schema.Type.INT, Schema.Type.FLOAT, Schema.Type.STR, Schema.Type.BOOL, Schema.Type.DATETIME},
                    )
                )
            )
        return in_ports, [
            OutPort(
                name="packed_row",
                description="The packed row.",
            )
        ]

    @override
    def infer_output_schemas(self, input_schemas: Dict[str, Schema]) -> Dict[str, Schema]:
        if "base_row" in input_schemas:
            # append new columns to the base row
            baserow = deepcopy(input_schemas["base_row"])
            assert baserow.tab is not None
            for col in self.cols:
                assert col is not None
                col_type = input_schemas[col].to_coltype()
                baserow = baserow.append_col(col, col_type)
            output_schema = baserow
            assert baserow.tab is not None
            self._col_types = baserow.tab.col_types
            return {
                "packed_row": output_schema
            }
        else:
            # create a new row with only the new columns
            col_types: Dict[str, ColType] = {}
            for col in self.cols:
                assert col is not None
                col_type = input_schemas[col].to_coltype()
                col_types[col] = col_type
            output_schema = Schema(
                type=Schema.Type.TABLE,
                tab=TableSchema(col_types=col_types)
            )
            self._col_types = col_types
            return {
                "packed_row": output_schema
            }

    @override
    def process(self, input: Dict[str, Data]) -> Dict[str, Data]:
        output_row_dict: Dict[str, Any] = {}
        if "base_row" in input:
            base_row = input["base_row"]
            assert isinstance(base_row.payload, Table)
            df = base_row.payload.df
            if len(df) != 1:
                raise NodeExecutionError(
                    node_id=self.id,
                    err_msg=f"Input base_row must contain exactly one row, got {len(df)} rows.",
                )
            for col in df.columns:
                output_row_dict[col] = df.iloc[0][col]
        for col in self.cols:
            assert col is not None
            if col not in input:
                raise NodeExecutionError(
                    node_id=self.id,
                    err_msg=f"Input for column '{col}' is missing.",
                )
            value = input[col].payload
            output_row_dict[col] = value
        # create a new table with a single row
        output_df = DataFrame([output_row_dict])
        assert self._col_types is not None
        output_table = Table(
            col_types=self._col_types, 
            df=output_df
        )
        output_data = Data(payload=output_table)
        return {
            "packed_row": output_data
        }

    @override
    @classmethod
    def hint(cls, input_schemas: Dict[str, Schema], current_params: Dict) -> Dict[str, Any]:
        hint = {}
        if "cols" in current_params:
            inputs = ["base_row"]
            inputs.extend(current_params["cols"])
            hint["inputs"] = inputs
        return hint
