#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Langdao解析器Review工具

对比显示原始数据和解析结果，便于人工review。
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from unified.parsers.langdao import LangdaoParser
from unified.models.entry import DictionaryEntry

SAMPLES_PATH = Path(__file__).parent / "comprehensive_samples"
OUTPUT_PATH = Path(__file__).parent / "comprehensive_samples"


def parse_and_compare():
    """解析所有样例并生成对比报告"""
    
    # 加载样例
    samples_file = SAMPLES_PATH / "langdao_comprehensive.json"
    with open(samples_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    samples = data['samples']
    parser = LangdaoParser()
    
    results = []
    success = 0
    failed = 0
    issues = []
    
    for sample in samples:
        word = sample['word']
        raw_content = sample['raw_content']
        
        # 解析
        entry = parser.parse(word, raw_content)
        
        if entry:
            success += 1
            parsed_data = entry.to_dict()
            
            # 检查潜在问题
            issue_list = []
            if not entry.pronunciations:
                issue_list.append("无音标")
            if not entry.senses:
                issue_list.append("无释义")
            if len(entry.senses) == 1 and len(raw_content.split('\n')) > 3:
                issue_list.append("可能漏解析释义")
            
            results.append({
                "word": word,
                "raw_content": raw_content,
                "parsed": parsed_data,
                "parse_quality": entry.parse_quality,
                "issues": issue_list,
                "status": "success"
            })
            
            if issue_list:
                issues.append({
                    "word": word,
                    "issues": issue_list,
                    "raw_content": raw_content[:200]
                })
        else:
            failed += 1
            results.append({
                "word": word,
                "raw_content": raw_content,
                "parsed": None,
                "parse_quality": 0,
                "issues": ["解析失败"],
                "status": "failed"
            })
            issues.append({
                "word": word,
                "issues": ["解析失败"],
                "raw_content": raw_content[:200]
            })
    
    print(f"解析完成: 成功 {success}, 失败 {failed}")
    print(f"有问题的条目: {len(issues)}")
    
    # 保存解析结果
    output_file = OUTPUT_PATH / "langdao_parse_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "total": len(samples),
            "success": success,
            "failed": failed,
            "issues_count": len(issues),
            "results": results
        }, f, ensure_ascii=False, indent=2)
    print(f"✅ 解析结果已保存: {output_file}")
    
    # 生成对比报告
    generate_comparison_report(results, issues, OUTPUT_PATH / "langdao_parse_comparison.md")
    print(f"✅ 对比报告已生成: {OUTPUT_PATH / 'langdao_parse_comparison.md'}")
    
    return results, issues


def generate_comparison_report(results, issues, output_path):
    """生成原始数据与解析结果对比报告"""
    
    report = f"""# Langdao解析器 - 原始数据与解析结果对比

> 生成时间: 2026-01-08  
> 总样例数: {len(results)}  
> 解析成功: {sum(1 for r in results if r['status'] == 'success')}  
> 有问题: {len(issues)}

---

## 📊 解析统计

| 指标 | 数值 |
|------|------|
| 总样例 | {len(results)} |
| 成功 | {sum(1 for r in results if r['status'] == 'success')} |
| 失败 | {sum(1 for r in results if r['status'] == 'failed')} |
| 有问题 | {len(issues)} |
| 成功率 | {sum(1 for r in results if r['status'] == 'success')/len(results)*100:.1f}% |

---

## ⚠️ 需要关注的问题

"""
    
    if issues:
        for issue in issues[:20]:
            report += f"### `{issue['word']}`\n"
            report += f"- 问题: {', '.join(issue['issues'])}\n"
            report += f"- 原始内容片段: `{issue['raw_content']}`\n\n"
    else:
        report += "无明显问题\n\n"
    
    report += """
---

## 🔍 详细对比（按字母顺序）

以下展示每个词条的原始数据和解析结果对比:

"""
    
    # 按字母顺序排列
    sorted_results = sorted(results, key=lambda x: x['word'].lower())
    
    for r in sorted_results:
        word = r['word']
        raw = r['raw_content']
        parsed = r['parsed']
        quality = r.get('parse_quality', 0)
        issues_str = ', '.join(r.get('issues', [])) if r.get('issues') else '无'
        
        # 截断过长内容
        raw_display = raw
        if len(raw) > 1200:
            raw_display = raw[:1200] + "\n... [截断]"
        
        report += f"### `{word}`\n\n"
        report += f"**解析质量**: {quality} | **问题**: {issues_str}\n\n"
        
        report += "#### 原始数据\n\n"
        report += f"```\n{raw_display}\n```\n\n"
        
        report += "#### 解析结果\n\n"
        
        if parsed:
            # 音标
            if parsed.get('pronunciations'):
                phonetics = [p.get('ipa', '') for p in parsed['pronunciations']]
                report += f"**音标**: {phonetics}\n\n"
            else:
                report += "**音标**: 无\n\n"
            
            # 释义
            report += f"**释义** ({len(parsed.get('senses', []))}个):\n\n"
            for i, sense in enumerate(parsed.get('senses', [])):
                pos = sense.get('pos', '-')
                definition = sense.get('definition', '')
                domain = sense.get('domain', '')
                
                report += f"{i+1}. **[{pos}]** {definition}"
                if domain:
                    report += f" _(领域: {domain})_"
                report += "\n"
            
            # 相关词组
            phrases = parsed.get('related_phrases', [])
            if phrases:
                report += f"\n**相关词组** ({len(phrases)}个): "
                report += ', '.join([p.get('phrase', '') for p in phrases[:10]])
                if len(phrases) > 10:
                    report += f" ... 等{len(phrases)}个"
                report += "\n"
        else:
            report += "解析失败\n"
        
        report += "\n---\n\n"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)


def show_sample_comparisons(count=10):
    """在终端展示几个样例对比"""
    
    samples_file = SAMPLES_PATH / "langdao_comprehensive.json"
    with open(samples_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    samples = data['samples'][:count]
    parser = LangdaoParser()
    
    print("=" * 70)
    print("Langdao解析器 - 样例对比展示")
    print("=" * 70)
    
    for sample in samples:
        word = sample['word']
        raw = sample['raw_content']
        
        entry = parser.parse(word, raw)
        
        print(f"\n{'='*60}")
        print(f"【{word}】")
        print(f"{'='*60}")
        
        print("\n📄 原始数据:")
        print("-" * 40)
        if len(raw) > 500:
            print(raw[:500] + "\n... [截断]")
        else:
            print(raw)
        
        print("\n📊 解析结果:")
        print("-" * 40)
        
        if entry:
            if entry.pronunciations:
                print(f"音标: {[p.ipa for p in entry.pronunciations]}")
            
            print(f"释义数: {len(entry.senses)}")
            for i, sense in enumerate(entry.senses[:5]):
                pos = sense.pos or '-'
                domain = f" [{sense.domain}]" if sense.domain else ""
                print(f"  {i+1}. [{pos}]{domain} {sense.definition[:60]}...")
            
            if len(entry.senses) > 5:
                print(f"  ... 等{len(entry.senses)}个释义")
            
            if entry.related_phrases:
                print(f"相关词组: {len(entry.related_phrases)}个")
        else:
            print("解析失败!")


if __name__ == '__main__':
    # 先展示几个样例
    show_sample_comparisons(5)
    
    print("\n" + "=" * 70)
    print("开始全量解析并生成报告...")
    print("=" * 70)
    
    # 全量解析
    parse_and_compare()

