from io import StringIO
from typing import Dict, Literal, override

import pandas

from server.config import DEFAULT_TIMEZONE
from server.models.data import Data, File, Table
from server.models.exception import (
    NodeParameterError,
)
from server.models.schema import (
    FileSchema,
    Pattern,
    Schema,
    TableSchema,
)

from ..base_node import BaseNode, InPort, OutPort, register_node

"""
This file defies nodes to convert from files or to files.
"""

@register_node()
class TableFromFileNode(BaseNode):
    """
    A node to generate a table from a file.
    """

    @override
    def validate_parameters(self) -> None:
        if not self.type == "TableFromFileNode":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="type",
                err_msg="Node type must be 'TableFromFileNode'.",
            )
        return

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [
            InPort(
                name="file",
                description="The input file to generate table from.",
                accept=Pattern(types={Schema.Type.FILE}, file_formats={"csv", "json", "xlsx"}),
            )
        ], [OutPort(name="table", description="The generated table from file.")]

    @override
    def infer_output_schemas(
        self, input_schemas: Dict[str, Schema]
    ) -> Dict[str, Schema]:
        # To get actual schema, need to read CSV file during static analysis stage.
        file_schema = input_schemas["file"].file
        assert file_schema is not None
        assert file_schema.col_types is not None
        return {
            "table": Schema(
                type=Schema.Type.TABLE, tab=TableSchema(col_types=file_schema.col_types)
            )
        }

    @override
    def process(self, input: Dict[str, Data]) -> Dict[str, Data]:
        file_data = input["file"]
        assert isinstance(file_data.payload, File)
        file_manager = self.global_config.file_manager
        user_id = self.global_config.user_id
        file_content = file_manager.read_sync(file_data.payload, user_id=user_id)
        file_format = file_data.payload.format
        df: pandas.DataFrame
        if file_format == "csv":
            df = pandas.read_csv(StringIO(file_content.decode("utf-8")))
        elif file_format == "json":
            df = pandas.read_json(StringIO(file_content.decode("utf-8")))
        elif file_format == "xlsx":
            df = pandas.read_excel(StringIO(file_content.decode("utf-8")))
        else:
            raise ValueError(f"Unsupported file format: {file_format}")
        out_table = Data.from_df(df)

        # add default timezone if not specified in csv file
        assert isinstance(out_table.payload, Table)
        for col_name in df.select_dtypes(include=["datetime64[ns]"]).columns:
            # If a datetime column is naive, localize it to UTC.
            if getattr(df[col_name].dt, "tz", None) is None:
                df[col_name] = df[col_name].dt.tz_localize(DEFAULT_TIMEZONE)  # type: ignore

        return {"table": out_table}

@register_node()
class TableToFileNode(BaseNode):
    """
    A node to generate a file from a table.
    """
    filename: str | None = None  # Optional filename for the output file.
    format: Literal["csv", "xlsx", "json"]

    @override
    def validate_parameters(self) -> None:
        if not self.type == "TableToFileNode":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="type",
                err_msg="Node type must be 'TableToFileNode'.",
            )
        if self.filename is None:
            self.filename = f"{self.id}.{self.format}"
        return

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [
            InPort(
                name="table",
                description="The input table to generate file from.",
                accept=Pattern(types={Schema.Type.TABLE}),
            )
        ], [OutPort(name="file", description="The generated file from table.")]

    @override
    def infer_output_schemas(
        self, input_schemas: Dict[str, Schema]
    ) -> Dict[str, Schema]:
        assert "table" in input_schemas
        assert input_schemas["table"].tab is not None
        col_types = input_schemas["table"].tab.col_types
        return {
            "file": Schema(
                type=Schema.Type.FILE,
                file=FileSchema(
                    format=self.format,
                    col_types=col_types,
                ),
            )
        }

    @override
    def process(self, input: Dict[str, Data]) -> Dict[str, Data]:
        file_manager = self.global_config.file_manager
        assert self.filename is not None
        
        table_data = input["table"]
        assert isinstance(table_data.payload, Table)
        df = table_data.payload.df
        buffer = file_manager.get_buffer()
        if self.format == "csv":
            df.to_csv(buffer, index=False)
        elif self.format == "xlsx":
            df.to_excel(buffer, index=False)
        elif self.format == "json":
            df.to_json(buffer, orient="records", lines=True)
        else:
            raise AssertionError(f"Unsupported file format: {self.format}")
        file = file_manager.write_sync(
            self.filename, 
            buffer, self.format,
            user_id=self.global_config.user_id, 
            node_id=self.id, 
            project_id=self.global_config.project_id
        )
        return {"file": Data(payload=file)}

