from io import StringIO
from typing import Dict, override

import pandas

from server.config import DEFAULT_TIMEZONE
from server.models.data import Data, File, Table
from server.models.exception import (
    NodeParameterError,
)
from server.models.schema import (
    Pattern,
    Schema,
    TableSchema,
)

from ..base_node import BaseNode, InPort, OutPort, register_node

"""
This file defies nodes to convert from files or to files.
"""

@register_node
class TableFromCSVNode(BaseNode):
    """
    A node to generate a table from a CSV file.
    """

    @override
    def validate_parameters(self) -> None:
        if not self.type == "TableFromCSVNode":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="type",
                err_msg="Node type must be 'TableFromCSVNode'.",
            )
        return

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [
            InPort(
                name="csv_file",
                description="The input CSV file to generate table from.",
                accept=Pattern(types={Schema.Type.FILE}, file_formats={"csv"}),
            )
        ], [OutPort(name="table", description="The generated table from CSV.")]

    @override
    def infer_output_schemas(
        self, input_schemas: Dict[str, Schema]
    ) -> Dict[str, Schema]:
        # To get actual schema, need to read CSV file during static analysis stage.
        file_schema = input_schemas["csv_file"].file
        assert file_schema is not None
        assert file_schema.col_types is not None
        return {
            "table": Schema(
                type=Schema.Type.TABLE, tab=TableSchema(col_types=file_schema.col_types)
            )
        }

    @override
    def process(self, input: Dict[str, Data]) -> Dict[str, Data]:
        csv_file_data = input["csv_file"]
        assert isinstance(csv_file_data.payload, File)
        file_manager = self.global_config.file_manager
        user_id = self.global_config.user_id
        file_content = file_manager.read_sync(csv_file_data.payload, user_id=user_id)
        df = pandas.read_csv(StringIO(file_content.decode("utf-8")))
        out_table = Data.from_df(df)

        # add default timezone if not specified in csv file
        assert isinstance(out_table.payload, Table)
        for col_name in df.select_dtypes(include=["datetime64[ns]"]).columns:
            # If a datetime column is naive, localize it to UTC.
            if getattr(df[col_name].dt, "tz", None) is None:
                df[col_name] = df[col_name].dt.tz_localize(DEFAULT_TIMEZONE)  # type: ignore

        return {"table": out_table}
