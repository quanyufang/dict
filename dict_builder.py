#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
字典构造程序 - 汉语拼音辞典

实现分层构造策略：
1. 基础汉字字典（常用字 -> 通用规范汉字 -> 全部汉字）
2. 词语字典（成语 -> 常用词语 -> 全部词语）
3. 合并优化和StarDict生成
"""

import os
import sys
import json
import sqlite3
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path
import argparse


@dataclass
class Character:
    """汉字数据结构"""
    char: str
    pinyin: List[str]
    strokes: int
    radicals: str
    frequency: int
    structure: str
    traditional: Optional[str] = None
    variant: Optional[str] = None
    explanations: Optional[List[Dict]] = None


@dataclass
class Word:
    """词语数据结构"""
    word: str
    pinyin: str
    abbr: str
    explanation: str
    source: Optional[Dict] = None
    quote: Optional[Dict] = None
    story: Optional[List[str]] = None
    similar: Optional[List[str]] = None
    opposite: Optional[List[str]] = None
    example: Optional[str] = None
    usage: Optional[str] = None
    notice: Optional[str] = None


class DictionaryBuilder:
    """字典构造器"""
    
    def __init__(self, data_dir: str, output_dir: str):
        """
        初始化字典构造器
        
        Args:
            data_dir: 数据源目录路径
            output_dir: 输出目录路径
        """
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.db_path = self.output_dir / "chinese_dictionary.db"
        
        # 确保输出目录存在
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 设置日志
        self.setup_logging()
        
        # 初始化数据库
        self.init_database()
        
    def setup_logging(self):
        """设置日志配置"""
        log_file = self.output_dir / "dict_builder.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def init_database(self):
        """初始化SQLite数据库"""
        self.logger.info("初始化数据库...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建汉字表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS characters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                char TEXT UNIQUE NOT NULL,
                pinyin TEXT NOT NULL,
                strokes INTEGER,
                radicals TEXT,
                frequency INTEGER,
                structure TEXT,
                traditional TEXT,
                variant TEXT,
                explanations TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建词语表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS words (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word TEXT UNIQUE NOT NULL,
                pinyin TEXT NOT NULL,
                abbr TEXT NOT NULL,
                explanation TEXT,
                source TEXT,
                quote TEXT,
                story TEXT,
                similar TEXT,
                opposite TEXT,
                example TEXT,
                usage TEXT,
                notice TEXT,
                word_type TEXT DEFAULT 'word',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_char_frequency ON characters(frequency)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_char_pinyin ON characters(pinyin)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_word_pinyin ON words(pinyin)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_word_type ON words(word_type)')
        
        conn.commit()
        conn.close()
        
        self.logger.info(f"数据库初始化完成: {self.db_path}")
        
    def _fix_json_format(self, content: str) -> str:
        """
        修复JSON格式问题
        
        Args:
            content: 原始JSON内容
            
        Returns:
            str: 修复后的JSON内容
        """
        # 移除开头和结尾的空白字符
        content = content.strip()
        
        # 如果开头不是 [，添加 [
        if not content.startswith('['):
            content = '[' + content
        
        # 如果结尾不是 ]，修复结尾
        if not content.endswith(']'):
            # 移除最后一个逗号和换行符，然后添加 ]
            content = content.rstrip().rstrip(',').rstrip() + '\n]'
        
        return content
        
    def load_character_data(self) -> List[Character]:
        """加载汉字数据"""
        self.logger.info("加载汉字数据...")
        
        characters = []
        
        # 加载基础汉字数据
        char_base_path = self.data_dir / "character" / "char_base.json"
        if char_base_path.exists():
            with open(char_base_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 修复JSON格式问题
            content = self._fix_json_format(content)
            char_base_data = json.loads(content)
                
            for item in char_base_data:
                char = Character(
                    char=item['char'],
                    pinyin=item['pinyin'],
                    strokes=item.get('strokes', 0),
                    radicals=item.get('radicals', ''),
                    frequency=item.get('frequency', 5),
                    structure=item.get('structure', ''),
                    traditional=item.get('traditional'),
                    variant=item.get('variant')
                )
                characters.append(char)
                
            self.logger.info(f"加载基础汉字数据: {len(characters)} 个")
        
        # 加载详细解释数据
        char_detail_path = self.data_dir / "character" / "char_detail.json"
        if char_detail_path.exists():
            with open(char_detail_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 修复JSON格式问题
            content = self._fix_json_format(content)
            char_detail_data = json.loads(content)
                
            # 创建字符到解释的映射
            detail_map = {item['char']: item for item in char_detail_data}
            
            # 合并解释数据
            for char in characters:
                if char.char in detail_map:
                    char.explanations = detail_map[char.char].get('pronunciations', [])
                    
            self.logger.info(f"加载汉字详细解释数据: {len(detail_map)} 个")
        
        return characters
    
    def load_word_data(self) -> List[Word]:
        """加载词语数据"""
        self.logger.info("加载词语数据...")
        
        words = []
        
        # 加载成语数据
        idiom_path = self.data_dir / "idiom" / "idiom.json"
        if idiom_path.exists():
            with open(idiom_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 修复JSON格式问题
            content = self._fix_json_format(content)
            idiom_data = json.loads(content)
                
            for item in idiom_data:
                word = Word(
                    word=item['word'],
                    pinyin=item['pinyin'],
                    abbr=item['abbr'],
                    explanation=item.get('explanation', ''),
                    source=item.get('source'),
                    quote=item.get('quote'),
                    story=item.get('story'),
                    similar=item.get('similar'),
                    opposite=item.get('opposite'),
                    example=item.get('example'),
                    usage=item.get('usage'),
                    notice=item.get('notice')
                )
                words.append(word)
                
            self.logger.info(f"加载成语数据: {len(words)} 个")
        
        # 加载词语数据
        word_path = self.data_dir / "word" / "word.json"
        if word_path.exists():
            with open(word_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 修复JSON格式问题
            content = self._fix_json_format(content)
            word_data = json.loads(content)
                
            for item in word_data:
                # 跳过已经在成语中的词
                if not any(w.word == item['word'] for w in words):
                    # 处理缺少的字段，提供默认值
                    word = Word(
                        word=item['word'],
                        pinyin=item['pinyin'],
                        abbr=item.get('abbr', ''),  # 如果没有abbr字段，使用空字符串
                        explanation=item.get('explanation', ''),
                        source=item.get('source'),
                        quote=item.get('quote'),
                        story=item.get('story'),
                        similar=item.get('similar'),
                        opposite=item.get('opposite'),
                        example=item.get('example'),
                        usage=item.get('usage'),
                        notice=item.get('notice')
                    )
                    words.append(word)
                    
            self.logger.info(f"加载词语数据: {len(words)} 个")
        
        return words
    
    def build_character_dictionary(self, characters: List[Character]):
        """构建汉字字典"""
        self.logger.info("构建汉字字典...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 按频率分组处理
        frequency_groups = {}
        for char in characters:
            freq = char.frequency
            if freq not in frequency_groups:
                frequency_groups[freq] = []
            frequency_groups[freq].append(char)
        
        # 按频率顺序处理（0=最常用，1=较常用，2=次常用，3=二级字，4=三级字，5=生僻字）
        for freq in sorted(frequency_groups.keys()):
            chars = frequency_groups[freq]
            self.logger.info(f"处理频率 {freq} 的汉字: {len(chars)} 个")
            
            for char in chars:
                try:
                    cursor.execute('''
                        INSERT OR REPLACE INTO characters 
                        (char, pinyin, strokes, radicals, frequency, structure, 
                         traditional, variant, explanations)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        char.char,
                        json.dumps(char.pinyin, ensure_ascii=False),
                        char.strokes,
                        char.radicals,
                        char.frequency,
                        char.structure,
                        char.traditional,
                        char.variant,
                        json.dumps(char.explanations, ensure_ascii=False) if char.explanations else None
                    ))
                except Exception as e:
                    self.logger.error(f"插入汉字失败 {char.char}: {e}")
        
        conn.commit()
        conn.close()
        
        self.logger.info("汉字字典构建完成")
    
    def build_word_dictionary(self, words: List[Word]):
        """构建词语字典"""
        self.logger.info("构建词语字典...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 按类型分组处理
        idiom_count = 0
        word_count = 0
        
        for word in words:
            try:
                # 判断是否为成语（长度>=4且包含成语特征）
                is_idiom = (len(word.word) >= 4 and 
                           (word.source or word.story or word.usage))
                
                word_type = 'idiom' if is_idiom else 'word'
                
                cursor.execute('''
                    INSERT OR REPLACE INTO words 
                    (word, pinyin, abbr, explanation, source, quote, story,
                     similar, opposite, example, usage, notice, word_type)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    word.word,
                    word.pinyin,
                    word.abbr,
                    word.explanation,
                    json.dumps(word.source, ensure_ascii=False) if word.source else None,
                    json.dumps(word.quote, ensure_ascii=False) if word.quote else None,
                    json.dumps(word.story, ensure_ascii=False) if word.story else None,
                    json.dumps(word.similar, ensure_ascii=False) if word.similar else None,
                    json.dumps(word.opposite, ensure_ascii=False) if word.opposite else None,
                    word.example,
                    word.usage,
                    word.notice,
                    word_type
                ))
                
                if is_idiom:
                    idiom_count += 1
                else:
                    word_count += 1
                    
            except Exception as e:
                self.logger.error(f"插入词语失败 {word.word}: {e}")
        
        conn.commit()
        conn.close()
        
        self.logger.info(f"词语字典构建完成: 成语 {idiom_count} 个，词语 {word_count} 个")
    
    def generate_statistics(self):
        """生成统计信息"""
        self.logger.info("生成统计信息...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 汉字统计
        cursor.execute('SELECT COUNT(*) FROM characters')
        total_chars = cursor.fetchone()[0]
        
        cursor.execute('SELECT frequency, COUNT(*) FROM characters GROUP BY frequency ORDER BY frequency')
        char_freq_stats = cursor.fetchall()
        
        # 词语统计
        cursor.execute('SELECT COUNT(*) FROM words')
        total_words = cursor.fetchone()[0]
        
        cursor.execute('SELECT word_type, COUNT(*) FROM words GROUP BY word_type')
        word_type_stats = cursor.fetchall()
        
        conn.close()
        
        # 输出统计信息
        stats_file = self.output_dir / "statistics.txt"
        with open(stats_file, 'w', encoding='utf-8') as f:
            f.write("汉语拼音辞典 - 数据统计\n")
            f.write("=" * 50 + "\n\n")
            
            f.write(f"汉字总数: {total_chars}\n")
            f.write("汉字频率分布:\n")
            for freq, count in char_freq_stats:
                freq_names = {0: "最常用", 1: "较常用", 2: "次常用", 
                             3: "二级字", 4: "三级字", 5: "生僻字"}
                f.write(f"  {freq_names.get(freq, f'频率{freq}')}: {count} 个\n")
            
            f.write(f"\n词语总数: {total_words}\n")
            f.write("词语类型分布:\n")
            for word_type, count in word_type_stats:
                type_names = {'idiom': '成语', 'word': '词语'}
                f.write(f"  {type_names.get(word_type, word_type)}: {count} 个\n")
        
        self.logger.info(f"统计信息已保存到: {stats_file}")
        
        return {
            'total_chars': total_chars,
            'char_freq_stats': char_freq_stats,
            'total_words': total_words,
            'word_type_stats': word_type_stats
        }
    
    def build(self):
        """执行完整的字典构建流程"""
        try:
            self.logger.info("开始构建汉语拼音辞典...")
            
            # 第一阶段：构建汉字字典
            self.logger.info("第一阶段：构建汉字字典")
            characters = self.load_character_data()
            self.build_character_dictionary(characters)
            
            # 第二阶段：构建词语字典
            self.logger.info("第二阶段：构建词语字典")
            words = self.load_word_data()
            self.build_word_dictionary(words)
            
            # 第三阶段：生成统计信息
            self.logger.info("第三阶段：生成统计信息")
            stats = self.generate_statistics()
            
            self.logger.info("字典构建完成！")
            self.logger.info(f"汉字总数: {stats['total_chars']}")
            self.logger.info(f"词语总数: {stats['total_words']}")
            
        except Exception as e:
            self.logger.error(f"字典构建失败: {e}")
            raise


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='汉语拼音辞典构建程序',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python dict_builder.py --data-dir chinese-dictionary-main --output-dir output
  
参数说明:
  --data-dir: 数据源目录路径（包含character、word、idiom子目录）
  --output-dir: 输出目录路径
        """
    )
    
    parser.add_argument('--data-dir', required=True, help='数据源目录路径')
    parser.add_argument('--output-dir', required=True, help='输出目录路径')
    
    args = parser.parse_args()
    
    try:
        # 创建字典构造器并执行构建
        builder = DictionaryBuilder(args.data_dir, args.output_dir)
        builder.build()
        print(f"\n🎉 字典构建完成！")
        print(f"输出目录: {args.output_dir}")
        print(f"数据库文件: {builder.db_path}")
        print(f"统计信息: {args.output_dir}/statistics.txt")
        
    except Exception as e:
        print(f"\n❌ 字典构建失败: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
