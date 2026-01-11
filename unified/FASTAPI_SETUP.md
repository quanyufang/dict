# FastAPI词典查询服务 - 设置指南

## ✅ 已完成

1. **FastAPI服务端** - 已完成（`api/`目录）
2. **前端页面** - 已更新（适配FastAPI API格式）
3. **数据库设计** - 已完成（PostgreSQL表结构）

## 🚀 快速开始

### 1. 安装依赖

```bash
cd /Users/fangyu/work/fishenglish/Daemon/dict/src/unified/api
pip install -r requirements.txt
```

**依赖列表**：
- fastapi==0.104.1
- uvicorn[standard]==0.24.0
- asyncpg==0.29.0
- pydantic==2.5.0

### 2. 配置数据库

设置环境变量（推荐）：

```bash
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=fishenglish_dict
export DB_USER=fishenglish
export DB_PASSWORD=your_password_here
```

或直接修改 `api/config.py` 中的默认值。

### 3. 创建数据库

```bash
# 创建数据库
createdb fishenglish_dict

# 导入表结构
cd /Users/fangyu/work/fishenglish/Daemon/dict/src/unified/database
psql -d fishenglish_dict -f postgresql_schema.sql
```

### 4. 启动服务

**方式1：使用启动脚本（推荐）**

```bash
cd /Users/fangyu/work/fishenglish/Daemon/dict/src/unified/api
python3 run_server.py
```

**方式2：使用uvicorn**

```bash
cd /Users/fangyu/work/fishenglish/Daemon/dict/src/unified
uvicorn unified.api.main:app --host 0.0.0.0 --port 8000 --reload
```

**方式3：直接运行main.py**

```bash
cd /Users/fangyu/work/fishenglish/Daemon/dict/src/unified
python3 -m unified.api.main
```

服务将在 `http://localhost:8000` 启动。

### 5. 测试服务

**使用curl**：
```bash
# 健康检查
curl http://localhost:8000/health

# 查询词条（需要有数据）
curl "http://localhost:8000/api/dict/query?key=have&sources=oxford&fuzzy=false"
```

**使用浏览器**：
- API文档：`http://localhost:8000/docs` （Swagger UI）
- 健康检查：`http://localhost:8000/health`

### 6. 打开前端页面

浏览器打开：`file:///Users/fangyu/WebstormProjects/feweb/dict-query.html`

## 📋 API端点

### 1. 查询词条

```
GET /api/dict/query?key={word}&sources={source1,source2}&fuzzy={true/false}&limit={number}
```

### 2. 下一个词条

```
GET /api/dict/next?key={word}&source={sourceId}
```

### 3. 上一个词条

```
GET /api/dict/prev?key={word}&source={sourceId}
```

### 4. 健康检查

```
GET /health
```

## 📁 文件清单

### FastAPI服务端
- `api/main.py` - FastAPI主应用 ✅
- `api/config.py` - 配置管理 ✅
- `api/database.py` - 数据库连接 ✅
- `api/models.py` - Pydantic数据模型 ✅
- `api/service.py` - 业务逻辑层 ✅
- `api/requirements.txt` - 依赖列表 ✅
- `api/run_server.py` - 启动脚本 ✅
- `api/README.md` - 详细文档 ✅

### 前端
- `feweb/dict-query.html` - 查询页面（已更新API地址） ✅

### 数据库
- `database/postgresql_schema.sql` - 表结构 ✅
- `database/README.md` - 数据库文档 ✅
- `database/DATABASE_SETUP.md` - 设置指南 ✅

## 🔧 开发说明

### 导入路径

从`src`目录运行：
```python
from unified.api.main import app
from unified.api.service import DictionaryService
```

### 添加新端点

在 `main.py` 中添加：

```python
@app.get("/api/dict/new-endpoint")
async def new_endpoint():
    # 实现逻辑
    pass
```

### 修改业务逻辑

在 `service.py` 中添加新方法：

```python
async def new_method(self, param: str):
    async with get_db() as conn:
        # 实现逻辑
        pass
```

## ⚠️ 注意事项

1. **Python版本**：需要Python 3.8+
2. **数据库**：确保PostgreSQL已安装并运行
3. **端口**：默认8000端口，如果被占用可通过环境变量修改
4. **数据导入**：使用数据导入工具将词典数据导入PostgreSQL（待实现）

## 🔗 相关文档

- API详细文档：`api/README.md`
- 数据库设计：`database/README.md`
- 数据库设置：`database/DATABASE_SETUP.md`
- 项目待办：`PROJECT_TODO.md`

