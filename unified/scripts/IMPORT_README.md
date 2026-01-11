# 数据导入工具使用说明

## 概述

`import_to_postgresql.py` 用于将解析后的词典数据导入 PostgreSQL 数据库。

## 功能特性

- ✅ 支持从 JSON 文件导入
- ✅ 支持批量导入（可配置批量大小）
- ✅ 自动处理重复条目（使用 ON CONFLICT）
- ✅ 自动创建索引条目（支持遍历查询）
- ✅ 自动更新统计信息
- ✅ 支持干运行模式（仅验证数据，不实际导入）
- ✅ 详细的日志输出

## 使用方法

### 1. 导入单个 JSON 文件

```bash
cd /Users/fangyu/work/fishenglish/Daemon/dict/src/unified/scripts
source ../venv/bin/activate

# 导入 oxford 词典数据
python import_to_postgresql.py \
    --source oxford \
    --file ../samples/oxford_samples.json

# 导入 langdao 词典数据
python import_to_postgresql.py \
    --source langdao \
    --file ../samples/langdao_samples.json
```

### 2. 批量导入目录下的所有 JSON 文件

```bash
# 导入 samples 目录下所有 JSON 文件
python import_to_postgresql.py \
    --source oxford \
    --dir ../samples/
```

### 3. 使用自定义批量大小

```bash
# 使用更大的批量大小（默认100）
python import_to_postgresql.py \
    --source oxford \
    --file ../samples/oxford_samples.json \
    --batch-size 500
```

### 4. 干运行模式（验证数据）

```bash
# 仅验证数据，不实际导入
python import_to_postgresql.py \
    --source oxford \
    --file ../samples/oxford_samples.json \
    --dry-run
```

### 5. 不更新统计信息

```bash
# 导入数据但不更新统计信息
python import_to_postgresql.py \
    --source oxford \
    --file ../samples/oxford_samples.json \
    --no-stats
```

## 参数说明

| 参数 | 简写 | 必需 | 说明 |
|------|------|------|------|
| `--file` | `-f` | 是* | JSON 文件路径 |
| `--dir` | `-d` | 是* | JSON 文件目录（批量导入） |
| `--source` | `-s` | 是 | 词典来源ID (oxford/langdao/gcide/xiandai/chinese_dict) |
| `--batch-size` | - | 否 | 批量大小（默认100） |
| `--no-stats` | - | 否 | 不更新统计信息 |
| `--dry-run` | - | 否 | 仅验证，不实际导入 |

*注：必须指定 `--file` 或 `--dir` 其中之一

## JSON 文件格式

支持两种 JSON 格式：

### 格式1：列表格式

```json
[
  {
    "headword": "good",
    "source_id": "oxford",
    "senses": [...],
    ...
  },
  {
    "headword": "bad",
    "source_id": "oxford",
    "senses": [...],
    ...
  }
]
```

### 格式2：对象格式

```json
{
  "entries": [
    {
      "headword": "good",
      "source_id": "oxford",
      "senses": [...],
      ...
    },
    {
      "headword": "bad",
      "source_id": "oxford",
      "senses": [...],
      ...
    }
  ]
}
```

## 导入流程

1. **加载 JSON 文件**：从文件或目录加载词典条目
2. **过滤数据**：根据 `--source` 参数过滤指定来源的条目
3. **批量导入**：
   - 插入 `dictionary_entries` 表（使用 ON CONFLICT 处理重复）
   - 插入 `dictionary_index` 表（用于遍历查询）
4. **更新统计**：更新 `dictionary_stats` 表（除非使用 `--no-stats`）

## 重复处理

如果数据库中已存在相同的条目（相同的 `headword` 和 `source_id`），导入工具会：

- **更新**现有条目的数据（保留原有的 `id` 和 `created_at`）
- **更新** `updated_at` 时间戳
- **覆盖**所有字段（包括 JSONB 字段）

## 排序键生成

导入工具会自动为每个条目生成排序键（`sort_key`），用于支持"上一个/下一个"遍历查询：

- **英文**：转为小写，去除空格
- **中文**：使用 Unicode 规范化

## 示例输出

```
2026-01-11 09:30:00 - INFO - 开始导入 100 条条目...
2026-01-11 09:30:01 - INFO - 处理批次 1/1 (100 条)...
2026-01-11 09:30:05 - INFO - 导入完成！
2026-01-11 09:30:05 - INFO - 成功: 100 条
2026-01-11 09:30:05 - INFO - 失败: 0 条
2026-01-11 09:30:05 - INFO - 总计: 100 条
2026-01-11 09:30:05 - INFO - 
按词典统计:
  oxford:
    条目数: 100
    释义数: 450
    例句数: 890
```

## 注意事项

1. **数据库连接**：确保数据库配置正确（`api/config.py` 或环境变量）
2. **权限**：确保数据库用户有 INSERT、UPDATE 权限
3. **内存**：大量数据建议使用较小的 `--batch-size`
4. **备份**：导入前建议备份数据库

## 故障排除

### 导入失败

检查：
1. 数据库连接是否正常
2. 用户是否有足够权限
3. JSON 文件格式是否正确
4. 查看日志中的详细错误信息

### 性能问题

- 使用更大的 `--batch-size`（但要注意内存）
- 确保数据库索引已创建
- 关闭统计信息更新（`--no-stats`）

### 重复数据

- 导入工具会自动处理重复，使用 `ON CONFLICT` 更新现有记录
- 如果需要完全替换，先删除旧数据再导入

