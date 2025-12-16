<div align="center">
  <img src="client/public/logo.png" alt="NodePy logo" style="width: 500px">
  <!-- <h1>NodePy</h1> -->
</div>

# NodePy
NodePy 是一个基于节点的金融数据分析平台，允许用户通过可视化界面创建和执行复杂的数据处理和分析工作流。NodePy 提供了丰富的节点类型，涵盖数据导入、清洗、转换、分析和可视化等功能。
## 快速开始
1. 克隆仓库
    ```bash
    git clone https://github.com/LKLLLLLLLLLL/NodePy.git
    cd NodePy
    ```
2. 安装依赖
    请先确保已经安装uv, npm。
    ```bash
    # 安装构建依赖
    uv sync
    # 安装前端依赖
    cd client
    npm install
    ```
3. 构建并运行
    请先确保已经安装docker。
    ```bash
    cd ..
    uv run task prod
    ```
4. 自定义配置
    你可以通过编辑`/server/config.py`文件来修改服务器配置，例如数据库连接、缓存设置等。
## 开发
## 使用和生产环境接近的测试环境
```bash
uv run task dev
```
访问http://localhost:8000
## 使用实时更新的测试环境
```bash
uv run task dev
npm run dev
```
访问http://localhost:5173
## 快速生成 API 客户端代码
```bash
cd client
npm run gen_api
```
## 将某个项目持久化为example项目
```bash
docker exec -it nodepy-server uv run task persist <project_name> [example_name]
```
## 检查代码格式
```bash
uv run task check
```