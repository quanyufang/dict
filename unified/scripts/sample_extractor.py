#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
词典样例数据提取工具

从各词典中提取代表性词条，用于分析格式差异和设计统一数据结构。
"""

import os
import sys
import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict


@dataclass
class DictSample:
    """词典样例数据"""
    dictionary_id: str
    word: str
    raw_content: str
    notes: str = ""  # 人工备注


class SampleExtractor:
    """样例数据提取器"""
    
    # 要提取的英文样例词汇（覆盖不同类型）
    ENGLISH_SAMPLE_WORDS = [
        # 常用简单词
        "good", "bad", "go", "come", "make",
        # 多义词
        "run", "set", "take", "get", "put",
        # 名词
        "book", "water", "time", "people", "world",
        # 形容词
        "beautiful", "important", "different", "possible",
        # 动词变形
        "running", "taken", "went", "better", "best",
        # 短语/习语
        "give up", "look for",
        # 专业词汇
        "algorithm", "database", "philosophy",
        # 生僻词
        "serendipity", "ephemeral",
    ]
    
    # 要提取的中文样例词汇
    CHINESE_SAMPLE_WORDS = [
        # 常用字
        "一", "人", "大", "中", "国",
        # 常用词
        "学习", "工作", "朋友", "时间", "问题",
        # 成语
        "一帆风顺", "画龙点睛", "守株待兔", "亡羊补牢",
        # 多音字
        "行", "了", "着", "的",
        # 词组
        "中国人", "计算机",
    ]
    
    def __init__(self, dict_base_path: str):
        """
        初始化提取器
        
        Args:
            dict_base_path: 词典文件所在目录
        """
        self.dict_base_path = Path(dict_base_path)
        self.samples: Dict[str, List[DictSample]] = {}
        
    def extract_from_stardict(self, 
                               dict_id: str,
                               db_filename: str, 
                               content_filename: str,
                               sample_words: List[str]) -> List[DictSample]:
        """
        从StarDict格式词典提取样例
        
        Args:
            dict_id: 词典标识
            db_filename: 索引数据库文件名
            content_filename: 内容文件名
            sample_words: 要提取的词汇列表
            
        Returns:
            提取的样例列表
        """
        db_path = self.dict_base_path / db_filename
        content_path = self.dict_base_path / content_filename
        
        if not db_path.exists():
            print(f"⚠️  数据库文件不存在: {db_path}")
            return []
        if not content_path.exists():
            print(f"⚠️  内容文件不存在: {content_path}")
            return []
            
        print(f"\n📖 正在从 {dict_id} 提取样例...")
        
        samples = []
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        with open(content_path, 'rb') as content_file:
            for word in sample_words:
                # 查询索引
                cursor.execute(
                    'SELECT offset, length FROM wordIndex WHERE word = ?',
                    (word.lower(),)
                )
                result = cursor.fetchone()
                
                if result:
                    offset, length = result
                    # 读取内容
                    content_file.seek(offset)
                    raw_bytes = content_file.read(length)
                    try:
                        raw_content = raw_bytes.decode('utf-8')
                    except UnicodeDecodeError:
                        raw_content = raw_bytes.decode('utf-8', errors='replace')
                    
                    sample = DictSample(
                        dictionary_id=dict_id,
                        word=word,
                        raw_content=raw_content
                    )
                    samples.append(sample)
                    print(f"  ✓ {word}")
                else:
                    print(f"  ✗ {word} (未找到)")
        
        conn.close()
        print(f"  共提取 {len(samples)} 个样例")
        return samples
    
    def extract_all(self):
        """提取所有词典的样例"""
        
        # Oxford英汉词典
        self.samples['oxford'] = self.extract_from_stardict(
            'oxford',
            'oxford-gb.db',
            'oxford-gb.dictcontent',
            self.ENGLISH_SAMPLE_WORDS
        )
        
        # 现代汉语词典
        self.samples['xiandaihanyucidian'] = self.extract_from_stardict(
            'xiandaihanyucidian',
            'xiandaihanyucidian.db',
            'xiandaihanyucidian.dictcontent',
            self.CHINESE_SAMPLE_WORDS
        )
        
        # GCIDE英英词典
        self.samples['gcide'] = self.extract_from_stardict(
            'gcide',
            'gcide.db',
            'gcide.dictcontent',
            self.ENGLISH_SAMPLE_WORDS
        )
        
        # 朗道英汉词典
        self.samples['langdao'] = self.extract_from_stardict(
            'langdao',
            'langdao-ec-gb.db',
            'langdao-ec-gb.dictcontent',
            self.ENGLISH_SAMPLE_WORDS
        )
        
        # 汉语拼音词典
        self.samples['chinese_dict'] = self.extract_from_stardict(
            'chinese_dict',
            'chinese_dict.db',
            'chinese_dict.dictcontent',
            self.CHINESE_SAMPLE_WORDS
        )
        
    def save_samples(self, output_dir: str):
        """
        保存样例到JSON文件
        
        Args:
            output_dir: 输出目录
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        for dict_id, samples in self.samples.items():
            if not samples:
                continue
                
            # 转换为可序列化格式
            data = {
                'dictionary_id': dict_id,
                'sample_count': len(samples),
                'samples': [asdict(s) for s in samples]
            }
            
            output_file = output_path / f"{dict_id}_samples.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 已保存: {output_file}")
    
    def print_sample(self, dict_id: str, word: str):
        """打印指定词条的原始内容"""
        if dict_id not in self.samples:
            print(f"词典 {dict_id} 没有样例")
            return
            
        for sample in self.samples[dict_id]:
            if sample.word == word:
                print(f"\n{'='*60}")
                print(f"词典: {dict_id}")
                print(f"词条: {word}")
                print(f"{'='*60}")
                print(sample.raw_content)
                print(f"{'='*60}\n")
                return
        
        print(f"未找到词条: {word}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='词典样例数据提取工具')
    parser.add_argument('--dict-path', required=True, help='词典文件目录')
    parser.add_argument('--output', default='./samples', help='输出目录')
    parser.add_argument('--word', help='只提取指定词汇')
    parser.add_argument('--dict', help='只从指定词典提取')
    
    args = parser.parse_args()
    
    extractor = SampleExtractor(args.dict_path)
    extractor.extract_all()
    extractor.save_samples(args.output)
    
    # 打印一些样例
    print("\n" + "="*60)
    print("样例预览")
    print("="*60)
    
    # 打印 "good" 在各词典中的内容
    for dict_id in ['oxford', 'gcide', 'langdao']:
        extractor.print_sample(dict_id, 'good')
    
    # 打印中文样例
    for dict_id in ['xiandaihanyucidian', 'chinese_dict']:
        extractor.print_sample(dict_id, '一帆风顺')


if __name__ == '__main__':
    main()

