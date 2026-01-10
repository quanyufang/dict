#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Oxford词典样例提取工具

提取更多样例，包含原始数据，用于详细分析。
"""

import os
import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import random

# 词典文件目录
DICT_BASE_PATH = Path(__file__).parent.parent.parent / "app_dictfiles"
OUTPUT_PATH = Path(__file__).parent.parent / "comprehensive_samples"


# Oxford样例词汇 - 覆盖各种复杂情况
OXFORD_SAMPLES = [
    # ========== 基础词 ==========
    "a", "the", "is", "are", "be", "have", "has", "had",
    "do", "does", "did", "will", "would", "can", "could",
    "good", "bad", "big", "small", "new", "old", "long", "short",
    "go", "come", "make", "take", "get", "put", "give", "keep",
    "say", "tell", "ask", "see", "look", "find", "know", "think",
    
    # ========== 多义词（Oxford格式复杂）==========
    "run", "set", "take", "get", "put", "turn", "break", "fall",
    "hold", "stand", "sit", "lie", "cut", "draw", "play", "work",
    "call", "point", "hand", "face", "head", "back", "part", "side",
    
    # ========== 名词 ==========
    "book", "water", "time", "people", "world", "day", "year", "life",
    "man", "woman", "child", "house", "school", "company", "system",
    "problem", "question", "answer", "idea", "fact", "reason", "case",
    
    # ========== 形容词 ==========
    "beautiful", "important", "different", "possible", "available",
    "great", "little", "high", "low", "large", "young", "right", "wrong",
    
    # ========== 动词变形 ==========
    "running", "taken", "went", "gone", "better", "best", "worse", "worst",
    "being", "having", "doing", "saying", "going", "coming", "making",
    
    # ========== 专业词汇 ==========
    "algorithm", "database", "philosophy", "psychology", "economy",
    "technology", "environment", "government", "development", "management",
    
    # ========== 短语/习语 ==========
    "give up", "look for", "come up", "go on", "take off",
]


def query_word(db_path: Path, content_path: Path, word: str) -> Optional[Tuple[str, int, int]]:
    """从词典查询单词，返回 (内容, offset, length)"""
    if not db_path.exists() or not content_path.exists():
        return None
        
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # 尝试精确匹配
    cursor.execute('SELECT offset, length FROM wordIndex WHERE word = ?', (word.lower(),))
    result = cursor.fetchone()
    
    # 如果没找到，尝试原始大小写
    if not result and word != word.lower():
        cursor.execute('SELECT offset, length FROM wordIndex WHERE word = ?', (word,))
        result = cursor.fetchone()
    
    conn.close()
    
    if not result:
        return None
        
    offset, length = result
    
    with open(content_path, 'rb') as f:
        f.seek(offset)
        raw_bytes = f.read(length)
        try:
            content = raw_bytes.decode('utf-8')
        except UnicodeDecodeError:
            content = raw_bytes.decode('utf-8', errors='replace')
    
    return (content, offset, length)


def get_random_words_from_db(db_path: Path, count: int = 50) -> List[str]:
    """从数据库随机抽取单词"""
    if not db_path.exists():
        return []
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    cursor.execute(f'SELECT word FROM wordIndex ORDER BY RANDOM() LIMIT {count}')
    words = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    return words


def extract_oxford_comprehensive():
    """全面提取Oxford词典样例"""
    db_path = DICT_BASE_PATH / "oxford-gb.db"
    content_path = DICT_BASE_PATH / "oxford-gb.dictcontent"
    
    print("=" * 60)
    print("Oxford英汉词典 - 全面样例提取")
    print("=" * 60)
    
    # 1. 指定词汇
    samples = []
    found_count = 0
    not_found = []
    
    for word in OXFORD_SAMPLES:
        result = query_word(db_path, content_path, word)
        if result:
            content, offset, length = result
            samples.append({
                "word": word,
                "raw_content": content,
                "offset": offset,
                "length": length,
                "source": "specified"
            })
            found_count += 1
        else:
            not_found.append(word)
    
    print(f"指定词汇: 找到 {found_count}/{len(OXFORD_SAMPLES)}")
    if not_found:
        print(f"未找到: {not_found[:10]}{'...' if len(not_found) > 10 else ''}")
    
    # 2. 随机抽样补充
    random_words = get_random_words_from_db(db_path, 50)
    random_found = 0
    
    for word in random_words:
        # 跳过已有的
        if any(s['word'].lower() == word.lower() for s in samples):
            continue
        
        result = query_word(db_path, content_path, word)
        if result:
            content, offset, length = result
            samples.append({
                "word": word,
                "raw_content": content,
                "offset": offset,
                "length": length,
                "source": "random"
            })
            random_found += 1
    
    print(f"随机抽样: 添加 {random_found} 个")
    print(f"总计样例: {len(samples)}")
    
    return samples


def analyze_oxford_format(samples: List[Dict]) -> Dict:
    """详细分析Oxford词典格式"""
    import re
    
    analysis = {
        "total_samples": len(samples),
        "format_patterns": {},
        "statistics": {},
        "special_cases": [],
    }
    
    stats = {
        "has_phonetic": 0,
        "has_uk_us_phonetic": 0,  # 英式美式分开
        "has_pos": 0,
        "has_numbered_senses": 0,  # 数字序号
        "has_lettered_senses": 0,  # 字母序号
        "has_examples": 0,  # * 开头的例句
        "has_grammar_notes": 0,  # [attrib]等
        "has_idm": 0,  # IDM 习语
        "has_phr_v": 0,  # PHR V 动词短语
        "has_cross_ref": 0,  # => 交叉引用
        "avg_length": 0,
        "max_length": 0,
        "min_length": float('inf'),
        "pos_distribution": {},
        "grammar_notes": set(),
    }
    
    patterns_found = {
        "phonetic_slash_separated": 0,  # /英; 美/
        "phonetic_single": 0,            # /单一音标/
        "pos_standard": 0,               # n, v, adj, adv
        "sense_numbers": 0,               # 1, 2, 3
        "sense_letters": 0,               # (a), (b), (c)
        "example_star": 0,                # * 开头
        "grammar_bracket": 0,            # [attrib]
        "idm_section": 0,                 # IDM
        "phr_v_section": 0,               # PHR V
        "cross_ref_arrow": 0,             # =>
    }
    
    special_cases = []
    
    for sample in samples:
        content = sample['raw_content']
        word = sample['word']
        length = len(content)
        
        stats['avg_length'] += length
        stats['max_length'] = max(stats['max_length'], length)
        stats['min_length'] = min(stats['min_length'], length)
        
        # 音标检测
        phonetic_match = re.search(r'/([^/]+);([^/]+)/', content)
        if phonetic_match:
            stats['has_phonetic'] += 1
            stats['has_uk_us_phonetic'] += 1
            patterns_found['phonetic_slash_separated'] += 1
        elif re.search(r'/[^/]+/', content):
            stats['has_phonetic'] += 1
            patterns_found['phonetic_single'] += 1
        
        # 词性检测
        pos_matches = re.findall(r'\b(n|v|adj|adv|prep|conj|pron|interj|det|aux|modal|art)\b', content)
        if pos_matches:
            stats['has_pos'] += 1
            patterns_found['pos_standard'] += 1
            for pos in pos_matches:
                stats['pos_distribution'][pos] = stats['pos_distribution'].get(pos, 0) + 1
        
        # 数字序号
        if re.search(r'(?:^|\s)(\d+)\s+[^\d]', content, re.MULTILINE):
            stats['has_numbered_senses'] += 1
            patterns_found['sense_numbers'] += 1
        
        # 字母序号
        if re.search(r'\(([a-z])\)', content):
            stats['has_lettered_senses'] += 1
            patterns_found['sense_letters'] += 1
        
        # 例句
        if re.search(r'\* [^*]+', content):
            stats['has_examples'] += 1
            patterns_found['example_star'] += 1
        
        # 语法说明
        grammar_matches = re.findall(r'\[([^\]]+)\]', content)
        if grammar_matches:
            stats['has_grammar_notes'] += 1
            patterns_found['grammar_bracket'] += 1
            stats['grammar_notes'].update(grammar_matches)
        
        # IDM
        if 'IDM' in content:
            stats['has_idm'] += 1
            patterns_found['idm_section'] += 1
        
        # PHR V
        if 'PHR V' in content:
            stats['has_phr_v'] += 1
            patterns_found['phr_v_section'] += 1
        
        # 交叉引用
        if '=>' in content:
            stats['has_cross_ref'] += 1
            patterns_found['cross_ref_arrow'] += 1
        
        # 特殊案例
        if length < 50:
            special_cases.append({
                "type": "very_short",
                "word": word,
                "content": content[:200],
                "note": "内容极短"
            })
        elif length > 5000:
            special_cases.append({
                "type": "very_long",
                "word": word,
                "length": length,
                "note": "内容极长"
            })
    
    stats['avg_length'] = stats['avg_length'] / len(samples) if samples else 0
    stats['grammar_notes'] = list(stats['grammar_notes'])[:20]  # 限制数量
    
    analysis['statistics'] = stats
    analysis['format_patterns'] = patterns_found
    analysis['special_cases'] = special_cases[:20]
    
    return analysis


def main():
    """主函数"""
    OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
    
    # 提取Oxford样例
    oxford_samples = extract_oxford_comprehensive()
    
    # 保存完整样例
    output_file = OUTPUT_PATH / "oxford_comprehensive.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "dictionary_id": "oxford",
            "dictionary_name": "牛津英汉词典",
            "total_samples": len(oxford_samples),
            "samples": oxford_samples
        }, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 样例数据已保存: {output_file}")
    
    # 详细分析
    analysis = analyze_oxford_format(oxford_samples)
    
    analysis_file = OUTPUT_PATH / "oxford_detailed_analysis.json"
    with open(analysis_file, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)
    print(f"✅ 分析结果已保存: {analysis_file}")
    
    # 打印一些统计
    print("\n" + "=" * 60)
    print("格式分析统计")
    print("=" * 60)
    print(f"有音标: {analysis['statistics']['has_phonetic']}/{len(oxford_samples)}")
    print(f"有词性: {analysis['statistics']['has_pos']}/{len(oxford_samples)}")
    print(f"有数字序号: {analysis['statistics']['has_numbered_senses']}/{len(oxford_samples)}")
    print(f"有字母序号: {analysis['statistics']['has_lettered_senses']}/{len(oxford_samples)}")
    print(f"有例句: {analysis['statistics']['has_examples']}/{len(oxford_samples)}")
    print(f"有语法说明: {analysis['statistics']['has_grammar_notes']}/{len(oxford_samples)}")
    print(f"有IDM: {analysis['statistics']['has_idm']}/{len(oxford_samples)}")
    print(f"有PHR V: {analysis['statistics']['has_phr_v']}/{len(oxford_samples)}")
    print(f"平均长度: {analysis['statistics']['avg_length']:.0f} 字符")
    
    return oxford_samples, analysis


if __name__ == '__main__':
    main()

