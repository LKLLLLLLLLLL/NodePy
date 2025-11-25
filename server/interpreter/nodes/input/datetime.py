from datetime import datetime
from typing import override

from server.config import DEFAULT_TIMEZONE
from server.models.data import Data
from server.models.exception import NodeParameterError
from server.models.schema import Schema

from ..base_node import BaseNode, InPort, OutPort, register_node


@register_node()
class DateTimeNode(BaseNode):
    """
    A node to generate current date and time.
    """
    value: str
    _value: datetime | None = None

    @override
    def validate_parameters(self) -> None:
        if not self.type == "DateTimeNode":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="type",
                err_msg="Node type must be 'DateTimeNode'."
            )
        try:
            self._value = datetime.fromisoformat(self.value)
        except Exception as e:
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="value",
                err_msg=f"value must be a valid datetime string. Error: {str(e)}"
            )
        if self._value.tzinfo is None:
            self._value = self._value.replace(tzinfo=DEFAULT_TIMEZONE)
        return

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [], [OutPort(name="datetime", description="The datetime value")]

    @override
    def infer_output_schemas(self, input_schemas: dict[str, Schema]) -> dict[str, Schema]:
        return {"datetime": Schema(type=Schema.Type.DATETIME)}

    @override
    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        assert self._value is not None
        return {"datetime": Data(payload=self._value)}