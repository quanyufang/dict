#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成Oxford解析器完整报告（覆盖之前文件）
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from unified.parsers.oxford import OxfordParser


def generate_full_report():
    """生成完整报告"""
    
    # 加载样例数据
    samples_file = Path(__file__).parent.parent / "comprehensive_samples" / "oxford_comprehensive.json"
    with open(samples_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    parser = OxfordParser()
    
    # 解析所有样例
    results = []
    success = 0
    failed = 0
    total_senses = 0
    total_examples = 0
    
    for sample in data['samples']:
        word = sample['word']
        raw_content = sample['raw_content']
        
        entry = parser.parse(word, raw_content)
        
        result = {
            "word": word,
            "raw_content": raw_content,
            "content_length": len(raw_content),
            "parsed": entry is not None,
            "parse_quality": entry.parse_quality if entry else 0,
            "pronunciation_count": len(entry.pronunciations) if entry else 0,
            "sense_count": len(entry.senses) if entry else 0,
            "example_count": sum(len(s.examples) for s in entry.senses) if entry else 0,
            "parse_notes": entry.parse_notes if entry else [],
            "pattern_type": entry.parse_notes[0].split(': ')[-1] if entry and entry.parse_notes else "unknown",
        }
        
        results.append(result)
        
        if entry and entry.senses:
            success += 1
            total_senses += len(entry.senses)
            total_examples += result['example_count']
        else:
            failed += 1
    
    # 分类问题
    issues = {
        "no_pronunciation": [],
        "no_senses": [],
        "low_quality": [],
        "few_senses": [],
        "no_examples": [],
        "very_short": [],
        "very_long": [],
    }
    
    for r in results:
        if not r['parsed'] or not r['sense_count']:
            issues['no_senses'].append(r)
        elif not r['pronunciation_count']:
            issues['no_pronunciation'].append(r)
        elif r['parse_quality'] < 0.8:
            issues['low_quality'].append(r)
        elif r['sense_count'] <= 1 and r['content_length'] > 500:
            issues['few_senses'].append(r)
        elif r['content_length'] > 300 and r['example_count'] == 0:
            issues['no_examples'].append(r)
        
        if r['content_length'] < 50:
            issues['very_short'].append(r)
        elif r['content_length'] > 8000:
            issues['very_long'].append(r)
    
    # 生成报告
    output_dir = Path(__file__).parent.parent / "comprehensive_samples"
    
    # 1. 更新问题数据JSON
    issues_data = {
        "total_samples": len(results),
        "issues_summary": {
            k: len(v) for k, v in issues.items()
        },
        "all_issues": {
            k: [r for r in v] for k, v in issues.items()
        },
        "statistics": {
            "success": success,
            "failed": failed,
            "total_senses": total_senses,
            "total_examples": total_examples,
            "avg_senses": total_senses / success if success > 0 else 0,
            "avg_examples": total_examples / success if success > 0 else 0,
        }
    }
    
    with open(output_dir / "oxford_issues_data.json", 'w', encoding='utf-8') as f:
        json.dump(issues_data, f, ensure_ascii=False, indent=2)
    
    # 2. 生成问题报告（覆盖原文件）
    report_content = f"""# Oxford解析器问题案例汇总（已更新）

> 生成时间: 2026-01-08（已改进）  
> 总样例数: {len(results)}  
> 解析成功率: {success}/{len(results)} ({success/len(results)*100:.1f}%)

---

## 📊 解析统计

| 指标 | 数值 |
|------|------|
| 总样例 | {len(results)} |
| 解析成功 | {success} ({success/len(results)*100:.1f}%) |
| 解析失败 | {failed} |
| 平均释义数 | {issues_data['statistics']['avg_senses']:.1f} |
| 平均例句数 | {issues_data['statistics']['avg_examples']:.1f} |

---

## 📊 问题分类统计

| 问题类型 | 数量 | 占比 |
|---------|------|------|
| 无音标 | {len(issues['no_pronunciation'])} | {len(issues['no_pronunciation'])/len(results)*100:.1f}% |
| 无释义 | {len(issues['no_senses'])} | {len(issues['no_senses'])/len(results)*100:.1f}% |
| 质量分 < 0.8 | {len(issues['low_quality'])} | {len(issues['low_quality'])/len(results)*100:.1f}% |
| 释义数 <= 1（可能漏解析） | {len(issues['few_senses'])} | {len(issues['few_senses'])/len(results)*100:.1f}% |
| 无例句（长条目） | {len(issues['no_examples'])} | {len(issues['no_examples'])/len(results)*100:.1f}% |
| 超短条目 (<50字符) | {len(issues['very_short'])} | {len(issues['very_short'])/len(results)*100:.1f}% |
| 超长条目 (>8000字符) | {len(issues['very_long'])} | {len(issues['very_long'])/len(results)*100:.1f}% |

---

## 1️⃣ 无音标案例 ({len(issues['no_pronunciation'])}个)

"""
    
    for case in issues['no_pronunciation'][:20]:
        report_content += f"### `{case['word']}` (长度: {case['content_length']})\n\n"
        report_content += f"**原始数据**:\n```\n{case['raw_content'][:500]}{'...' if len(case['raw_content']) > 500 else ''}\n```\n\n"
        report_content += f"**解析结果**: 质量分 {case['parse_quality']}, 释义数 {case['sense_count']}, 格式类型: {case.get('pattern_type', 'unknown')}\n\n"
        if case['parse_notes']:
            report_content += f"**备注**: {', '.join(case['parse_notes'])}\n\n"
        report_content += "---\n\n"
    
    report_content += f"""
## 2️⃣ 可能漏解析的案例 ({len(issues['few_senses'])}个)

"""
    
    for case in sorted(issues['few_senses'], key=lambda x: x['content_length'], reverse=True)[:15]:
        report_content += f"### `{case['word']}` (长度: {case['content_length']}, 释义数: {case['sense_count']})\n\n"
        report_content += f"**原始数据**:\n```\n{case['raw_content'][:800]}{'...' if len(case['raw_content']) > 800 else ''}\n```\n\n"
        report_content += f"**解析结果**: 格式类型: {case.get('pattern_type', 'unknown')}, 例句数: {case['example_count']}\n\n"
        report_content += "---\n\n"
    
    report_content += f"""
## 3️⃣ 格式类型分布

"""
    
    # 统计格式类型
    pattern_counts = {}
    for r in results:
        pattern = r.get('pattern_type', 'unknown')
        pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
    
    report_content += "| 格式类型 | 数量 | 占比 |\n"
    report_content += "|---------|------|------|\n"
    for pattern, count in sorted(pattern_counts.items(), key=lambda x: -x[1]):
        report_content += f"| {pattern} | {count} | {count/len(results)*100:.1f}% |\n"
    
    report_content += "\n---\n\n"
    
    report_content += """
## 4️⃣ 需要review的特殊case

### give up (测试用例)
- 格式类型: phrase_heading
- 预期: 多个sense，包括短语标题+子sense
- 实际: 已识别格式类型，但需要验证sense分割是否正确

### come up (测试用例)
- 格式类型: direct_letter_numbered
- 预期: 字母序号系列 (a)-(g) + 变体短语
- 实际: 已识别格式类型，但需要验证变体短语分割是否正确

---
"""
    
    with open(output_dir / "oxford_issues_report.md", 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"✅ 报告已更新: {output_dir / 'oxford_issues_report.md'}")
    print(f"✅ 数据已更新: {output_dir / 'oxford_issues_data.json'}")
    print()
    print(f"统计: 成功{success}, 失败{failed}, 平均释义{issues_data['statistics']['avg_senses']:.1f}, 平均例句{issues_data['statistics']['avg_examples']:.1f}")


if __name__ == '__main__':
    generate_full_report()

