from typing import Any, Dict, override

from pydantic import PrivateAttr

from server.models.data import Data, Table
from server.models.exception import NodeParameterError
from server.models.schema import ColType, Pattern, Schema, TableSchema

from ..base_node import BaseNode, InPort, OutPort, register_node


@register_node()
class LagFeatureNode(BaseNode):
    """
    A feature engineering node to generate lag features (past values) and 
    target features (future values) for time series forecasting.
    It transforms a time series problem into a supervised learning problem.
    """
    lag_cols: list[str]  # Columns to generate lag features from
    window_size: int     # How many past steps to look back (e.g., 5 means t-1...t-5)
    gengerate_target: bool  # Whether to generate target feature
    target_col: str | None = None # Column to predict (optional, for training generation)
    horizon: int | None = None  # How many future steps to predict (e.g., 1 means t+1)
    drop_nan: bool # Whether to drop rows with NaN values created by shifting

    _output_col_types: Dict[str, ColType] | None = PrivateAttr(default=None)

    @override
    def validate_parameters(self) -> None:
        if not self.type == "LagFeatureNode":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="type",
                err_msg="Node type parameter mismatch.",
            )
        if self.window_size < 1:
            raise NodeParameterError(
                node_id=self.id, 
                err_param_key="window_size", 
                err_msg="Window size must be >= 1.")
        if self.gengerate_target and (self.horizon is None or self.horizon < 1):
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="horizon",
                err_msg="Horizon must be >= 1."
            )
        if not self.lag_cols:
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="lag_cols",
                err_msg="At least one lag column must be specified."
            )
        if self.gengerate_target and not self.target_col:
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="target_col",
                err_msg="Target column must be specified when generating target features."
            )
        return

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        lag_col_types = {col: {ColType.FLOAT, ColType.INT, ColType.BOOL} for col in self.lag_cols}
        target_col_types = {self.target_col: {ColType.FLOAT, ColType.INT}} if self.target_col else {}
        return [
            InPort(
                name="table",
                description="Input time series table.",
                accept=Pattern(
                    types={Schema.Type.TABLE},
                    table_columns={**lag_col_types, **target_col_types})
            )
        ], [
            OutPort(
                name="table",
                description="Table with added lag and target features."
            )
        ]

    @override
    def infer_output_schemas(self, input_schemas: Dict[str, Schema]) -> Dict[str, Schema]:
        input_schema = input_schemas["table"]
        assert input_schema.tab is not None
        
        # Copy input schema
        new_schema = input_schema.tab.col_types.copy()
        
        # 1. Add Lag Features (e.g., close_lag_1, close_lag_2)
        for col in self.lag_cols:
            if col not in new_schema:
                raise NodeParameterError(
                    node_id=self.id, 
                    err_param_key="lag_cols", 
                    err_msg=f"Column '{col}' not found in input table."
                )
            col_type = new_schema[col]
            for i in range(1, self.window_size + 1):
                new_schema[f"{col}_lag_{i}"] = col_type
        
        # 2. Add Target Feature (e.g., close_target_1)
        # This shifts the future value to the current row for training
        if self.gengerate_target:
            assert self.target_col is not None
            if self.target_col not in new_schema:
                 raise NodeParameterError(
                    node_id=self.id, 
                    err_param_key="target_col", 
                    err_msg=f"Column '{self.target_col}' not found."
                )
            col_type = new_schema[self.target_col]
            # Naming convention: target column usually implies the label
            new_schema[f"{self.target_col}_target_{self.horizon}"] = col_type

        self._output_col_types = new_schema
        return {
            "table": Schema(
                type=Schema.Type.TABLE,
                tab=TableSchema(col_types=new_schema)
            )
        }

    @override
    def process(self, input: Dict[str, Data]) -> Dict[str, Data]:
        input_table = input["table"]
        assert isinstance(input_table.payload, Table)
        df = input_table.payload.df.copy()
        
        # 1. Generate Lag Features (Shift Positive)
        # t-1, t-2 ...
        for col in self.lag_cols:
            for i in range(1, self.window_size + 1):
                col_name = f"{col}_lag_{i}"
                df[col_name] = df[col].shift(i)
        
        # 2. Generate Target Feature (Shift Negative)
        # t+1 (future) moved to t (current)
        if self.gengerate_target:
            assert self.target_col is not None
            assert self.horizon is not None
            col_name = f"{self.target_col}_target_{self.horizon}"
            df[col_name] = df[self.target_col].shift(-self.horizon)
            
        # 3. Drop NaN
        if self.drop_nan:
            df.dropna(inplace=True)

        assert self._output_col_types is not None
        return {
            "table": Data(payload=Table(df=df, col_types=self._output_col_types))
        }

    @override
    @classmethod
    def hint(cls, input_schemas: Dict[str, Schema], current_params: Dict) -> Dict[str, Any]:
        hint = {}
        if "table" in input_schemas:
            table_schema = input_schemas["table"]
            if table_schema.tab is not None:
                col_choices = [
                    col for col, col_type in table_schema.tab.col_types.items()
                    if col_type in {ColType.FLOAT, ColType.INT}
                ]
                hint["lag_col_choices"] = col_choices
                hint["target_col_choices"] = col_choices
        return hint
