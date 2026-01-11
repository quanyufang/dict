# 词典查询网站 - 使用说明

## 概述

这是一个词典查询网站，支持：
1. **Key查询**：精确查询和模糊查询词条
2. **遍历查询**：查看上一个/下一个词条（按字母顺序）

## 已实现的功能

### ✅ 后端API

**文件位置**：`/Users/fangyu/work/fishenglish/backend/src/main/java/top/fishreading/backend/dict/`

**API端点**：
- `GET /api/dict/query?key={word}&sources={source1,source2}&fuzzy={true/false}&limit={number}`
  - 查询词条（支持精确和模糊查询）
  - 支持多词典查询
- `GET /api/dict/next?key={word}&source={sourceId}`
  - 获取下一个词条
- `GET /api/dict/prev?key={word}&source={sourceId}`
  - 获取上一个词条

### ✅ 前端页面

**文件位置**：`/Users/fangyu/WebstormProjects/feweb/dict-query.html`

**功能**：
- 词条搜索（精确/模糊查询）
- 多词典选择
- 上一个/下一个遍历
- 键盘快捷键支持（← →）
- 结果展示（词头、发音、释义、例句等）

### ✅ 数据库表结构

**文件位置**：`/Users/fangyu/work/fishenglish/Daemon/dict/src/unified/database/`

**表**：
- `dictionary_entries` - 词典条目主表
- `dictionary_index` - 词典索引表（用于遍历查询）
- `dictionary_stats` - 词典统计表

## 使用步骤

### 1. 设置PostgreSQL数据库

参考 `database/DATABASE_SETUP.md`：

```bash
# 创建数据库
createdb fishenglish_dict

# 导入表结构
psql -d fishenglish_dict -f database/postgresql_schema.sql
```

### 2. 配置后端数据源

更新 `backend/src/main/resources/application-dev.yml` 或创建 `application-dict.yml`：

```yaml
# PostgreSQL数据源配置（词典数据库）
spring:
  datasource:
    url: jdbc:postgresql://localhost:5432/fishenglish_dict
    username: fishenglish
    password: your_password_here
    driver-class-name: org.postgresql.Driver
```

**注意**：如果同时使用MySQL和PostgreSQL，需要配置多数据源。当前实现假设PostgreSQL是主数据源。

### 3. 启动后端服务

```bash
cd /Users/fangyu/work/fishenglish/backend
mvn spring-boot:run
```

后端服务将在 `http://localhost:8080` 启动。

### 4. 打开前端页面

在浏览器中打开：
- 本地文件：`file:///Users/fangyu/WebstormProjects/feweb/dict-query.html`
- 或者通过Web服务器：`http://localhost:8000/dict-query.html`

### 5. 测试查询

1. 在搜索框输入词头（如"have"）
2. 选择要查询的词典（如"牛津英汉"）
3. 点击"查询"按钮
4. 查看结果
5. 使用"上一个"/"下一个"按钮遍历词条

## 下一步工作

### ⏳ 待完成

1. **数据导入工具** - 将解析后的词典数据导入PostgreSQL
   - 创建 `scripts/import_to_postgresql.py`
   - 实现批量导入功能
   - 生成sort_key用于遍历查询

2. **多数据源配置**（如果需要）
   - 如果MySQL和PostgreSQL同时使用，需要配置多数据源
   - 创建数据源配置类

3. **测试和优化**
   - 测试API接口
   - 性能优化（索引、缓存等）
   - 错误处理优化

4. **前端改进**（可选）
   - 添加加载动画
   - 添加错误提示
   - 响应式设计优化
   - 添加更多功能（收藏、分享等）

## API使用示例

### 查询词条

```bash
# 精确查询
curl "http://localhost:8080/api/dict/query?key=have&sources=oxford&fuzzy=false"

# 模糊查询
curl "http://localhost:8080/api/dict/query?key=have&sources=oxford&fuzzy=true&limit=10"

# 多词典查询
curl "http://localhost:8080/api/dict/query?key=have&sources=oxford,langdao,gcide"
```

### 遍历查询

```bash
# 下一个词条
curl "http://localhost:8080/api/dict/next?key=have&source=oxford"

# 上一个词条
curl "http://localhost:8080/api/dict/prev?key=have&source=oxford"
```

## 数据结构说明

### 查询响应格式

```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": 1,
      "headword": "have",
      "sourceId": "oxford",
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

### 导航响应格式

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "headword": "had",
    "sourceId": "oxford",
    "hasNext": true,
    "hasPrev": true,
    "entry": {
      // 词条完整信息（同查询响应）
    }
  }
}
```

## 注意事项

1. **PostgreSQL驱动**：已添加到 `pom.xml`，确保Maven依赖已更新
2. **MyBatis Plus配置**：已更新 `type-aliases-package`，包含dict模块
3. **JSONB处理**：当前使用String字段存储JSON，需要手动解析（可后续优化为JSONB类型处理器）
4. **多数据源**：如果同时使用MySQL和PostgreSQL，需要配置多数据源

## 相关文件

- 数据库表结构：`database/postgresql_schema.sql`
- 数据库设置指南：`database/DATABASE_SETUP.md`
- 后端API：`backend/src/main/java/top/fishreading/backend/dict/`
- 前端页面：`feweb/dict-query.html`
- 项目待办列表：`PROJECT_TODO.md`

