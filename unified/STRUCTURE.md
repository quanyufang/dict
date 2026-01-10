# 项目结构说明

> 最后更新: 2026-01-08

## 📁 目录结构

```
unified/
├── README.md                    # 项目主文档
├── STRUCTURE.md                 # 本文件（结构说明）
│
├── docs/                        # 📚 文档目录
│   ├── INDEX.md                # 文档索引（推荐先看这个）
│   ├── OXFORD_PARSER.md        # Oxford解析器完整文档（整合版）⭐
│   ├── OXFORD_PARSER_STATUS.md # 开发状态和功能列表
│   ├── OXFORD_BAD_CASES.md     # Bad case记录和修复方案
│   ├── README.md               # 文档说明
│   └── archive/                # 归档文档（已整合到主文档）
│       ├── OXFORD_PARSER_IMPROVEMENT_PLAN.md
│       ├── OXFORD_ISSUES_FOR_REVIEW.md
│       └── COME_UP_CASE_ANALYSIS.md
│
├── parsers/                     # 🔧 解析器核心代码
│   ├── __init__.py
│   ├── base.py                 # 基础解析器类
│   ├── oxford.py               # Oxford解析器
│   └── langdao.py              # Langdao解析器
│
├── models/                      # 📋 数据模型
│   ├── __init__.py
│   └── entry.py                # 统一数据模型（DictionaryEntry等）
│
├── scripts/                     # 🛠️ 工具脚本
│   ├── extract_samples.py      # 提取样例
│   ├── extract_comprehensive_samples.py # 提取全面样例
│   ├── extract_oxford_samples.py # 提取Oxford样例
│   ├── analyze_formats.py      # 分析格式
│   ├── analyze_oxford_issues.py # 分析Oxford问题
│   ├── generate_oxford_report.py # 生成报告
│   ├── langdao_parse_review.py # Langdao解析审查
│   └── sample_extractor.py     # 样例提取器
│
├── tests/                       # 🧪 测试脚本
│   ├── test_parsers.py         # 解析器测试
│   ├── test_oxford_parser.py   # Oxford解析器测试
│   └── test_bad_cases.py       # Bad cases统一测试
│
├── samples/                     # 📦 样例数据
│   ├── oxford_samples.json
│   ├── langdao_samples.json
│   └── ...
│
├── comprehensive_samples/       # 📦 完整样例和报告
│   ├── oxford_comprehensive.json
│   ├── oxford_issues_report.md
│   ├── oxford_issues_data.json
│   └── ...
│
└── analysis/                    # 📊 分析结果
    ├── format_comparison_report.md
    └── ...
```

## 📝 文档说明

### 主要文档
- **`README.md`** - 项目主文档，包含快速开始和目录结构
- **`docs/OXFORD_PARSER.md`** ⭐ - Oxford解析器完整文档（整合版，推荐阅读）
- **`docs/INDEX.md`** - 文档索引，帮助导航所有文档

### 详细文档
- **`docs/OXFORD_PARSER_STATUS.md`** - 开发状态和功能列表
- **`docs/OXFORD_BAD_CASES.md`** - Bad case记录和修复方案

### 归档文档
已整合到主文档，保留在 `docs/archive/` 作为历史参考

## 🛠️ 工具脚本

所有工具脚本都在 `scripts/` 目录：
- **提取脚本** - 从词典文件提取样例
- **分析脚本** - 分析格式和问题
- **报告脚本** - 生成分析报告

## 🧪 测试脚本

所有测试脚本都在 `tests/` 目录：
- **解析器测试** - 测试各解析器功能
- **Bad cases测试** - 统一测试所有记录的bad case

## 📦 数据文件

- **`samples/`** - 初始提取的样例数据
- **`comprehensive_samples/`** - 全面样例和解析报告
- **`analysis/`** - 格式分析和比较结果

## 🚀 运行方式

所有脚本需要从 `src` 目录运行（使用模块方式）：

```bash
cd /Users/fangyu/work/fishenglish/Daemon/dict/src

# 运行测试
python3 -m unified.tests.test_bad_cases

# 运行工具脚本
python3 -m unified.scripts.generate_oxford_report
```

## 📋 开发规范

1. **文档集中管理**：所有文档放在 `docs/` 目录
2. **脚本分类存放**：工具脚本在 `scripts/`，测试脚本在 `tests/`
3. **数据分类存储**：样例数据在 `samples/` 和 `comprehensive_samples/`
4. **Bad case记录**：所有bad case记录到 `docs/OXFORD_BAD_CASES.md`
5. **统一测试**：修复后运行 `tests/test_bad_cases.py` 验证

