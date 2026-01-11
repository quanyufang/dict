# 词典查询API服务（FastAPI）

## 概述

基于FastAPI的词典查询服务，支持key查询和遍历查询功能。

## 功能

- ✅ Key查询（精确/模糊查询）
- ✅ 遍历查询（上一个/下一个词条）
- ✅ 多词典支持
- ✅ JSONB数据存储（PostgreSQL）
- ✅ CORS支持（前端跨域请求）

## 安装依赖

```bash
cd /Users/fangyu/work/fishenglish/Daemon/dict/src/unified/api
pip install -r requirements.txt
```

或使用Python虚拟环境：

```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# 或 venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

## 配置

### 环境变量

创建 `.env` 文件（可选）：

```bash
# 数据库配置
DB_HOST=localhost
DB_PORT=5432
DB_NAME=fishenglish_dict
DB_USER=fishenglish
DB_PASSWORD=your_password_here

# API配置
API_HOST=0.0.0.0
API_PORT=8000

# CORS配置
CORS_ORIGINS=*
```

或在 `config.py` 中直接修改默认值。

## 运行服务

### 方式1：直接运行

```bash
cd /Users/fangyu/work/fishenglish/Daemon/dict/src/unified/api
python3 main.py
```

### 方式2：使用uvicorn

```bash
cd /Users/fangyu/work/fishenglish/Daemon/dict/src/unified
uvicorn unified.api.main:app --host 0.0.0.0 --port 8000 --reload
```

服务将在 `http://localhost:8000` 启动。

## API端点

### 1. 根路径

```bash
GET /
```

返回API信息。

### 2. 查询词条

```bash
GET /api/dict/query?key={word}&sources={source1,source2}&fuzzy={true/false}&limit={number}
```

**参数**：
- `key` (必填): 查询词头
- `sources` (可选): 词典来源列表，用逗号分隔（如：`oxford,langdao`）
- `fuzzy` (可选): 是否模糊查询（默认false）
- `limit` (可选): 返回结果数量限制（默认10，最大100）

**示例**：
```bash
# 精确查询
curl "http://localhost:8000/api/dict/query?key=have&sources=oxford&fuzzy=false"

# 模糊查询
curl "http://localhost:8000/api/dict/query?key=have&sources=oxford&fuzzy=true&limit=10"

# 多词典查询
curl "http://localhost:8000/api/dict/query?key=have&sources=oxford,langdao"
```

### 3. 获取下一个词条

```bash
GET /api/dict/next?key={word}&source={sourceId}
```

**参数**：
- `key` (必填): 当前词头
- `source` (必填): 词典来源ID

**示例**：
```bash
curl "http://localhost:8000/api/dict/next?key=have&source=oxford"
```

### 4. 获取上一个词条

```bash
GET /api/dict/prev?key={word}&source={sourceId}
```

**参数**：
- `key` (必填): 当前词头
- `source` (必填): 词典来源ID

**示例**：
```bash
curl "http://localhost:8000/api/dict/prev?key=have&source=oxford"
```

### 5. 健康检查

```bash
GET /health
```

检查服务状态和数据库连接。

## 响应格式

### 查询响应

```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": 1,
      "headword": "have",
      "source_id": "oxford",
      "pronunciations": [
        {"ipa": "/hæv/", "region": "uk"}
      ],
      "senses": [
        {
          "sense_number": "1",
          "pos": "v",
          "definition": "有, 据有（某物）",
          "examples": [
            {
              "text": "He has a house in London.",
              "translation": "他在伦敦有一所房子."
            }
          ]
        }
      ]
    }
  ]
}
```

### 导航响应

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "headword": "had",
    "source_id": "oxford",
    "has_next": true,
    "has_prev": true,
    "entry": {
      // 词条完整信息（同查询响应）
    }
  }
}
```

## 测试

### 使用curl测试

```bash
# 测试查询
curl "http://localhost:8000/api/dict/query?key=have&sources=oxford&fuzzy=false"

# 测试下一个
curl "http://localhost:8000/api/dict/next?key=have&source=oxford"

# 测试上一个
curl "http://localhost:8000/api/dict/prev?key=have&source=oxford"

# 健康检查
curl "http://localhost:8000/health"
```

### 使用浏览器

打开浏览器访问：
- `http://localhost:8000/docs` - Swagger UI文档
- `http://localhost:8000/redoc` - ReDoc文档

## 前端集成

前端页面已更新，API地址为：`http://localhost:8000/api/dict`

前端文件：`/Users/fangyu/WebstormProjects/feweb/dict-query.html`

## 注意事项

1. **数据库连接**：确保PostgreSQL数据库已启动，并且已创建表结构
2. **端口冲突**：如果8000端口被占用，可通过环境变量`API_PORT`修改
3. **CORS配置**：生产环境应设置具体的CORS origins，而不是"*"
4. **数据导入**：使用数据导入工具将词典数据导入PostgreSQL

## 开发

### 项目结构

```
api/
├── __init__.py
├── main.py              # FastAPI主应用
├── config.py            # 配置
├── database.py          # 数据库连接
├── models.py            # Pydantic模型
├── service.py           # 业务逻辑
├── requirements.txt     # 依赖列表
└── README.md           # 本文档
```

### 添加新功能

1. 在 `service.py` 中添加业务逻辑
2. 在 `main.py` 中添加API端点
3. 在 `models.py` 中添加数据模型
4. 测试新功能

