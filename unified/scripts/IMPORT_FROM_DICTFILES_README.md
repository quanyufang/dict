# 全量数据导入工具使用说明

## 概述

`import_from_dictfiles.py` 用于从原始词典文件（`.db` + `.dictcontent`）全量导入数据到PostgreSQL数据库。

## 数据源

**原始词典文件位置**：`/Users/fangyu/work/fishenglish/Daemon/dict/app_dictfiles/`

包含以下词典：
- `oxford-gb.db` + `oxford-gb.dictcontent` - 牛津英汉词典
- `langdao-ec-gb.db` + `langdao-ec-gb.dictcontent` - 朗道英汉词典
- `gcide.db` + `gcide.dictcontent` - GCIDE英英词典
- `xiandaihanyucidian.db` + `xiandaihanyucidian.dictcontent` - 现代汉语词典

## 使用方法

### 1. 导入单个词典

```bash
cd /Users/fangyu/work/fishenglish/Daemon/dict/src/unified/scripts
source ../venv/bin/activate
python import_from_dictfiles.py --source oxford
```

### 2. 导入所有词典

```bash
python import_from_dictfiles.py --all
```

### 3. 测试导入（限制数量）

```bash
# 只导入前100条进行测试
python import_from_dictfiles.py --source oxford --limit 100
```

### 4. 自定义批量大小

```bash
# 使用更大的批量大小（默认100）
python import_from_dictfiles.py --source oxford --batch-size 500
```

## 参数说明

- `--source`: 词典ID，可选值：`oxford`, `langdao`, `gcide`, `xiandaihanyucidian`
- `--all`: 导入所有词典
- `--batch-size`: 批量处理大小（默认100）
- `--limit`: 限制导入数量（用于测试）

## 工作流程

1. **读取索引文件**：从 `.db` 文件中读取所有词条列表
2. **读取原始内容**：从 `.dictcontent` 文件中读取每个词条的原始内容
3. **解析数据**：使用对应的解析器解析原始内容
4. **批量导入**：将解析后的数据批量插入到PostgreSQL数据库
5. **更新索引**：更新 `dictionary_index` 表以支持遍历查询

## 输出信息

脚本会输出详细的进度和统计信息：

```
============================================================
开始导入: 牛津英汉词典 (oxford)
索引文件: /Users/fangyu/work/fishenglish/Daemon/dict/app_dictfiles/oxford-gb.db
正文文件: /Users/fangyu/work/fishenglish/Daemon/dict/app_dictfiles/oxford-gb.dictcontent
============================================================
正在读取词条列表...
总词条数: 39292
进度: 100/39292 已解析: 98 已导入: 98 失败: 2 速度: 25.3 条/秒
...
正在更新索引表...
索引表已更新: oxford (共 39290 条索引)
============================================================
导入完成: 牛津英汉词典
总词条数: 39292
解析成功: 39290
解析失败: 2
导入成功: 39290
导入失败: 0
耗时: 1550.2 秒
============================================================
```

## 注意事项

1. **数据库连接**：确保PostgreSQL数据库已启动，且配置正确（`unified/api/config.py`）
2. **数据重复**：使用 `ON CONFLICT` 处理重复，相同词头会更新
3. **解析失败**：部分词条可能解析失败（如特殊格式），会记录在统计中
4. **索引更新**：导入完成后会自动更新索引表，支持遍历查询功能
5. **性能**：大数据量导入需要较长时间，建议在服务器上运行

## 预期导入时间

根据词典大小估算：
- Oxford（~39K词条）：约25-30分钟
- Langdao（~数万词条）：约20-30分钟
- GCIDE（~10万+词条）：约1-2小时
- 现代汉语词典（~数万词条）：约20-30分钟

## 故障排查

1. **文件不存在**：检查 `app_dictfiles/` 目录下是否有对应的 `.db` 和 `.dictcontent` 文件
2. **数据库连接失败**：检查数据库配置和网络连接
3. **解析器错误**：部分词条格式特殊可能导致解析失败，这是正常的
4. **内存不足**：如果内存不足，可以减小 `--batch-size` 参数

