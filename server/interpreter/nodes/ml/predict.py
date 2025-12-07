import copy
from typing import Dict, override

from pydantic import PrivateAttr

from server.models.data import Data, Model, Table
from server.models.exception import (
    NodeExecutionError,
    NodeParameterError,
    NodeValidationError,
)
from server.models.schema import (
    ColType,
    Pattern,
    Schema,
)

from ..base_node import BaseNode, InPort, OutPort, register_node


@register_node()
class PredictNode(BaseNode):
    """
    A node to perform predictions using a pre-trained machine learning model.
    """
    _col_types: dict[str, ColType] | None = PrivateAttr(default=None)
    _output_col_mapping: dict[str, str] | None = PrivateAttr(default=None)

    @override
    def validate_parameters(self) -> None:
        if not self.type == "PredictNode":
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
                description="Input table containing features for prediction.",
                accept=Pattern(
                    types={Schema.Type.TABLE},
                    table_columns={},
                )
            ),
            InPort(
                name="model",
                description="Pre-trained machine learning model.",
                accept=Pattern(
                    types={Schema.Type.MODEL},
                    model=set(),
                )
            )
        ], [
            OutPort(
                name="table",
                description="Output table with predictions.",
            )
        ]

    @override
    def infer_output_schemas(self, input_schemas: Dict[str, Schema]) -> Dict[str, Schema]:
        input_table_schema = input_schemas["table"]
        input_model_schema = input_schemas["model"]

        assert input_table_schema.tab is not None
        table_col_types = input_table_schema.tab.col_types.copy()
        assert input_model_schema.model is not None
        model_schema = input_model_schema.model

        # 1. check required feature columns
        required_feature_cols = model_schema.input_cols
        for col, coltype in required_feature_cols.items():
            if col not in table_col_types:
                raise NodeValidationError(
                    node_id=self.id,
                    err_input="table",
                    err_msg=f"Missing required feature column '{col}' for prediction.",
                )
            if table_col_types[col] != coltype:
                if coltype == ColType.FLOAT and table_col_types[col] == ColType.INT:
                    pass  # allow int to float conversion
                else:
                    raise NodeValidationError(
                        node_id=self.id,
                        err_input="table",
                        err_msg=f"Feature column '{col}' has type '{table_col_types[col]}', "
                        f"expected '{coltype}'.",
                    )

        # 2. Generate output column names and check for conflicts
        output_cols = model_schema.output_cols
        table_schema = copy.copy(input_table_schema)
        mapping = {}

        for col, coltype in output_cols.items():
            new_col_name = f"{col}_pred"

            # Check for conflicts
            assert table_schema.tab is not None
            if not table_schema.tab.validate_new_col_name(new_col_name):
                raise NodeValidationError(
                    node_id=self.id,
                    err_input="table",
                    err_msg=f"Output column '{new_col_name}' already exists in the table. "
                    f"Please rename the existing column or the model target.",
                )

            table_schema = table_schema.append_col(new_col_name, coltype)
            mapping[col] = new_col_name

        assert table_schema.tab is not None
        self._col_types = table_schema.tab.col_types
        self._output_col_mapping = mapping

        return {"table": table_schema}
        
    @override
    def process(self, input: Dict[str, Data]) -> Dict[str, Data]:
        input_table_data = input["table"]
        assert isinstance(input_table_data.payload, Table)
        df = input_table_data.payload.df.copy()
        assert self._col_types is not None
        assert self._output_col_mapping is not None

        input_model_data = input["model"]
        assert isinstance(input_model_data.payload, Model)
        model = input_model_data.payload.model
        model_schema = input_model_data.payload.metadata

        # 1. prepare feature data
        feature_cols = list(model_schema.input_cols.keys())

        x = df[feature_cols]

        # 2. perform prediction (generic interface)
        if not hasattr(model, "predict"):
            raise NodeExecutionError(
                node_id=self.id,
                err_msg="The provided model does not have a 'predict' method.",
            )
        predictions = model.predict(x)  # type: ignore

        # 3. write results
        output_col_names = list(self._output_col_mapping.values())

        if len(output_col_names) == 1:
            # single output case
            df[output_col_names[0]] = predictions
        else:
            # multi-output case, predictions is usually a 2D array
            # assume the column order of predictions matches the order defined in output_cols
            if hasattr(predictions, "shape") and len(predictions.shape) > 1:
                if predictions.shape[1] != len(output_col_names):
                    raise NodeExecutionError(
                        node_id=self.id,
                        err_msg=f"Model output shape {predictions.shape} mismatch with schema {len(output_col_names)}.",
                    )
                df[output_col_names] = predictions
            else:
                # handle some special cases or raise error
                raise NodeExecutionError(
                    node_id=self.id,
                    err_msg="Unexpected prediction output shape for multi-output model.",
                )

        output_data = Data(
            payload=Table(
                df=df,
                col_types=self._col_types,
            )
        )
        return {"table": output_data}
