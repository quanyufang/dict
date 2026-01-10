#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析Oxford解析器的问题案例

汇总解析质量低、失败或异常的case供review。
"""

import sys
import json
from pathlib import Path
from typing import List, Dict

sys.path.insert(0, str(Path(__file__).parent.parent))

from unified.parsers.oxford import OxfordParser


def analyze_all_samples():
    """分析所有样例，找出问题case"""
    
    samples_file = Path(__file__).parent.parent / "comprehensive_samples" / "oxford_comprehensive.json"
    
    if not samples_file.exists():
        print(f"样例文件不存在: {samples_file}")
        return
    
    with open(samples_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    parser = OxfordParser()
    
    issues = {
        "no_pronunciation": [],      # 无音标
        "no_senses": [],              # 无释义
        "low_quality": [],            # 质量分 < 0.8
        "few_senses": [],             # 释义数 <= 1（可能漏解析）
        "no_examples": [],            # 无例句（长条目应该有意义）
        "unusual_format": [],         # 格式异常
        "very_long": [],              # 超长条目
        "very_short": [],             # 超短条目
    }
    
    all_results = []
    
    print("=" * 70)
    print("Oxford解析器问题分析")
    print("=" * 70)
    
    for sample in data['samples']:
        word = sample['word']
        raw_content = sample['raw_content']
        content_length = len(raw_content)
        
        entry = parser.parse(word, raw_content)
        
        result = {
            "word": word,
            "raw_content": raw_content,
            "content_length": content_length,
            "parsed": entry is not None,
            "parse_quality": entry.parse_quality if entry else 0,
            "pronunciation_count": len(entry.pronunciations) if entry else 0,
            "sense_count": len(entry.senses) if entry else 0,
            "example_count": sum(len(s.examples) for s in entry.senses) if entry else 0,
            "parse_notes": entry.parse_notes if entry else [],
            "entry": entry.to_dict() if entry else None,
        }
        
        all_results.append(result)
        
        # 分类问题
        if not entry:
            issues["no_senses"].append(result)
        elif not entry.pronunciations:
            issues["no_pronunciation"].append(result)
        elif not entry.senses:
            issues["no_senses"].append(result)
        elif entry.parse_quality < 0.8:
            issues["low_quality"].append(result)
        elif len(entry.senses) <= 1 and content_length > 500:
            # 长条目但只有1个释义，可能漏解析
            issues["few_senses"].append(result)
        
        # 检查例句
        if entry and len(entry.senses) > 0:
            total_examples = sum(len(s.examples) for s in entry.senses)
            if total_examples == 0 and content_length > 300:
                # 长条目但无例句
                issues["no_examples"].append(result)
        
        # 长度异常
        if content_length < 50:
            issues["very_short"].append(result)
        elif content_length > 8000:
            issues["very_long"].append(result)
        
        # 检查格式异常
        if entry and entry.parse_notes:
            if any("异常" in note or "格式" in note for note in entry.parse_notes):
                issues["unusual_format"].append(result)
    
    return issues, all_results


def generate_issues_report(issues: Dict, all_results: List[Dict], output_path: Path):
    """生成问题报告"""
    
    report = f"""# Oxford解析器问题案例汇总

> 生成时间: 2026-01-08  
> 总样例数: {len(all_results)}

---

## 📊 问题分类统计

| 问题类型 | 数量 | 占比 |
|---------|------|------|
| 无音标 | {len(issues['no_pronunciation'])} | {len(issues['no_pronunciation'])/len(all_results)*100:.1f}% |
| 无释义 | {len(issues['no_senses'])} | {len(issues['no_senses'])/len(all_results)*100:.1f}% |
| 质量分 < 0.8 | {len(issues['low_quality'])} | {len(issues['low_quality'])/len(all_results)*100:.1f}% |
| 释义数 <= 1（可能漏解析） | {len(issues['few_senses'])} | {len(issues['few_senses'])/len(all_results)*100:.1f}% |
| 无例句（长条目） | {len(issues['no_examples'])} | {len(issues['no_examples'])/len(all_results)*100:.1f}% |
| 超短条目 (<50字符) | {len(issues['very_short'])} | {len(issues['very_short'])/len(all_results)*100:.1f}% |
| 超长条目 (>8000字符) | {len(issues['very_long'])} | {len(issues['very_long'])/len(all_results)*100:.1f}% |

---

## 1️⃣ 无音标案例

"""
    
    for case in issues['no_pronunciation'][:20]:  # 限制数量
        report += f"### `{case['word']}` (长度: {case['content_length']})\n\n"
        report += f"**原始数据**:\n```\n{case['raw_content'][:500]}{'...' if len(case['raw_content']) > 500 else ''}\n```\n\n"
        report += f"**解析结果**: 质量分 {case['parse_quality']}, 释义数 {case['sense_count']}\n\n"
        if case['parse_notes']:
            report += f"**备注**: {', '.join(case['parse_notes'])}\n\n"
        report += "---\n\n"
    
    report += """
## 2️⃣ 无释义案例

"""
    
    for case in issues['no_senses'][:20]:
        report += f"### `{case['word']}` (长度: {case['content_length']})\n\n"
        report += f"**原始数据**:\n```\n{case['raw_content']}\n```\n\n"
        report += "---\n\n"
    
    report += """
## 3️⃣ 质量分 < 0.8 案例

"""
    
    for case in sorted(issues['low_quality'], key=lambda x: x['parse_quality'])[:20]:
        report += f"### `{case['word']}` (质量分: {case['parse_quality']}, 长度: {case['content_length']})\n\n"
        report += f"**原始数据**:\n```\n{case['raw_content'][:600]}{'...' if len(case['raw_content']) > 600 else ''}\n```\n\n"
        report += f"**解析结果**: 音标 {case['pronunciation_count']}, 释义 {case['sense_count']}, 例句 {case['example_count']}\n\n"
        if case['parse_notes']:
            report += f"**备注**: {', '.join(case['parse_notes'])}\n\n"
        report += "---\n\n"
    
    report += """
## 4️⃣ 可能漏解析的案例（长条目但只有1个释义）

"""
    
    for case in sorted(issues['few_senses'], key=lambda x: x['content_length'], reverse=True)[:20]:
        report += f"### `{case['word']}` (长度: {case['content_length']}, 释义数: {case['sense_count']})\n\n"
        report += f"**原始数据**:\n```\n{case['raw_content'][:800]}{'...' if len(case['raw_content']) > 800 else ''}\n```\n\n"
        report += f"**解析结果**:\n"
        if case['entry']:
            for i, sense in enumerate(case['entry'].get('senses', [])[:3]):
                report += f"- [{i+1}] {sense.get('pos', '-')} #{sense.get('sense_number', '-')}: {sense.get('definition', '')[:100]}...\n"
        report += "\n---\n\n"
    
    report += """
## 5️⃣ 无例句的长条目

"""
    
    for case in sorted(issues['no_examples'], key=lambda x: x['content_length'], reverse=True)[:15]:
        report += f"### `{case['word']}` (长度: {case['content_length']}, 释义数: {case['sense_count']})\n\n"
        report += f"**原始数据片段**:\n```\n{case['raw_content'][:600]}{'...' if len(case['raw_content']) > 600 else ''}\n```\n\n"
        report += "---\n\n"
    
    report += """
## 6️⃣ 超短条目 (<50字符)

"""
    
    for case in issues['very_short'][:15]:
        report += f"### `{case['word']}` (长度: {case['content_length']})\n\n"
        report += f"**原始数据**:\n```\n{case['raw_content']}\n```\n\n"
        report += f"**解析结果**: 音标 {case['pronunciation_count']}, 释义 {case['sense_count']}\n\n"
        report += "---\n\n"
    
    report += """
## 7️⃣ 超长条目 (>8000字符)

"""
    
    for case in issues['very_long']:
        report += f"### `{case['word']}` (长度: {case['content_length']})\n\n"
        report += f"**原始数据 (前1000字符)**:\n```\n{case['raw_content'][:1000]}...\n```\n\n"
        report += f"**解析结果**: 释义 {case['sense_count']}, 例句 {case['example_count']}, 质量分 {case['parse_quality']}\n\n"
        report += "---\n\n"
    
    # 添加完整数据JSON
    report += """
---

## 📋 完整问题数据 (JSON)

所有问题case的完整数据已保存在: `oxford_issues_data.json`

"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✅ 问题报告已生成: {output_path}")


def main():
    """主函数"""
    output_dir = Path(__file__).parent.parent / "comprehensive_samples"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    issues, all_results = analyze_all_samples()
    
    # 生成报告
    report_path = output_dir / "oxford_issues_report.md"
    generate_issues_report(issues, all_results, report_path)
    
    # 保存完整JSON数据
    issues_data = {
        "total_samples": len(all_results),
        "issues_summary": {
            "no_pronunciation": len(issues['no_pronunciation']),
            "no_senses": len(issues['no_senses']),
            "low_quality": len(issues['low_quality']),
            "few_senses": len(issues['few_senses']),
            "no_examples": len(issues['no_examples']),
            "very_short": len(issues['very_short']),
            "very_long": len(issues['very_long']),
        },
        "all_issues": {
            k: [r for r in v] for k, v in issues.items()
        }
    }
    
    json_path = output_dir / "oxford_issues_data.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(issues_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 完整数据已保存: {json_path}")
    
    # 打印统计
    print("\n" + "=" * 70)
    print("问题统计")
    print("=" * 70)
    print(f"总样例: {len(all_results)}")
    print(f"无音标: {len(issues['no_pronunciation'])}")
    print(f"无释义: {len(issues['no_senses'])}")
    print(f"质量分 < 0.8: {len(issues['low_quality'])}")
    print(f"可能漏解析: {len(issues['few_senses'])}")
    print(f"无例句(长条目): {len(issues['no_examples'])}")
    print(f"超短条目: {len(issues['very_short'])}")
    print(f"超长条目: {len(issues['very_long'])}")


if __name__ == '__main__':
    main()

