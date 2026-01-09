#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接从本地词典文件提取样例数据

运行方式：
    python extract_samples.py
"""

import os
import sys
import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# 词典文件目录
DICT_BASE_PATH = Path(__file__).parent.parent.parent / "app_dictfiles"
OUTPUT_PATH = Path(__file__).parent / "samples"

# 词典配置
DICT_CONFIGS = {
    'oxford': {
        'db': 'oxford-gb.db',
        'content': 'oxford-gb.dictcontent',
        'name': '牛津英汉词典',
        'index_lang': 'en',
        'explain_lang': 'zh-en'
    },
    'xiandaihanyucidian': {
        'db': 'xiandaihanyucidian.db', 
        'content': 'xiandaihanyucidian.dictcontent',
        'name': '现代汉语词典',
        'index_lang': 'zh',
        'explain_lang': 'zh'
    },
    'gcide': {
        'db': 'gcide.db',
        'content': 'gcide.dictcontent',
        'name': 'GCIDE英英词典',
        'index_lang': 'en',
        'explain_lang': 'en'
    },
    'langdao': {
        'db': 'langdao-ec-gb.db',
        'content': 'langdao-ec-gb.dictcontent',
        'name': '朗道英汉词典',
        'index_lang': 'en',
        'explain_lang': 'zh'
    },
    'chinese_dict': {
        'db': 'chinese_dict.db',
        'content': 'chinese_dict.dictcontent',
        'name': '汉语拼音词典',
        'index_lang': 'zh',
        'explain_lang': 'zh'
    }
}

# 英文样例词汇（覆盖不同类型）
ENGLISH_SAMPLES = [
    # 常用简单词
    "good", "bad", "go", "come", "make",
    # 多义词
    "run", "set", "take", "get", "put",
    # 名词
    "book", "water", "time", "people", "world",
    # 形容词
    "beautiful", "important", "different",
    # 动词变形
    "running", "went", "better", "best",
    # 专业词汇
    "algorithm", "database", "philosophy",
]

# 中文样例词汇
CHINESE_SAMPLES = [
    # 常用字
    "一", "人", "大", "中", "国",
    # 常用词  
    "学习", "工作", "朋友", "时间", "问题",
    # 成语
    "一帆风顺", "画龙点睛", "守株待兔",
    # 多音字
    "行", "了", "着", "的",
]


def query_word(db_path: Path, content_path: Path, word: str) -> Optional[str]:
    """从词典查询单词"""
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
            return raw_bytes.decode('utf-8')
        except UnicodeDecodeError:
            return raw_bytes.decode('utf-8', errors='replace')


def extract_samples():
    """提取所有词典样例"""
    OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
    
    all_samples = {}
    
    for dict_id, config in DICT_CONFIGS.items():
        db_path = DICT_BASE_PATH / config['db']
        content_path = DICT_BASE_PATH / config['content']
        
        print(f"\n📖 {config['name']} ({dict_id})")
        print(f"   数据库: {db_path.exists()}, 内容: {content_path.exists()}")
        
        if not db_path.exists():
            print(f"   ⚠️  数据库不存在，跳过")
            continue
            
        # 选择合适的样例词汇
        if config['index_lang'] == 'zh':
            sample_words = CHINESE_SAMPLES
        else:
            sample_words = ENGLISH_SAMPLES
            
        samples = []
        for word in sample_words:
            content = query_word(db_path, content_path, word)
            if content:
                samples.append({
                    'word': word,
                    'raw_content': content,
                    'content_length': len(content)
                })
                print(f"   ✓ {word} ({len(content)} bytes)")
            else:
                print(f"   ✗ {word}")
        
        if samples:
            all_samples[dict_id] = {
                'dictionary_id': dict_id,
                'dictionary_name': config['name'],
                'index_language': config['index_lang'],
                'explanation_language': config['explain_lang'],
                'sample_count': len(samples),
                'samples': samples
            }
            
            # 保存单独文件
            output_file = OUTPUT_PATH / f"{dict_id}_samples.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(all_samples[dict_id], f, ensure_ascii=False, indent=2)
            print(f"   ✅ 已保存 {len(samples)} 个样例到 {output_file.name}")
    
    # 保存汇总文件
    summary_file = OUTPUT_PATH / "all_samples_summary.json"
    summary = {
        'total_dictionaries': len(all_samples),
        'dictionaries': list(all_samples.keys()),
        'samples_per_dict': {k: v['sample_count'] for k, v in all_samples.items()}
    }
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*60}")
    print(f"提取完成！共 {len(all_samples)} 个词典")
    print(f"样例文件保存在: {OUTPUT_PATH}")
    
    return all_samples


def print_sample_comparison(all_samples: Dict, word: str):
    """打印同一词汇在不同词典中的内容"""
    print(f"\n{'='*80}")
    print(f"词汇对比: {word}")
    print(f"{'='*80}")
    
    for dict_id, data in all_samples.items():
        for sample in data['samples']:
            if sample['word'] == word:
                print(f"\n【{data['dictionary_name']}】")
                print("-" * 40)
                # 限制显示长度
                content = sample['raw_content']
                if len(content) > 2000:
                    content = content[:2000] + "\n... (truncated)"
                print(content)
                break


if __name__ == '__main__':
    samples = extract_samples()
    
    # 打印一些对比
    if samples:
        print_sample_comparison(samples, 'good')
        print_sample_comparison(samples, 'run')

