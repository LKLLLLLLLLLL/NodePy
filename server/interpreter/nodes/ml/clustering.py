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
    generate_default_col_name,
)

from ..base_node import BaseNode, InPort, OutPort, register_node


@register_node()
class KMeansClusteringNode(BaseNode):
    """
    A node to perform K-Means clustering using specified feature columns.
    """
    feature_cols: list[str]
    n_clusters: int

    _cluster_label_col: str | None = PrivateAttr(default=None)
    _col_types: Dict[str, Any] | None = PrivateAttr(default=None)
    _model_schema: ModelSchema | None = PrivateAttr(default=None)

    @override
    def validate_parameters(self) -> None:
        if not self.type == "KMeansClusteringNode":
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
        if self.n_clusters <= 0:
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="n_clusters",
                err_msg="Number of clusters must be a positive integer.",
            )
        self._cluster_label_col = generate_default_col_name(
            id=self.id,
            annotation="cluster_label",
        )
        return

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        feature_col_types = {col: {ColType.FLOAT, ColType.INT} for col in self.feature_cols}

        return [
            InPort(
                name="table",
                description="Input table containing feature columns.",
                accept=Pattern(
                    types={Schema.Type.TABLE},
                    table_columns=feature_col_types,
                )
            )
        ], [
            OutPort(
                name="table",
                description="Output table with cluster labels."
            ),
            OutPort(
                name="model",
                description="Trained K-Means model."
            )
        ]

    @override
    def infer_output_schemas(self, input_schemas: Dict[str, Schema]) -> Dict[str, Schema]:
        table_schema = input_schemas["table"]
        # generate table schema
        assert self._cluster_label_col is not None
        output_schema = table_schema.append_col(
            self._cluster_label_col, 
            ColType.INT
        )
        assert output_schema.tab is not None
        self._col_types = output_schema.tab.col_types
        # generate model schema
        assert table_schema.tab is not None
        feature_cols_schema = {col: table_schema.tab.col_types[col] for col in self.feature_cols}
        self._model_schema = ModelSchema(
            model_type=ModelSchema.Type.CLUSTERING,
            input_cols=feature_cols_schema,
            output_cols={self._cluster_label_col: ColType.INT},
        )
        return {
            "table": output_schema,
            "model": Schema(
                type=Schema.Type.MODEL,
                model=self._model_schema,
            )
        }

    @override
    def process(self, input: Dict[str, Data]) -> Dict[str, Data]:
        from sklearn.cluster import KMeans
        
        input_data = input["table"]
        assert isinstance(input_data.payload, Table)
        df = input_data.payload.df.copy()

        feature_data = df[self.feature_cols]
        kmeans = KMeans(n_clusters=self.n_clusters)
        df[self._cluster_label_col] = kmeans.fit_predict(feature_data)
        assert self._col_types is not None
        output_table = Table(
            df=df,
            col_types=self._col_types,
        )
        assert self._model_schema is not None
        output_model = Model(
            model=kmeans,
            metadata=self._model_schema,
        )
        return {
            "table": Data(
                payload=output_table
            ),
            "model": Data(
                payload=output_model
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
                    if col_type in {ColType.INT, ColType.FLOAT}:
                        feature_cols_choices.append(col)
            hint["feature_cols_choices"] = feature_cols_choices
        return hint
