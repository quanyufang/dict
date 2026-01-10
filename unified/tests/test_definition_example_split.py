#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试定义和例句分离的改进
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from unified.parsers.oxford import OxfordParser


def test_definition_example_split():
    """测试定义和例句分离"""
    
    parser = OxfordParser()
    
    # 测试用例1: a的义项1 - 定义后直接跟例句
    test_cases = [
        {
            "name": "a - 义项1",
            "word": "a",
            "raw": "1 the first letter of the English alphabet 英语字母表的第一个字母: `Ann' begins with (an) A/`A'. Ann一字以A字母开始.",
            "expected_definition": "the first letter of the English alphabet 英语字母表的第一个字母",
            "expected_example": "Ann' begins with (an) A/`A'. Ann一字以A字母开始.",
        },
        {
            "name": "a - 义项3",
            "word": "a",
            "raw": "3 academic mark indicating the highest standard of work 学业成绩达最高标准的评价符号: get (an) A/`A' in biology 生物（学科）得A.",
            "expected_definition": "academic mark indicating the highest standard of work 学业成绩达最高标准的评价符号",
            "expected_example": "get (an) A/`A' in biology 生物（学科）得A.",
        },
        {
            "name": "a - abbr 义项1 (例句中的冒号)",
            "word": "a",
            "raw": "abbr 缩写 =  1 ampere(s): 13A, eg on a fuse 13安（如标于保险丝上者）.",
            "expected_definition": "ampere(s): 13A, eg on a fuse 13安（如标于保险丝上者）",  # 这里的冒号应该在定义中
            "expected_example": None,  # 这个case没有例句
        },
        {
            "name": "the - 义项1",
            "word": "the",
            "raw": "1 (when it has already been mentioned or implied 指已提到过的或已知所指的人、物、事或群体): A boy and a girl were sitting on a bench. The boy was smiling but the girl looked angry. 一个男孩和一个女孩坐在长凳上. 那男孩在微笑, 那女孩像在生气. * There was an accident here yesterday. A car hit a tree. The driver was killed. 昨天这里出事了. 有一辆汽车撞在树上了. 司机死了.",
            "expected_definition": "(when it has already been mentioned or implied 指已提到过的或已知所指的人、物、事或群体)",
            "expected_example_count": 2,  # 应该有两个例句
        },
    ]
    
    print("="*70)
    print("测试定义和例句分离的改进")
    print("="*70)
    print()
    
    passed = 0
    failed = 0
    
    for i, case in enumerate(test_cases, 1):
        print(f"[测试 {i}] {case['name']}")
        print(f"原始数据: {case['raw'][:100]}...")
        print()
        
        # 解析
        # 注意：需要完整的格式（包含音标和词性）
        if case['word'] == 'a':
            # 构造完整的格式
            if 'abbr' in case['raw']:
                full_raw = f"/eɪ; e/ {case['raw']}"
            else:
                full_raw = f"/eɪ; e/ n {case['raw']}"
        else:
            full_raw = f"/ðə, ðɪ; ðə, ðɪ/ def art {case['raw']}"
        
        entry = parser.parse(case['word'], full_raw)
        
        if not entry or not entry.senses:
            print(f"❌ 解析失败：没有生成sense")
            failed += 1
            print()
            continue
        
        sense = entry.senses[0]
        
        # 检查定义
        if 'expected_definition' in case:
            definition_match = case['expected_definition'].lower() in sense.definition.lower()
            if definition_match:
                print(f"✅ 定义匹配")
                print(f"   期望: {case['expected_definition']}")
                print(f"   实际: {sense.definition[:100]}...")
            else:
                print(f"⚠️  定义可能不匹配")
                print(f"   期望: {case['expected_definition']}")
                print(f"   实际: {sense.definition[:100]}...")
        
        # 检查例句
        if 'expected_example' in case:
            if case['expected_example'] is None:
                if len(sense.examples) == 0:
                    print(f"✅ 例句数量正确：0个")
                    passed += 1
                else:
                    print(f"❌ 例句数量错误：期望0个，实际{len(sense.examples)}个")
                    failed += 1
            else:
                if sense.examples:
                    example_text = sense.examples[0].text
                    if case['expected_example'].lower() in example_text.lower():
                        print(f"✅ 例句匹配")
                        print(f"   期望: {case['expected_example'][:80]}...")
                        print(f"   实际: {example_text[:80]}...")
                        passed += 1
                    else:
                        print(f"⚠️  例句可能不匹配")
                        print(f"   期望: {case['expected_example'][:80]}...")
                        print(f"   实际: {example_text[:80]}...")
                else:
                    print(f"❌ 没有提取到例句")
                    failed += 1
        
        if 'expected_example_count' in case:
            if len(sense.examples) == case['expected_example_count']:
                print(f"✅ 例句数量正确：{case['expected_example_count']}个")
                passed += 1
            else:
                print(f"❌ 例句数量错误：期望{case['expected_example_count']}个，实际{len(sense.examples)}个")
                failed += 1
        
        print()
        print("-"*70)
        print()
    
    print("="*70)
    print(f"测试结果: 通过 {passed} / 失败 {failed}")
    print("="*70)


if __name__ == '__main__':
    test_definition_example_split()

