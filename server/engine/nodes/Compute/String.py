from ..BaseNode import BaseNode, InPort, OutPort, register_node
from server.models.exception import NodeParameterError, NodeValidationError
from server.models.data import Table, Data
from server.models.schema import Pattern, Schema, generate_default_col_name, check_no_illegal_cols, ColType
import pandas as pd
from typing import override

"""
This file defines compute nodes for string operations.
String processing nodes for primitive str inputs/outputs.
"""

"""
String processing nodes for primitive str inputs/outputs.
"""

@register_node
class ClipStringNode(BaseNode):
    """Clip a string by start/end indices."""
    start: int | None = None
    end: int | None = None

    @override
    def validate_parameters(self) -> None:
        if not self.type == "ClipStringNode":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="type",
                err_msg="Node type must be 'ClipStringNode'."
            )

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [
            InPort(name="input", description="String input", accept=Pattern(types={Schema.Type.STR}), optional=False)
        ], [
            OutPort(name="output", description="Clipped string")
        ]

    @override
    def infer_output_schemas(self, input_schemas: dict[str, Schema]) -> dict[str, Schema]:
        return {"output": Schema(type=Schema.Type.STR)}

    @override
    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        v = input["input"].payload
        assert isinstance(v, str)
        res = v[self.start:self.end]
        return {"output": Data(payload=res)}

@register_node
class SubStringNode(BaseNode):
    """Extract substring between start and end substrings."""
    start: str | None = None
    end: str | None = None

    @override
    def validate_parameters(self) -> None:
        if not self.type == "SubStringNode":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="type",
                err_msg="Node type must be 'SubStringNode'."
            )
        if self.start is None and self.end is None:
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="start/end",
                err_msg="At least one of start or end must be provided."
            )

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [
            InPort(name="input", description="String input", accept=Pattern(types={Schema.Type.STR}), optional=False)
        ], [
            OutPort(name="output", description="Extracted substring")
        ]

    @override
    def infer_output_schemas(self, input_schemas: dict[str, Schema]) -> dict[str, Schema]:
        return {"output": Schema(type=Schema.Type.STR)}

    @override
    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        v = input["input"].payload
        assert isinstance(v, str)

        # return empty string if input is empty
        if v == "":
            return {"output": Data(payload="")}

        res: str
        # calculate start index
        if self.start is not None:
            start_found = v.find(self.start)
            if start_found == -1:
                # not found, return empty
                return {"output": Data(payload="")}
            start_idx = start_found + len(self.start)
        else:
            start_idx = 0

        # calculate end index
        if self.end is not None:
            end_found = v.find(self.end, start_idx)
            if end_found == -1:
                return {"output": Data(payload="")}
            end_idx = end_found
        else:
            end_idx = len(v)

        # start beyond end, return empty
        if start_idx > end_idx:
            res = ""
        else:
            res = v[start_idx:end_idx]
        return {"output": Data(payload=res)}

@register_node
class StripStringNode(BaseNode):
    """Strip characters from both ends."""
    chars: str | None = None

    @override
    def validate_parameters(self) -> None:
        if not self.type == "StripStringNode":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="type",
                err_msg="Node type must be 'StripStringNode'."
            )

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [
            InPort(name="input", description="String input", accept=Pattern(types={Schema.Type.STR}), optional=False)
        ], [
            OutPort(name="output", description="Stripped string")
        ]

    @override
    def infer_output_schemas(self, input_schemas: dict[str, Schema]) -> dict[str, Schema]:
        return {"output": Schema(type=Schema.Type.STR)}

    @override
    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        v = input["input"].payload
        assert isinstance(v, str)
        res = v.strip(self.chars)
        return {"output": Data(payload=res)}

@register_node
class ReplaceStringNode(BaseNode):
    """Replace occurrences of substr with another substr."""
    old: str
    new: str

    @override
    def validate_parameters(self) -> None:
        if not self.type == "ReplaceStringNode":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="type",
                err_msg="Node type must be 'ReplaceStringNode'."
            )
        if self.old == "":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="old",
                err_msg="old cannot be empty"
            )

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [
            InPort(name="input", description="String input", accept=Pattern(types={Schema.Type.STR}), optional=False)
        ], [
            OutPort(name="output", description="String with replacements")
        ]

    @override
    def infer_output_schemas(self, input_schemas: dict[str, Schema]) -> dict[str, Schema]:
        return {"output": Schema(type=Schema.Type.STR)}

    @override
    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        v = input["input"].payload
        assert isinstance(v, str)
        res = v.replace(self.old, self.new)
        return {"output": Data(payload=res)}

@register_node
class UpperStringNode(BaseNode):
    """Convert string to upper case."""

    @override
    def validate_parameters(self) -> None:
        if not self.type == "UpperStringNode":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="type",
                err_msg="Node type must be 'UpperStringNode'."
            )

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [
            InPort(name="input", description="String input", accept=Pattern(types={Schema.Type.STR}), optional=False)
        ], [
            OutPort(name="output", description="Uppercase string")
        ]

    @override
    def infer_output_schemas(self, input_schemas: dict[str, Schema]) -> dict[str, Schema]:
        return {"output": Schema(type=Schema.Type.STR)}

    @override
    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        v = input["input"].payload
        assert isinstance(v, str)
        res = v.upper()
        return {"output": Data(payload=res)}

@register_node
class LowerStringNode(BaseNode):
    """Convert string to lower case."""

    @override
    def validate_parameters(self) -> None:
        if not self.type == "LowerStringNode":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="type",
                err_msg="Node type must be 'LowerStringNode'."
            )

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [
            InPort(name="input", description="String input", accept=Pattern(types={Schema.Type.STR}), optional=False)
        ], [
            OutPort(name="output", description="Lowercase string")
        ]

    @override
    def infer_output_schemas(self, input_schemas: dict[str, Schema]) -> dict[str, Schema]:
        return {"output": Schema(type=Schema.Type.STR)}

    @override
    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        v = input["input"].payload
        assert isinstance(v, str)
        res = v.lower()
        return {"output": Data(payload=res)}
    

"""
String processing nodes between primitive str and table.
"""

@register_node
class TableAppendStringNode(BaseNode):
    """Append a single string to every value in a table column and write to result_col."""
    column: str
    result_col: str | None  # None indicates to use default name

    @override
    def validate_parameters(self) -> None:
        if not self.type == "TableAppendStringNode":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="type",
                err_msg="Node type must be 'TableAppendStringNode'."
            )
        if self.column.strip() == "":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="column",
                err_msg="column cannot be empty"
            )
        if self.result_col is None:
            self.result_col = generate_default_col_name(self.id, "appended")
        if self.result_col.strip() == "":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="result_col",
                err_msg="result_col cannot be empty"
            )
        if self.column == self.result_col:
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="result_col",
                err_msg="result_col cannot be the same as column"
            )
        if check_no_illegal_cols([self.result_col]) is False:
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="column/result_col",
                err_msg="column/result_col cannot be _index or _rowid"
            )
        return

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [
            InPort(name="table", description="Input table", accept=Pattern(types={Schema.Type.TABLE}, table_columns={self.column: {ColType.STR}}), optional=False),
            InPort(name="string", description="String to append", accept=Pattern(types={Schema.Type.STR}), optional=False)
        ], [
            OutPort(name="output", description="Output table with appended strings")
        ]

    @override
    def infer_output_schemas(self, input_schemas: dict[str, Schema]) -> dict[str, Schema]:
        table_schema = input_schemas["table"]
        assert table_schema.tab is not None
        
        # Static validation: check if new column already exists
        assert self.result_col is not None
        if not table_schema.tab.validate_new_col_name(self.result_col):
            raise NodeValidationError(
                node_id=self.id,
                err_input='table',
                err_msg=f"result_col '{self.result_col}' already exists in input table."
            )
        
        # Build output col_types: copy input and add result_col as STRING
        output_schema = input_schemas["table"].append_col(self.result_col, ColType.STR)

        return {"output": output_schema}

    @override
    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        table = input["table"].payload
        append_str = input["string"].payload
        assert isinstance(table, Table)
        assert isinstance(append_str, str)
        
        result = table.df.copy()
        # Preserve NaN values: direct string operations on StringDtype preserve NA
        result[self.result_col] = result[self.column] + append_str

        assert self.result_col is not None
        return {"output": Data(payload=Table(df=result, col_types={**table.col_types, self.result_col: ColType.STR}))}

@register_node
class TablePrependStringNode(BaseNode):
    """Prepend a single string to every value in a table column and write to result_col."""
    column: str
    result_col: str | None = None  # None indicates to use default name

    @override
    def validate_parameters(self) -> None:
        if not self.type == "TablePrependStringNode":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="type",
                err_msg="Node type must be 'TablePrependStringNode'."
            )
        if self.column.strip() == "":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="column",
                err_msg="column cannot be empty"
            )
        if self.result_col is None:
            self.result_col = generate_default_col_name(self.id, "prepended")
        if self.result_col.strip() == "":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="result_col",
                err_msg="result_col cannot be empty"
            )
        if self.column == self.result_col:
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="result_col",
                err_msg="result_col cannot be the same as column"
            )
        if check_no_illegal_cols([self.result_col]) is False:
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="column/result_col",
                err_msg="column/result_col cannot be _index or _rowid"
            )
        return

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [
            InPort(name="table", description="Input table", accept=Pattern(types={Schema.Type.TABLE}, table_columns={self.column: {ColType.STR}}), optional=False),
            InPort(name="string", description="String to prepend", accept=Pattern(types={Schema.Type.STR}), optional=False)
        ], [
            OutPort(name="output", description="Output table with prepended strings")
        ]

    @override
    def infer_output_schemas(self, input_schemas: dict[str, Schema]) -> dict[str, Schema]:
        table_schema = input_schemas["table"]
        assert table_schema.tab is not None
        
        # Static validation: check if new column already exists
        assert self.result_col is not None
        if not table_schema.tab.validate_new_col_name(self.result_col):
            raise NodeValidationError(
                node_id=self.id,
                err_input="table",
                err_msg=f"result_col '{self.result_col}' already exists in input table."
            )
        
        # Build output col_types: copy input and add result_col as STRING
        output_schemas = input_schemas["table"].append_col(self.result_col, ColType.STR)

        return {"output": output_schemas}

    @override
    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        table = input["table"].payload
        prepend_str = input["string"].payload
        assert isinstance(table, Table)
        assert isinstance(prepend_str, str)

        result = table.df.copy()
        # Preserve NaN values: direct string operations on StringDtype preserve NA
        result[self.result_col] = prepend_str + result[self.column]

        assert self.result_col is not None
        return {"output": Data(payload=Table(df=result, col_types={**table.col_types, self.result_col: ColType.STR}))}

@register_node
class TableContainsStringNode(BaseNode):
    """Check whether each value in a table column contains a given substring, output boolean column."""
    column: str
    result_col: str | None  # None indicates to use default name

    @override
    def validate_parameters(self) -> None:
        if not self.type == "TableContainsStringNode":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="type",
                err_msg="Node type must be 'TableContainsStringNode'."
            )
        if self.column.strip() == "":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="column",
                err_msg="column cannot be empty"
            )
        if self.result_col is None:
            self.result_col = generate_default_col_name(self.id, "contains")
        if self.result_col.strip() == "":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="result_col",
                err_msg="result_col cannot be empty"
            )
        if self.column == self.result_col:
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="result_col",
                err_msg="result_col cannot be the same as column"
            )
        if check_no_illegal_cols([self.result_col]) is False:
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="column/result_col",
                err_msg="column/result_col cannot be _index or _rowid"
            )
        return

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [
            InPort(name="table", description="Input table", accept=Pattern(types={Schema.Type.TABLE}, table_columns={self.column: {ColType.STR}}), optional=False),
            InPort(name="substring", description="Substring to search for", accept=Pattern(types={Schema.Type.STR}), optional=False)
        ], [
            OutPort(name="output", description="Output table with boolean results")
        ]

    @override
    def infer_output_schemas(self, input_schemas: dict[str, Schema]) -> dict[str, Schema]:
        assert input_schemas["table"].tab is not None
        input_table = input_schemas["table"].tab

        # check if new column already exists
        assert self.result_col is not None
        if not input_table.validate_new_col_name(self.result_col):
            raise NodeValidationError(
                node_id=self.id,
                err_input="table",
                err_msg=f"result_col '{self.result_col}' already exists in input table."
            )
        # Build output col_types: copy input and add result_col as BOOL
        output_schema = input_schemas["table"].append_col(self.result_col, ColType.BOOL)

        return {"output": output_schema}

    @override
    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        table = input["table"].payload
        substr = input["substring"].payload
        assert isinstance(table, Table)
        assert isinstance(substr, str)
        
        result = table.df.copy()
        # Preserve NaN: str.contains will keep NaN as NaN
        assert isinstance(result[self.column], pd.Series)
        result[self.result_col] = (
            result[self.column].str.contains(substr)
        )

        assert self.result_col is not None
        return {"output": Data(payload=Table(df=result, col_types={**table.col_types, self.result_col: ColType.BOOL}))}

@register_node
class TableStringLengthNode(BaseNode):
    """Compute the length of each string in a table column, output integer column."""
    column: str
    result_col: str | None

    @override
    def validate_parameters(self) -> None:
        if not self.type == "TableStringLengthNode":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="type",
                err_msg="Node type must be 'TableStringLengthNode'."
            )
        if self.column.strip() == "":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="column",
                err_msg="column cannot be empty"
            )
        if self.result_col is None:
            self.result_col = generate_default_col_name(self.id, "length")
        if self.result_col.strip() == "":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="result_col",
                err_msg="result_col cannot be empty"
            )
        if self.column == self.result_col:
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="result_col",
                err_msg="result_col cannot be the same as column"
            )
        if check_no_illegal_cols([self.result_col]) is False:
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="column/result_col",
                err_msg="column/result_col cannot be _index or _rowid"
            )
        return

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [
            InPort(name="table", description="Input table", accept=Pattern(types={Schema.Type.TABLE}, table_columns={self.column: {ColType.STR}}), optional=False)
        ], [
            OutPort(name="output", description="Output table with string lengths")
        ]

    @override
    def infer_output_schemas(self, input_schemas: dict[str, Schema]) -> dict[str, Schema]:
        assert input_schemas["table"].tab is not None
        input_table = input_schemas["table"].tab

        # check if new column already exists
        assert self.result_col is not None
        if not input_table.validate_new_col_name(self.result_col):
            raise NodeValidationError(
                node_id=self.id,
                err_input="table",
                err_msg=f"result_col '{self.result_col}' already exists in input table."
            )
        # Build output col_types: copy input and add result_col as INT
        output_schema = input_schemas["table"].append_col(self.result_col, ColType.INT)

        return {"output": output_schema}

    @override
    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        table = input["table"].payload
        assert isinstance(table, Table)
        
        result = table.df.copy()
        # Preserve NaN: str.len() on StringDtype will preserve NaN
        result[self.result_col] = result[self.column].str.len()

        assert self.result_col is not None
        return {"output": Data(payload=Table(df=result, col_types={**table.col_types, self.result_col: ColType.INT}))}

@register_node
class TableStartWithStringNode(BaseNode):
    """Check whether each value in a table column starts with a given substring, output boolean column."""
    column: str
    result_col: str | None  # None indicates to use default name

    @override
    def validate_parameters(self) -> None:
        if not self.type == "TableStartWithStringNode":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="type",
                err_msg="Node type must be 'TableStartWithStringNode'."
            )
        if self.column.strip() == "":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="column",
                err_msg="column cannot be empty"
            )
        if self.result_col is None:
            self.result_col = generate_default_col_name(self.id, "starts_with")
        if self.result_col.strip() == "":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="result_col",
                err_msg="result_col cannot be empty"
            )
        if self.column == self.result_col:
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="result_col",
                err_msg="result_col cannot be the same as column"
            )
        if check_no_illegal_cols([self.result_col]) is False:
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="column/result_col",
                err_msg="column/result_col cannot be _index or _rowid"
            )
        return

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [
            InPort(name="table", description="Input table", accept=Pattern(types={Schema.Type.TABLE}, table_columns={self.column: {ColType.STR}}), optional=False),
            InPort(name="substring", description="Substring to search for", accept=Pattern(types={Schema.Type.STR}), optional=False)
        ], [
            OutPort(name="output", description="Output table with boolean results")
        ]

    @override
    def infer_output_schemas(self, input_schemas: dict[str, Schema]) -> dict[str, Schema]:
        assert input_schemas["table"].tab is not None
        input_table = input_schemas["table"].tab

        # check if new column already exists
        assert self.result_col is not None
        if not input_table.validate_new_col_name(self.result_col):
            raise NodeValidationError(
                node_id=self.id,
                err_input="table",
                err_msg=f"result_col '{self.result_col}' already exists in input table."
            )
        # Build output col_types: copy input and add result_col as BOOL
        output_schema = input_schemas["table"].append_col(self.result_col, ColType.BOOL)

        return {"output": output_schema}

    @override
    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        table = input["table"].payload
        substr = input["substring"].payload
        assert isinstance(table, Table)
        assert isinstance(substr, str)
        
        result = table.df.copy()
        # Preserve NaN: str.startswith will keep NaN as NaN
        result[self.result_col] = (
            result[self.column].str.startswith(substr)
        )

        assert self.result_col is not None
        return {"output": Data(payload=Table(df=result, col_types={**table.col_types, self.result_col: ColType.BOOL}))}

@register_node
class TableEndWithStringNode(BaseNode):
    """Check whether each value in a table column ends with a given substring, output boolean column."""
    column: str
    result_col: str | None  # None indicates to use default name

    @override
    def validate_parameters(self) -> None:
        if not self.type == "TableEndWithStringNode":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="type",
                err_msg="Node type must be 'TableEndWithStringNode'."
            )
        if self.column.strip() == "":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="column",
                err_msg="column cannot be empty"
            )
        if self.result_col is None:
            self.result_col = generate_default_col_name(self.id, "end_with")
        if self.result_col.strip() == "":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="result_col",
                err_msg="result_col cannot be empty"
            )
        if self.column == self.result_col:
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="result_col",
                err_msg="result_col cannot be the same as column"
            )
        if check_no_illegal_cols([self.result_col]) is False:
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="column/result_col",
                err_msg="column/result_col cannot be _index or _rowid"
            )
        return

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [
            InPort(name="table", description="Input table", accept=Pattern(types={Schema.Type.TABLE}, table_columns={self.column: {ColType.STR}}), optional=False),
            InPort(name="substring", description="Substring to search for", accept=Pattern(types={Schema.Type.STR}), optional=False)
        ], [
            OutPort(name="output", description="Output table with boolean results")
        ]

    @override
    def infer_output_schemas(self, input_schemas: dict[str, Schema]) -> dict[str, Schema]:
        assert input_schemas["table"].tab is not None
        input_table = input_schemas["table"].tab

        # check if new column already exists
        assert self.result_col is not None
        if not input_table.validate_new_col_name(self.result_col):
            raise NodeValidationError(
                node_id=self.id,
                err_input="table",
                err_msg=f"result_col '{self.result_col}' already exists in input table."
            )
        # Build output col_types: copy input and add result_col as BOOL
        output_schema = input_schemas["table"].append_col(self.result_col, ColType.BOOL)

        return {"output": output_schema}

    @override
    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        table = input["table"].payload
        substr = input["substring"].payload
        assert isinstance(table, Table)
        assert isinstance(substr, str)
        
        result = table.df.copy()
        # Preserve NaN: str.endswith will keep NaN as NaN
        result[self.result_col] = (
            result[self.column].str.endswith(substr)
        )

        assert self.result_col is not None
        return {"output": Data(payload=Table(df=result, col_types={**table.col_types, self.result_col: ColType.BOOL}))}

@register_node
class TableReplaceStringNode(BaseNode):
    """Replace occurrences of old substring with new substring for each value in a table column."""
    column: str
    result_col: str | None  # None indicates to use default name

    @override
    def validate_parameters(self) -> None:
        if not self.type == "TableReplaceStringNode":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="type",
                err_msg="Node type must be 'TableReplaceStringNode'."
            )
        if self.column.strip() == "":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="column",
                err_msg="column cannot be empty"
            )
        if self.result_col is None:
            self.result_col = generate_default_col_name(self.id, "replaced")
        if self.result_col.strip() == "":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="result_col",
                err_msg="result_col cannot be empty"
            )
        if self.column == self.result_col:
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="result_col",
                err_msg="result_col cannot be the same as column"
            )
        if check_no_illegal_cols([self.result_col]) is False:
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="column/result_col",
                err_msg="column/result_col cannot be _index or _rowid"
            )
        return

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [
            InPort(name="table", description="Input table", accept=Pattern(types={Schema.Type.TABLE}, table_columns={self.column: {ColType.STR}}), optional=False),
            InPort(name="old", description="Old substring to replace", accept=Pattern(types={Schema.Type.STR}), optional=False),
            InPort(name="new", description="New substring to replace with", accept=Pattern(types={Schema.Type.STR}), optional=False)
        ], [
            OutPort(name="output", description="Output table with replaced values")
        ]

    @override
    def infer_output_schemas(self, input_schemas: dict[str, Schema]) -> dict[str, Schema]:
        assert input_schemas["table"].tab is not None
        input_table = input_schemas["table"].tab

        # check if new column already exists
        assert self.result_col is not None
        if not input_table.validate_new_col_name(self.result_col):
            raise NodeValidationError(
                node_id=self.id,
                err_input="table",
                err_msg=f"result_col '{self.result_col}' already exists in input table."
            )
        # Build output col_types: copy input and add result_col as STRING
        output_schema = input_schemas["table"].append_col(self.result_col, ColType.STR)

        return {"output": output_schema}

    @override
    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        table = input["table"].payload
        old_substr = input["old"].payload
        new_substr = input["new"].payload
        assert isinstance(table, Table)
        assert isinstance(old_substr, str)
        assert isinstance(new_substr, str)
        
        result = table.df.copy()
        # Preserve NaN: str.replace on StringDtype will preserve NaN
        result[self.result_col] = result[self.column].str.replace(old_substr, new_substr, regex=False)

        assert self.result_col is not None
        return {"output": Data(payload=Table(df=result, col_types={**table.col_types, self.result_col: ColType.STR}))}
