from datetime import datetime
from typing import Dict, override

from pydantic import PrivateAttr

from server.config import DEFAULT_TIMEZONE
from server.lib.FinancialDataManager import DataType, Interval
from server.models.data import Data
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
)

from ..base_node import BaseNode, InPort, OutPort, register_node


@register_node()
class KlineNode(BaseNode):
    """
    Node to generate real time financial Kline data in 1-minute intervals.
    User can specify the start time and end time with parameters or the input ports.
    """
    data_type: DataType
    symbol: str
    start_time: str | None = None # ISO format string
    end_time: str | None = None # ISO format string
    interval: Interval = "1m"

    _start_time_dt: datetime | None = PrivateAttr(default=None)
    _end_time_dt: datetime | None = PrivateAttr(default=None)
    _col_types: Dict[str, ColType] | None = PrivateAttr(default=None)

    @override
    def validate_parameters(self) -> None:
        if self.type != "KlineNode":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="type",
                err_msg="Node type mismatch.",
            )
        if self.symbol.strip() == "":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="symbol",
                err_msg="Symbol cannot be empty.",
            )
        if self.start_time is not None:
            try:
                # convert to datetime with default timezone
                self._start_time_dt = datetime.fromisoformat(self.start_time).astimezone(DEFAULT_TIMEZONE)
            except Exception:
                raise NodeParameterError(
                    node_id=self.id,
                    err_param_key="start_time",
                    err_msg="Invalid start_time format. Must be ISO format string.",
                )
        if self.end_time is not None:
            try:
                self._end_time_dt = datetime.fromisoformat(self.end_time).astimezone(DEFAULT_TIMEZONE)
            except Exception:
                raise NodeParameterError(
                    node_id=self.id,
                    err_param_key="end_time",
                    err_msg="Invalid end_time format. Must be ISO format string.",
                )
        if (self._start_time_dt is not None 
        and self._end_time_dt is not None 
        and self._start_time_dt >= self._end_time_dt):
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="start_time",
                err_msg="start_time must be earlier than end_time.",
            )
        return

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [
            InPort(
                name="start_time",
                description="Start time in ISO format string (overrides parameter if provided).",
                optional=True,
                accept=Pattern(types={Schema.Type.DATETIME}),
            ),
            InPort(
                name="end_time",
                description="End time in ISO format string (overrides parameter if provided).",
                optional=True,
                accept=Pattern(types={Schema.Type.DATETIME}),
            )
        ], [
            OutPort(
                name="kline_data",
                description="Generated Kline data in 1-minute intervals.",
            )
        ]

    @override
    def infer_output_schemas(self, input_schemas: Dict[str, Schema]) -> Dict[str, Schema]:
        output_col_types = {
            "Open Time": ColType.DATETIME,
            "Open": ColType.FLOAT,
            "High": ColType.FLOAT,
            "Low": ColType.FLOAT,
            "Close": ColType.FLOAT,
            "Volume": ColType.FLOAT,
        }
        self._col_types = output_col_types
        if self._start_time_dt is None:
            if "start_time" not in input_schemas:
                raise NodeValidationError(
                    node_id=self.id,
                    err_input="start_time",
                    err_msg="start_time must be provided either as parameter or input port.",
                )
        if self._end_time_dt is None:
            if "end_time" not in input_schemas:
                raise NodeValidationError(
                    node_id=self.id,
                    err_input="end_time",
                    err_msg="end_time must be provided either as parameter or input port.",
                )
        return {
            "kline_data": Schema(
                type=Schema.Type.TABLE,
                tab=TableSchema(
                    col_types=output_col_types
                )
            )
        }

    @override
    def process(self, input: Dict[str, Data]) -> Dict[str, Data]:
        # Determine start and end times
        start_time = self._start_time_dt
        end_time = self._end_time_dt
        if "start_time" in input:
            assert isinstance(input["start_time"].payload, datetime)
            start_time = input["start_time"].payload
        if "end_time" in input:
            assert isinstance(input["end_time"].payload, datetime)
            end_time = input["end_time"].payload
        assert start_time is not None and end_time is not None
        if start_time >= end_time:
            raise NodeExecutionError(
                node_id=self.id,
                err_msg="start_time must be earlier than end_time during execution.",
            )
        # Fetch Kline data from FinancialDataManager API
        financial_data_manager = self.global_config.financial_data_manager
        try:
            table = financial_data_manager.get_data(
                symbol=self.symbol,
                data_type=self.data_type,
                start_time=start_time,
                end_time=end_time,
                interval=self.interval,
            )
        except Exception as e:
            raise NodeExecutionError(
                node_id=self.id,
                err_msg=f"Failed to fetch Kline data: {str(e)}",
            )
        return {
            "kline_data": Data(
                payload=table
            )
        }
