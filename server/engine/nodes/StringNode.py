from .BaseNode import BaseNode, InPort, OutPort, Data, Schema, NodeValidationError
from .Utils import Visualization, validate_no_index_column_conflict
from pandas import DataFrame

"""
String processing nodes for primitive str inputs/outputs.
Each node follows the same strict validation and typing style used in other nodes.
"""

class StringNode(BaseNode):
    """Node to generate a user-provided string"""
    value: str

    def validate_parameters(self) -> None:
        if not self.type == "StringNode":
            raise NodeValidationError("Node type must be 'StringNode'.")
        if self.value is None:
            raise NodeValidationError("value cannot be None")

    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [], [OutPort(name="output", description="String output")]

    def validate_input(self, input: dict[str, Data]) -> None:
        pass

    def infer_output_schema(self, input_schema: dict[str, Schema]) -> dict[str, Schema]:
        return {"output": Schema(type=Schema.DataType.STR)}

    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        self.vis = Visualization(node_id=self.id, type=Visualization.Type.STR, payload=self.value)
        return {"output": Data(sche=Schema(type=Schema.DataType.STR), payload=self.value)}


class ClipStringNode(BaseNode):
    """Clip a string by start/end indices."""
    start: int | None = None
    end: int | None = None

    def validate_parameters(self) -> None:
        if not self.type == "ClipStringNode":
            raise NodeValidationError("Node type must be 'ClipStringNode'.")

    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [InPort(name="input", accept_types={Schema.DataType.STR})], [OutPort(name="output")]

    def validate_input(self, input: dict[str, Data]) -> None:
        pass

    def infer_output_schema(self, input_schema: dict[str, Schema]) -> dict[str, Schema]:
        return {"output": Schema(type=Schema.DataType.STR)}

    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        v = input["input"].payload
        assert isinstance(v, str)
        res = v[self.start:self.end]
        self.vis = Visualization(node_id=self.id, type=Visualization.Type.STR, payload=res)
        return {"output": Data(sche=Schema(type=Schema.DataType.STR), payload=res)}

class SubStringNode(BaseNode):
    """Extract substring between start and end substrings."""
    start: str | None = None
    end: str | None = None

    def validate_parameters(self) -> None:
        if not self.type == "SubStringNode":
            raise NodeValidationError("Node type must be 'SubStringNode'.")
        if self.start is None and self.end is None:
            raise NodeValidationError("At least one of start or end must be provided.")

    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [InPort(name="input", accept_types={Schema.DataType.STR})], [OutPort(name="output")]

    def validate_input(self, input: dict[str, Data]) -> None:
        pass

    def infer_output_schema(self, input_schema: dict[str, Schema]) -> dict[str, Schema]:
        return {"output": Schema(type=Schema.DataType.STR)}

    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        v = input["input"].payload
        assert isinstance(v, str)

        # return empty string if input is empty
        if v == "":
            self.vis = Visualization(
                node_id=self.id, type=Visualization.Type.STR, payload=""
            )
            return {"output": Data(sche=Schema(type=Schema.DataType.STR), payload="")}

        res: str
        # calculate start index
        if self.start is not None:
            start_found = v.find(self.start)
            if start_found == -1:
                # not found, return empty
                res = ""
                self.vis = Visualization(node_id=self.id, type=Visualization.Type.STR, payload=res)
                return {"output": Data(sche=Schema(type=Schema.DataType.STR), payload=res)}
            start_idx = start_found + len(self.start)
        else:
            start_idx = 0

        # calculate end index
        if self.end is not None:
            end_found = v.find(self.end, start_idx)
            if end_found == -1:
                res = ""
                self.vis = Visualization(node_id=self.id, type=Visualization.Type.STR, payload=res)
                return {"output": Data(sche=Schema(type=Schema.DataType.STR), payload=res)}
            end_idx = end_found
        else:
            end_idx = len(v)

        # start beyond end, return empty
        if start_idx > end_idx:
            res = ""
        else:
            res = v[start_idx:end_idx]
        self.vis = Visualization(node_id=self.id, type=Visualization.Type.STR, payload=res)
        return {"output": Data(sche=Schema(type=Schema.DataType.STR), payload=res)}

class StripStringNode(BaseNode):
    """Strip characters from both ends."""
    chars: str | None = None

    def validate_parameters(self) -> None:
        if not self.type == "StripStringNode":
            raise NodeValidationError("Node type must be 'StripStringNode'.")

    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [InPort(name="input", accept_types={Schema.DataType.STR})], [OutPort(name="output")]

    def validate_input(self, input: dict[str, Data]) -> None:
        pass

    def infer_output_schema(self, input_schema: dict[str, Schema]) -> dict[str, Schema]:
        return {"output": Schema(type=Schema.DataType.STR)}

    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        v = input["input"].payload
        assert isinstance(v, str)
        res = v.strip(self.chars)
        self.vis = Visualization(node_id=self.id, type=Visualization.Type.STR, payload=res)
        return {"output": Data(sche=Schema(type=Schema.DataType.STR), payload=res)}


class ReplaceStringNode(BaseNode):
    """Replace occurrences of substr with another substr."""
    old: str
    new: str

    def validate_parameters(self) -> None:
        if not self.type == "ReplaceStringNode":
            raise NodeValidationError("Node type must be 'ReplaceStringNode'.")
        if self.old == "":
            raise NodeValidationError("old cannot be empty")

    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [InPort(name="input", accept_types={Schema.DataType.STR})], [OutPort(name="output")]

    def validate_input(self, input: dict[str, Data]) -> None:
        pass

    def infer_output_schema(self, input_schema: dict[str, Schema]) -> dict[str, Schema]:
        return {"output": Schema(type=Schema.DataType.STR)}

    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        v = input["input"].payload
        assert isinstance(v, str)
        res = v.replace(self.old, self.new)
        self.vis = Visualization(node_id=self.id, type=Visualization.Type.STR, payload=res)
        return {"output": Data(sche=Schema(type=Schema.DataType.STR), payload=res)}


class JoinStringNode(BaseNode):
    """Merge multiple strings into one using separator."""
    sep: str

    def validate_parameters(self) -> None:
        if not self.type == "JoinStringNode":
            raise NodeValidationError("Node type must be 'JoinStringNode'.")

    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        # accept a TABLE of strings or multiple primitive inputs is out of scope; keep primitive list
        return [InPort(name="input", accept_types={Schema.DataType.STR})], [OutPort(name="output")]

    def validate_input(self, input: dict[str, Data]) -> None:
        pass

    def infer_output_schema(self, input_schema: dict[str, Schema]) -> dict[str, Schema]:
        return {"output": Schema(type=Schema.DataType.STR)}

    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        v = input["input"].payload
        assert isinstance(v, str)
        # If user wants to merge a delimited string, just return as-is
        res = v
        self.vis = Visualization(node_id=self.id, type=Visualization.Type.STR, payload=res)
        return {"output": Data(sche=Schema(type=Schema.DataType.STR), payload=res)}


class SplitStringNode(BaseNode):
    """Split a string by delimiter and return as TABLE with one column 'value'."""
    delimiter: str
    column_name: str

    def validate_parameters(self) -> None:
        if not self.type == "SplitStringNode":
            raise NodeValidationError("Node type must be 'SplitStringNode'.")
        if self.column_name.strip() == "":
            raise NodeValidationError("column_name cannot be empty")

    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [InPort(name="input", accept_types={Schema.DataType.STR})], [OutPort(name="output")]

    def validate_input(self, input: dict[str, Data]) -> None:
        pass

    def infer_output_schema(self, input_schema: dict[str, Schema]) -> dict[str, Schema]:
        cols = {self.column_name: {Schema.ColumnType.STR}}
        return {"output": Schema(type=Schema.DataType.TABLE, columns=cols)}

    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        from pandas import DataFrame
        v = input["input"].payload
        assert isinstance(v, str)
        parts = v.split(self.delimiter)
        df = DataFrame({self.column_name: parts})
        self.vis = Visualization(node_id=self.id, type=Visualization.Type.TABLE, payload=df)
        return {"output": Data(sche=Schema(type=Schema.DataType.TABLE, columns={self.column_name: {Schema.ColumnType.STR}}), payload=df)}


class UpperStringNode(BaseNode):
    """Convert string to upper case."""
    def validate_parameters(self) -> None:
        if not self.type == "UpperStringNode":
            raise NodeValidationError("Node type must be 'UpperStringNode'.")

    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [InPort(name="input", accept_types={Schema.DataType.STR})], [OutPort(name="output")]

    def validate_input(self, input: dict[str, Data]) -> None:
        pass

    def infer_output_schema(self, input_schema: dict[str, Schema]) -> dict[str, Schema]:
        return {"output": Schema(type=Schema.DataType.STR)}

    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        v = input["input"].payload
        assert isinstance(v, str)
        res = v.upper()
        self.vis = Visualization(node_id=self.id, type=Visualization.Type.STR, payload=res)
        return {"output": Data(sche=Schema(type=Schema.DataType.STR), payload=res)}


class LowerStringNode(BaseNode):
    """Convert string to lower case."""
    def validate_parameters(self) -> None:
        if not self.type == "LowerStringNode":
            raise NodeValidationError("Node type must be 'LowerStringNode'.")

    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [InPort(name="input", accept_types={Schema.DataType.STR})], [OutPort(name="output")]

    def validate_input(self, input: dict[str, Data]) -> None:
        pass

    def infer_output_schema(self, input_schema: dict[str, Schema]) -> dict[str, Schema]:
        return {"output": Schema(type=Schema.DataType.STR)}

    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        v = input["input"].payload
        assert isinstance(v, str)
        res = v.lower()
        self.vis = Visualization(node_id=self.id, type=Visualization.Type.STR, payload=res)
        return {"output": Data(sche=Schema(type=Schema.DataType.STR), payload=res)}

"""
The operator nodes between str input and table input.
"""
class TableAppendStringNode(BaseNode):
    """Append a single string to every value in a table column and write to result_col."""
    column: str
    result_col: str

    def validate_parameters(self) -> None:
        if not self.type == "TableAppendStringNode":
            raise NodeValidationError("Node type must be 'TableAppendStringNode'.")
        if self.column == "" or self.column.strip() == "":
            raise NodeValidationError("column cannot be empty.")
        if self.result_col == "" or self.result_col.strip() == "":
            raise NodeValidationError("result_col cannot be empty.")
        validate_no_index_column_conflict([self.result_col])

    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [
            InPort(
                name="table_input",
                accept_types={Schema.DataType.TABLE},
                table_columns={self.column: {Schema.ColumnType.STR}},
                description="Input table",
                required=True,
            ),
            InPort(
                name="value_input",
                accept_types={Schema.DataType.STR},
                description="String to append",
                required=True,
            ),
        ], [OutPort(name="output", description="Output table with appended column")] 

    def validate_input(self, input: dict[str, Data]) -> None:
        pass

    def _compute_output_schema(self, input_schema: dict[str, Schema]) -> Schema:
        input_cols = input_schema["table_input"].columns
        assert(input_cols is not None)
        if self.result_col in input_cols:
            raise NodeValidationError(f"result_col '{self.result_col}' already exists in input table.")
        return Schema(type=Schema.DataType.TABLE, columns={self.result_col: {Schema.ColumnType.STR}} | input_cols)

    def infer_output_schema(self, input_schema: dict[str, Schema]) -> dict[str, Schema]:
        return {"output": self._compute_output_schema(input_schema)}

    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        table_data = input["table_input"].payload
        value = input["value_input"].payload
        assert(isinstance(table_data, DataFrame))
        assert(isinstance(value, str))

        result_rows = table_data.copy()
        # ensure string type then vectorized append
        result_rows[self.result_col] = result_rows[self.column].astype(str) + value

        self.vis = Visualization(node_id=self.id, type=Visualization.Type.TABLE, payload=result_rows)

        return {"output": Data(sche=self._compute_output_schema({"table_input": input["table_input"].sche}), payload=result_rows)}


class TablePrependStringNode(BaseNode):
    """Prepend a single string to every value in a table column and write to result_col."""
    column: str
    result_col: str

    def validate_parameters(self) -> None:
        if not self.type == "TablePrependStringNode":
            raise NodeValidationError("Node type must be 'TablePrependStringNode'.")
        if self.column == "" or self.column.strip() == "":
            raise NodeValidationError("column cannot be empty.")
        if self.result_col == "" or self.result_col.strip() == "":
            raise NodeValidationError("result_col cannot be empty.")
        validate_no_index_column_conflict([self.result_col])

    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [
            InPort(
                name="table_input",
                accept_types={Schema.DataType.TABLE},
                table_columns={self.column: {Schema.ColumnType.STR}},
                description="Input table",
                required=True,
            ),
            InPort(
                name="value_input",
                accept_types={Schema.DataType.STR},
                description="String to prepend",
                required=True,
            ),
        ], [OutPort(name="output", description="Output table with prepended column")] 

    def validate_input(self, input: dict[str, Data]) -> None:
        pass

    def _compute_output_schema(self, input_schema: dict[str, Schema]) -> Schema:
        input_cols = input_schema["table_input"].columns
        assert(input_cols is not None)
        if self.result_col in input_cols:
            raise NodeValidationError(f"result_col '{self.result_col}' already exists in input table.")
        return Schema(type=Schema.DataType.TABLE, columns={self.result_col: {Schema.ColumnType.STR}} | input_cols)

    def infer_output_schema(self, input_schema: dict[str, Schema]) -> dict[str, Schema]:
        return {"output": self._compute_output_schema(input_schema)}

    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        table_data = input["table_input"].payload
        value = input["value_input"].payload
        assert(isinstance(table_data, DataFrame))
        assert(isinstance(value, str))

        result_rows = table_data.copy()
        result_rows[self.result_col] = value + result_rows[self.column].astype(str)

        self.vis = Visualization(node_id=self.id, type=Visualization.Type.TABLE, payload=result_rows)

        return {"output": Data(sche=self._compute_output_schema({"table_input": input["table_input"].sche}), payload=result_rows)}


class TableContainsStringNode(BaseNode):
    """Check whether each value in a table column contains a given substring, output boolean column."""
    column: str
    result_col: str

    def validate_parameters(self) -> None:
        if not self.type == "TableContainsStringNode":
            raise NodeValidationError("Node type must be 'TableContainsStringNode'.")
        if self.column == "" or self.column.strip() == "":
            raise NodeValidationError("column cannot be empty.")
        if self.result_col == "" or self.result_col.strip() == "":
            raise NodeValidationError("result_col cannot be empty.")
        validate_no_index_column_conflict([self.result_col])

    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [
            InPort(
                name="table_input",
                accept_types={Schema.DataType.TABLE},
                table_columns={self.column: {Schema.ColumnType.STR}},
                description="Input table",
                required=True,
            ),
            InPort(
                name="value_input",
                accept_types={Schema.DataType.STR},
                description="Substring to search for",
                required=True,
            ),
        ], [OutPort(name="output", description="Output table with boolean result column")] 

    def validate_input(self, input: dict[str, Data]) -> None:
        pass

    def _compute_output_schema(self, input_schema: dict[str, Schema]) -> Schema:
        input_cols = input_schema["table_input"].columns
        assert(input_cols is not None)
        if self.result_col in input_cols:
            raise NodeValidationError(f"result_col '{self.result_col}' already exists in input table.")
        return Schema(type=Schema.DataType.TABLE, columns={self.result_col: {Schema.ColumnType.BOOL}} | input_cols)

    def infer_output_schema(self, input_schema: dict[str, Schema]) -> dict[str, Schema]:
        return {"output": self._compute_output_schema(input_schema)}

    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        table_data = input["table_input"].payload
        value = input["value_input"].payload
        assert(isinstance(table_data, DataFrame))
        assert(isinstance(value, str))

        result_rows = table_data.copy()
        result_rows[self.result_col] = result_rows[self.column].astype(str).str.contains(value)

        self.vis = Visualization(node_id=self.id, type=Visualization.Type.TABLE, payload=result_rows)

        return {"output": Data(sche=self._compute_output_schema({"table_input": input["table_input"].sche}), payload=result_rows)}


class TableStartsWithStringNode(BaseNode):
    """Check whether each value in a table column startswith given substring."""
    column: str
    result_col: str

    def validate_parameters(self) -> None:
        if not self.type == "TableStartsWithStringNode":
            raise NodeValidationError("Node type must be 'TableStartsWithStringNode'.")
        if self.column == "" or self.column.strip() == "":
            raise NodeValidationError("column cannot be empty.")
        if self.result_col == "" or self.result_col.strip() == "":
            raise NodeValidationError("result_col cannot be empty.")
        validate_no_index_column_conflict([self.result_col])

    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [
            InPort(
                name="table_input",
                accept_types={Schema.DataType.TABLE},
                table_columns={self.column: {Schema.ColumnType.STR}},
                description="Input table",
                required=True,
            ),
            InPort(
                name="value_input",
                accept_types={Schema.DataType.STR},
                description="Prefix to check",
                required=True,
            ),
        ], [OutPort(name="output", description="Output table with boolean result column")] 

    def validate_input(self, input: dict[str, Data]) -> None:
        pass

    def _compute_output_schema(self, input_schema: dict[str, Schema]) -> Schema:
        input_cols = input_schema["table_input"].columns
        assert(input_cols is not None)
        if self.result_col in input_cols:
            raise NodeValidationError(f"result_col '{self.result_col}' already exists in input table.")
        return Schema(type=Schema.DataType.TABLE, columns={self.result_col: {Schema.ColumnType.BOOL}} | input_cols)

    def infer_output_schema(self, input_schema: dict[str, Schema]) -> dict[str, Schema]:
        return {"output": self._compute_output_schema(input_schema)}

    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        table_data = input["table_input"].payload
        value = input["value_input"].payload
        assert(isinstance(table_data, DataFrame))
        assert(isinstance(value, str))

        result_rows = table_data.copy()
        result_rows[self.result_col] = result_rows[self.column].astype(str).str.startswith(value)

        self.vis = Visualization(node_id=self.id, type=Visualization.Type.TABLE, payload=result_rows)

        return {"output": Data(sche=self._compute_output_schema({"table_input": input["table_input"].sche}), payload=result_rows)}


class TableEndsWithStringNode(BaseNode):
    """Check whether each value in a table column endswith given substring."""
    column: str
    result_col: str

    def validate_parameters(self) -> None:
        if not self.type == "TableEndsWithStringNode":
            raise NodeValidationError("Node type must be 'TableEndsWithStringNode'.")
        if self.column == "" or self.column.strip() == "":
            raise NodeValidationError("column cannot be empty.")
        if self.result_col == "" or self.result_col.strip() == "":
            raise NodeValidationError("result_col cannot be empty.")
        validate_no_index_column_conflict([self.result_col])

    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [
            InPort(
                name="table_input",
                accept_types={Schema.DataType.TABLE},
                table_columns={self.column: {Schema.ColumnType.STR}},
                description="Input table",
                required=True,
            ),
            InPort(
                name="value_input",
                accept_types={Schema.DataType.STR},
                description="Suffix to check",
                required=True,
            ),
        ], [OutPort(name="output", description="Output table with boolean result column")] 

    def validate_input(self, input: dict[str, Data]) -> None:
        pass

    def _compute_output_schema(self, input_schema: dict[str, Schema]) -> Schema:
        input_cols = input_schema["table_input"].columns
        assert(input_cols is not None)
        if self.result_col in input_cols:
            raise NodeValidationError(f"result_col '{self.result_col}' already exists in input table.")
        return Schema(type=Schema.DataType.TABLE, columns={self.result_col: {Schema.ColumnType.BOOL}} | input_cols)

    def infer_output_schema(self, input_schema: dict[str, Schema]) -> dict[str, Schema]:
        return {"output": self._compute_output_schema(input_schema)}

    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        table_data = input["table_input"].payload
        value = input["value_input"].payload
        assert(isinstance(table_data, DataFrame))
        assert(isinstance(value, str))

        result_rows = table_data.copy()
        result_rows[self.result_col] = result_rows[self.column].astype(str).str.endswith(value)

        self.vis = Visualization(node_id=self.id, type=Visualization.Type.TABLE, payload=result_rows)

        return {"output": Data(sche=self._compute_output_schema({"table_input": input["table_input"].sche}), payload=result_rows)}


class TableReplaceStringNode(BaseNode):
    """Replace occurrences of old substring with new substring for each value in a table column."""
    column: str
    result_col: str

    def validate_parameters(self) -> None:
        if not self.type == "TableReplaceStringNode":
            raise NodeValidationError("Node type must be 'TableReplaceStringNode'.")
        if self.column == "" or self.column.strip() == "":
            raise NodeValidationError("column cannot be empty.")
        if self.result_col == "" or self.result_col.strip() == "":
            raise NodeValidationError("result_col cannot be empty.")
        validate_no_index_column_conflict([self.result_col])

    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [
            InPort(
                name="table_input",
                accept_types={Schema.DataType.TABLE},
                table_columns={self.column: {Schema.ColumnType.STR}},
                description="Input table",
                required=True,
            ),
            InPort(
                name="old_input",
                accept_types={Schema.DataType.STR},
                description="Old substring",
                required=True,
            ),
            InPort(
                name="new_input",
                accept_types={Schema.DataType.STR},
                description="New substring",
                required=True,
            ),
        ], [OutPort(name="output", description="Output table with replaced strings")] 

    def validate_input(self, input: dict[str, Data]) -> None:
        pass

    def _compute_output_schema(self, input_schema: dict[str, Schema]) -> Schema:
        input_cols = input_schema["table_input"].columns
        assert(input_cols is not None)
        if self.result_col in input_cols:
            raise NodeValidationError(f"result_col '{self.result_col}' already exists in input table.")
        return Schema(type=Schema.DataType.TABLE, columns={self.result_col: {Schema.ColumnType.STR}} | input_cols)

    def infer_output_schema(self, input_schema: dict[str, Schema]) -> dict[str, Schema]:
        return {"output": self._compute_output_schema(input_schema)}

    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        table_data = input["table_input"].payload
        old = input["old_input"].payload
        new = input["new_input"].payload
        assert(isinstance(table_data, DataFrame))
        assert(isinstance(old, str) and isinstance(new, str))

        result_rows = table_data.copy()
        # pandas replace on series
        result_rows[self.result_col] = result_rows[self.column].astype(str).str.replace(old, new)

        self.vis = Visualization(node_id=self.id, type=Visualization.Type.TABLE, payload=result_rows)

        return {"output": Data(sche=self._compute_output_schema({"table_input": input["table_input"].sche}), payload=result_rows)}

