#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
词典格式分析工具

分析各词典的原始数据格式，识别格式规则，为解析器开发提供依据。
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Set, Optional
from collections import Counter


SAMPLES_PATH = Path(__file__).parent / "samples"
OUTPUT_PATH = Path(__file__).parent / "analysis"


def analyze_oxford(samples: List[Dict]) -> Dict:
    """分析牛津词典格式"""
    analysis = {
        "dictionary_id": "oxford",
        "dictionary_name": "牛津英汉词典",
        "format_description": "纯文本格式，紧凑排列，类似纸质词典",
        "identified_patterns": [],
        "sample_analysis": []
    }
    
    patterns = []
    
    # 分析样例
    for sample in samples:
        word = sample['word']
        content = sample['raw_content']
        
        sample_info = {
            "word": word,
            "length": len(content),
            "features": []
        }
        
        # 1. 音标模式: /xxx; xxx/
        phonetic_match = re.search(r'/([^/]+);([^/]+)/', content)
        if phonetic_match:
            sample_info["features"].append(f"音标: {phonetic_match.group(0)[:50]}")
            if "phonetic" not in patterns:
                patterns.append({
                    "name": "phonetic",
                    "pattern": r'/([^/]+);([^/]+)/',
                    "description": "音标格式: /英式; 美式/",
                    "example": phonetic_match.group(0)
                })
        
        # 2. 词性模式: adj, n, v, adv 等
        pos_pattern = r'\b(n|v|adj|adv|prep|conj|pron|interj|det|aux|modal)\b'
        pos_matches = re.findall(pos_pattern, content)
        if pos_matches:
            sample_info["features"].append(f"词性: {', '.join(set(pos_matches))}")
        
        # 3. 序号模式: 1, 2, 3... 或 (a), (b), (c)...
        num_pattern = r'(?:^|\s)(\d+)\s+[^\d]'
        num_matches = re.findall(num_pattern, content)
        if num_matches:
            sample_info["features"].append(f"数字序号: 1-{max(int(n) for n in num_matches)}")
        
        letter_pattern = r'\(([a-z])\)'
        letter_matches = re.findall(letter_pattern, content)
        if letter_matches:
            sample_info["features"].append(f"字母序号: ({min(letter_matches)})-({max(letter_matches)})")
        
        # 4. 星号标记: * 开头的例句
        star_count = content.count('* ')
        if star_count > 0:
            sample_info["features"].append(f"星号例句: {star_count}个")
            if "example_star" not in [p['name'] for p in patterns]:
                patterns.append({
                    "name": "example_star",
                    "pattern": r'\* [^*]+',
                    "description": "例句以 * 开头",
                    "example": re.search(r'\* [^*]{0,100}', content).group(0) if re.search(r'\* [^*]{0,100}', content) else ""
                })
        
        # 5. 短语箭头: =>
        arrow_count = content.count('=>')
        if arrow_count > 0:
            sample_info["features"].append(f"箭头引用: {arrow_count}个")
        
        # 6. 方括号: [attrib], [pred] 等语法说明
        bracket_matches = re.findall(r'\[[^\]]+\]', content)
        if bracket_matches:
            sample_info["features"].append(f"方括号注释: {len(bracket_matches)}个")
            unique_brackets = set(bracket_matches)
            if "grammar_bracket" not in [p['name'] for p in patterns]:
                patterns.append({
                    "name": "grammar_bracket",
                    "pattern": r'\[[^\]]+\]',
                    "description": "语法说明使用方括号",
                    "examples": list(unique_brackets)[:5]
                })
        
        # 7. 中英文混合
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', content))
        english_words = len(re.findall(r'[a-zA-Z]+', content))
        sample_info["features"].append(f"中英比例: 中{chinese_chars}字/英{english_words}词")
        
        # 8. 习语/短语: IDM 标记
        if 'IDM' in content:
            sample_info["features"].append("包含IDM习语")
        
        # 9. 动词短语: PHR V 标记
        if 'PHR V' in content:
            sample_info["features"].append("包含PHR V动词短语")
        
        analysis["sample_analysis"].append(sample_info)
    
    analysis["identified_patterns"] = patterns
    
    # 格式总结
    analysis["format_summary"] = """
## 牛津英汉词典格式总结

### 基本结构
1. **音标**: `/英式音标; 美式音标/` 格式
2. **词性**: 使用标准缩写 (n, v, adj, adv, prep...)
3. **义项**: 数字序号 (1, 2, 3...) 表示主要释义
4. **细分**: 字母序号 (a), (b), (c)... 表示释义细分

### 特殊标记
- `*` 开头: 例句
- `=>` : 交叉引用
- `[attrib]`: 定语用法
- `[pred]`: 表语用法
- `[esp passive]`: 尤其被动语态
- `IDM`: 习语 (idiom)
- `PHR V`: 动词短语 (phrasal verb)

### 语言特点
- 中英混合：英文释义配中文翻译
- 紧凑排版：连续文本，无明显分隔
"""
    
    return analysis


def analyze_gcide(samples: List[Dict]) -> Dict:
    """分析GCIDE词典格式"""
    analysis = {
        "dictionary_id": "gcide",
        "dictionary_name": "GCIDE英英词典",
        "format_description": "类似Webster词典风格，带有词源和引用",
        "identified_patterns": [],
        "sample_analysis": []
    }
    
    patterns = []
    
    for sample in samples:
        word = sample['word']
        content = sample['raw_content']
        
        sample_info = {
            "word": word,
            "length": len(content),
            "features": []
        }
        
        # 1. 词条标题: Word \Word\ 格式
        title_match = re.search(r'\\([^\\]+)\\', content)
        if title_match:
            sample_info["features"].append(f"标题格式: \\{title_match.group(1)}\\")
            if "title" not in [p['name'] for p in patterns]:
                patterns.append({
                    "name": "title",
                    "pattern": r'\\([^\\]+)\\',
                    "description": "词条标题使用反斜杠包围"
                })
        
        # 2. 词性和词源: a., n., v. i., v. t. 等
        pos_matches = re.findall(r'\b(a\.|n\.|v\. i\.|v\. t\.|adv\.|prep\.|conj\.|pron\.)', content)
        if pos_matches:
            sample_info["features"].append(f"词性: {', '.join(set(pos_matches))}")
        
        # 3. 年份标记: [1913 Webster]
        year_matches = re.findall(r'\[(\d{4})\s+\w+\]', content)
        if year_matches:
            sample_info["features"].append(f"年份标记: {', '.join(set(year_matches))}")
            if "source_year" not in [p['name'] for p in patterns]:
                patterns.append({
                    "name": "source_year",
                    "pattern": r'\[(\d{4})\s+\w+\]',
                    "description": "来源和年份标记，如 [1913 Webster]"
                })
        
        # 4. 引用: --Author
        quote_matches = re.findall(r'--([A-Z][a-zA-Z]+)', content)
        if quote_matches:
            sample_info["features"].append(f"引用来源: {len(quote_matches)}个")
            if "citation" not in [p['name'] for p in patterns]:
                patterns.append({
                    "name": "citation",
                    "pattern": r'--([A-Z][a-zA-Z]+)',
                    "description": "引用来源，如 --Shak. (Shakespeare)"
                })
        
        # 5. 序号: 1., 2., 3. 或 (a), (b)
        num_pattern = r'^   (\d+)\.'
        num_matches = re.findall(num_pattern, content, re.MULTILINE)
        if num_matches:
            sample_info["features"].append(f"数字释义: {len(num_matches)}个")
        
        # 6. 词根标记: {root}
        root_matches = re.findall(r'\{([^}]+)\}', content)
        if root_matches:
            sample_info["features"].append(f"词根引用: {len(root_matches)}个")
            if "root_ref" not in [p['name'] for p in patterns]:
                patterns.append({
                    "name": "root_ref",
                    "pattern": r'\{([^}]+)\}',
                    "description": "词根或相关词引用，使用花括号",
                    "examples": root_matches[:5]
                })
        
        # 7. 同义词: Syn:
        if 'Syn:' in content or 'Syn.' in content:
            sample_info["features"].append("包含同义词")
        
        # 8. 缩进层级
        indent_levels = set(len(line) - len(line.lstrip()) 
                          for line in content.split('\n') 
                          if line.strip())
        sample_info["features"].append(f"缩进层级: {len(indent_levels)}级")
        
        analysis["sample_analysis"].append(sample_info)
    
    analysis["identified_patterns"] = patterns
    
    analysis["format_summary"] = """
## GCIDE英英词典格式总结

### 基本结构
1. **标题**: `\\Word\\` 格式，反斜杠包围
2. **词性**: `n.`, `v. i.`, `v. t.`, `a.`, `adv.` 等
3. **年份**: `[1913 Webster]` 标记来源和版本年份
4. **词源**: 包含词根和语源信息

### 特殊标记
- `{word}`: 交叉引用其他词条
- `--Author`: 引用来源（如 --Shak.）
- `Syn:` / `Ant:`: 同义词/反义词
- 缩进: 表示层级关系

### 语言特点
- 纯英文释义
- 包含丰富词源学信息
- 带有文学引用
- 格式较古老，类似传统纸质词典
"""
    
    return analysis


def analyze_langdao(samples: List[Dict]) -> Dict:
    """分析朗道词典格式"""
    analysis = {
        "dictionary_id": "langdao",
        "dictionary_name": "朗道英汉词典",
        "format_description": "简洁格式，分行清晰",
        "identified_patterns": [],
        "sample_analysis": []
    }
    
    patterns = []
    
    for sample in samples:
        word = sample['word']
        content = sample['raw_content']
        
        sample_info = {
            "word": word,
            "length": len(content),
            "features": []
        }
        
        # 1. 音标: *[xxx] 格式
        phonetic_match = re.search(r'\*\[([^\]]+)\]', content)
        if phonetic_match:
            sample_info["features"].append(f"音标: *[{phonetic_match.group(1)}]")
            if "phonetic" not in [p['name'] for p in patterns]:
                patterns.append({
                    "name": "phonetic",
                    "pattern": r'\*\[([^\]]+)\]',
                    "description": "音标格式: *[音标]"
                })
        
        # 2. 词性: n., v., a., ad. 等
        pos_matches = re.findall(r'\b(n\.|v\.|a\.|ad\.|prep\.|conj\.|pron\.|int\.)', content)
        if pos_matches:
            sample_info["features"].append(f"词性: {', '.join(set(pos_matches))}")
        
        # 3. 专业标签: 【经】【计】【医】等
        domain_matches = re.findall(r'【([^】]+)】', content)
        if domain_matches:
            sample_info["features"].append(f"专业领域: {', '.join(set(domain_matches))}")
            if "domain" not in [p['name'] for p in patterns]:
                patterns.append({
                    "name": "domain",
                    "pattern": r'【([^】]+)】',
                    "description": "专业领域标签，如【经】【计】【医】",
                    "examples": list(set(domain_matches))[:5]
                })
        
        # 4. 相关词组标记
        if '相关词组:' in content or '相关词组：' in content:
            sample_info["features"].append("包含相关词组")
            if "related" not in [p['name'] for p in patterns]:
                patterns.append({
                    "name": "related",
                    "pattern": r'相关词组[:：]',
                    "description": "相关词组部分"
                })
        
        # 5. 分行特征
        lines = content.strip().split('\n')
        sample_info["features"].append(f"行数: {len(lines)}")
        
        analysis["sample_analysis"].append(sample_info)
    
    analysis["identified_patterns"] = patterns
    
    analysis["format_summary"] = """
## 朗道英汉词典格式总结

### 基本结构
1. **音标**: `*[音标]` 格式，星号开头
2. **词性**: `n.`, `v.`, `a.`, `ad.` 等标准缩写
3. **释义**: 中文释义，逗号分隔多个含义
4. **词组**: `相关词组:` 列出常用搭配

### 特殊标记
- `【经】【计】【医】`: 专业领域标签
- 分行清晰，每类信息独立一行

### 语言特点
- 以中文释义为主
- 格式简洁清晰
- 适合快速查阅
"""
    
    return analysis


def analyze_xiandai(samples: List[Dict]) -> Dict:
    """分析现代汉语词典格式"""
    analysis = {
        "dictionary_id": "xiandaihanyucidian",
        "dictionary_name": "现代汉语词典",
        "format_description": "HTML格式，结构化标记",
        "identified_patterns": [],
        "sample_analysis": []
    }
    
    patterns = []
    
    for sample in samples:
        word = sample['word']
        content = sample['raw_content']
        
        sample_info = {
            "word": word,
            "length": len(content),
            "features": []
        }
        
        # 1. HTML标签
        html_tags = set(re.findall(r'<([a-zA-Z]+)', content))
        if html_tags:
            sample_info["features"].append(f"HTML标签: {', '.join(html_tags)}")
        
        # 2. 拼音
        pinyin_match = re.search(r'[\u0101-\u01FF\u00E0-\u00FF]+|[āáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜ]+', content)
        if pinyin_match:
            sample_info["features"].append(f"拼音: 包含")
        
        # 3. 释义编号
        num_matches = re.findall(r'[①②③④⑤⑥⑦⑧⑨⑩]', content)
        if num_matches:
            sample_info["features"].append(f"圆圈数字: {len(num_matches)}个")
            if "circled_num" not in [p['name'] for p in patterns]:
                patterns.append({
                    "name": "circled_num",
                    "pattern": r'[①②③④⑤⑥⑦⑧⑨⑩]',
                    "description": "使用圆圈数字编号释义"
                })
        
        # 4. 词性标记: 〈名〉〈动〉〈形〉等
        pos_matches = re.findall(r'〈([^〉]+)〉', content)
        if pos_matches:
            sample_info["features"].append(f"词性标记: {', '.join(set(pos_matches))}")
            if "pos_bracket" not in [p['name'] for p in patterns]:
                patterns.append({
                    "name": "pos_bracket",
                    "pattern": r'〈([^〉]+)〉',
                    "description": "词性使用尖括号，如〈名〉〈动〉"
                })
        
        # 5. 例句标记: ～ 代替词头
        tilde_count = content.count('～')
        if tilde_count > 0:
            sample_info["features"].append(f"波浪线(～): {tilde_count}个")
        
        # 6. 词条分隔
        if '◎' in content:
            sample_info["features"].append("包含◎分隔符")
        
        analysis["sample_analysis"].append(sample_info)
    
    analysis["identified_patterns"] = patterns
    
    analysis["format_summary"] = """
## 现代汉语词典格式总结

### 基本结构
1. **拼音**: 带声调的拼音字母
2. **词性**: `〈名〉〈动〉〈形〉〈副〉` 等
3. **释义**: 圆圈数字编号 ①②③...
4. **例句**: 使用 `～` 代替词头

### 特殊标记
- HTML格式标签
- `◎` 分隔不同读音或词性
- 繁体/异体字标注

### 语言特点
- 纯中文内容
- 规范的现代汉语释义
- 包含词性和用法说明
"""
    
    return analysis


def analyze_chinese_dict(samples: List[Dict]) -> Dict:
    """分析汉语拼音词典格式"""
    analysis = {
        "dictionary_id": "chinese_dict",
        "dictionary_name": "汉语拼音词典",
        "format_description": "JSON格式，结构化数据",
        "identified_patterns": [],
        "sample_analysis": []
    }
    
    for sample in samples:
        word = sample['word']
        content = sample['raw_content']
        
        sample_info = {
            "word": word,
            "length": len(content),
            "features": []
        }
        
        # 检测是否为JSON
        try:
            data = json.loads(content)
            sample_info["features"].append("JSON格式")
            sample_info["features"].append(f"字段: {', '.join(data.keys())}")
            
            if isinstance(data, dict):
                for key, value in data.items():
                    if isinstance(value, str):
                        sample_info["features"].append(f"{key}: 字符串")
                    elif isinstance(value, list):
                        sample_info["features"].append(f"{key}: 数组[{len(value)}]")
                    elif isinstance(value, dict):
                        sample_info["features"].append(f"{key}: 对象")
        except json.JSONDecodeError:
            sample_info["features"].append("非JSON格式")
        
        analysis["sample_analysis"].append(sample_info)
    
    analysis["format_summary"] = """
## 汉语拼音词典格式总结

### 基本结构
- JSON格式存储
- 包含拼音、释义、例句等字段
- 结构化数据，易于解析

### 语言特点
- 标准JSON格式
- 拼音使用数字声调或带调字母
- 适合程序化处理
"""
    
    return analysis


def main():
    """主函数"""
    OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
    
    all_analysis = {}
    
    # 加载并分析各词典样例
    analyzers = {
        'oxford': analyze_oxford,
        'xiandaihanyucidian': analyze_xiandai,
        'gcide': analyze_gcide,
        'langdao': analyze_langdao,
        'chinese_dict': analyze_chinese_dict
    }
    
    for dict_id, analyzer in analyzers.items():
        sample_file = SAMPLES_PATH / f"{dict_id}_samples.json"
        if not sample_file.exists():
            print(f"⚠️  样例文件不存在: {sample_file}")
            continue
            
        with open(sample_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"\n📊 分析 {dict_id}...")
        analysis = analyzer(data['samples'])
        all_analysis[dict_id] = analysis
        
        # 保存单独分析结果
        output_file = OUTPUT_PATH / f"{dict_id}_analysis.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, ensure_ascii=False, indent=2)
        print(f"   ✅ 已保存: {output_file.name}")
    
    # 生成综合分析报告
    report = generate_comparison_report(all_analysis)
    report_file = OUTPUT_PATH / "format_comparison_report.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\n📄 综合报告: {report_file}")


def generate_comparison_report(all_analysis: Dict) -> str:
    """生成格式对比报告"""
    report = """# 词典格式对比分析报告

## 概述

本报告分析了五种词典的原始数据格式，为设计统一数据结构提供依据。

## 词典列表

| 词典 | 格式类型 | 索引语言 | 解释语言 |
|------|----------|----------|----------|
| 牛津英汉 | 纯文本 | 英文 | 中英混合 |
| 现代汉语 | HTML | 中文 | 中文 |
| GCIDE | 纯文本 | 英文 | 英文 |
| 朗道英汉 | 纯文本 | 英文 | 中文 |
| 汉语拼音 | JSON | 中文 | 中文 |

"""
    
    # 添加各词典详细分析
    for dict_id, analysis in all_analysis.items():
        report += f"\n---\n\n{analysis.get('format_summary', '')}\n"
    
    report += """
---

## 统一格式设计建议

基于以上分析，统一数据结构应包含：

### 1. 基础字段
- `headword`: 词头
- `source_id`: 来源词典
- `pronunciations`: 发音列表（支持多种音标格式）

### 2. 释义结构
- 按词性分组
- 支持层级编号（主释义 + 细分）
- 例句与释义关联

### 3. 扩展信息
- 领域标签（专业术语）
- 语体标记（正式/口语）
- 相关词（同/反义词、词组）

### 4. 原始数据
- 保留原始内容用于调试
- 记录解析质量分数

## 下一步

1. 根据此分析完善 `models/entry.py` 数据结构
2. 实现各词典的解析器
3. 在FastAPI网站验证解析效果
"""
    
    return report


if __name__ == '__main__':
    main()

