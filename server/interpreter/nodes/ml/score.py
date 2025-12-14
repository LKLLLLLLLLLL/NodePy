from typing import Dict, Literal, override

from sklearn.metrics import root_mean_squared_error

from server.models.data import Data, Model, Table
from server.models.exception import (
    NodeExecutionError,
    NodeParameterError,
    NodeValidationError,
)
from server.models.schema import (
    ModelSchema,
    Pattern,
    Schema,
)

from ..base_node import BaseNode, InPort, OutPort, register_node


@register_node()
class RegressionScoreNode(BaseNode):
    """
    A node to perform regression scoring using a pre-trained machine learning model.
    It applies the model to input data and output the score.
    """
    metric: Literal["mse", "rmse", "mae", "r2"] # Scoring metric to use

    @override
    def validate_parameters(self) -> None:
        if not self.type == "RegressionScoreNode":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="type",
                err_msg="Node type parameter mismatch.",
            )
        return

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [
            InPort(
                name="table",
                description="Input table containing features for scoring.",
                accept=Pattern(
                    types={Schema.Type.TABLE},
                    table_columns={},
                )
            ),
            InPort(
                name="model",
                description="Pre-trained regression model.",
                accept=Pattern(
                    types={Schema.Type.MODEL},
                    model=set(),
                )
            )
        ], [
            OutPort(
                name="score",
                description="Output score based on the specified metric.",
            )
        ]

    @override
    def infer_output_schemas(self, input_schemas: Dict[str, Schema]) -> Dict[str, Schema]:
        input_table_schema = input_schemas["table"]
        input_model_schema = input_schemas["model"]

        assert input_table_schema.tab is not None
        assert input_model_schema.model is not None
        
        # check if the models is a regression model
        if input_model_schema.model.model_type != ModelSchema.Type.REGRESSION:
            raise NodeValidationError(
                node_id=self.id,
                err_input="model",
                err_msg="Model must be a regression model."
            )

        # check if the feature columns in the input table match the model's expected input, both colnames and types
        table_col_types = input_table_schema.tab.col_types.copy()
        model_schema = input_model_schema.model
        model_feature_cols = model_schema.input_cols
        for col, col_type in table_col_types.items():
            if col not in model_feature_cols:
                raise NodeValidationError(
                    node_id=self.id,
                    err_input="table",
                    err_msg=f"Column '{col}' is not a required feature for the model."
                )
            if col_type != model_feature_cols[col]:
                raise NodeValidationError(
                    node_id=self.id,
                    err_input="table",
                    err_msg=f"Column '{col}' type mismatch: expected {model_feature_cols[col]}, got {col_type}."
                )
        # check if the model output matches the columns in the input table
        model_output_cols = model_schema.output_cols
        if len(model_output_cols) != 1:
            raise NodeValidationError(
                node_id=self.id,
                err_input="model",
                err_msg="Model must have exactly one output column for scoring."
            )
        for col, col_type in model_output_cols.items():
            if col not in table_col_types:
                raise NodeValidationError(
                    node_id=self.id,
                    err_input="table",
                    err_msg=f"Output column '{col}' is not present in the input table."
                )
            if table_col_types[col] != col_type:
                raise NodeValidationError(
                    node_id=self.id,
                    err_input="table",
                    err_msg=f"Output column '{col}' type mismatch: expected {col_type}, got {table_col_types[col]}."
                )
        # create output schema
        return {
            "score": Schema(
                type=Schema.Type.FLOAT,
            )
        }
    

    @override
    def process(self, input: Dict[str, Data]) -> Dict[str, Data]:
        input_data = input["table"]
        assert isinstance(input_data.payload, Table)
        df = input_data.payload.df.copy()
        
        input_model_data = input["model"]
        assert isinstance(input_model_data.payload, Model)
        model = input_model_data.payload
        
        assert model is not None
        # preform model prediction
        x = df[list(model.metadata.input_cols.keys())]
        if not hasattr(model.model, "predict"):
            raise NodeExecutionError(
                node_id=self.id,
                err_msg="Model does not have a 'predict' method."
            )
        y_pred = model.model.predict(x) # type: ignore
        # calculate the score based on the specified metric
        score: float
        if self.metric == "mse":
            from sklearn.metrics import mean_squared_error
            score = mean_squared_error(df[model.metadata.output_cols.keys()], y_pred)
        elif self.metric == "rmse":
            from sklearn.metrics import mean_squared_error
            score = root_mean_squared_error(df[model.metadata.output_cols.keys()], y_pred)
        elif self.metric == "mae":
            from sklearn.metrics import mean_absolute_error
            score = mean_absolute_error(df[model.metadata.output_cols.keys()], y_pred)
        elif self.metric == "r2":
            from sklearn.metrics import r2_score
            score = r2_score(df[model.metadata.output_cols.keys()], y_pred)
        else:
            assert False, f"Unknown metric: {self.metric}"

        return {
            "score": Data(payload=score)
        }        


@register_node()
class ClassificationScoreNode(BaseNode):
    """
    A node to perform classification scoring using a pre-trained machine learning model.
    It applies the model to input data and outputs the score.
    """
    metric: Literal["accuracy", "f1", "precision", "recall"]  # Scoring metric to use

    @override
    def validate_parameters(self) -> None:
        if not self.type == "ClassificationScoreNode":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="type",
                err_msg="Node type parameter mismatch.",
            )
        return

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [
            InPort(
                name="table",
                description="Input table containing features for scoring.",
                accept=Pattern(
                    types={Schema.Type.TABLE},
                    table_columns={},
                )
            ),
            InPort(
                name="model",
                description="Pre-trained classification model.",
                accept=Pattern(
                    types={Schema.Type.MODEL},
                    model=set(),
                )
            )
        ], [
            OutPort(
                name="score",
                description="Output score based on the specified metric.",
            )
        ]

    @override
    def infer_output_schemas(self, input_schemas: Dict[str, Schema]) -> Dict[str, Schema]:
        input_table_schema = input_schemas["table"]
        input_model_schema = input_schemas["model"]

        assert input_table_schema.tab is not None
        assert input_model_schema.model is not None
        
        # check if the models is a classification model
        if input_model_schema.model.model_type != ModelSchema.Type.CLASSIFICATION:
            raise NodeValidationError(
                node_id=self.id,
                err_input="model",
                err_msg="Model must be a classification model."
            )

        # check if the feature columns in the input table match the model's expected input, both colnames and types
        table_col_types = input_table_schema.tab.col_types.copy()
        model_schema = input_model_schema.model
        model_feature_cols = model_schema.input_cols
        for col, col_type in model_feature_cols.items():
            if col not in table_col_types:
                raise NodeValidationError(
                    node_id=self.id,
                    err_input="table",
                    err_msg=f"Column '{col}' is not a required feature for the model."
                )
            if table_col_types[col] != col_type:
                raise NodeValidationError(
                    node_id=self.id,
                    err_input="table",
                    err_msg=f"Column '{col}' type mismatch: expected {col_type}, got {table_col_types[col]}."
                )
        # check if the model output matches the columns in the input table
        model_output_cols = model_schema.output_cols
        if len(model_output_cols) != 1:
            raise NodeValidationError(
                node_id=self.id,
                err_input="model",
                err_msg="Model must have exactly one output column for scoring."
            )
        for col, col_type in model_output_cols.items():
            if col not in table_col_types:
                raise NodeValidationError(
                    node_id=self.id,
                    err_input="table",
                    err_msg=f"Output column '{col}' is not present in the input table."
                )
            if table_col_types[col] != col_type:
                raise NodeValidationError(
                    node_id=self.id,
                    err_input="table",
                    err_msg=f"Output column '{col}' type mismatch: expected {col_type}, got {table_col_types[col]}."
                )
        
        # create output schema
        return {
            "score": Schema(
                type=Schema.Type.FLOAT,
            )
        }

    @override
    def process(self, input: Dict[str, Data]) -> Dict[str, Data]:
        input_data = input["table"]
        assert isinstance(input_data.payload, Table)
        df = input_data.payload.df.copy()
        
        input_model_data = input["model"]
        assert isinstance(input_model_data.payload, Model)
        model = input_model_data.payload
        
        assert model is not None
        # preform model prediction
        x = df[list(model.metadata.input_cols.keys())]
        if not hasattr(model.model, "predict"):
            raise NodeExecutionError(
                node_id=self.id,
                err_msg="Model does not have a 'predict' method."
            )
        y_pred = model.model.predict(x)  # type: ignore
        
        # calculate the score based on the specified metric
        score: float
        if self.metric == "accuracy":
            from sklearn.metrics import accuracy_score
            score = float(accuracy_score(df[model.metadata.output_cols.keys()], y_pred))
        elif self.metric == "f1":
            from sklearn.metrics import f1_score
            score = float(f1_score(df[model.metadata.output_cols.keys()], y_pred))
        elif self.metric == "precision":
            from sklearn.metrics import precision_score
            score = float(precision_score(df[model.metadata.output_cols.keys()], y_pred))
        elif self.metric == "recall":
            from sklearn.metrics import recall_score
            score = float(recall_score(df[model.metadata.output_cols.keys()], y_pred))
        else:
            assert False, f"Unknown metric: {self.metric}"

        return {
            "score": Data(payload=score)
        }
