#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试改进后的bad cases
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from unified.parsers.oxford import OxfordParser


def test_bad_cases():
    """测试之前的bad cases"""
    
    parser = OxfordParser()
    
    # Bad cases列表
    test_cases = [
        {
            "name": "making - IDM习语解析",
            "word": "making",
            "raw": "/ˈmeɪkɪŋ; `mekɪŋ/ n (idm 习语) be the making of sb make sb succeed or develop well 使某人成功或顺利: These two years of hard work will be the making of him. 这两年的艰苦工作能把他造就成材. have the makings of sth have the qualities needed to become sth 有条件成为某事物: She has the makings of a good lawyer. 她具备当个好律师的素质. in the `making in the course of being made, formed or developed 在制造、形成或发展的过程中: This first novel is the work of a writer in the making, ie not yet an expert writer. 这第一本小说是作者正在成长锻炼中的作品. * This model was two years in the making, ie took two years to make. 这一型号的产品是用了两年时间制成的.",
            "expected_senses": 3,  # 应该是3个习语短语
            "description": "应该提取3个习语短语，每个都有定义和例句"
        },
        {
            "name": "important - 只解析了一个sense",
            "word": "important",
            "raw": "/ɪmˈpɔːtnt; ɪm`pɔrtnt/ adj  1 ~ (to sb/sth) very serious and significant; of great value or concern 重要的; 重大的; 非常有价值的: an important decision, announcement, meeting 重要的决定、宣布、会议 * It is vitally important to cancel the order immediately. 最重要的是要立即取消一一定单. * It is important that students (should) attend/for students to attend all the lectures. 所有的课学生都应该去听, 这是很重要的. * They need more money now but, more important, they need long-term help. 目前他们需要更多的钱, 不过更重要的是他们需要长期的援助. * It's important to me that you should be there. 你应该在场, 这对我来说很重要.  2 (of a person) having great influence or authority; influential （指人）有很大影响或权威的: She was clearly an important person. 她显然是个有影响的人. * It's not as if he was very important in the company hierarchy. 他在公司的领导层中似乎无多大权力.",
            "expected_senses": 2,  # 应该是2个sense
            "description": "应该提取2个sense"
        },
        {
            "name": "gone - 混合格式",
            "word": "gone",
            "raw": "pp of go.\n/gɒn; <i>US</i> gɔːn; ˇɔn/ adj  1 [pred 作表语] past; departed 过去; 离去: Gone are the days when you could buy a three-course meal for under 1. 一顿饭吃三道菜不到1英镑, 这日子一去不复返了.  2 (used after a phrase expressing time in weeks or months 用于表示星期或月的时间短语之後) having been pregnant for the specified period of time 已怀孕一段时间的: She's seven months gone. 她已有七个月的身孕.  3 (idm 习语) be gone on sb (infml 口) be very much in love with sb; be infatuated with sb 与某人热恋; 迷恋某人: It's a pity Peter's so gone on Jane. 彼得如此迷恋简, 真遗憾. ,going, ,going, `gone (said by an auctioneer to show that bidding must stop because an item has been sold 拍卖商用语, 表示某物售出而停止出价).\nprep later than; past (in time) 晚于; （时间上）已过: It's gone six o'clock already. 现在已过了六点钟.",
            "expected_senses": 4,  # 应该是4个sense（adj的3个 + prep的1个）
            "description": "应该正确处理混合格式，提取所有sense"
        },
        {
            "name": "a - 定义和例句分离（义项1）",
            "word": "a",
            "raw": "/eɪ; e/ n (pl A's, a's / eIz; ez/)  1 the first letter of the English alphabet 英语字母表的第一个字母: `Ann' begins with (an) A/`A'. Ann一字以A字母开始.",
            "expected_senses": 1,
            "expected_examples": 1,
            "description": "应该正确分离定义和例句"
        },
    ]
    
    print("="*70)
    print("测试改进后的Bad Cases")
    print("="*70)
    print()
    
    passed = 0
    failed = 0
    warnings = 0
    
    for i, case in enumerate(test_cases, 1):
        print(f"[测试 {i}] {case['name']}")
        print(f"说明: {case['description']}")
        print()
        
        # 解析
        entry = parser.parse(case['word'], case['raw'])
        
        if not entry or not entry.senses:
            print(f"❌ 解析失败：没有生成sense")
            failed += 1
            print()
            continue
        
        # 检查sense数量
        if 'expected_senses' in case:
            actual_senses = len(entry.senses)
            if actual_senses == case['expected_senses']:
                print(f"✅ Sense数量正确：{actual_senses}个")
                passed += 1
            else:
                print(f"⚠️  Sense数量不匹配：期望{case['expected_senses']}个，实际{actual_senses}个")
                warnings += 1
        
        # 检查例句数量
        if 'expected_examples' in case:
            total_examples = sum(len(sense.examples) for sense in entry.senses)
            if total_examples == case['expected_examples']:
                print(f"✅ 例句数量正确：{total_examples}个")
                passed += 1
            else:
                print(f"⚠️  例句数量不匹配：期望{case['expected_examples']}个，实际{total_examples}个")
                warnings += 1
        
        # 显示详细信息
        print(f"解析结果：")
        print(f"  音标数: {len(entry.pronunciations)}")
        print(f"  释义数: {len(entry.senses)}")
        
        for j, sense in enumerate(entry.senses, 1):
            print(f"    Sense {j}:")
            print(f"      词性: {sense.pos}")
            print(f"      义项编号: {sense.sense_number}")
            print(f"      定义: {sense.definition[:80]}...")
            print(f"      例句数: {len(sense.examples)}")
            if sense.examples:
                print(f"      例句1: {sense.examples[0].text[:60]}...")
        
        print()
        print("-"*70)
        print()
    
    print("="*70)
    print(f"测试结果: 通过 {passed} / 警告 {warnings} / 失败 {failed}")
    print("="*70)


if __name__ == '__main__':
    test_bad_cases()

