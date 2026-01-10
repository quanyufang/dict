#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一测试Oxford解析器的bad cases

用于验证所有记录的bad case是否都已解决
"""

import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

sys.path.insert(0, str(Path(__file__).parent.parent))

from unified.parsers.oxford import OxfordParser
from unified.models.entry import DictionaryEntry


@dataclass
class BadCase:
    """Bad case定义"""
    word: str
    content: str
    expected_senses: int
    expected_pronunciations: int = 0
    expected_examples_per_sense: Dict[int, int] = None  # {sense_index: expected_examples}
    description: str = ""
    
    def __post_init__(self):
        if self.expected_examples_per_sense is None:
            self.expected_examples_per_sense = {}


class BadCaseTester:
    """Bad case测试器"""
    
    def __init__(self):
        self.parser = OxfordParser()
        self.cases = self._load_bad_cases()
    
    def _load_bad_cases(self) -> List[BadCase]:
        """加载所有bad cases"""
        cases = []
        
        # Case 1: important - 词形变化误匹配
        cases.append(BadCase(
            word="important",
            content="""/ɪmˈpɔːtnt; ɪm`pɔrtnt/ 
adj  
1 ~ (to sb/sth) very serious and significant; of great value or concern 重要的; 重大的; 非常有价值的: 
an important decision, announcement, meeting 重要的决定、宣布、会议 
* It is vitally important to cancel the order immediately. 最重要的是要立即取消这一定单. 
* It is important that students (should) attend/for students to attend all the lectures. 所有的课学生都应该去听, 这是很重要的. 
* They need more money now but, more important, they need long-term help. 目前他们需要更多的钱, 不过更重要的是他们需要长期的援助. 
* It's important to me that you should be there. 你应该在场, 这对我来说很重要.  
2 (of a person) having great influence or authority; influential （指人）有很大影响或权威的: She was clearly an important person. 她显然是个有影响的人. 
* It's not as if he was very important in the company hierarchy. 他在公司的领导层中似乎无多大权力.""",
            expected_senses=2,
            expected_pronunciations=2,  # UK and US
            expected_examples_per_sense={0: 4, 1: 1},  # sense #1有4个例句, sense #2有1个例句
            description="词形变化误匹配导致遗漏第一个sense"
        ))
        
        # Case 2: gone - 混合格式（交叉引用+完整定义）
        cases.append(BadCase(
            word="gone",
            content="""pp of go.
/gɒn; <i>US</i> gɔːn; ˇɔn/ 
adj  
1 [pred 作表语] past; departed 过去; 离去: 
Gone are the days when you could buy a three-course meal for under 1. 一顿饭吃三道菜不到1英镑, 这日子一去不复返了.  
2 (used after a phrase expressing time in weeks or months 用于表示星期或月的时间短语之後) having been pregnant for the specified period of time 已怀孕一段时间的: 
She's seven months gone. 她已有七个月的身孕.  
3 (idm 习语) be gone on sb (infml 口) be very much in love with sb; be infatuated with sb 与某人热恋; 迷恋某人: 
It's a pity Peter's so gone on Jane. 彼得如此迷恋简, 真遗憾. 
,going, ,going, `gone (said by an auctioneer to show that bidding must stop because an item has been sold 拍卖商用语, 表示某物售出而停止出价).
prep 
later than; past (in time) 晚于; （时间上）已过:
It's gone six o'clock already. 现在已过了六点钟.""",
            expected_senses=5,  # 1个交叉引用 + 3个adj + 1个prep
            expected_pronunciations=3,  # UK, US, US
            expected_examples_per_sense={1: 1, 2: 1, 3: 1, 4: 1},  # adj和prep的sense都有例句
            description="混合格式（交叉引用+完整定义）"
        ))
        
        return cases
    
    def test_all(self) -> Dict[str, Tuple[bool, str]]:
        """测试所有bad cases"""
        results = {}
        
        print("="*70)
        print("Oxford解析器Bad Cases统一测试")
        print("="*70)
        print()
        
        for i, case in enumerate(self.cases, 1):
            print(f"[{i}/{len(self.cases)}] 测试: {case.word}")
            print(f"    描述: {case.description}")
            print(f"    预期: {case.expected_senses}个sense, {case.expected_pronunciations}个音标")
            
            # 解析
            entry = self.parser.parse(case.word, case.content)
            
            # 验证
            success, message = self._validate_case(entry, case)
            results[case.word] = (success, message)
            
            if success:
                print(f"    ✅ 通过: {message}")
            else:
                print(f"    ❌ 失败: {message}")
            print()
        
        return results
    
    def _validate_case(self, entry: Optional[DictionaryEntry], case: BadCase) -> Tuple[bool, str]:
        """验证单个case"""
        if entry is None:
            return False, "解析失败，返回None"
        
        # 检查sense数量
        if len(entry.senses) < case.expected_senses:
            return False, f"sense数量不足：预期{case.expected_senses}个，实际{len(entry.senses)}个"
        
        # 检查音标数量
        if case.expected_pronunciations > 0:
            if len(entry.pronunciations) < case.expected_pronunciations:
                return False, f"音标数量不足：预期{case.expected_pronunciations}个，实际{len(entry.pronunciations)}个"
        
        # 检查例句数量（如果指定）
        if case.expected_examples_per_sense:
            for sense_idx, expected_examples in case.expected_examples_per_sense.items():
                if sense_idx < len(entry.senses):
                    actual_examples = len(entry.senses[sense_idx].examples)
                    if actual_examples < expected_examples:
                        return False, f"sense #{sense_idx+1}例句不足：预期{expected_examples}个，实际{actual_examples}个"
        
        # 检查解析质量
        if entry.parse_quality < 0.8:
            return False, f"解析质量过低：{entry.parse_quality}"
        
        # 基本验证通过
        sense_info = f"{len(entry.senses)}个sense"
        if entry.pronunciations:
            sense_info += f", {len(entry.pronunciations)}个音标"
        total_examples = sum(len(s.examples) for s in entry.senses)
        if total_examples > 0:
            sense_info += f", {total_examples}个例句"
        
        return True, sense_info
    
    def print_summary(self, results: Dict[str, Tuple[bool, str]]):
        """打印测试摘要"""
        print("="*70)
        print("测试摘要")
        print("="*70)
        
        total = len(results)
        passed = sum(1 for success, _ in results.values() if success)
        failed = total - passed
        
        print(f"总case数: {total}")
        print(f"通过: {passed} ✅")
        print(f"失败: {failed} ❌")
        print()
        
        if failed > 0:
            print("失败的case:")
            for word, (success, message) in results.items():
                if not success:
                    print(f"  ❌ {word}: {message}")
        else:
            print("🎉 所有case都通过了！")


def main():
    tester = BadCaseTester()
    results = tester.test_all()
    tester.print_summary(results)
    
    # 返回退出码
    all_passed = all(success for success, _ in results.values())
    return 0 if all_passed else 1


if __name__ == '__main__':
    exit(main())

