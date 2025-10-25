from ..BaseNode import BaseNode,InPort, OutPort, register_node
from typing import Literal, override
from server.models.exception import NodeParameterError, NodeValidationError, NodeExecutionError
from server.models.data import Table, Data
from server.models.schema import (
    Pattern,
    Schema,
    generate_default_col_name,
    check_no_illegal_cols,
    ColType,
)
import numpy as np

"""
A series of nodes to compute columns of tables vectorizedly.
Each node corresponds to a specific node in ComputeNode.py.
"""

"""
Calculate between primitive and table column.
"""

@register_node
class TabBinPrimNumComputeNode(BaseNode):
    """
    Compute binary numeric operation on a table column a primitive number.
    Supported ops: ADD, SUB, MUL, DIV, POW
    """
    op: Literal["ADD", "SUB", "MUL", "TAB_DIV_PRIM", "PRIM_DIV_TAB", "TAB_POW_PRIM", "PRIM_POW_TAB"]
    col: str # the column to operate on
    result_col: str | None = None  # if None, use default result col name

    @override
    def validate_parameters(self) -> None:
        if not self.type == "TabBinPrimNumComputeNode":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="type",
                err_msg="Node type must be 'TabBinPrimNumComputeNode'."
            )
        if self.col.strip() == "":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="col",
                err_msg="Column name cannot be empty."
            )
        if self.result_col is None:
            self.result_col = generate_default_col_name(self.id, "result")
        if self.result_col.strip() == "":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="result_col",
                err_msg="Result column name cannot be empty."
            )
        if self.col == self.result_col:
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="result_col",
                err_msg="Result column name cannot be the same as input column name."
            )
        if check_no_illegal_cols([self.result_col]) is False:
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="result_col",
                err_msg="Result column name cannot start with reserved prefix '_' or be whitespace only."
            )
        return

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [
            InPort(name='table', description='Input table', accept=Pattern(types={Schema.Type.TABLE}, table_columns={self.col: {ColType.INT, ColType.FLOAT}}), optional=False),
            InPort(name='num', description='Input primitive number', accept=Pattern(types={Schema.Type.INT, Schema.Type.FLOAT}), optional=False)
        ], [
            OutPort(name='table', description='Output table with computed column')
        ]

    @override
    def infer_output_schemas(self, input_schemas: dict[str, Schema]) -> dict[str, Schema]:
        assert input_schemas['table'].tab is not None
        in_tab = input_schemas['table'].tab

        # 1. check if new column name is exists
        assert self.result_col is not None
        if not in_tab.validate_new_col_name(self.result_col):
            raise NodeValidationError(
                node_id=self.id,
                err_input='table',
                err_msg=f"Result column name '{self.result_col}' already exists in input table."
            )
        # 2. check if the table col and the num is in same type
        col_type = in_tab.col_types.get(self.col)
        assert col_type is not None
        num_type = input_schemas['num']
        if col_type != num_type:
            raise NodeValidationError(
                node_id=self.id,
                err_inputs=['table', 'num'],
                err_msgs=["",
                        f"Table column '{self.col}' type '{col_type}' does not match primitive number type '{num_type}'."]
            )
        # 3. build output schema
        res_col_type = None
        if self.op in {"ADD", "SUB", "MUL"}:
            res_col_type = col_type
        else:
            res_col_type = ColType.FLOAT
        output_schema = input_schemas['table'].append_col(self.result_col, res_col_type)

        return {'table': output_schema}

    @override
    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        table = input['table'].payload
        num = input['num'].payload
        assert isinstance(table, Table)
        assert isinstance(num, (int, float))
        assert self.result_col is not None

        df = table.df.copy()
        series = df[self.col]
        
        if self.op == "ADD":
            df[self.result_col] = series + num
        elif self.op == "SUB":
            df[self.result_col] = series - num
        elif self.op == "MUL":
            df[self.result_col] = series * num
        elif self.op == "TAB_DIV_PRIM":
            if num == 0:
                raise NodeExecutionError(
                    node_id=self.id,
                    err_msg="Division by zero error."
                )
            df[self.result_col] = series / num
        elif self.op == "PRIM_DIV_TAB":
            # Check for division by zero, but NaN values should be preserved
            if (series == 0).any():
                raise NodeExecutionError(
                    node_id=self.id,
                    err_msg="Division by zero error."
                )
            df[self.result_col] = num / series
        elif self.op == "TAB_POW_PRIM":
            df[self.result_col] = series ** num
        elif self.op == "PRIM_POW_TAB":
            df[self.result_col] = num ** series
        else:
            raise NodeExecutionError(
                node_id=self.id,
                err_msg=f"Unsupported operation '{self.op}'."
            )
        
        # convert back to Table
        out_table = Data.from_df(df)
        return {'table': out_table}

@register_node
class TabBinPrimBoolComputeNode(BaseNode):
    """
    Compute binary boolean operation on a table column a primitive number.
    Supported ops: AND, OR, XOR, SUB
    """
    op: Literal["AND", "OR", "XOR", "PRIM_SUB_TAB", "TAB_SUB_PRIM"]
    col: str # the column to operate on
    result_col: str | None = None  # if None, use default result col name

    @override
    def validate_parameters(self) -> None:
        if not self.type == "TabBinPrimBoolComputeNode":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="type",
                err_msg="Node type must be 'TabBinPrimBoolComputeNode'."
            )
        if self.col.strip() == "":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="col",
                err_msg="Column name cannot be empty."
            )
        if self.result_col is None:
            self.result_col = generate_default_col_name(self.id, "result")
        if self.result_col.strip() == "":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="result_col",
                err_msg="Result column name cannot be empty."
            )
        if self.col == self.result_col:
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="result_col",
                err_msg="Result column name cannot be the same as input column name."
            )
        if check_no_illegal_cols([self.result_col]) is False:
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="result_col",
                err_msg="Result column name cannot start with reserved prefix '_' or be whitespace only."
            )
        return

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [
            InPort(name='table', description='Input table', accept=Pattern(types={Schema.Type.TABLE}, table_columns={self.col: {ColType.BOOL}}), optional=False),
            InPort(name='bool', description='Input primitive boolean', accept=Pattern(types={Schema.Type.BOOL}), optional=False)
        ], [
            OutPort(name='table', description='Output table with computed column')
        ]

    @override
    def infer_output_schemas(self, input_schemas: dict[str, Schema]) -> dict[str, Schema]:
        assert input_schemas['table'].tab is not None
        in_tab = input_schemas['table'].tab

        # 1. check if new column name is exists
        assert self.result_col is not None
        if not in_tab.validate_new_col_name(self.result_col):
            raise NodeValidationError(
                node_id=self.id,
                err_input='table',
                err_msg=f"Result column name '{self.result_col}' already exists in input table."
            )
        
        # 2. check if the table col and the bool is in same type
        col_type = in_tab.col_types.get(self.col)
        assert col_type is not None
        if col_type != ColType.BOOL:
            raise NodeValidationError(
                node_id=self.id,
                err_input='table',
                err_msg=f"Table column '{self.col}' type '{col_type}' is not boolean."
            )
        
        # 3. build output schema
        output_schema = input_schemas['table'].append_col(self.result_col, ColType.BOOL)
        return {"table": output_schema}

    @override
    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        table = input['table'].payload
        boolean = input['bool'].payload
        assert isinstance(table, Table)
        assert isinstance(boolean, bool)
        assert self.result_col is not None

        df = table.df.copy()
        series = df[self.col]
        
        if self.op == "AND":
            df[self.result_col] = series & boolean
        elif self.op == "OR":
            df[self.result_col] = series | boolean
        elif self.op == "XOR":
            df[self.result_col] = series ^ boolean
        elif self.op == "TAB_SUB_PRIM":
            df[self.result_col] = series & (not boolean)
        elif self.op == "PRIM_SUB_TAB":
            df[self.result_col] = boolean & ~series
        else:
            raise NodeExecutionError(
                node_id=self.id,
                err_msg=f"Unsupported operation '{self.op}'."
            )
        
        # convert back to Table
        out_table = Data.from_df(df)
        return {'table': out_table}


"""
Calculate in one column.
"""

@register_node
class TabUnaryNumComputeNode(BaseNode):
    """
    Compute unary numeric operation on a table column.
    Supported ops: ABS, NEG, EXP, LOG, SQRT
    """
    op: Literal["ABS", "NEG", "EXP", "LOG", "SQRT"]
    col: str # the column to operate on
    result_col: str | None = None  # if None, use default result col name

    @override
    def validate_parameters(self) -> None:
        if not self.type == "TabUnaryNumComputeNode":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="type",
                err_msg="Node type must be 'TabUnaryNumComputeNode'."
            )
        if self.col.strip() == "":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="col",
                err_msg="Column name cannot be empty."
            )
        if self.result_col is None:
            self.result_col = generate_default_col_name(self.id, "result")
        if self.result_col.strip() == "":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="result_col",
                err_msg="Result column name cannot be empty."
            )
        if self.col == self.result_col:
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="result_col",
                err_msg="Result column name cannot be the same as input column name."
            )
        if check_no_illegal_cols([self.result_col]) is False:
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="result_col",
                err_msg="Result column name cannot start with reserved prefix '_' or be whitespace only."
            )
        return

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [
            InPort(name='table', description='Input table', accept=Pattern(types={Schema.Type.TABLE}, table_columns={self.col: {ColType.INT, ColType.FLOAT}}), optional=False)
        ], [
            OutPort(name='table', description='Output table with computed column')
        ]

    @override
    def infer_output_schemas(self, input_schemas: dict[str, Schema]) -> dict[str, Schema]:
        assert input_schemas['table'].tab is not None
        in_tab = input_schemas['table'].tab

        # 1. check if new column name is exists
        assert self.result_col is not None
        if not in_tab.validate_new_col_name(self.result_col):
            raise NodeValidationError(
                node_id=self.id,
                err_input='table',
                err_msg=f"Result column name '{self.result_col}' already exists in input table."
            )
        # 2. build output schema
        output_schema = input_schemas['table'].append_col(self.result_col, ColType.FLOAT if self.op in {"LOG", "SQRT"} else in_tab.col_types[self.col])
        
        return {'table': output_schema}

    @override
    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        table = input['table'].payload
        assert isinstance(table, Table)
        assert self.result_col is not None
        
        df = table.df.copy()
        series = df[self.col]
        
        if self.op == "ABS":
            df[self.result_col] = series.abs()
        elif self.op == "NEG":
            df[self.result_col] = -series
        elif self.op == "EXP":
            df[self.result_col] = np.exp(series)
        elif self.op == "LOG":
            if (series <= 0).fillna(False).any():
                raise NodeExecutionError(
                    node_id=self.id,
                    err_msg="Logarithm of non-positive number error."
                )
            df[self.result_col] = np.log(series)
        elif self.op == "SQRT":
            if (series < 0).fillna(False).any():
                raise NodeExecutionError(
                    node_id=self.id,
                    err_msg="Square root of negative number error."
                )
            df[self.result_col] = np.sqrt(series)
        else:
            raise NodeExecutionError(
                node_id=self.id,
                err_msg=f"Unsupported operation '{self.op}'."
            )
        
        # convert back to Table
        out_table = Data.from_df(df)
        return {'table': out_table}

@register_node
class TabUnaryBoolComputeNode(BaseNode):
    """
    Compute unary boolean operation on a table column.
    Supported ops: NOT
    """
    op: Literal["NOT"]
    col: str # the column to operate on
    result_col: str | None = None  # if None, use default result col name

    @override
    def validate_parameters(self) -> None:
        if not self.type == "TabUnaryBoolComputeNode":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="type",
                err_msg="Node type must be 'TabUnaryBoolComputeNode'."
            )
        if self.col.strip() == "":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="col",
                err_msg="Column name cannot be empty."
            )
        if self.result_col is None:
            self.result_col = generate_default_col_name(self.id, "result")
        if self.result_col.strip() == "":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="result_col",
                err_msg="Result column name cannot be empty."
            )
        if self.col == self.result_col:
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="result_col",
                err_msg="Result column name cannot be the same as input column name."
            )
        if check_no_illegal_cols([self.result_col]) is False:
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="result_col",
                err_msg="Result column name cannot start with reserved prefix '_' or be whitespace only."
            )
        return

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [
            InPort(name='table', description='Input table', accept=Pattern(types={Schema.Type.TABLE}, table_columns={self.col: {ColType.BOOL}}), optional=False)
        ], [
            OutPort(name='table', description='Output table with computed column')
        ]

    @override
    def infer_output_schemas(self, input_schemas: dict[str, Schema]) -> dict[str, Schema]:
        assert input_schemas['table'].tab is not None
        in_tab = input_schemas['table'].tab

        # 1. check if new column name is exists
        assert self.result_col is not None
        if not in_tab.validate_new_col_name(self.result_col):
            raise NodeValidationError(
                node_id=self.id,
                err_input='table',
                err_msg=f"Result column name '{self.result_col}' already exists in input table."
            )
        # 2. build output schema
        output_schema = input_schemas['table'].append_col(self.result_col, ColType.BOOL)
        return {'table': output_schema}

    @override
    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        table = input['table'].payload
        assert isinstance(table, Table)
        assert self.result_col is not None
        
        df = table.df.copy()
        series = df[self.col]
        
        if self.op == "NOT":
            df[self.result_col] = ~series
        else:
            raise NodeExecutionError(
                node_id=self.id,
                err_msg=f"Unsupported operation '{self.op}'."
            )
        
        # convert back to Table
        out_table = Data.from_df(df)
        return {'table': out_table}


"""
Calculate between two table columns.
"""

@register_node
class ColBinNumComputeNode(BaseNode):
    """
    Compute binary numeric operation on two table columns.
    Supported ops: ADD, SUB, MUL, DIV, POW
    """
    op: Literal["ADD", "SUB", "MUL", "DIV", "POW"]
    col1: str # the first column to operate on
    col2: str # the second column to operate on
    result_col: str | None = None  # if None, use default result col name

    @override
    def validate_parameters(self) -> None:
        if not self.type == "ColBinNumComputeNode":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="type",
                err_msg="Node type must be 'ColBinNumComputeNode'."
            )
        if self.col1.strip() == "":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="col1",
                err_msg="First column name cannot be empty."
            )
        if self.col2.strip() == "":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="col2",
                err_msg="Second column name cannot be empty."
            )
        if self.col1 == self.col2:
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="col2",
                err_msg="Second column name cannot be the same as first column name."
            )
        if self.result_col is None:
            self.result_col = generate_default_col_name(self.id, "result")
        if self.result_col.strip() == "":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="result_col",
                err_msg="Result column name cannot be empty."
            )
        if self.result_col in {self.col1, self.col2}:
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="result_col",
                err_msg="Result column name cannot be the same as input column names."
            )
        if check_no_illegal_cols([self.result_col]) is False:
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="result_col",
                err_msg="Result column name cannot start with reserved prefix '_' or be whitespace only."
            )
        return

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [
            InPort(
                name='table', 
                description='Input table', 
                accept=Pattern(
                    types={Schema.Type.TABLE}, 
                    table_columns={self.col1: {ColType.INT, ColType.FLOAT}, 
                                   self.col2: {ColType.INT, ColType.FLOAT}}), optional=False)
        ], [
            OutPort(name='table', description='Output table with computed column')
        ]

    @override
    def infer_output_schemas(self, input_schemas: dict[str, Schema]) -> dict[str, Schema]:
        assert input_schemas['table'].tab is not None
        in_tab = input_schemas['table'].tab

        # 1. check if new column name is exists
        assert self.result_col is not None
        if not in_tab.validate_new_col_name(self.result_col):
            raise NodeValidationError(
                node_id=self.id,
                err_input='table',
                err_msg=f"Result column name '{self.result_col}' already exists in input table."
            )
        # 2. check if the two columns are in same type
        col1_type = in_tab.col_types.get(self.col1)
        col2_type = in_tab.col_types.get(self.col2)
        assert col1_type is not None
        assert col2_type is not None
        if col1_type != col2_type:
            raise NodeValidationError(
                node_id=self.id,
                err_input='table',
                err_msg=f"Table column '{self.col1}' type '{col1_type}' does not match column '{self.col2}' type '{col2_type}'."
            )
        # 3. build output schema
        res_col_type = None
        if self.op in {"ADD", "SUB", "MUL"}:
            res_col_type = col1_type
        else:
            res_col_type = ColType.FLOAT
        output_schema = input_schemas['table'].append_col(self.result_col, res_col_type)
        
        return {'table': output_schema}

    @override
    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        table = input['table'].payload
        assert isinstance(table, Table)
        assert self.result_col is not None

        df = table.df.copy()
        series1 = df[self.col1]
        series2 = df[self.col2]
        
        if self.op == "ADD":
            df[self.result_col] = series1 + series2
        elif self.op == "SUB":
            df[self.result_col] = series1 - series2
        elif self.op == "MUL":
            df[self.result_col] = series1 * series2
        elif self.op == "DIV":
            # Check for division by zero, but NaN values should be preserved
            if (series2 == 0).any():
                raise NodeExecutionError(
                    node_id=self.id,
                    err_msg="Division by zero error."
                )
            df[self.result_col] = (
                series1.astype("float64") / series2.astype("float64")
            ).astype("float64")
        elif self.op == "POW":
            df[self.result_col] = series1 ** series2
        else:
            raise NodeExecutionError(
                node_id=self.id,
                err_msg=f"Unsupported operation '{self.op}'."
            )
        
        # convert back to Table
        out_table = Data.from_df(df)
        return {'table': out_table}

@register_node
class ColBinBoolComputeNode(BaseNode):
    """
    Compute binary boolean operation on two table columns.
    Supported ops: AND, OR, XOR, SUB
    """
    op: Literal["AND", "OR", "XOR", "SUB"]
    col1: str # the first column to operate on
    col2: str # the second column to operate on
    result_col: str | None = None  # if None, use default result col name

    @override
    def validate_parameters(self) -> None:
        if not self.type == "ColBinBoolComputeNode":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="type",
                err_msg="Node type must be 'ColBinBoolComputeNode'."
            )
        if self.col1.strip() == "":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="col1",
                err_msg="First column name cannot be empty."
            )
        if self.col2.strip() == "":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="col2",
                err_msg="Second column name cannot be empty."
            )
        if self.col1 == self.col2:
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="col2",
                err_msg="Second column name cannot be the same as first column name."
            )
        if self.result_col is None:
            self.result_col = generate_default_col_name(self.id, "result")
        if self.result_col.strip() == "":
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="result_col",
                err_msg="Result column name cannot be empty."
            )
        if self.result_col in {self.col1, self.col2}:
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="result_col",
                err_msg="Result column name cannot be the same as input column names."
            )
        if check_no_illegal_cols([self.result_col]) is False:
            raise NodeParameterError(
                node_id=self.id,
                err_param_key="result_col",
                err_msg="Result column name cannot start with reserved prefix '_' or be whitespace only."
            )
        return

    @override
    def port_def(self) -> tuple[list[InPort], list[OutPort]]:
        return [
            InPort(
                name='table', 
                description='Input table', 
                accept=Pattern(
                    types={Schema.Type.TABLE}, 
                    table_columns={self.col1: {ColType.BOOL}, 
                                   self.col2: {ColType.BOOL}}), optional=False)
        ], [
            OutPort(name='table', description='Output table with computed column')
        ]

    @override
    def infer_output_schemas(self, input_schemas: dict[str, Schema]) -> dict[str, Schema]:
        assert input_schemas['table'].tab is not None
        in_tab = input_schemas['table'].tab

        # 1. check if new column name is exists
        assert self.result_col is not None
        if not in_tab.validate_new_col_name(self.result_col):
            raise NodeValidationError(
                node_id=self.id,
                err_input='table',
                err_msg=f"Result column name '{self.result_col}' already exists in input table."
            )
        # 2. build output schema
        output_schema = input_schemas['table'].append_col(self.result_col, ColType.BOOL)
        
        return {'table': output_schema}

    @override
    def process(self, input: dict[str, Data]) -> dict[str, Data]:
        table = input['table'].payload
        assert isinstance(table, Table)
        assert self.result_col is not None

        df = table.df.copy()
        series1 = df[self.col1]
        series2 = df[self.col2]
        
        if self.op == "AND":
            df[self.result_col] = series1 & series2
        elif self.op == "OR":
            df[self.result_col] = series1 | series2
        elif self.op == "XOR":
            df[self.result_col] = series1 ^ series2
        elif self.op == "SUB":
            df[self.result_col] = series1 & ~series2
        else:
            raise NodeExecutionError(
                node_id=self.id,
                err_msg=f"Unsupported operation '{self.op}'."
            )
        
        # convert back to Table
        out_table = Data.from_df(df)
        return {'table': out_table}

@register_node
class ColCmpNode(BaseNode):
    """
    A node to compare two columns in a table and output a boolean column.
    """
