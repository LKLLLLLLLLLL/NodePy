# tests/nodes — 测试框架说明

## 概述

本目录提供一套轻量的测试框架与便捷函数，用于对 `server/interpreter/nodes` 下的节点代码进行单元、静态和运行时测试。

## 设计要点

- 在测试收集（pytest import）阶段注入少量伪实现（`FileManager`、`FinancialDataManager`、`CacheManager`），避免导入时触发对 MinIO/Redis/数据库的依赖。
- 将所有节点测试放置在 `tests/nodes` 下。
- 提供若干 helper，简化 `Table` / `Schema` / `Data` 的构造与断言。

## 快速运行

在项目根目录运行（推荐通过 `uv` 以使用项目虚拟环境）：

```bash
uv run pytest -q tests/nodes
```

或者运行单个文件：

```bash
uv run pytest -q tests/nodes/test_number_binop.py
```

## 主要文件

- `conftest.py` — 注入伪模块并提供 pytest fixture：`test_file_root`, `inject_fake_modules`, `node_registry`, `global_config`, `node_ctor`。
- `utils.py` — 提供便捷构造函数（见下文）。
- `test_*` — 示例测试文件（已包含 `test_node_framework.py` 和 `test_number_binop.py`）。

## 提供的便捷函数（`tests/nodes/utils.py`）

- `table_from_dict(data: Dict[str, list], col_types: Dict[str, ColType] | None = None) -> Data`
  - 从列字典构造一个 `Table` 并封装为 `Data`；会自动添加 `_index` 列并尝试推断列类型。

- `table_from_records(records: Iterable[Dict[str, Any]]) -> Data`
  - 从记录（行）列表构造 `Table`。

- `schema_from_coltypes(col_types: Dict[str, ColType]) -> Schema`
  - 根据列类型字典构造 `Table` 类型的 `Schema`。

- `make_schema(typ: str) -> Schema`
  - 快速构造原始类型 `Schema`，支持：`int`, `float`, `str`, `bool`, `Datetime`, `Table`, `File`。

- `make_data(payload: Any) -> Data`
  - 将一个原始 payload 包装成 `Data` 对象（便于简洁传参）。

## 使用示例

```python
from tests.nodes.utils import table_from_dict, make_schema, make_data

# 构造 table data
tbl = table_from_dict({"a": [1,2,3], "b": [10.0, 20.0, 30.0]})

# 构造 primitive schema
schema = make_schema("int")

# 包装原始 payload
d = make_data(42)
```

## 为更多节点写测试

1. 如果某些节点依赖更复杂的外部行为，先在 `tests/nodes/conftest.py` 中为对应依赖注入更丰富的 fake 实现（例如模拟 `FileManager.read_sync` 返回特定文件内容）。
2. 使用 `node_ctor` 构造节点：

```python
node = node_ctor("SomeNodeType", id="n1", param1=..., ...)
```

3. 使用 `infer_schema` 做静态分析：

```python
out_schema = node.infer_schema(input_schemas)
```

4. 使用 `execute` 做运行时测试：

```python
outputs = node.execute({"in1": Data(payload=...), ...})
```

## 测试要求
- 编写测试用例的参考应为 `docs/nodes.md` 中的节点定义与说明，最好不要参考节点实现细节，如节点的定义文件。
- 所有测试文件按照分类放到 `tests/nodes/nodes/<category>/test_<nodename>.py`，确保一个节点一个文件。
- 每个节点都应该有对应的测试文件。
- 每个节点的测试：
  - 至少包含四个阶段 (Construction, Hint, Static Analysis, Execution) 的测试 (如果某个节点不支持hint阶段，可省略该阶段测试)。
  - 每个阶段应包含2个及以上的正常情况测试和3个及以上的异常情况测试。
- 对应节点定义文件的测试覆盖率不低于90%。
