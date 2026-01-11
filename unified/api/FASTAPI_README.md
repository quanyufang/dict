# FastAPI词典查询服务 - 快速开始

## ✅ 已完成的工作

### 1. FastAPI服务端

**文件位置**：`/Users/fangyu/work/fishenglish/Daemon/dict/src/unified/api/`

**主要文件**：
- `main.py` - FastAPI主应用
- `config.py` - 配置管理
- `database.py` - 数据库连接（asyncpg）
- `models.py` - Pydantic数据模型
- `service.py` - 业务逻辑层
- `requirements.txt` - 依赖列表

**API端点**：
- `GET /api/dict/query` - 查询词条（支持精确/模糊查询）
- `GET /api/dict/next` - 获取下一个词条
- `GET /api/dict/prev` - 获取上一个词条
- `GET /health` - 健康检查
- `GET /docs` - Swagger UI文档
- `GET /redoc` - ReDoc文档

### 2. 前端页面

**文件位置**：`/Users/fangyu/WebstormProjects/feweb/dict-query.html`

**功能**：
- ✅ 词条搜索（精确/模糊查询）
- ✅ 多词典选择
- ✅ 上一个/下一个遍历
- ✅ 键盘快捷键支持（← →）
- ✅ 结果展示（词头、发音、释义、例句等）
- ✅ 适配FastAPI API格式

### 3. 数据库设计

**文件位置**：`/Users/fangyu/work/fishenglish/Daemon/dict/src/unified/database/`

- ✅ PostgreSQL表结构（`postgresql_schema.sql`）
- ✅ 数据库文档（`README.md`、`DATABASE_SETUP.md`）

## 🚀 快速开始

### 1. 安装依赖

```bash
cd /Users/fangyu/work/fishenglish/Daemon/dict/src/unified/api
pip install -r requirements.txt
```

### 2. 配置数据库

创建 `.env` 文件或设置环境变量：

```bash
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=fishenglish_dict
export DB_USER=fishenglish
export DB_PASSWORD=your_password_here
```

或直接修改 `api/config.py` 中的默认值。

### 3. 创建数据库表

```bash
# 创建数据库
createdb fishenglish_dict

# 导入表结构
cd /Users/fangyu/work/fishenglish/Daemon/dict/src/unified/database
psql -d fishenglish_dict -f postgresql_schema.sql
```

### 4. 启动服务

```bash
cd /Users/fangyu/work/fishenglish/Daemon/dict/src/unified
python3 -m unified.api.main
```

或使用uvicorn：

```bash
cd /Users/fangyu/work/fishenglish/Daemon/dict/src/unified
uvicorn unified.api.main:app --host 0.0.0.0 --port 8000 --reload
```

或使用启动脚本：

```bash
cd /Users/fangyu/work/fishenglish/Daemon/dict/src/unified/api
python3 start_server.py
```

服务将在 `http://localhost:8000` 启动。

### 5. 测试API

**使用curl**：
```bash
# 查询词条
curl "http://localhost:8000/api/dict/query?key=have&sources=oxford&fuzzy=false"

# 下一个词条
curl "http://localhost:8000/api/dict/next?key=have&source=oxford"

# 上一个词条
curl "http://localhost:8000/api/dict/prev?key=have&source=oxford"

# 健康检查
curl "http://localhost:8000/health"
```

**使用浏览器**：
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### 6. 打开前端页面

浏览器打开：
- 本地文件：`file:///Users/fangyu/WebstormProjects/feweb/dict-query.html`
- 或通过Web服务器：`http://localhost:8000/dict-query.html`

## 📋 API使用说明

### 查询词条

```bash
GET /api/dict/query?key={word}&sources={source1,source2}&fuzzy={true/false}&limit={number}
```

**参数**：
- `key` (必填): 查询词头
- `sources` (可选): 词典来源列表，用逗号分隔
- `fuzzy` (可选): 是否模糊查询（默认false）
- `limit` (可选): 返回结果数量限制（默认10，最大100）

**响应格式**：
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": 1,
      "headword": "have",
      "source_id": "oxford",
      "pronunciations": [...],
      "senses": [...]
    }
  ]
}
```

### 遍历查询

```bash
GET /api/dict/next?key={word}&source={sourceId}
GET /api/dict/prev?key={word}&source={sourceId}
```

**参数**：
- `key` (必填): 当前词头
- `source` (必填): 词典来源ID

**响应格式**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "headword": "had",
    "source_id": "oxford",
    "has_next": true,
    "has_prev": true,
    "entry": {...}
  }
}
```

## 🔧 开发说明

### 项目结构

```
unified/api/
├── __init__.py
├── main.py              # FastAPI主应用
├── config.py            # 配置管理
├── database.py          # 数据库连接（asyncpg）
├── models.py            # Pydantic数据模型
├── service.py           # 业务逻辑层
├── requirements.txt     # 依赖列表
├── README.md           # 详细文档
├── start_server.py     # 启动脚本
└── run.sh              # Shell启动脚本
```

### 修改配置

编辑 `api/config.py` 或设置环境变量：

```python
# config.py
DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "fishenglish_dict"
DB_USER = "fishenglish"
DB_PASSWORD = "your_password"
```

### 添加新功能

1. 在 `service.py` 中添加业务逻辑方法
2. 在 `main.py` 中添加API端点
3. 在 `models.py` 中添加数据模型（如需要）
4. 测试新功能

## ⚠️ 注意事项

1. **Python版本**：需要Python 3.8+
2. **PostgreSQL驱动**：使用asyncpg（异步PostgreSQL驱动）
3. **导入路径**：从`src`目录运行时，使用`unified.api`模块路径
4. **数据库连接**：确保PostgreSQL已启动，并且已创建表结构
5. **端口配置**：默认端口8000，可通过环境变量`API_PORT`修改

## 📝 与Java服务端的区别

1. **技术栈**：Python FastAPI vs Java Spring Boot
2. **异步支持**：FastAPI原生支持异步，使用asyncpg异步数据库驱动
3. **API格式**：基本一致，但FastAPI自动生成OpenAPI文档
4. **部署**：FastAPI可以使用uvicorn部署，更灵活

## 🔗 相关文档

- 数据库设计：`../database/README.md`
- 数据库设置：`../database/DATABASE_SETUP.md`
- 项目待办：`../PROJECT_TODO.md`
- 前端页面：`/Users/fangyu/WebstormProjects/feweb/dict-query.html`

