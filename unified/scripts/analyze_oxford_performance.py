#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析Oxford解析器性能
- 重新解析所有样例
- 收集bad case
- 对比改进前后的解析成功率
"""

import sys
import json
import re
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass, asdict

sys.path.insert(0, str(Path(__file__).parent.parent))

from unified.parsers.oxford import OxfordParser


@dataclass
class ParseResult:
    """解析结果"""
    word: str
    raw_content: str
    content_length: int
    parsed: bool
    parse_quality: float
    pronunciation_count: int
    sense_count: int
    example_count: int
    parse_notes: List[str]
    pattern_type: str
    issues: List[str] = None
    
    def __post_init__(self):
        if self.issues is None:
            self.issues = []


def analyze_parsing_results(samples: List[Dict]) -> Dict[str, Any]:
    """分析解析结果，收集bad case"""
    parser = OxfordParser()
    
    results = []
    bad_cases = {
        "no_pronunciation": [],
        "no_senses": [],
        "low_quality": [],
        "few_senses": [],  # 可能漏解析
        "no_examples_long": [],  # 长条目但无例句
        "very_short": [],  # <50字符
        "very_long": [],  # >8000字符
        "definition_issues": [],  # 定义文本有问题
        "example_issues": [],  # 例句提取有问题
    }
    
    for sample in samples:
        word = sample['word']
        raw_content = sample['raw_content']
        
        entry = parser.parse(word, raw_content)
        
        # 提取解析结果
        result = ParseResult(
            word=word,
            raw_content=raw_content,
            content_length=len(raw_content),
            parsed=entry is not None,
            parse_quality=entry.parse_quality if entry else 0,
            pronunciation_count=len(entry.pronunciations) if entry else 0,
            sense_count=len(entry.senses) if entry else 0,
            example_count=sum(len(s.examples) for s in entry.senses) if entry else 0,
            parse_notes=entry.parse_notes if entry else [],
            pattern_type=entry.parse_notes[0].split(': ')[-1] if entry and entry.parse_notes else "unknown",
        )
        
        # 分析问题
        issues = []
        
        if not result.parsed or not result.sense_count:
            issues.append("no_senses")
            bad_cases["no_senses"].append(asdict(result))
        
        if not result.pronunciation_count:
            issues.append("no_pronunciation")
            bad_cases["no_pronunciation"].append(asdict(result))
        
        if result.parse_quality < 0.8:
            issues.append("low_quality")
            bad_cases["low_quality"].append(asdict(result))
        
        if result.sense_count <= 1 and result.content_length > 500:
            issues.append("few_senses")
            bad_cases["few_senses"].append(asdict(result))
        
        if result.content_length > 300 and result.example_count == 0:
            issues.append("no_examples_long")
            bad_cases["no_examples_long"].append(asdict(result))
        
        if result.content_length < 50:
            issues.append("very_short")
            bad_cases["very_short"].append(asdict(result))
        
        if result.content_length > 8000:
            issues.append("very_long")
            bad_cases["very_long"].append(asdict(result))
        
        # 检查定义文本问题（包含冒号后内容、例句片段等）
        if entry:
            has_definition_issue = False
            for i, sense in enumerate(entry.senses):
                if not sense.definition:
                    continue
                    
                # 检查1: 定义中是否包含明显的例句片段（大写字母开头+中文翻译）
                # 格式: 定义 例句. 翻译.
                if re.search(r'[A-Z][^.]*\.\s+[\u4e00-\u9fff]', sense.definition):
                    has_definition_issue = True
                    break
                
                # 检查2: 定义中包含冒号但不在结尾，且后面有内容（可能是漏提取的例句）
                colon_pos = sense.definition.find(':')
                if colon_pos > 0 and colon_pos < len(sense.definition) - 1:
                    after_colon = sense.definition[colon_pos+1:].strip()
                    # 如果冒号后有明显的句子（大写字母开头）
                    if after_colon and re.match(r'^[A-Z]', after_colon):
                        has_definition_issue = True
                        break
                
                # 检查3: 定义过长且无例句（可能包含例句但没有提取）
                if len(sense.definition) > 300 and result.example_count == 0:
                    # 检查是否包含可能的例句模式
                    if re.search(r'[A-Z][^.]*\.', sense.definition):
                        has_definition_issue = True
                        break
            
            if has_definition_issue:
                if word not in [bc['word'] for bc in bad_cases["definition_issues"]]:
                    bad_cases["definition_issues"].append(asdict(result))
        
        result.issues = issues
        results.append(result)
    
    # 统计信息
    total = len(results)
    success_count = sum(1 for r in results if r.parsed and r.sense_count > 0)
    avg_senses = sum(r.sense_count for r in results) / success_count if success_count > 0 else 0
    avg_examples = sum(r.example_count for r in results) / success_count if success_count > 0 else 0
    
    # 分类统计
    issues_summary = {
        k: len(v) for k, v in bad_cases.items()
    }
    
    return {
        "total_samples": total,
        "success_count": success_count,
        "failed_count": total - success_count,
        "success_rate": success_count / total if total > 0 else 0,
        "avg_senses": avg_senses,
        "avg_examples": avg_examples,
        "issues_summary": issues_summary,
        "bad_cases": bad_cases,
        "all_results": [asdict(r) for r in results],
    }


def generate_comparison_report(analysis_data: Dict, output_path: Path):
    """生成对比报告"""
    
    report = f"""# Oxford解析器性能分析报告

> 生成时间: 2026-01-08  
> 总样例数: {analysis_data['total_samples']}

---

## 📊 解析统计

| 指标 | 数值 | 占比 |
|------|------|------|
| 总样例 | {analysis_data['total_samples']} | 100% |
| 解析成功 | {analysis_data['success_count']} | {analysis_data['success_rate']*100:.1f}% |
| 解析失败 | {analysis_data['failed_count']} | {(1-analysis_data['success_rate'])*100:.1f}% |
| 平均释义数 | {analysis_data['avg_senses']:.1f} | - |
| 平均例句数 | {analysis_data['avg_examples']:.1f} | - |

---

## 📊 问题统计

| 问题类型 | 数量 | 占比 | 说明 |
|---------|------|------|------|
| 无音标 | {analysis_data['issues_summary']['no_pronunciation']} | {analysis_data['issues_summary']['no_pronunciation']/analysis_data['total_samples']*100:.1f}% | 主要是交叉引用和短语词条 |
| 无释义 | {analysis_data['issues_summary']['no_senses']} | {analysis_data['issues_summary']['no_senses']/analysis_data['total_samples']*100:.1f}% | 解析失败 |
| 质量分 < 0.8 | {analysis_data['issues_summary']['low_quality']} | {analysis_data['issues_summary']['low_quality']/analysis_data['total_samples']*100:.1f}% | 解析质量较低 |
| 释义数 <= 1（可能漏解析） | {analysis_data['issues_summary']['few_senses']} | {analysis_data['issues_summary']['few_senses']/analysis_data['total_samples']*100:.1f}% | **重点关注** |
| 无例句（长条目） | {analysis_data['issues_summary']['no_examples_long']} | {analysis_data['issues_summary']['no_examples_long']/analysis_data['total_samples']*100:.1f}% | 可能例句提取失败 |
| 定义文本问题 | {analysis_data['issues_summary']['definition_issues']} | {analysis_data['issues_summary']['definition_issues']/analysis_data['total_samples']*100:.1f}% | 定义中可能包含例句或冗余内容 |
| 超短条目 (<50字符) | {analysis_data['issues_summary']['very_short']} | {analysis_data['issues_summary']['very_short']/analysis_data['total_samples']*100:.1f}% | 可能是交叉引用 |
| 超长条目 (>8000字符) | {analysis_data['issues_summary']['very_long']} | {analysis_data['issues_summary']['very_long']/analysis_data['total_samples']*100:.1f}% | 可能需要特殊处理 |

---

## 🔴 Bad Cases 详细列表

### 1️⃣ 可能漏解析（释义数 <= 1，但内容长度 > 500）

**重点关注这些case，可能包含多个义项但只解析出1个。**

"""
    
    # 按长度排序，优先处理最长的
    few_senses_cases = sorted(
        analysis_data['bad_cases']['few_senses'],
        key=lambda x: x['content_length'],
        reverse=True
    )
    
    for i, case in enumerate(few_senses_cases[:15], 1):
        report += f"""#### {i}. `{case['word']}` (长度: {case['content_length']}, 释义数: {case['sense_count']})

**原始数据**:
```
{case['raw_content'][:500]}{'...' if len(case['raw_content']) > 500 else ''}
```

**解析结果**:
- 格式类型: {case['pattern_type']}
- 释义数: {case['sense_count']}
- 例句数: {case['example_count']}
- 解析质量: {case['parse_quality']}
- 问题: {', '.join(case['issues'] if case.get('issues') else [])}

---

"""
    
    report += f"""
### 2️⃣ 定义文本问题（定义中可能包含例句或冗余内容）

"""
    
    for i, case in enumerate(analysis_data['bad_cases']['definition_issues'][:10], 1):
        report += f"""#### {i}. `{case['word']}` (长度: {case['content_length']})

**原始数据**:
```
{case['raw_content'][:400]}{'...' if len(case['raw_content']) > 400 else ''}
```

**解析结果**:
- 释义数: {case['sense_count']}
- 例句数: {case['example_count']}

**问题**: 定义文本可能包含例句片段或冗余内容

---

"""
    
    report += f"""
### 3️⃣ 无例句（长条目，长度 > 300）

"""
    
    for i, case in enumerate(analysis_data['bad_cases']['no_examples_long'][:10], 1):
        report += f"""#### {i}. `{case['word']}` (长度: {case['content_length']})

**原始数据**:
```
{case['raw_content'][:300]}{'...' if len(case['raw_content']) > 300 else ''}
```

**解析结果**:
- 释义数: {case['sense_count']}
- 例句数: {case['example_count']} (应该 > 0)

**问题**: 长条目但未提取到例句，可能是例句格式特殊

---

"""
    
    report += """
## 📝 建议

1. **重点关注"可能漏解析"的case**：这些case内容较长但只解析出1个释义，可能包含多个义项
2. **检查定义文本问题**：定义中可能包含例句片段，需要改进文本分割逻辑
3. **优化例句提取**：长条目但无例句，可能是例句格式特殊，需要改进例句识别逻辑

---

## 📋 完整数据

完整数据已保存在JSON文件中，便于进一步分析。

"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)


def main():
    """主函数"""
    # 加载样例数据
    samples_file = Path(__file__).parent.parent / "comprehensive_samples" / "oxford_comprehensive.json"
    
    print("="*70)
    print("Oxford解析器性能分析")
    print("="*70)
    print()
    
    with open(samples_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    samples = data['samples']
    print(f"加载样例: {len(samples)}个")
    print()
    
    # 分析解析结果
    print("分析解析结果...")
    analysis_data = analyze_parsing_results(samples)
    
    print("="*70)
    print("解析统计")
    print("="*70)
    print(f"总样例: {analysis_data['total_samples']}")
    print(f"成功: {analysis_data['success_count']} ({analysis_data['success_rate']*100:.1f}%)")
    print(f"失败: {analysis_data['failed_count']}")
    print(f"平均释义数: {analysis_data['avg_senses']:.1f}")
    print(f"平均例句数: {analysis_data['avg_examples']:.1f}")
    print()
    
    print("="*70)
    print("问题统计")
    print("="*70)
    for issue_type, count in analysis_data['issues_summary'].items():
        percentage = count / analysis_data['total_samples'] * 100
        print(f"{issue_type}: {count} ({percentage:.1f}%)")
    print()
    
    # 保存结果
    output_dir = Path(__file__).parent.parent / "comprehensive_samples"
    
    # 保存JSON数据
    json_output = output_dir / "oxford_performance_analysis.json"
    with open(json_output, 'w', encoding='utf-8') as f:
        json.dump(analysis_data, f, ensure_ascii=False, indent=2)
    print(f"✅ 数据已保存: {json_output}")
    
    # 生成报告
    report_output = output_dir / "oxford_performance_report.md"
    generate_comparison_report(analysis_data, report_output)
    print(f"✅ 报告已保存: {report_output}")
    
    # 重点bad cases（可能漏解析）
    few_senses = sorted(
        analysis_data['bad_cases']['few_senses'],
        key=lambda x: x['content_length'],
        reverse=True
    )
    
    print()
    print("="*70)
    print("重点关注：可能漏解析的Bad Cases")
    print("="*70)
    print(f"共 {len(few_senses)} 个case（释义数 <= 1，但内容长度 > 500）")
    print()
    
    for i, case in enumerate(few_senses[:10], 1):
        print(f"[{i}] {case['word']}: 长度{case['content_length']}, 释义数{case['sense_count']}, 例句数{case['example_count']}")
    
    print()
    print("="*70)
    print("分析完成！")
    print("="*70)
    print(f"请查看报告: {report_output}")
    print(f"请查看数据: {json_output}")


if __name__ == '__main__':
    main()

