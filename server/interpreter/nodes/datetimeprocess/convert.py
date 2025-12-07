from datetime import datetime, timedelta
from typing import Literal, override

from server.config import DEFAULT_TIMEZONE
from server.models.data import Data
from server.models.exception import (
    NodeExecutionError,
    NodeParameterError,
)
from server.models.schema import Pattern, Schema

from ..base_node import BaseNode, InPort, OutPort, register_node

"""
This file defines conversion nodes between datetime data and other type data.
"""

@register_node()
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
            delta = timedelta(days=value)
        elif self.unit == "HOURS":
            delta = timedelta(hours=value)
        elif self.unit == "MINUTES":
            delta = timedelta(minutes=value)
        elif self.unit == "SECONDS":
            delta = timedelta(seconds=value)
        else:
            raise NodeExecutionError(
                node_id=self.id,
                err_msg=f"Unsupported unit: {self.unit}"
            )
        epoch = datetime(1970, 1, 1, tzinfo=DEFAULT_TIMEZONE)
        result_datetime = epoch + delta
        return {"datetime": Data(payload=result_datetime)}

@register_node()
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
            result_datetime = datetime.fromisoformat(value)
            if result_datetime.tzinfo is None:
                result_datetime = result_datetime.replace(tzinfo=DEFAULT_TIMEZONE)
        except Exception as e:
            raise NodeExecutionError(
                node_id=self.id,
                err_msg=f"Failed to convert string to datetime: {str(e)}"
            )
        return {"datetime": Data(payload=result_datetime)}

@register_node()
class DatetimePrintNode(BaseNode):
    """
    A node to print datetime value to string output.
    User can specify the print pattern in standard datetime format.
    """
    format: str

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
            OutPort(name="output", description="The resulting string after formatting the datetime value"),
        ]

    @override
    def infer_output_schemas(self, input_schemas: dict[str, Schema]) -> dict[str, Schema]:
        return {"output": Schema(type=Schema.Type.STR)}

    @override
    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        datetime_value = input["datetime"].payload
        assert isinstance(datetime_value, datetime)
        formatted_string = datetime_value.strftime(self.format)
        return {"output": Data(payload=formatted_string)}

@register_node()
class DatetimeToTimestampNode(BaseNode):
    """
    Convert input datetime data to float timestamp.
    """
    unit: Literal["DAYS", "HOURS", "MINUTES", "SECONDS"]

    @override
    def validate_parameters(self) -> None:
        if not self.type == "DatetimeToTimestampNode":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="type",
                err_msg="Node type must be 'DatetimeToTimestampNode'."
            )
        return

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [
            InPort(
                name="datetime", 
                description="Input datetime data to be converted to timestamp.",
                optional=False,
                accept=Pattern(types={Schema.Type.DATETIME})
            ),
        ], [
            OutPort(
                name="timestamp",
                description="Output float timestamp after conversion.",
            )
        ]

    @override
    def infer_output_schemas(self, input_schemas: dict[str, Schema]) -> dict[str, Schema]:
        return {'timestamp': Schema(type=Schema.Type.FLOAT)}

    @override
    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        datetime_value = input["datetime"].payload
        assert isinstance(datetime_value, datetime)

        epoch = datetime(1970, 1, 1).replace(tzinfo=DEFAULT_TIMEZONE)
        delta = datetime_value - epoch

        if self.unit == "DAYS":
            timestamp = delta.total_seconds() / 86400.0
        elif self.unit == "HOURS":
            timestamp = delta.total_seconds() / 3600.0
        elif self.unit == "MINUTES":
            timestamp = delta.total_seconds() / 60.0
        elif self.unit == "SECONDS":
            timestamp = delta.total_seconds()
        else:
            raise NodeExecutionError(
                node_id=self.id,
                err_msg=f"Unsupported unit: {self.unit}"
            )

        return {'timestamp': Data(payload=timestamp)}
    