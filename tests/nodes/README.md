# tests/nodes — Test Framework Description

## Overview

This directory provides a lightweight test framework and utility functions for unit, static, and runtime testing of node code under `server/interpreter/nodes`.

## Design Points

- Inject minimal fake implementations (`FileManager`, `FinancialDataManager`, `CacheManager`) during the test collection (pytest import) phase to avoid triggering dependencies on MinIO/Redis/database during import.
- Place all node tests under `tests/nodes`.
- Provide several helpers to simplify the construction and assertions of `Table` / `Schema` / `Data`.

## Quick Run

Run in the project root directory (recommended via `uv` to use the project virtual environment):

```bash
uv run pytest -q tests/nodes
```

Or run a single file:

```bash
uv run pytest -q tests/nodes/test_number_binop.py
```

## Main Files

- `conftest.py` — Injects fake modules and provides pytest fixtures: `test_file_root`, `inject_fake_modules`, `node_registry`, `global_config`, `node_ctor`.
- `utils.py` — Provides utility constructors (see below).
- `test_*` — Example test files (includes `test_node_framework.py` and `test_number_binop.py`).

## Provided Utility Functions (`tests/nodes/utils.py`)

- `table_from_dict(data: Dict[str, list], col_types: Dict[str, ColType] | None = None) -> Data`
  - Constructs a `Table` from a column dictionary and wraps it as `Data`; automatically adds `_index` column and attempts to infer column types.

- `table_from_records(records: Iterable[Dict[str, Any]]) -> Data`
  - Constructs a `Table` from a list of records (rows).

- `schema_from_coltypes(col_types: Dict[str, ColType]) -> Schema`
  - Constructs a `Table` type `Schema` based on a column types dictionary.

- `make_schema(typ: str) -> Schema`
  - Quickly constructs a primitive type `Schema`, supports: `int`, `float`, `str`, `bool`, `Datetime`, `Table`, `File`.

- `make_data(payload: Any) -> Data`
  - Wraps a raw payload into a `Data` object (for concise parameter passing).

## Usage Example

```python
from tests.nodes.utils import table_from_dict, make_schema, make_data

# Construct table data
tbl = table_from_dict({"a": [1,2,3], "b": [10.0, 20.0, 30.0]})

# Construct primitive schema
schema = make_schema("int")

# Wrap raw payload
d = make_data(42)
```

## Writing Tests for More Nodes

1. If some nodes depend on more complex external behavior, first inject richer fake implementations for the corresponding dependencies in `tests/nodes/conftest.py` (e.g., mock `FileManager.read_sync` to return specific file content).
2. Use `node_ctor` to construct nodes:

```python
node = node_ctor("SomeNodeType", id="n1", param1=..., ...)
```

3. Use `infer_schema` for static analysis:

```python
out_schema = node.infer_schema(input_schemas)
```

4. Use `execute` for runtime testing:

```python
outputs = node.execute({"in1": Data(payload=...), ...})
```

## Testing Requirements
- Test cases should reference the node definitions and descriptions in `docs/nodes.md`, preferably without referring to implementation details like node definition files.
- All test files should be placed in `tests/nodes/nodes/<category>/test_<nodename>.py` by category, ensuring one file per node.
- Each node should have a corresponding test file.
- Each node's tests:
  - Should include at least four phases (Construction, Hint, Static Analysis, Execution) (if a node does not support the hint phase, that phase can be omitted).
  - Each phase should include 2 or more normal case tests and 3 or more exception case tests.
- Test coverage for the corresponding node definition files should be no less than 90%.
