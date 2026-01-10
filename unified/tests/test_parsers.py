#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
解析器测试脚本
"""

import sys
import json
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from unified.parsers.langdao import LangdaoParser
from unified.models.entry import DictionaryEntry


def test_langdao():
    """测试朗道解析器"""
    print("=" * 60)
    print("测试朗道英汉词典解析器")
    print("=" * 60)
    
    # 测试样例
    test_cases = [
        ("good", """*[gud]
n. 善行, 好处, 利益
a. 好的, 优良的, 上等的, 愉快的, 有益的, 好心的, 慈善的, 虔诚的
【经】 货物; 好的
相关词组:
  for good
  for good or for evil
  good and
  good for"""),
        
        ("run", """*[rʌn]
n. 跑, 赛跑, 奔跑, 奔跑的路程, 趋向, 流出, 运转时间, 连续
vi. 跑, 奔跑, 跑步, 赛跑, 竞赛, 行驶, 运转, 进行, 蔓延
vt. 使跑, 参赛, 追究, 驾驶, 开动, 管理, 经营, 使流出, 运行
a. 熔化的, 融化的, 浇铸的
run的过去式和过去分词
【计】 运行
相关词组:
  run rampant
  in the long run"""),

        ("beautiful", """*['bju:tiful]
a. 美丽的"""),
        
        ("algorithm", """*['ælɡәriðәm]
n. 算法, 演算法则
【计】 算法"""),
    ]
    
    parser = LangdaoParser()
    
    for word, content in test_cases:
        print(f"\n{'='*40}")
        print(f"单词: {word}")
        print(f"{'='*40}")
        
        entry = parser.parse(word, content)
        
        if entry:
            print(f"音标: {[p.ipa for p in entry.pronunciations]}")
            print(f"释义数: {len(entry.senses)}")
            for i, sense in enumerate(entry.senses):
                print(f"  [{i+1}] {sense.pos or '-'}: {sense.definition[:50]}...")
                if sense.domain:
                    print(f"      领域: {sense.domain}")
            print(f"相关词组: {len(entry.related_phrases)}个")
            print(f"解析质量: {entry.parse_quality}")
        else:
            print("解析失败!")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


def load_real_samples():
    """从实际样例文件加载数据测试"""
    samples_file = Path(__file__).parent / "samples" / "langdao_samples.json"
    
    if not samples_file.exists():
        print(f"样例文件不存在: {samples_file}")
        return
    
    with open(samples_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("=" * 60)
    print(f"从实际样例测试: {data['dictionary_name']}")
    print(f"样例数: {data['sample_count']}")
    print("=" * 60)
    
    parser = LangdaoParser()
    
    success = 0
    failed = 0
    
    for sample in data['samples']:
        word = sample['word']
        content = sample['raw_content']
        
        entry = parser.parse(word, content)
        
        if entry and entry.senses:
            success += 1
            print(f"✓ {word}: {len(entry.senses)}个释义, 质量{entry.parse_quality}")
        else:
            failed += 1
            print(f"✗ {word}: 解析失败")
    
    print(f"\n结果: 成功{success}, 失败{failed}, 成功率{success/(success+failed)*100:.1f}%")


if __name__ == "__main__":
    test_langdao()
    print("\n")
    load_real_samples()

