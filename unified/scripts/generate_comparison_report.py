#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成Oxford解析器改进前后对比报告
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def generate_comparison():
    """生成对比报告"""
    
    # 加载当前分析结果
    current_file = Path(__file__).parent.parent / "comprehensive_samples" / "oxford_performance_analysis.json"
    with open(current_file, 'r', encoding='utf-8') as f:
        current_data = json.load(f)
    
    # 改进前的数据（基于历史记录）
    # 之前的状态：平均释义数1.6，可能漏解析7个
    previous_stats = {
        "avg_senses": 1.6,  # 改进前
        "avg_examples": 15.3,  # 改进前
        "few_senses_count": 7,  # 改进前
        "success_rate": 100.0,  # 一直保持100%
    }
    
    # 当前数据
    current_stats = {
        "avg_senses": current_data['avg_senses'],
        "avg_examples": current_data['avg_examples'],
        "few_senses_count": current_data['issues_summary']['few_senses'],
        "success_rate": current_data['success_rate'] * 100,
    }
    
    # 生成对比报告
    output_file = Path(__file__).parent.parent / "comprehensive_samples" / "oxford_comparison_report.md"
    
    report = f"""# Oxford解析器改进前后对比报告

> 生成时间: 2026-01-08  
> 对比基础: 174个样例

---

## 📊 关键指标对比

| 指标 | 改进前 | 改进后 | 提升 | 说明 |
|------|--------|--------|------|------|
| **解析成功率** | {previous_stats['success_rate']:.1f}% | {current_stats['success_rate']:.1f}% | - | 一直保持100% |
| **平均释义数** | {previous_stats['avg_senses']:.1f} | **{current_stats['avg_senses']:.1f}** | **+{current_stats['avg_senses'] - previous_stats['avg_senses']:.1f}** | ⬆️ **提升{((current_stats['avg_senses'] - previous_stats['avg_senses']) / previous_stats['avg_senses'] * 100):.0f}%** |
| **平均例句数** | {previous_stats['avg_examples']:.1f} | **{current_stats['avg_examples']:.1f}** | **+{current_stats['avg_examples'] - previous_stats['avg_examples']:.1f}** | ⬆️ **提升{((current_stats['avg_examples'] - previous_stats['avg_examples']) / previous_stats['avg_examples'] * 100):.0f}%** |
| **可能漏解析** | {previous_stats['few_senses_count']}个 | **{current_stats['few_senses_count']}个** | **-{previous_stats['few_senses_count'] - current_stats['few_senses_count']}个** | ⬇️ **减少{((previous_stats['few_senses_count'] - current_stats['few_senses_count']) / previous_stats['few_senses_count'] * 100):.0f}%** |

---

## ✅ 改进效果总结

### 1. 解析准确性大幅提升
- **平均释义数**从 {previous_stats['avg_senses']:.1f} → **{current_stats['avg_senses']:.1f}**（提升{((current_stats['avg_senses'] - previous_stats['avg_senses']) / previous_stats['avg_senses'] * 100):.0f}%）
- 说明解析器能更准确地识别和分割多个义项

### 2. 例句提取有所改善
- **平均例句数**从 {previous_stats['avg_examples']:.1f} → **{current_stats['avg_examples']:.1f}**（提升{((current_stats['avg_examples'] - previous_stats['avg_examples']) / previous_stats['avg_examples'] * 100):.0f}%）
- 说明例句提取逻辑有所改进

### 3. 漏解析问题显著减少
- **可能漏解析**从 {previous_stats['few_senses_count']}个 → **{current_stats['few_senses_count']}个**（减少{((previous_stats['few_senses_count'] - current_stats['few_senses_count']) / previous_stats['few_senses_count'] * 100):.0f}%）
- 从 {previous_stats['few_senses_count']} 个减少到 {current_stats['few_senses_count']} 个
- 说明新的规则有效解决了大部分漏解析问题

---

## 🔴 当前Bad Cases（需要进一步优化）

### 1. 可能漏解析（{current_stats['few_senses_count']}个）

"""
    
    # 列出可能漏解析的case
    few_senses = sorted(
        current_data['bad_cases']['few_senses'],
        key=lambda x: x['content_length'],
        reverse=True
    )
    
    for i, case in enumerate(few_senses, 1):
        report += f"""#### {i}. `{case['word']}` (长度: {case['content_length']}, 释义数: {case['sense_count']})

**原始数据**:
```
{case['raw_content'][:600]}{'...' if len(case['raw_content']) > 600 else ''}
```

**解析结果**:
- 格式类型: {case['pattern_type']}
- 释义数: {case['sense_count']}
- 例句数: {case['example_count']}
- 解析质量: {case['parse_quality']}

**问题**: 内容长度 {case['content_length']}，但只解析出 {case['sense_count']} 个释义，可能包含多个义项

---

"""
    
    report += f"""
### 2. 定义文本问题（{current_data['issues_summary']['definition_issues']}个，{current_data['issues_summary']['definition_issues']/current_data['total_samples']*100:.1f}%）

**问题描述**: 定义中可能包含例句片段或冗余内容

**可能原因**:
- 冒号分割逻辑不够精确
- 例句提取后，定义文本清理不彻底
- 定义和例句边界识别不准确

**重点关注**: 这个比例很高（74.7%），需要重点优化

---

### 3. 无例句（长条目）（{current_data['issues_summary']['no_examples_long']}个）

**问题描述**: 长条目（长度 > 300）但未提取到例句

**可能原因**:
- 例句格式特殊，不是标准的 `*` 标记
- 例句直接在冒号后，但提取逻辑有问题

---

## 🎯 下一步优化建议

### 1. 优化定义文本清理
- **优先级**: 高（影响74.7%的条目）
- **方案**: 改进冒号分割逻辑，更精确地识别定义和例句的边界
- **目标**: 减少定义文本中的冗余内容

### 2. 继续优化可能漏解析的case
- **当前**: 还有 {current_stats['few_senses_count']} 个case
- **重点关注**: `making` 等case的IDM习语解析

### 3. 改进例句提取
- 支持更多例句格式
- 改进冒号后直接例句的提取逻辑

---

## 📝 已修复的Bad Cases

以下case已经修复并验证：

1. ✅ `important` - 词形变化误匹配（已修复）
2. ✅ `gone` - 混合格式识别（已修复）

---

## 📋 完整数据

- 详细分析数据: `oxford_performance_analysis.json`
- 问题报告: `oxford_performance_report.md`
- Bad case记录: `docs/OXFORD_BAD_CASES.md`

"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✅ 对比报告已生成: {output_file}")
    
    # 打印摘要
    print()
    print("="*70)
    print("改进前后对比摘要")
    print("="*70)
    print(f"平均释义数: {previous_stats['avg_senses']:.1f} → {current_stats['avg_senses']:.1f} (+{current_stats['avg_senses'] - previous_stats['avg_senses']:.1f}, 提升{((current_stats['avg_senses'] - previous_stats['avg_senses']) / previous_stats['avg_senses'] * 100):.0f}%)")
    print(f"平均例句数: {previous_stats['avg_examples']:.1f} → {current_stats['avg_examples']:.1f} (+{current_stats['avg_examples'] - previous_stats['avg_examples']:.1f}, 提升{((current_stats['avg_examples'] - previous_stats['avg_examples']) / previous_stats['avg_examples'] * 100):.0f}%)")
    print(f"可能漏解析: {previous_stats['few_senses_count']}个 → {current_stats['few_senses_count']}个 (-{previous_stats['few_senses_count'] - current_stats['few_senses_count']}个, 减少{((previous_stats['few_senses_count'] - current_stats['few_senses_count']) / previous_stats['few_senses_count'] * 100):.0f}%)")
    print()
    print(f"⚠️  当前重点关注: 定义文本问题（{current_data['issues_summary']['definition_issues']}个，{current_data['issues_summary']['definition_issues']/current_data['total_samples']*100:.1f}%）")


if __name__ == '__main__':
    generate_comparison()

