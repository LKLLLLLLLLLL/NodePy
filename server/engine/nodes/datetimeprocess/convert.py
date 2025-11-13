from ..base_node import BaseNode, InPort, OutPort, register_node
from typing import Literal, override
from server.models.exception import (
    NodeParameterError,
    NodeExecutionError,
)
from server.models.data import Data
from server.models.schema import Pattern, Schema
from pandas import Timestamp, Timedelta

"""
This file defines conversion nodes between datetime data and other type data.
"""

@register_node
class ToDatetimeNode(BaseNode):
    """
    This node converts input data of num types to datetime type.
    Supported input types are: INT, FLOAT.
    The input number is treated as a timestamp in seconds since epoch.
    """
    unit: Literal["DAYS", "HOURS", "MINUTES", "SECONDS"]

    @override
    def validate_parameters(self) -> None:
        if not self.type == "ToDatetimeNode":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="type",
                err_msg="Node type must be 'ToDatetimeNode'."
            )
        return

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [
            InPort(
                name="value", 
                description="The input numeric value to convert to datetime",
                optional=False,
                accept=Pattern(types={Schema.Type.INT, Schema.Type.FLOAT})
            ),
        ], [
            OutPort(name="datetime", description="The resulting datetime value after conversion"),
        ]

    @override
    def infer_output_schemas(self, input_schemas: dict[str, Schema]) -> dict[str, Schema]:
        return {"datetime": Schema(type=Schema.Type.DATETIME)}

    @override
    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        value = input["value"].payload
        assert isinstance(value, (int, float))
        if self.unit == "DAYS":
            delta = Timedelta(days=value)
        elif self.unit == "HOURS":
            delta = Timedelta(hours=value)
        elif self.unit == "MINUTES":
            delta = Timedelta(minutes=value)
        elif self.unit == "SECONDS":
            delta = Timedelta(seconds=value)
        else:
            raise NodeExecutionError(
                node_id=self.id,
                err_msg=f"Unsupported unit: {self.unit}"
            )
        epoch = Timestamp("1970-01-01")
        result_datetime = epoch + delta
        return {"datetime": Data(payload=result_datetime)}

@register_node
class StrToDatetimeNode(BaseNode):
    """
    This node converts input data of string type to datetime type.
    The input string should be in a format recognized by pandas Timestamp.
    """

    @override
    def validate_parameters(self) -> None:
        if not self.type == "StrToDatetimeNode":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="type",
                err_msg="Node type must be 'StrToDatetimeNode'."
            )
        return

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [
            InPort(
                name="value", 
                description="The input string value to convert to datetime",
                optional=False,
                accept=Pattern(types={Schema.Type.STR})
            ),
        ], [
            OutPort(name="datetime", description="The resulting datetime value after conversion"),
        ]

    @override
    def infer_output_schemas(self, input_schemas: dict[str, Schema]) -> dict[str, Schema]:
        return {"datetime": Schema(type=Schema.Type.DATETIME)}

    @override
    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        value = input["value"].payload
        assert isinstance(value, str)
        try:
            result_datetime = Timestamp(value)
        except Exception as e:
            raise NodeExecutionError(
                node_id=self.id,
                err_msg=f"Failed to convert string to datetime: {str(e)}"
            )
        return {"datetime": Data(payload=result_datetime)}

@register_node
class DatetimePrintNode(BaseNode):
    """
    A node to print datetime value to string output.
    User can specify the print pattern in standard datetime format.
    """
    pattern: str

    @override
    def validate_parameters(self) -> None:
        if not self.type == "DatetimePrintNode":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="type",
                err_msg="Node type must be 'DatetimePrintNode'."
            )
        return

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [
            InPort(
                name="datetime", 
                description="The input datetime value to print",
                optional=False,
                accept=Pattern(types={Schema.Type.DATETIME})
            ),
        ], [
            OutPort(name="string", description="The resulting string after formatting the datetime value"),
        ]

    @override
    def infer_output_schemas(self, input_schemas: dict[str, Schema]) -> dict[str, Schema]:
        return {"string": Schema(type=Schema.Type.STR)}

    @override
    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        datetime_value = input["datetime"].payload
        assert isinstance(datetime_value, Timestamp)
        formatted_string = datetime_value.strftime(self.pattern)
        return {"string": Data(payload=formatted_string)}