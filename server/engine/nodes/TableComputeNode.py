from .BaseNode import BaseNode, InPort, OutPort, Data, Schema, NodeValidationError
from .Utils import Visualization, validate_no_index_column_conflict
from pandas import DataFrame
from typing import Literal
import operator

"""
A series of nodes to compute columns of tables vectorizedly.
Each node corresponds to a specific node in ComputeNode.py.
"""


class TableBinNumComputeNode(BaseNode):
	"""
	Compute binary numeric operation on a table column and either a primitive value
	or another table column. The result is appended as a new column.
	Supported ops: ADD, SUB, MUL, DIV, POW
	"""
	op: Literal["ADD", "SUB", "MUL", "DIV", "POW"]
	left_col: str
	right_col: str | None = None  # if None, use primitive input 'value'
	result_col: str

	_OP_MAP = {
		"ADD": operator.add,
		"SUB": operator.sub,
		"MUL": operator.mul,
		"DIV": operator.truediv,
		"POW": operator.pow,
	}

	def validate_parameters(self) -> None:
		if not self.type == "TableBinNumComputeNode":
			raise NodeValidationError("Node type must be 'TableBinNumComputeNode'.")
		if self.left_col.strip() == "":
			raise NodeValidationError("left_col cannot be empty")
		if self.result_col.strip() == "":
			raise NodeValidationError("result_col cannot be empty")
		validate_no_index_column_conflict([self.result_col])

	def port_def(self) -> tuple[list[InPort], list[OutPort]]:
		# left table required, right can be table or primitive 'value'
		return [
			InPort(name="table", accept_types={Schema.DataType.TABLE}, table_columns={self.left_col: {Schema.ColumnType.INT, Schema.ColumnType.FLOAT}}),
			InPort(name="value", accept_types={Schema.DataType.INT, Schema.DataType.FLOAT}, required=(self.right_col is None)),
			InPort(name="table_right", accept_types={Schema.DataType.TABLE}, table_columns=(None if self.right_col is None else {self.right_col: {Schema.ColumnType.INT, Schema.ColumnType.FLOAT}}), required=(self.right_col is not None)),
		], [OutPort(name="output")]

	def validate_input(self, input: dict[str, Data]) -> None:
		# runtime payload checks and reuse static schema computation
		if "table" not in input:
			raise NodeValidationError("Missing 'table' input at runtime")
		df = input["table"].payload
		from pandas import DataFrame
		if not isinstance(df, DataFrame):
			raise NodeValidationError("Payload for 'table' must be a DataFrame")
		if len(df) == 0:
			raise NodeValidationError("Input table is empty")
		if self.left_col not in df.columns:
			raise NodeValidationError(f"Left column '{self.left_col}' not found in payload DataFrame.")

		if self.right_col is not None:
			if "table_right" not in input:
				raise NodeValidationError("Missing 'table_right' input at runtime")
			rdf = input["table_right"].payload
			if not isinstance(rdf, DataFrame):
				raise NodeValidationError("Payload for 'table_right' must be a DataFrame")
			if self.right_col not in rdf.columns:
				raise NodeValidationError(f"Right column '{self.right_col}' not found in table_right payload.")
		else:
			if "value" not in input:
				raise NodeValidationError("Missing 'value' input at runtime")
			val = input["value"].payload
			if not isinstance(val, (int, float)):
				raise NodeValidationError("value must be numeric")

		# reuse static checks that validate columns etc. using schemas
		schema_dict = {k: v.sche for k, v in input.items()}
		self._compute_output_schema(schema_dict)

	def _compute_output_schema(self, input_schema: dict[str, Schema]) -> Schema:
		# Strict static checks: require table schema and column info
		if "table" not in input_schema:
			raise NodeValidationError("Missing schema for 'table' input")
		table_schema = input_schema["table"]
		if table_schema.columns is None:
			raise NodeValidationError("Input table schema must include columns information.")
		if self.left_col not in table_schema.columns:
			raise NodeValidationError(f"Left column '{self.left_col}' not found in table schema.")
		table_cols = table_schema.columns
		if self.result_col in table_cols:
			raise NodeValidationError(f"result_col '{self.result_col}' already exists in input table.")
		# result is FLOAT if either operand FLOAT or op is DIV
		# determine left column declared types (fallback to numeric set if unknown)
		if input_schema["table"].columns is not None and self.left_col in input_schema["table"].columns:
			left_types = input_schema["table"].columns[self.left_col]
		else:
			left_types = {Schema.ColumnType.INT, Schema.ColumnType.FLOAT}
		right_is_float = False
		if self.right_col is not None:
			# table_right must be present in input_schema when right_col is used
			if "table_right" not in input_schema:
				raise NodeValidationError("Missing schema for table_right")
			right_schema = input_schema["table_right"]
			if right_schema.columns is None:
				raise NodeValidationError("table_right schema must include columns information.")
			if self.right_col not in right_schema.columns:
				raise NodeValidationError(f"Right column '{self.right_col}' not found in table_right schema.")
			right_types = right_schema.columns[self.right_col]
			right_is_float = Schema.ColumnType.FLOAT in right_types
		else:
			if "value" not in input_schema:
				raise NodeValidationError("Missing schema for value")
			vtype = input_schema["value"].type
			right_is_float = (vtype == Schema.DataType.FLOAT)

		left_is_float = Schema.ColumnType.FLOAT in left_types
		if self.op == "DIV" or left_is_float or right_is_float:
			result_col_type = Schema.ColumnType.FLOAT
		else:
			result_col_type = Schema.ColumnType.INT

		new_cols = {**(input_schema["table"].columns or {}), self.result_col: {result_col_type}}
		return Schema(type=Schema.DataType.TABLE, columns=new_cols)

	def infer_output_schema(self, input_schema: dict[str, Schema]) -> dict[str, Schema]:
		return {"output": self._compute_output_schema(input_schema)}

	def process(self, input: dict[str, Data]) -> dict[str, Data]:
		# assume validate_input has already checked presence/columns and types
		df = input["table"].payload
		assert isinstance(df, DataFrame), "Payload for 'table' must be a DataFrame"
		left_ser = df[self.left_col]

		if self.right_col is not None:
			right_df = input["table_right"].payload
			assert isinstance(right_df, DataFrame), "Payload for 'table_right' must be a DataFrame"
			right_ser = right_df[self.right_col]
			op_func = self._OP_MAP[self.op]
			result = op_func(left_ser, right_ser)
		else:
			value = input["value"].payload
			assert isinstance(value, (int, float))
			op_func = self._OP_MAP[self.op]
			result = op_func(left_ser, value)

		result_df = df.copy()
		result_df[self.result_col] = result

		self.vis = Visualization(node_id=self.id, type=Visualization.Type.TABLE, payload=result_df)
		# build schema dict only with available inputs
		schema_dict: dict[str, Schema] = {"table": input["table"].sche}
		if "table_right" in input:
			schema_dict["table_right"] = input["table_right"].sche
		if "value" in input:
			schema_dict["value"] = input["value"].sche
		out_schema = self._compute_output_schema(schema_dict)
		return {"output": Data(sche=out_schema, payload=result_df)}


class TableUnaryNumComputeNode(BaseNode):
	"""
	Compute unary numeric operation on a table column and append result.
	Supported ops: NEG, ABS, SQRT
	"""
	op: Literal["NEG", "ABS", "SQRT"]
	column: str
	result_col: str

	def validate_parameters(self) -> None:
		if not self.type == "TableUnaryNumComputeNode":
			raise NodeValidationError("Node type must be 'TableUnaryNumComputeNode'.")
		if self.column.strip() == "":
			raise NodeValidationError("column cannot be empty")
		if self.result_col.strip() == "":
			raise NodeValidationError("result_col cannot be empty")
		validate_no_index_column_conflict([self.result_col])

	def port_def(self) -> tuple[list[InPort], list[OutPort]]:
		return [InPort(name="table", accept_types={Schema.DataType.TABLE}, table_columns={self.column: {Schema.ColumnType.INT, Schema.ColumnType.FLOAT}})], [OutPort(name="output")]

	def validate_input(self, input: dict[str, Data]) -> None:
		# runtime checks for presence and payload types + reuse static schema check
		if "table" not in input:
			raise NodeValidationError("Missing 'table' input at runtime")
		df = input["table"].payload
		from pandas import DataFrame
		if not isinstance(df, DataFrame):
			raise NodeValidationError("Payload for 'table' must be a DataFrame")
		if self.column not in df.columns:
			raise NodeValidationError(f"Column '{self.column}' not found in payload DataFrame.")
		# reuse static schema computation
		self._compute_output_schema({"table": input["table"].sche})

	def _compute_output_schema(self, input_schema: dict[str, Schema]) -> Schema:
		# Strict static checks: require table schema and column info
		if "table" not in input_schema:
			raise NodeValidationError("Missing schema for 'table' input")
		table_schema = input_schema["table"]
		if table_schema.columns is None:
			raise NodeValidationError("Input table schema must include columns information.")
		if self.column not in table_schema.columns:
			raise NodeValidationError(f"Column '{self.column}' not found in table schema.")
		cols = table_schema.columns
		if self.result_col in cols:
			raise NodeValidationError(f"result_col '{self.result_col}' already exists in input table.")
		# SQRT produces float
		if self.op == "SQRT":
			res_type = Schema.ColumnType.FLOAT
		else:
			# preserve input numeric type if possible
			in_types = table_schema.columns[self.column]
			res_type = Schema.ColumnType.FLOAT if Schema.ColumnType.FLOAT in in_types else Schema.ColumnType.INT
		new_cols = {**cols, self.result_col: {res_type}}
		return Schema(type=Schema.DataType.TABLE, columns=new_cols)

	def infer_output_schema(self, input_schema: dict[str, Schema]) -> dict[str, Schema]:
		return {"output": self._compute_output_schema(input_schema)}

	def process(self, input: dict[str, Data]) -> dict[str, Data]:
		# assume validate_input performed payload checks
		df = input["table"].payload
		assert isinstance(df, DataFrame), "Payload for 'table' must be a DataFrame"
		ser = df[self.column]
		if self.op == "NEG":
			res = -ser
		elif self.op == "ABS":
			res = ser.abs()
		elif self.op == "SQRT":
			# vectorized sqrt: cast to float and use Series.pow
			res = ser.astype(float).pow(0.5)
		else:
			raise NodeValidationError(f"Unsupported op: {self.op}")

		out_df = df.copy()
		out_df[self.result_col] = res
		self.vis = Visualization(node_id=self.id, type=Visualization.Type.TABLE, payload=out_df)
		out_schema = self._compute_output_schema({"table": input["table"].sche})
		return {"output": Data(sche=out_schema, payload=out_df)}


class TableBoolBinComputeNode(BaseNode):
	"""
	Compute boolean binary operation on table columns or column vs primitive, append result bool column.
	Supported ops: AND, OR, XOR, SUB
	"""
	op: Literal["AND", "OR", "XOR", "SUB"]
	left_col: str
	right_col: str | None = None
	result_col: str

	_OP_MAP = {
		"AND": operator.and_,
		"OR": operator.or_,
		"XOR": operator.xor,
		# SUB treated as left and not right
	}

	def validate_parameters(self) -> None:
		if not self.type == "TableBoolBinComputeNode":
			raise NodeValidationError("Node type must be 'TableBoolBinComputeNode'.")
		if self.left_col.strip() == "":
			raise NodeValidationError("left_col cannot be empty")
		if self.result_col.strip() == "":
			raise NodeValidationError("result_col cannot be empty")
		validate_no_index_column_conflict([self.result_col])

	def port_def(self) -> tuple[list[InPort], list[OutPort]]:
		return [
			InPort(name="table", accept_types={Schema.DataType.TABLE}, table_columns={self.left_col: {Schema.ColumnType.BOOL}}),
			InPort(name="table_right", accept_types={Schema.DataType.TABLE}, table_columns=(None if self.right_col is None else {self.right_col: {Schema.ColumnType.BOOL}}), required=(self.right_col is not None)),
		], [OutPort(name="output")]

	def validate_input(self, input: dict[str, Data]) -> None:
		# ensure table payload and left column exist, and table_right when required
		if "table" not in input:
			raise NodeValidationError("Missing 'table' input at runtime")
		df = input["table"].payload
		from pandas import DataFrame
		if not isinstance(df, DataFrame):
			raise NodeValidationError("Payload for 'table' must be a DataFrame")
		if self.left_col not in df.columns:
			raise NodeValidationError(f"Left column '{self.left_col}' not found in payload DataFrame.")
		if self.right_col is not None:
			if "table_right" not in input:
				raise NodeValidationError("Missing 'table_right' input at runtime")
			rdf = input["table_right"].payload
			if not isinstance(rdf, DataFrame):
				raise NodeValidationError("Payload for 'table_right' must be a DataFrame")
			if self.right_col not in rdf.columns:
				raise NodeValidationError(f"Right column '{self.right_col}' not found in table_right payload.")
		# reuse static checks
		schema_dict: dict[str, Schema] = {"table": input["table"].sche}
		if "table_right" in input:
			schema_dict["table_right"] = input["table_right"].sche
		self._compute_output_schema(schema_dict)

	def _compute_output_schema(self, input_schema: dict[str, Schema]) -> Schema:
		# Strict static checks: require table schema and column info
		if "table" not in input_schema:
			raise NodeValidationError("Missing schema for 'table' input")
		table_schema = input_schema["table"]
		if table_schema.columns is None:
			raise NodeValidationError("Input table schema must include columns information.")
		if self.left_col not in table_schema.columns:
			raise NodeValidationError(f"Left column '{self.left_col}' not found in table schema.")
		cols = table_schema.columns
		if self.result_col in cols:
			raise NodeValidationError(f"result_col '{self.result_col}' already exists in input table.")
		# if right_col present, check table_right schema
		if self.right_col is not None:
			if "table_right" not in input_schema:
				raise NodeValidationError("Missing schema for table_right")
			right_schema = input_schema["table_right"]
			if right_schema.columns is None:
				raise NodeValidationError("table_right schema must include columns information.")
			if self.right_col not in right_schema.columns:
				raise NodeValidationError(f"Right column '{self.right_col}' not found in table_right schema.")
		new_cols = {**cols, self.result_col: {Schema.ColumnType.BOOL}}
		return Schema(type=Schema.DataType.TABLE, columns=new_cols)

	def infer_output_schema(self, input_schema: dict[str, Schema]) -> dict[str, Schema]:
		return {"output": self._compute_output_schema(input_schema)}

	def process(self, input: dict[str, Data]) -> dict[str, Data]:
		# runtime: ensure table payload is DataFrame and has left_col
		if "table" not in input:
			raise NodeValidationError("Missing 'table' input at runtime")
		df = input["table"].payload
		assert isinstance(df, DataFrame), "Payload for 'table' must be a DataFrame"
		if self.left_col not in df.columns:
			raise NodeValidationError(f"Left column '{self.left_col}' not found in payload DataFrame.")
		left_ser = df[self.left_col]
		if self.right_col is not None:
			if "table_right" not in input:
				raise NodeValidationError("Missing 'table_right' input at runtime")
			right_df = input["table_right"].payload
			assert isinstance(right_df, DataFrame), "Payload for 'table_right' must be a DataFrame"
			if self.right_col not in right_df.columns:
				raise NodeValidationError(f"Right column '{self.right_col}' not found in table_right payload.")
			right_ser = right_df[self.right_col]
			if self.op == "SUB":
				result = left_ser & (~right_ser)
			else:
				op_func = self._OP_MAP[self.op]
				result = op_func(left_ser, right_ser).astype(bool)
		else:
			raise NodeValidationError("Right column must be provided for TableBoolBinComputeNode")

		out_df = df.copy()
		out_df[self.result_col] = result
		self.vis = Visualization(node_id=self.id, type=Visualization.Type.TABLE, payload=out_df)
		# build schema dict including optional inputs like table_right
		schema_dict: dict[str, Schema] = {"table": input["table"].sche}
		if "table_right" in input:
			schema_dict["table_right"] = input["table_right"].sche
		out_schema = self._compute_output_schema(schema_dict)
		return {"output": Data(sche=out_schema, payload=out_df)}

