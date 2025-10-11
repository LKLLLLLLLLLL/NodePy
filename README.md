# NodePy
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
    # 安装后端依赖
    cd ../server
    uv sync
    ```
3. 构建并运行
    请先确保已经安装docker。
    ```bash
    uv run dev
    ```
## 开发
## 使用和生产环境接近的测试环境
```bash
uv run dev
```
访问http://localhost:8000
## 使用实时更新的测试环境
```bash
uv run dev
cd client
npm run dev
```
访问http://localhost:5173