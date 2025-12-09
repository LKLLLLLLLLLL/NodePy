from typing import Any, Dict, override

from pydantic import PrivateAttr

from server.models.data import Data, Table
from server.models.exception import (
    NodeParameterError,
)
from server.models.schema import (
    ColType,
    Pattern,
    Schema,
    TableSchema,
)

from ..base_node import BaseNode, InPort, OutPort, register_node


@register_node()
class StandardScalerNode(BaseNode):
    """
    A node to perform standard scaling on specified feature columns.
    """
    feature_cols: list[str]

    _col_types: Dict[str, Any] | None = PrivateAttr(default=None)

    @override
    def validate_parameters(self) -> None:
        if not self.type == "StandardScalerNode":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="type",
                err_msg="Node type parameter mismatch.",
            )
        if not self.feature_cols:
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="feature_cols",
                err_msg="At least one feature column must be specified.",
            )
        for col in self.feature_cols:
            if col.strip() == "":
                raise NodeParameterError(
                    node_id=self.id,
                    err_param_key="feature_cols",
                    err_msg="Feature column names cannot be empty.",
                )
        return

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        feature_col_types = {col: {ColType.FLOAT, ColType.INT, ColType.BOOL} for col in self.feature_cols}
        return [
            InPort(
                name="table",
                description="Input table data for standard scaling.",
                accept=Pattern(
                    types={Schema.Type.TABLE},
                    table_columns=feature_col_types,
                )
            )
        ], [
            OutPort(
                name="scaled_table",
                description="Output table with scaled feature columns.",
            )
        ]

    @override
    def infer_output_schemas(self, input_schemas: Dict[str, Schema]) -> Dict[str, Schema]:
        input_table_data = input_schemas["table"]
        assert input_table_data.tab is not None
        table_schema = input_table_data.tab
        # for float or bool feature columns, the output type is float
        output_col_types = table_schema.col_types.copy()
        for col in self.feature_cols:
            output_col_types[col] = ColType.FLOAT
        self._col_types = output_col_types
        return {
            "scaled_table": Schema(
                type=Schema.Type.TABLE,
                tab=TableSchema(
                    col_types=output_col_types
                )
            )
        }

    @override
    def process(self, input: Dict[str, Data]) -> Dict[str, Data]:
        from sklearn.preprocessing import StandardScaler

        input_table_data = input["table"]
        assert isinstance(input_table_data.payload, Table)
        df = input_table_data.payload.df.copy()

        scaler = StandardScaler()
        df[self.feature_cols] = scaler.fit_transform(df[self.feature_cols])

        assert self._col_types is not None
        output_table = Table(
            df=df,
            col_types=self._col_types,
        )
        return {
            "scaled_table": Data(
                payload=output_table
            )
        }

    @override
    @classmethod
    def hint(cls, input_schemas: Dict[str, Schema], current_params: Dict) -> Dict[str, Any]:
        hint = {}
        if "table" in input_schemas:
            table_schema = input_schemas["table"]
            feature_cols_choices = []
            if table_schema.tab is not None:
                for col, col_type in table_schema.tab.col_types.items():
                    if col_type in {ColType.INT, ColType.FLOAT, ColType.BOOL}:
                        feature_cols_choices.append(col)
            hint["feature_cols_choices"] = feature_cols_choices
        return hint
