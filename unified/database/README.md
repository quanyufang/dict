# 词典数据库设计文档

## 概述

本文档描述了词典数据的PostgreSQL数据库表结构设计。

## 设计原则

1. **灵活存储**：使用JSONB存储灵活的词典数据结构（释义、例句等）
2. **快速查询**：使用索引支持快速key查询
3. **遍历支持**：使用索引表支持"上一个/下一个"遍历功能
4. **多词典支持**：通过source_id区分不同词典

## 表结构

### 1. dictionary_entries（词典条目主表）

存储所有词典条目的完整信息。

**主要字段**：
- `headword`: 词头（索引字段）
- `source_id`: 词典来源ID（oxford/gcide/langdao/xiandai/chinese_dict）
- `senses`: 释义数组（JSONB，必须字段）
- `pronunciations`: 发音信息（JSONB）
- `pinyin`: 拼音（中文词典用）
- 其他字段见SQL脚本

**索引**：
- `headword`: 支持快速词头查询
- `source_id, headword`: 支持精确查询
- `source_id, headword`: 支持遍历查询
- JSONB索引：支持JSON查询（如需要）

### 2. dictionary_index（词典索引表）

用于支持遍历查询的索引表。

**主要字段**：
- `source_id`: 词典来源ID
- `headword`: 词头
- `sort_key`: 排序键（用于排序，可能包含大小写、拼音等）
- `entry_id`: 关联到dictionary_entries.id

**索引**：
- `source_id, sort_key`: 支持快速遍历查询

**排序规则**：
- 英文词典：按字母顺序（不区分大小写）
- 中文词典：按拼音顺序

### 3. dictionary_stats（词典统计表）

存储词典统计信息。

**主要字段**：
- `source_id`: 词典来源ID
- `total_entries`: 总条目数
- `total_senses`: 总释义数
- `total_examples`: 总例句数
- `statistics`: 更多统计信息（JSONB）

## 查询模式

### 1. Key查询（精确查询）

```sql
SELECT * FROM dictionary_entries 
WHERE headword = 'have' AND source_id = 'oxford';
```

### 2. Key查询（模糊查询）

```sql
SELECT * FROM dictionary_entries 
WHERE headword LIKE 'have%' AND source_id = 'oxford'
ORDER BY headword LIMIT 20;
```

### 3. 遍历查询（下一个）

```sql
SELECT e.* FROM dictionary_entries e
JOIN dictionary_index i ON e.id = i.entry_id
WHERE i.source_id = 'oxford' 
  AND i.sort_key > (
      SELECT sort_key FROM dictionary_index 
      WHERE headword = 'have' AND source_id = 'oxford'
  )
ORDER BY i.sort_key
LIMIT 1;
```

### 4. 遍历查询（上一个）

```sql
SELECT e.* FROM dictionary_entries e
JOIN dictionary_index i ON e.id = i.entry_id
WHERE i.source_id = 'oxford' 
  AND i.sort_key < (
      SELECT sort_key FROM dictionary_index 
      WHERE headword = 'have' AND source_id = 'oxford'
  )
ORDER BY i.sort_key DESC
LIMIT 1;
```

### 5. 多词典查询

```sql
SELECT * FROM dictionary_entries 
WHERE headword = 'have' 
  AND source_id IN ('oxford', 'gcide', 'langdao')
ORDER BY source_id;
```

## 数据导入注意事项

1. **sort_key生成规则**：
   - 英文词典：使用`LOWER(headword)`作为sort_key
   - 中文词典：使用`pinyin`作为sort_key，如果没有pinyin则使用headword

2. **JSONB数据格式**：
   - `senses`: 数组，每个元素包含definition, pos, sense_number, examples等
   - `pronunciations`: 数组，每个元素包含ipa, region, audio_file等
   - 具体格式见`models/entry.py`的`to_dict()`方法

3. **批量导入优化**：
   - 使用COPY命令或批量INSERT
   - 导入后创建索引（如果数据量大）
   - 定期更新统计表

## 性能优化建议

1. **索引优化**：
   - 已创建必要的索引
   - 根据实际查询模式调整索引

2. **JSONB查询优化**：
   - 如果需要对JSONB字段进行复杂查询，考虑使用GIN索引
   - 已在senses和tags字段上创建GIN索引

3. **分区表（可选）**：
   - 如果数据量非常大，可以考虑按source_id分区

## 迁移脚本

创建数据库和表：

```bash
# 创建数据库
createdb fishenglish_dict

# 导入表结构
psql -d fishenglish_dict -f postgresql_schema.sql
```

