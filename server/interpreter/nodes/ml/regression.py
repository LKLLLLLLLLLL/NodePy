from typing import Any, Dict, override

from pydantic import PrivateAttr

from server.models.data import Data, Model, Table
from server.models.exception import (
    NodeParameterError,
)
from server.models.schema import (
    ColType,
    ModelSchema,
    Pattern,
    Schema,
)

from ..base_node import BaseNode, InPort, OutPort, register_node


@register_node()
class LinearRegressionNode(BaseNode):
    """
    A node to perform linear regression using specified feature columns and target column.
    """
    feature_cols: list[str]
    target_col: str

    _model_schema: ModelSchema | None = PrivateAttr(default=None)

    @override
    def validate_parameters(self) -> None:
        if not self.type == "LinearRegressionNode":
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
            if col == self.target_col:
                raise NodeParameterError(
                    node_id=self.id,
                    err_param_key="feature_cols",
                    err_msg=f"Feature column '{col}' cannot be the same as target column.",
                )
        if self.target_col.strip() == "":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="target_col",
                err_msg="Target column name cannot be empty.",
            )
        return

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        input_table_cols = {col: {ColType.FLOAT, ColType.INT, ColType.BOOL} for col in self.feature_cols}
        input_table_cols[self.target_col] = {ColType.FLOAT, ColType.INT}
        return [
            InPort(
                name="table",
                description="Input table for linear regression.",
                accept=Pattern(
                    types={Schema.Type.TABLE},
                    table_columns=input_table_cols,
                )
            ),
        ], [
            OutPort(
                name="model",
                description="Trained linear regression model.",
            ),
        ]

    @override
    def infer_output_schemas(self, input_schemas: Dict[str, Schema]) -> Dict[str, Schema]:
        model_schema = ModelSchema(
            model_type=ModelSchema.Type.REGRESSION,
            input_cols={col: ColType.FLOAT for col in self.feature_cols},
            output_cols={self.target_col: ColType.FLOAT},
        )
        self._model_schema = model_schema
        return {
            "model": Schema(
                type=Schema.Type.MODEL,
                model=model_schema,
            ),
        }

    @override
    def process(self, input: Dict[str, Data]) -> Dict[str, Data]:
        from sklearn.linear_model import LinearRegression
        input_table = input['table']
        assert isinstance(input_table.payload, Table)
        df = input_table.payload.df
        model = LinearRegression()
        x = df[self.feature_cols]
        y = df[self.target_col]
        model.fit(x, y)

        assert self._model_schema is not None
        model_data = Model(
            model=model,
            metadata=self._model_schema,
        )
        return {
            "model": Data(payload=model_data),
        }

    @override
    @classmethod
    def hint(cls, input_schemas: Dict[str, Schema], current_params: Dict) -> Dict[str, Any]:
        hint = {}
        if "table" in input_schemas:
            table_schema = input_schemas["table"]
            feature_col_choices = []
            target_col_choices = []
            if table_schema.tab is not None:
                for col_name, col_type in table_schema.tab.col_types.items():
                    if col_type in {ColType.FLOAT, ColType.INT, ColType.BOOL}:
                        feature_col_choices.append(col_name)
                    if col_type in {ColType.FLOAT, ColType.INT}:
                        target_col_choices.append(col_name)
            hint["feature_col_choices"] = feature_col_choices
            hint["target_col_choices"] = target_col_choices
        return hint


@register_node()
class RandomForestRegressionNode(BaseNode):
    """
    A node to perform random forest regression using specified feature columns and target column.
    """
    feature_cols: list[str]
    target_col: str
    n_estimators: int # Number of trees in the forest
    max_depth: int | None = None  # Maximum depth of the trees, None means no limit

    _col_types: Dict[str, ColType] = PrivateAttr(default={})
    _output_col_mapping: Dict[str, str] = PrivateAttr(default={})

    @override
    def validate_parameters(self) -> None:
        if not self.type == "RandomForestRegressionNode":
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
            if col == self.target_col:
                raise NodeParameterError(
                    node_id=self.id,
                    err_param_key="feature_cols",
                    err_msg=f"Feature column '{col}' cannot be the same as target column.",
                )
        if self.target_col.strip() == "":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="target_col",
                err_msg="Target column name cannot be empty.",
            )
        return

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        input_table_cols = {col: {ColType.FLOAT, ColType.INT, ColType.BOOL} for col in self.feature_cols}
        input_table_cols[self.target_col] = {ColType.FLOAT, ColType.INT}
        return [
            InPort(
                name="table",
                description="Input table for random forest regression.",
                accept=Pattern(
                    types={Schema.Type.TABLE},
                    table_columns=input_table_cols,
                )
            ),
        ], [
            OutPort(
                name="model",
                description="Trained random forest regression model.",
            ),
        ]

    @override
    def infer_output_schemas(self, input_schemas: Dict[str, Schema]) -> Dict[str, Schema]:
        model_schema = ModelSchema(
            model_type=ModelSchema.Type.REGRESSION,
            input_cols={col: ColType.FLOAT for col in self.feature_cols},
            output_cols={self.target_col: ColType.FLOAT},
        )
        return {
            "model": Schema(
                type=Schema.Type.MODEL,
                model=model_schema,
            ),
        }

    @override
    def process(self, input: Dict[str, Data]) -> Dict[str, Data]:
        from sklearn.ensemble import RandomForestRegressor
        input_table = input['table']
        assert isinstance(input_table.payload, Table)
        df = input_table.payload.df
        model = RandomForestRegressor(
            n_estimators=self.n_estimators, 
            max_depth=self.max_depth
        )
        x = df[self.feature_cols]
        y = df[self.target_col]
        model.fit(x, y)

        model_data = Model(
            model=model,
            metadata=ModelSchema(
                model_type=ModelSchema.Type.REGRESSION,
                input_cols={col: ColType.FLOAT for col in self.feature_cols},
                output_cols={self.target_col: ColType.FLOAT},
            ),
        )
        return {
            "model": Data(payload=model_data),
        }

    @override
    @classmethod
    def hint(cls, input_schemas: Dict[str, Schema], current_params: Dict) -> Dict[str, Any]:
        hint = {}
        if "table" in input_schemas:
            table_schema = input_schemas["table"]
            feature_col_choices = []
            target_col_choices = []
            if table_schema.tab is not None:
                for col_name, col_type in table_schema.tab.col_types.items():
                    if col_type in {ColType.FLOAT, ColType.INT, ColType.BOOL}:
                        feature_col_choices.append(col_name)
                    if col_type in {ColType.FLOAT, ColType.INT}:
                        target_col_choices.append(col_name)
            hint["feature_col_choices"] = feature_col_choices
            hint["target_col_choices"] = target_col_choices
        return hint
