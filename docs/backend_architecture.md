# NodePy 后端架构文档

本文档旨在从架构设计和实现细节两个维度，全面解析 NodePy 后端系统。

## 1. 总体架构设计

NodePy 采用微服务风格的容器化架构。系统主要由 Web 服务、异步任务队列、数据库和对象存储组成。

### 1.1 容器编排 (Docker Compose)

基础设施通过 `infra/docker-compose.yml`和 `infra/docker/docker-compose.prod.yml`(生产环境) 进行编排，包含以下核心服务：

| 服务名称 | 镜像/构建 | 端口 | 职责 |
| :--- | :--- | :--- | :--- |
| **server** | `infra/docker/server.Dockerfile` | 8000 | **API 网关与业务逻辑**。处理 HTTP 请求，管理项目元数据，触发异步任务。 |
| **celery-worker** | `infra/docker/worker.Dockerfile` | - | **计算引擎**。消费 Redis 中的任务，执行耗时的图计算和数据处理逻辑。 |
| **postgres** | `postgres:15` | 5432 | **关系型数据库**。存储用户信息、项目结构、节点配置等结构化数据。 |
| **redis** | `redis:alpine` | 6379 | **消息代理与缓存**。作为 Celery 的 Broker 和 Backend，同时用于 API 缓存。 |
| **minio** | `minio/minio` | 9000/9001 | **对象存储**。存储用户上传的数据文件、生成的图表图片等非结构化数据。 |

### 1.2 数据流向

1.  **请求处理**: 用户通过前端发起请求 -> `server` 容器 (FastAPI)。
2.  **任务调度**: 涉及运行项目(计算密集)时，`server` 将任务封装并推送到 `redis` 队列。
3.  **异步执行**: `celery-worker` 从 `redis` 获取任务，加载项目数据，执行 `interpreter` 逻辑。
4.  **状态反馈**: Worker 执行过程中，通过 Redis Stream 或数据库实时更新节点状态，前端通过轮询或 WebSocket 获取进度。
5.  **数据存取**: 结构化数据读写 `postgres`，大文件读写 `minio`。

**一个project的运行流程：**
1. 用户修改项目，触发前端调用`/api/project/sync`接口同步项目。  
(如果该项目正在运行，应由前端手动终止后再同步)
2. 服务器保存项目数据到数据库。
3. 服务器比对是否有拓扑结构变化，若有则将运行任务推送到Celery队列，并返回任务id作为前端查询依据。
4. 前端应通过任务id在`/api/project/status/{task_id}`接口建立websocket连接，实时获取任务进度。
5. Celery Worker 获取任务，加载项目数据，构建解释器并执行，通过redis stream实时回传任务状态，服务器端接收并转发给前端。
6. 如果前端通过ws发送任何消息，任务停止；或是ws断开，任务也停止。

---

## 2. Server 实现 (`server/`)

Server 端主要负责 RESTful API 的提供和基础设施的管理。

### 2.1 目录结构

```
server/
├── api/                # 路由层：处理 HTTP 请求
├── lib/                # 服务层：封装通用业务逻辑
├── models/             # 数据层：ORM 模型与 Pydantic Schema
├── config.py           # 全局配置
├── main.py             # FastAPI 应用入口
└── celery.py           # Celery 应用配置
```

### 2.2 核心模块

*   **API Layer (`server/api/`)**
    *   基于 FastAPI `APIRouter` 组织路由。
    *   `project.py`: 核心业务接口，包括项目的 CRUD、运行 (`execute_project_task`)、停止 (`revoke_project_task`)。
    *   `auth.py`: 基于 JWT 的用户认证。
    *   `files.py`: 代理 MinIO 操作，处理文件上传下载。
    *   更多API路由。

*   **Service Layer (`server/lib/`)**
    *   `DataManager.py`: 统一的数据源访问接口，支持从 CSV、Excel、Database 读取数据为 Pandas DataFrame。
    *   `FileManager.py`: 封装 MinIO SDK，提供文件存储、预签名 URL 生成等功能。
    *   `FinancialDataManager.py`: 专门处理金融数据的获取、缓存和更新（如股票行情）。
    *   `ProjectLock.py`: 基于 Redis 的分布式锁，防止同一个项目被并发修改或运行。

*   **Data Layer (`server/models/`)**
    *   `database.py`: SQLAlchemy 配置，提供同步 (`Session`) 和异步 (`AsyncSession`) 两种数据库会话。
    *   `project.py`: 定义了项目的 Pydantic 模型 (`ProjWorkflow`, `ProjNode`)，用于 JSON 序列化和前端交互。
    *   **类型系统**:
        *   `types.py`: 定义基础列类型 `ColType` (如 `INT`, `FLOAT`, `STR`, `DATETIME`)，负责与 Pandas dtype 的转换。
        *   `schema.py`: 定义静态类型信息 `TableSchema`，用于编译期的类型检查和推断。
        *   `data.py`: 定义运行时数据容器 `Table` (封装 DataFrame) 和 `Data`，负责运行时的数据校验和传递。

---

## 3. Interpreter 实现细节 (`server/interpreter/`)

Interpreter 是 NodePy 的核心计算引擎，负责解析和执行节点逻辑。

### 3.1 目录结构

```
server/interpreter/
├── nodes/              # 节点库：所有具体节点的实现
│   ├── base_node.py    # 节点基类
│   ├── context.py      # 节点执行上下文
│   └── ... (按功能分类的节点目录)
├── interpreter.py      # 解释器核心逻辑
└── task.py             # Celery 任务入口
```

### 3.2 核心组件

#### 3.2.1 节点系统 (`BaseNode`)
所有节点均继承自 `server.interpreter.nodes.base_node.BaseNode`，必须实现以下生命周期方法：
1.  **`validate_parameters()`**: 静态检查参数合法性（如：必填项是否为空，数值范围是否正确）。
2.  **`infer_output_schemas(input_schemas)`**: 根据输入端口的 Schema 推导输出端口的 Schema。这是前端实现“连线类型检查”和“智能提示”的基础。
3.  **`hint(input_schemas, current_params)`**: 根据当前的输入 Schema 和部分参数，为前端提供动态提示（如：根据上游数据列名，填充下拉选择框）。此阶段即使参数校验未通过也会执行。
4.  **`process(input_data)`**: 实际执行逻辑。接收输入数据 (`dict[str, Data]`)，返回输出数据。

#### 3.2.2 解释器 (`ProjectInterpreter`)
位于 `server/interpreter/interpreter.py`，主要职责：
*   **静态分析**: 在执行前遍历图结构，进行节点构造、Schema 推断和 Hint 生成，为前端提供实时反馈。
*   **拓扑排序**: 使用 `networkx` 对节点进行拓扑排序，确定执行顺序。
*   **控制流管理**: 通过 `ControlStructureManager` 识别 `For Loop` 等控制结构，处理循环执行逻辑。
*   **执行调度**: 依次调用节点的 `process` 方法，管理数据在节点间的传递。
*   **错误处理**: 捕获节点执行异常，标记出错节点并停止后续执行。

#### 3.2.3 异步任务 (`task.py`)
*   定义了 Celery 任务 `execute_project_task`。
*   负责初始化执行环境（数据库连接、Redis 队列）。
*   实例化 `ProjectInterpreter` 并调用其 `run` 方法。
*   处理任务取消 (`RevokeException`) 和超时。

### 3.3 节点执行流程

1.  **初始化**: Worker 接收项目 ID，从数据库加载项目 JSON。
2.  **构建图**: 将 JSON 转换为 `networkx` 图对象。
3.  **静态检查**: 遍历所有节点进行 `validate_parameters` 和 `infer_output_schemas`。
4.  **拓扑执行**:
    *   按拓扑序遍历节点。
    *   如果是普通节点：准备输入数据 -> 调用 `process` -> 缓存输出数据。
    *   如果是控制流节点（如 `ForEachRow`）：进入子图循环执行模式。
5.  **结果持久化**: 将关键节点的运行结果（如预览数据、图表配置）写入数据库或对象存储。
