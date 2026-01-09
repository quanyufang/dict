#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Oxford解析器测试工具
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from unified.parsers.oxford import OxfordParser


def test_with_samples():
    """使用实际样例测试"""
    samples_file = Path(__file__).parent / "comprehensive_samples" / "oxford_comprehensive.json"
    
    if not samples_file.exists():
        print(f"样例文件不存在: {samples_file}")
        return
    
    with open(samples_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    parser = OxfordParser()
    
    # 测试几个典型样例
    test_words = ['good', 'run', 'set', 'take', 'book', 'time']
    
    print("=" * 70)
    print("Oxford解析器测试")
    print("=" * 70)
    
    for word in test_words:
        sample = next((s for s in data['samples'] if s['word'] == word), None)
        if not sample:
            print(f"\n⚠️  未找到样例: {word}")
            continue
        
        print(f"\n{'='*60}")
        print(f"【{word}】")
        print(f"{'='*60}")
        
        raw_content = sample['raw_content']
        
        # 显示原始数据片段
        print("\n📄 原始数据 (前500字符):")
        print("-" * 40)
        print(raw_content[:500] + ("..." if len(raw_content) > 500 else ""))
        
        # 解析
        entry = parser.parse(word, raw_content)
        
        print("\n📊 解析结果:")
        print("-" * 40)
        
        if entry:
            # 音标
            if entry.pronunciations:
                phonetics = [f"{p.region}: {p.ipa}" for p in entry.pronunciations]
                print(f"音标: {phonetics}")
            else:
                print("音标: 无")
            
            # 释义
            print(f"\n释义数: {len(entry.senses)}")
            for i, sense in enumerate(entry.senses[:8]):  # 最多显示8个
                pos = sense.pos or '-'
                num = sense.sense_number or '-'
                grammar = f" [{sense.grammar_note}]" if sense.grammar_note else ""
                
                print(f"\n  [{i+1}] {pos} #{num}{grammar}")
                def_text = sense.definition
                if len(def_text) > 150:
                    def_text = def_text[:150] + "..."
                print(f"      定义: {def_text}")
                
                if sense.examples:
                    print(f"      例句: {len(sense.examples)}个")
                    for j, ex in enumerate(sense.examples[:2]):  # 显示前2个例句
                        ex_text = ex.text[:80] + "..." if len(ex.text) > 80 else ex.text
                        print(f"        - {ex_text}")
                        if ex.translation:
                            print(f"          → {ex.translation[:60]}")
            
            if len(entry.senses) > 8:
                print(f"\n  ... 等{len(entry.senses)}个释义")
            
            # 相关短语
            if entry.related_phrases:
                print(f"\n相关短语: {len(entry.related_phrases)}个")
            
            print(f"\n解析质量: {entry.parse_quality}")
            if entry.parse_notes:
                print(f"解析备注: {entry.parse_notes}")
        else:
            print("❌ 解析失败!")
    
    # 统计
    print("\n" + "=" * 70)
    print("全量测试统计")
    print("=" * 70)
    
    success = 0
    failed = 0
    total_senses = 0
    total_examples = 0
    
    for sample in data['samples']:
        entry = parser.parse(sample['word'], sample['raw_content'])
        if entry and entry.senses:
            success += 1
            total_senses += len(entry.senses)
            total_examples += sum(len(s.examples) for s in entry.senses)
        else:
            failed += 1
    
    print(f"总样例: {len(data['samples'])}")
    print(f"成功: {success} ({success/len(data['samples'])*100:.1f}%)")
    print(f"失败: {failed}")
    print(f"平均释义数: {total_senses/success:.1f}" if success > 0 else "")
    print(f"平均例句数: {total_examples/success:.1f}" if success > 0 else "")


if __name__ == '__main__':
    test_with_samples()

