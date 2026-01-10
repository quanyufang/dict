# 统一词典解析系统

## 项目目标

将各种格式不同的词典数据解析成统一的JSON结构，便于客户端渲染。

## 目录结构

```
unified/
├── README.md                    # 本文件（项目说明）
├── docs/                        # 📚 文档目录
│   ├── OXFORD_PARSER.md        # Oxford解析器完整文档（整合版）
│   ├── OXFORD_PARSER_STATUS.md # Oxford解析器开发状态
│   ├── OXFORD_BAD_CASES.md     # Bad case记录和修复方案
│   └── ...                     # 其他分析文档
├── parsers/                     # 🔧 解析器核心代码
│   ├── __init__.py
│   ├── base.py                 # 基础解析器类
│   ├── oxford.py               # Oxford解析器
│   ├── langdao.py              # Langdao解析器
│   └── ...                     # 其他解析器
├── models/                      # 📋 数据模型
│   ├── __init__.py
│   └── entry.py                # 统一数据模型
├── scripts/                     # 🛠️ 工具脚本
│   ├── extract_samples.py      # 样例提取
│   ├── analyze_formats.py      # 格式分析
│   ├── generate_oxford_report.py # 报告生成
│   └── ...                     # 其他工具脚本
├── tests/                       # 🧪 测试脚本
│   ├── test_parsers.py         # 解析器测试
│   ├── test_oxford_parser.py   # Oxford解析器测试
│   └── test_bad_cases.py       # Bad cases统一测试
├── samples/                     # 📦 样例数据
│   ├── oxford_samples.json
│   ├── langdao_samples.json
│   └── ...
├── comprehensive_samples/       # 📦 完整样例和报告
│   ├── oxford_comprehensive.json
│   ├── oxford_issues_report.md
│   └── ...
└── analysis/                    # 📊 分析结果
    ├── format_comparison_report.md
    └── ...
```

## 工作流程

1. **提取样例** - 从各词典提取代表性词条（`scripts/extract_samples.py`）
2. **分析格式** - 分析各词典的格式规则（`scripts/analyze_formats.py`）
3. **设计结构** - 基于实际数据设计统一结构（`models/entry.py`）
4. **实现解析** - 实现各词典解析器（`parsers/`）
5. **验证测试** - 测试解析结果（`tests/`）

## 词典列表

| 词典 | ID | 类型 | 优先级 | 状态 |
|------|-----|------|--------|------|
| 牛津英汉 | oxford-gb | 英汉 | 1 | ✅ 已实现 |
| 朗道英汉 | langdao-ec-gb | 英汉 | 4 | ✅ 已实现 |
| 现代汉语词典 | xiandaihanyucidian | 中文 | 2 | ⏳ 待实现 |
| GCIDE | gcide | 英英 | 3 | ⏳ 待实现 |
| 汉语拼音词典 | chinese_dict | 中文 | 5 | ✅ 已实现 |

## 快速开始

**注意**：所有脚本需要从 `src` 目录运行（因为使用了 `unified` 模块）

### 运行测试

```bash
cd /Users/fangyu/work/fishenglish/Daemon/dict/src

# 测试所有解析器
python3 -m unified.tests.test_parsers

# 测试Oxford解析器
python3 -m unified.tests.test_oxford_parser

# 测试bad cases
python3 -m unified.tests.test_bad_cases
```

### 提取样例

```bash
cd /Users/fangyu/work/fishenglish/Daemon/dict/src

# 提取所有词典样例
python3 -m unified.scripts.extract_samples

# 提取Oxford样例
python3 -m unified.scripts.extract_oxford_samples

# 提取全面样例
python3 -m unified.scripts.extract_comprehensive_samples
```

### 生成报告

```bash
cd /Users/fangyu/work/fishenglish/Daemon/dict/src

# 生成Oxford问题报告
python3 -m unified.scripts.generate_oxford_report

# 分析格式
python3 -m unified.scripts.analyze_formats

# 分析Oxford问题
python3 -m unified.scripts.analyze_oxford_issues
```

## 文档说明

- **`docs/OXFORD_PARSER.md`** ⭐ - Oxford解析器完整文档（整合版，推荐阅读）
- **`docs/INDEX.md`** - 文档索引，帮助导航所有文档
- **`docs/OXFORD_PARSER_STATUS.md`** - 开发状态和功能列表
- **`docs/OXFORD_BAD_CASES.md`** - Bad case记录和修复方案
- **`STRUCTURE.md`** - 项目结构说明

**推荐阅读顺序**：
1. 先看 `docs/INDEX.md` 了解文档结构
2. 再看 `docs/OXFORD_PARSER.md` 了解整体情况
3. 需要修复bad case时查看 `docs/OXFORD_BAD_CASES.md`

## 开发规范

1. **通用规则优先**：修复bad case时，尽量使用通用规则，避免针对单个单词的特殊处理
2. **记录所有case**：遇到的bad case都要记录到 `docs/OXFORD_BAD_CASES.md`
3. **统一测试**：修复后运行 `tests/test_bad_cases.py` 验证所有case
4. **文档集中管理**：所有文档放在 `docs/` 目录，避免分散


