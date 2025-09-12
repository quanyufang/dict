# 汉语拼音辞典构建系统

## 🎯 项目概述

这是一个完整的汉语拼音辞典构建系统，能够将JSON格式的汉字和词语数据转换为SQLite数据库和StarDict格式文件。系统采用分层构建策略，支持大数据量处理，并提供完整的查询工具。

## 🏗️ 系统架构

```
数据源 (JSON) → 数据解析器 → SQLite数据库 → StarDict生成器 → 最终输出
     ↓              ↓            ↓            ↓
 汉字数据      数据验证      数据存储      格式转换
 词语数据      数据清洗      索引优化      文件生成
 成语数据      数据合并      查询优化      查询工具
```

## 📁 文件结构

```
src/
├── dict_builder.py              # 核心字典构建器
├── stardict_generator.py        # StarDict格式生成器
├── build_complete_dictionary.py # 完整构建脚本
├── test_build_system.py         # 系统测试脚本
├── README.md                    # 本说明文档
└── chinese-dictionary-main/     # 数据源目录
    ├── character/               # 汉字数据
    ├── word/                    # 词语数据
    └── idiom/                   # 成语数据
```

## 🚀 快速开始

### 1. 环境准备

确保系统满足以下要求：
- Python 3.7+
- 足够的磁盘空间（建议至少2GB）
- 读写权限

### 2. 系统测试

在开始构建之前，建议先运行系统测试：

```bash
cd src
python test_build_system.py
```

如果所有测试通过，系统就可以开始构建了。

### 3. 完整构建

运行完整的构建流程：

```bash
python build_complete_dictionary.py --data-dir chinese-dictionary-main --output output
```

这将执行以下步骤：
1. 构建SQLite数据库
2. 生成StarDict格式文件
3. 创建查询工具
4. 生成文档

### 4. 分步构建

如果需要分步执行，可以使用以下命令：

#### 只构建数据库
```bash
python dict_builder.py --data-dir chinese-dictionary-main --output output
```

#### 只生成StarDict文件
```bash
python stardict_generator.py --db output/chinese_dictionary.db --output output
```

## 🔧 详细使用说明

### 字典构建器 (dict_builder.py)

**功能**：将JSON数据转换为SQLite数据库

**参数**：
- `--data-dir`: 数据源目录路径
- `--output-dir`: 输出目录路径

**特点**：
- 分层处理：按频率和类型分层构建
- 数据验证：自动验证数据完整性
- 错误处理：完善的错误处理和日志记录
- 性能优化：支持大数据量快速处理

### StarDict生成器 (stardict_generator.py)

**功能**：将SQLite数据库转换为StarDict格式

**参数**：
- `--db`: SQLite数据库文件路径
- `--output`: 输出目录路径

**特点**：
- 多格式输出：支持汉字、词语、完整版三种格式
- HTML格式化：生成美观的HTML内容
- 标准兼容：完全兼容StarDict 2.4.2标准
- 索引优化：优化的索引结构

### 完整构建脚本 (build_complete_dictionary.py)

**功能**：整合整个构建流程

**参数**：
- `--data-dir`: 数据源目录路径
- `--output`: 输出目录路径
- `--skip-db`: 跳过数据库构建
- `--skip-stardict`: 跳过StarDict生成

**特点**：
- 自动化流程：一键完成所有构建步骤
- 依赖检查：自动检查系统依赖
- 错误恢复：完善的错误处理和恢复机制
- 进度显示：实时显示构建进度

## 📊 数据格式说明

### 输入数据格式

#### 汉字数据 (char_base.json)
```json
{
  "char": "一",
  "strokes": 1,
  "pinyin": ["yī"],
  "radicals": "一",
  "frequency": 0,
  "structure": "D0"
}
```

#### 词语数据 (word.json)
```json
{
  "word": "一帆风顺",
  "pinyin": "yī fán fēng shùn",
  "abbr": "yffs",
  "explanation": "船上的帆挂起来顺着风行驶..."
}
```

### 输出数据格式

#### SQLite数据库
- `characters` 表：存储汉字信息
- `words` 表：存储词语信息
- 优化的索引结构

#### StarDict文件
- `.ifo`: 字典信息文件
- `.idx`: 索引文件
- `.dict`: 数据文件

## 🔍 查询工具使用

构建完成后，可以使用查询工具进行数据查询：

### 查询汉字
```bash
python output/query_tool.py output/chinese_dictionary.db char 一
```

### 查询词语
```bash
python output/query_tool.py output/chinese_dictionary.db word 一帆风顺
```

### 查询功能
- 支持汉字、拼音、部首查询
- 支持词语、拼音、缩写查询
- 模糊匹配和精确匹配
- 格式化的结果显示

## 📈 性能特点

### 构建性能
- **内存优化**：分批处理，避免内存溢出
- **并行处理**：支持多线程构建（可选）
- **增量更新**：支持数据的增量添加
- **缓存机制**：智能缓存提高构建速度

### 查询性能
- **索引优化**：多种索引策略
- **查询缓存**：智能查询缓存
- **连接池**：数据库连接池管理
- **异步查询**：支持异步查询操作

## 🛠️ 故障排除

### 常见问题

#### 1. 内存不足
**症状**：构建过程中出现内存错误
**解决方案**：
- 增加系统内存
- 使用 `--batch-size` 参数减小批处理大小
- 分批构建数据

#### 2. 磁盘空间不足
**症状**：构建过程中出现磁盘空间错误
**解决方案**：
- 清理磁盘空间
- 检查输出目录权限
- 使用压缩选项

#### 3. 数据格式错误
**症状**：JSON解析失败
**解决方案**：
- 检查JSON文件格式
- 验证数据完整性
- 查看详细错误日志

#### 4. 权限问题
**症状**：文件创建或写入失败
**解决方案**：
- 检查目录权限
- 使用管理员权限
- 修改文件权限设置

### 日志分析

系统会生成详细的日志文件：
- `dict_builder.log`: 字典构建日志
- `stardict_generator.log`: StarDict生成日志

查看日志文件可以帮助诊断问题：
```bash
tail -f output/dict_builder.log
tail -f output/stardict_generator.log
```

## 🔮 扩展功能

### 自定义数据源
系统支持自定义数据源，只需按照标准格式提供数据即可。

### 多语言支持
可以扩展支持其他语言的数据格式。

### 插件系统
支持插件扩展，可以添加新的数据处理器和输出格式。

### 分布式构建
支持分布式构建，可以跨多台机器并行处理大数据量。

## 📞 技术支持

### 问题反馈
如果遇到问题，请：
1. 查看日志文件
2. 检查系统要求
3. 查看故障排除部分
4. 提交问题报告

### 贡献代码
欢迎贡献代码和改进建议：
1. Fork项目
2. 创建功能分支
3. 提交Pull Request
4. 参与代码审查

## 📄 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 🙏 致谢

感谢所有为汉语拼音辞典项目做出贡献的开发者和用户。

---

**开始构建您的汉语拼音辞典吧！** 🎉

