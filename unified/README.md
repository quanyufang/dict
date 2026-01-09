# 统一词典解析系统

## 项目目标

将各种格式不同的词典数据解析成统一的JSON结构，便于客户端渲染。

## 目录结构

```
unified/
├── README.md              # 本文件
├── sample_extractor.py    # 样例数据提取工具
├── analyze_samples.py     # 样例分析工具
├── samples/               # 提取的样例数据
│   ├── oxford_samples.json
│   ├── xiandai_samples.json
│   ├── gcide_samples.json
│   ├── langdao_samples.json
│   └── chinese_dict_samples.json
├── parsers/               # 各词典解析器
│   ├── __init__.py
│   ├── base.py
│   ├── oxford.py
│   ├── xiandai.py
│   ├── gcide.py
│   └── langdao.py
├── models/                # 数据模型
│   ├── __init__.py
│   └── entry.py
└── tests/                 # 测试
```

## 工作流程

1. **提取样例** - 从各词典提取代表性词条
2. **分析格式** - 分析各词典的格式规则
3. **设计结构** - 基于实际数据设计统一结构
4. **实现解析** - 实现各词典解析器
5. **验证测试** - 测试解析结果

## 词典列表

| 词典 | ID | 类型 | 优先级 |
|------|-----|------|--------|
| 牛津英汉 | oxford-gb | 英汉 | 1 |
| 现代汉语词典 | xiandaihanyucidian | 中文 | 2 |
| GCIDE | gcide | 英英 | 3 |
| 朗道英汉 | langdao-ec-gb | 英汉 | 4 |
| 汉语拼音词典 | chinese_dict | 中文 | 5 |

