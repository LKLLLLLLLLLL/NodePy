from ..base_node import BaseNode, InPort, OutPort, register_node
from typing import Literal, override
from server.models.exception import (
    NodeParameterError,
    NodeExecutionError,
)
from server.models.data import Data
from server.models.schema import Pattern, Schema
from datetime import datetime, timedelta

"""
This file defines compute nodes between datetime data.
"""

@register_node
class DatetimeComputeNode(BaseNode):
    """
    This node performs computations between datetime data and float/int data.
    """
    op: Literal["ADD", "SUB"]
    unit: Literal["DAYS", "HOURS", "MINUTES", "SECONDS"]

    @override
    def validate_parameters(self) -> None:
        if not self.type == "DatetimeComputeNode":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="type",
                err_msg="Node type must be 'DateTimeComputeNode'."
            )
        return

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [
            InPort(
                name="datetime", 
                description="The input datetime value",
                optional=False,
                accept=Pattern(types={Schema.Type.DATETIME})
            ),
            InPort(
                name="value", 
                description="The float value to compute with datetime",
                optional=False,
                accept=Pattern(types={Schema.Type.FLOAT})
            ),
        ], [
            OutPort(name="result", description="The resulting datetime value after computation"),
        ]

    @override
    def infer_output_schemas(self, input_schemas: dict[str, Schema]) -> dict[str, Schema]:
        return {"result": Schema(type=Schema.Type.DATETIME)}

    @override
    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        datetime_value = input["datetime"].payload
        value = input["value"].payload

        assert isinstance(datetime_value, datetime)
        assert isinstance(value, (int, float))

        delta_kwargs = {}
        if self.unit == "DAYS":
            delta_kwargs["days"] = value
        elif self.unit == "HOURS":
            delta_kwargs["hours"] = value
        elif self.unit == "MINUTES":
            delta_kwargs["minutes"] = value
        elif self.unit == "SECONDS":
            delta_kwargs["seconds"] = value
        else:
            raise NodeExecutionError(
                node_id=self.id,
                err_msg=f"Unsupported unit '{self.unit}'."
            )

        delta = timedelta(**delta_kwargs)

        if self.op == "ADD":
            result_datetime = datetime_value + delta
        elif self.op == "SUB":
            result_datetime = datetime_value - delta
        else:
            raise NodeExecutionError(
                node_id=self.id,
                err_msg=f"Unsupported operation '{self.op}'."
            )

        return {"result": Data(payload=result_datetime)}
    
@register_node
class DatetimeDiffNode(BaseNode):
    """
    This node computes the difference between two datetime values in specified units.
    """
    
    unit: Literal["DAYS", "HOURS", "MINUTES", "SECONDS"]

    @override
    def validate_parameters(self) -> None:
        if not self.type == "DatetimeDifferenceNode":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="type",
                err_msg="Node type must be 'DatetimeDifferenceNode'."
            )
        return

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [
            InPort(
                name="datetime_x", 
                description="The first datetime value",
                optional=False,
                accept=Pattern(types={Schema.Type.DATETIME})
            ),
            InPort(
                name="datetime_y", 
                description="The second datetime value",
                optional=False,
                accept=Pattern(types={Schema.Type.DATETIME})
            ),
        ], [
            OutPort(name="difference", description="The difference between the two datetimes in specified units"),
        ]

    @override
    def infer_output_schemas(self, input_schemas: dict[str, Schema]) -> dict[str, Schema]:
        return {"difference": Schema(type=Schema.Type.FLOAT)}

    @override
    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        datetime_x = input["datetime_x"].payload
        datetime_y = input["datetime_y"].payload

        assert isinstance(datetime_x, datetime)
        assert isinstance(datetime_y, datetime)

        delta = datetime_x - datetime_y

        if self.unit == "DAYS":
            difference = delta.total_seconds() / 86400  # seconds in a day
        elif self.unit == "HOURS":
            difference = delta.total_seconds() / 3600  # seconds in an hour
        elif self.unit == "MINUTES":
            difference = delta.total_seconds() / 60  # seconds in a minute
        elif self.unit == "SECONDS":
            difference = delta.total_seconds()
        else:
            raise NodeExecutionError(
                node_id=self.id,
                err_msg=f"Unsupported unit '{self.unit}'."
            )

        if isinstance(difference, int):
            difference = float(difference)

        return {"difference": Data(payload=difference)}
