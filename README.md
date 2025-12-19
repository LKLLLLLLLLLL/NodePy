<div align="center">
  <img src="client/public/logo.png" alt="NodePy logo" style="width: 500px">
  <!-- <h1>NodePy</h1> -->
</div>

# NodePy

NodePy 是一个基于节点的金融数据分析平台，用户可以通过可视化界面创建和执行复杂的数据处理和分析工作流。NodePy 提供了丰富的节点类型，涵盖数据导入、清洗、转换、分析和可视化等功能。

![demo](client/public/demo.gif)

## 快速开始
请确保已经安装如下依赖：
- Docker & Docker Compose
- uv (Python 包管理器)
- Node.js & npm

1. 克隆仓库
    ```bash
    git clone https://github.com/LKLLLLLLLLLL/NodePy.git
    cd NodePy
    ```
2. 安装依赖
    请先确保已经安装uv, npm。
    ```bash
    # 安装 Python 依赖 (使用 uv)
    uv sync
    
    # 安装前端依赖
    cd client
    npm install
    cd ..
    ```
3. 自定义配置
    你可以通过编辑`/server/config.py`文件来修改服务器配置，例如数据库连接、缓存设置等。
4. 构建并启动生产环境
    ```bash
    uv run task prod
    ```

## 开发指南
### 启动开发环境
#### 方案一：混合开发模式
```bash
uv run task dev
npm run dev
```
访问http://localhost:5173
#### 方案二：全容器开发模式
```bash
uv run task dev
```
访问http://localhost:8000

### 常用命令
- 快速生成 API 客户端代码
    请确保server容器正在运行
    ```bash
    cd client
    npm run gen_api
    ```
- 将某个项目持久化为example
    ```bash
    docker exec -it nodepy-server uv run task persist <project_name> [example_name]
    ```
- 检查代码格式
    ```bash
    npm run type-check
    uv run task check
    ```
