from typing import Any, Dict, Literal, override

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
class LogisticRegressionNode(BaseNode):
    """
    A node to perform logistic regression using specified feature columns and target column.
    Support binary classification tasks and multiclass classification.
    """
    feature_cols: list[str]
    target_col: str

    _model_schema: ModelSchema | None = PrivateAttr(default=None)

    @override
    def validate_parameters(self) -> None:
        if not self.type == "LogisticRegressionNode":
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
        feature_col_types = {col: {ColType.FLOAT, ColType.INT} for col in self.feature_cols}
        target_col_types = {self.target_col: {ColType.BOOL, ColType.INT, ColType.STR, ColType.FLOAT}} if self.target_col else {}
        return [
            InPort(
                name="table",
                description="Input table containing features for training.",
                accept=Pattern(
                    types={Schema.Type.TABLE},
                    table_columns={**feature_col_types, **target_col_types}
                )
            )
        ], [
            OutPort(
                name="model",
                description="Output trained logistic regression model.",
            )
        ]

    @override
    def infer_output_schemas(self, input_schemas: Dict[str, Schema]) -> Dict[str, Schema]:
        input_table_schema = input_schemas["table"]
        assert input_table_schema.tab is not None
        table_col_types = input_table_schema.tab.col_types.copy()

        # Create model schema
        model_schema = ModelSchema(
            model_type=ModelSchema.Type.CLASSIFICATION,
            input_cols={col: table_col_types[col] for col in self.feature_cols},
            output_cols={self.target_col: ColType.BOOL} if self.target_col else {}
        )
        self._model_schema = model_schema
        
        return {
            "model": Schema(
                type=Schema.Type.MODEL,
                model=model_schema
            )
        }

    @override
    def process(self, input: Dict[str, Data]) -> Dict[str, Data]:
        from sklearn.linear_model import LogisticRegression

        input_table = input["table"].payload
        assert isinstance(input_table, Table), "Input data must be a Table."

        # Prepare feature matrix and target vector
        x = input_table.df[self.feature_cols]
        y = input_table.df[self.target_col]
        # Train logistic regression model
        model = LogisticRegression()
        model.fit(x, y)

        # Create Model object
        assert self._model_schema is not None
        model_obj = Model(
            model=model,
            metadata=self._model_schema,
        )

        return {
            "model": Data(payload=model_obj)
        }

    @override
    @classmethod
    def hint(cls, input_schemas: Dict[str, Schema], current_params: Dict) -> Dict[str, Any]:
        hint = {}
        if "table" in input_schemas:
            table_schema = input_schemas["table"]
            if table_schema.tab is not None:
                for col, col_type in table_schema.tab.col_types.items():
                    if col_type in {ColType.FLOAT, ColType.INT}:
                        hint.setdefault("feature_col_choices", []).append(col)
                    if col_type in {ColType.BOOL, ColType.INT, ColType.STR, ColType.FLOAT}:
                        hint.setdefault("target_col_choices", []).append(col)
        return hint


@register_node()
class SVCNode(BaseNode):
    """
    A node to perform Support Vector Classification using specified feature columns and target column.
    Support binary classification tasks and multiclass classification.
    """
    feature_cols: list[str]
    target_col: str
    kernel: Literal["linear", "poly", "rbf", "sigmoid"]

    _model_schema: ModelSchema | None = PrivateAttr(default=None)

    @override
    def validate_parameters(self) -> None:
        if not self.type == "SVCNode":
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
        feature_col_types = {col: {ColType.FLOAT, ColType.INT} for col in self.feature_cols}
        target_col_types = {self.target_col: {ColType.BOOL, ColType.INT, ColType.STR}} if self.target_col else {}
        return [
            InPort(
                name="table",
                description="Input table containing features for training.",
                accept=Pattern(
                    types={Schema.Type.TABLE},
                    table_columns={**feature_col_types, **target_col_types}
                )
            )
        ], [
            OutPort(
                name="model",
                description="Output trained SVC model.",
            )
        ]

    @override
    def infer_output_schemas(self, input_schemas: Dict[str, Schema]) -> Dict[str, Schema]:
        input_table_schema = input_schemas["table"]
        assert input_table_schema.tab is not None
        table_col_types = input_table_schema.tab.col_types.copy()

        # Create model schema
        model_schema = ModelSchema(
            model_type=ModelSchema.Type.CLASSIFICATION,
            input_cols={col: table_col_types[col] for col in self.feature_cols},
            output_cols={self.target_col: ColType.BOOL} if self.target_col else {}
        )
        self._model_schema = model_schema
        
        return {
            "model": Schema(
                type=Schema.Type.MODEL,
                model=model_schema
            )
        }

    @override
    def process(self, input: Dict[str, Data]) -> Dict[str, Data]:
        from sklearn.svm import SVC

        input_table = input["table"].payload
        assert isinstance(input_table, Table), "Input data must be a Table."

        # Prepare feature matrix and target vector
        x = input_table.df[self.feature_cols]
        y = input_table.df[self.target_col]
        # Train SVC model with specified kernel
        model = SVC(kernel=self.kernel)
        model.fit(x, y)

        # Create Model object
        assert self._model_schema is not None
        model_obj = Model(
            model=model,
            metadata=self._model_schema,
        )

        return {
            "model": Data(payload=model_obj)
        }

    @override
    @classmethod
    def hint(cls, input_schemas: Dict[str, Schema], current_params: Dict) -> Dict[str, Any]:
        hint = {}
        if "table" in input_schemas:
            table_schema = input_schemas["table"]
            if table_schema.tab is not None:
                for col, col_type in table_schema.tab.col_types.items():
                    if col_type in {ColType.FLOAT, ColType.INT}:
                        hint.setdefault("feature_col_choices", []).append(col)
                    elif col_type in {ColType.BOOL, ColType.INT, ColType.STR}:
                        hint.setdefault("target_col_choices", []).append(col)
        return hint
