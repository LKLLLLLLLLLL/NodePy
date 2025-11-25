from typing import Any, Dict, override

from server.models.data import Data, Table
from server.models.exception import (
    NodeParameterError,
)
from server.models.schema import (
    ColType,
    Pattern,
    Schema,
)

from ..base_node import BaseNode, InPort, OutPort, register_node


@register_node
class StatsNode(BaseNode):
    """
    A node to calculate basic statistics (mean, count, sum, std, min, max, 25%-quantile, 50%-quantile, 75%-quantile) for specified columns in a table.
    """
    col: str

    @override
    def validate_parameters(self) -> None:
        if not self.type == "StatsNode":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="type",
                err_msg="Node type parameter mismatch.",
            )
        return

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        input_table_cols = {self.col: {ColType.FLOAT, ColType.INT}}
        return [
            InPort(
                name="table",
                description="Input table for statistical analysis.",
                accept=Pattern(
                    types={Schema.Type.TABLE},
                    table_columns=input_table_cols,
                )
            )
        ], [
            OutPort(
                name="mean",
                description="Mean values of the specified column."
            ),
            OutPort(
                name="count",
                description="Count of non-null values of the specified column."
            ),
            OutPort(
                name="std",
                description="Standard deviation values of the specified column."
            ),
            OutPort(
                name="sum",
                description="Sum of the specified column."
            ),
            OutPort(
                name="min",
                description="Minimum values of the specified column."
            ),
            OutPort(
                name="max",
                description="Maximum values of the specified column."
            ),
            OutPort(
                name="quantile_25",
                description="25%-quantile values of the specified column."
            ),
            OutPort(
                name="quantile_50",
                description="50%-quantile (median) values of the specified column."
            ),
            OutPort(
                name="quantile_75",
                description="75%-quantile values of the specified column."
            ),
        ]

    @override
    def infer_output_schemas(
        self, input_schemas: Dict[str, Schema]
    ) -> Dict[str, Schema]:
        table_schema = input_schemas["table"]
        assert table_schema.tab is not None

        input_col_type = table_schema.tab.col_types[self.col]

        # Based on pandas behavior:
        # mean, std, quantile always return float
        # count always returns int
        # sum, min, max preserve the original dtype

        prim_type_map = {
            ColType.INT: Schema.Type.INT,
            ColType.FLOAT: Schema.Type.FLOAT,
        }

        same_as_input_schema = Schema(type=prim_type_map[input_col_type])
        float_schema = Schema(type=Schema.Type.FLOAT)
        int_schema = Schema(type=Schema.Type.INT)

        return {
            "mean": float_schema,
            "count": int_schema,
            "std": float_schema,
            "min": same_as_input_schema,
            "max": same_as_input_schema,
            "sum": same_as_input_schema,
            "quantile_25": float_schema,
            "quantile_50": float_schema,
            "quantile_75": float_schema,
        }

    @override
    def process(self, input: Dict[str, Data]) -> Dict[str, Data]:
        table_data = input["table"]
        assert isinstance(table_data.payload, Table)
        df = table_data.payload.df

        # Use .item() to extract the scalar value from numpy types
        mean = df[self.col].mean()
        std = df[self.col].std()
        count = df[self.col].count()
        sum_ = df[self.col].sum().item()
        min_ = df[self.col].min().item()
        max_ = df[self.col].max().item()
        quantile_25 = df[self.col].quantile(0.25)
        quantile_50 = df[self.col].quantile(0.50)
        quantile_75 = df[self.col].quantile(0.75)

        return {
            "mean": Data(payload=mean),
            "count": Data(payload=count),
            "sum": Data(payload=sum_),
            "std": Data(payload=std),
            "min": Data(payload=min_),
            "max": Data(payload=max_),
            "quantile_25": Data(payload=quantile_25),
            "quantile_50": Data(payload=quantile_50),
            "quantile_75": Data(payload=quantile_75),
        }

    @override
    @classmethod
    def hint(cls, input_schemas: Dict[str, Schema], current_params: Dict) -> Dict[str, Any]:
        col_choices = []
        if "table" in input_schemas:
            table_schema = input_schemas["table"]
            assert table_schema.tab is not None
            for col in table_schema.tab.col_types.keys():
                if table_schema.tab.col_types[col] in {ColType.INT, ColType.FLOAT}:
                    col_choices.append(col)
        return {
            "col_choices": col_choices,
        }

