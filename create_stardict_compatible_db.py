#!/usr/bin/env python3
# -*- coding: utf-8
"""
create_stardict_compatible_db.py - 创建与现有app兼容的StarDict格式数据库

这个脚本将chinese-dictionary的数据转换为与现有app兼容的格式：
1. 创建SQLite数据库，包含wordIndex表（id, word, offset, length）
2. 生成StarDict格式的dict文件
3. 生成StarDict格式的idx文件

使用方法:
    python create_stardict_compatible_db.py --db chinese_dictionary.db --output output_dir

输出文件:
    - chinese_dict.db: 与现有app兼容的SQLite数据库
    - chinese_dict.dict: StarDict格式的字典内容文件
    - chinese_dict.idx: StarDict格式的索引文件
    - chinese_dict.ifo: StarDict格式的信息文件
"""

import sys
import sqlite3
import struct
import json
import argparse
from pathlib import Path
from typing import List, Tuple, Dict, Any


class StarDictCompatibleBuilder:
    """创建与现有app兼容的StarDict格式数据库"""
    
    def __init__(self, source_db: str, output_dir: str):
        """
        初始化构建器
        
        Args:
            source_db: 源数据库路径（chinese_dictionary.db）
            output_dir: 输出目录路径
        """
        self.source_db = Path(source_db)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 输出文件路径
        self.dict_db_path = self.output_dir / "chinese_dict.db"
        self.dict_file_path = self.output_dir / "chinese_dict.dictcontent"
        self.idx_file_path = self.output_dir / "chinese_dict.idx"
        self.ifo_file_path = self.output_dir / "chinese_dict.ifo"
        
    def create_database_schema(self):
        """创建与现有app兼容的数据库表结构"""
        print("创建数据库表结构...")
        
        conn = sqlite3.connect(self.dict_db_path)
        cursor = conn.cursor()
        
        # 创建wordIndex表，与createDictSqliteDbIndex.py中的结构一致
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS wordIndex(
                `id` INTEGER PRIMARY KEY,
                `word` VARCHAR(128),
                `offset` INTEGER,
                `length` INTEGER,
                CONSTRAINT `word` UNIQUE (`word`)
            )
        ''')
        
        # 创建索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_word ON wordIndex(word)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_offset ON wordIndex(offset)')
        
        conn.commit()
        conn.close()
        
        print(f"数据库表结构创建完成: {self.dict_db_path}")
        
    def format_word_content(self, word_data: Dict[str, Any]) -> str:
        """
        格式化词语内容，提取有价值的信息
        
        Args:
            word_data: 词语数据字典
            
        Returns:
            str: 格式化的HTML内容
        """
        word = word_data.get('word', '')
        pinyin = word_data.get('pinyin', '')
        explanation = word_data.get('explanation', '')
        abbr = word_data.get('abbr', '')
        
        # 构建HTML内容
        html_parts = []
        
        # 标题行
        if pinyin:
            html_parts.append(f'<h2>{word} [{pinyin}]</h2>')
        else:
            html_parts.append(f'<h2>{word}</h2>')
        
        # 缩写
        if abbr:
            html_parts.append(f'<p><strong>缩写:</strong> {abbr}</p>')
        
        # 解释
        if explanation:
            html_parts.append(f'<p><strong>解释:</strong> {explanation}</p>')
        
        # 其他字段
        fields = [
            ('source', '来源'),
            ('quote', '引用'),
            ('story', '典故'),
            ('similar', '近义词'),
            ('opposite', '反义词'),
            ('example', '例句'),
            ('usage', '用法'),
            ('notice', '注意')
        ]
        
        for field, label in fields:
            value = word_data.get(field)
            if value:
                if isinstance(value, (list, dict)):
                    value = json.dumps(value, ensure_ascii=False)
                html_parts.append(f'<p><strong>{label}:</strong> {value}</p>')
        
        # 如果没有内容，提供默认信息
        if len(html_parts) <= 1:
            html_parts.append('<p>暂无详细解释</p>')
        
        return '\n'.join(html_parts)
        
    def format_character_content(self, char_data: Dict[str, Any]) -> str:
        """
        格式化汉字内容，提取有价值的信息
        
        Args:
            char_data: 汉字数据字典
            
        Returns:
            str: 格式化的HTML内容
        """
        char = char_data.get('char', '')
        pinyin = char_data.get('pinyin', [])
        strokes = char_data.get('strokes', 0)
        radicals = char_data.get('radicals', '')
        frequency = char_data.get('frequency', 0)
        structure = char_data.get('structure', '')
        traditional = char_data.get('traditional', '')
        variant = char_data.get('variant', '')
        explanations = char_data.get('explanations', [])
        
        # 构建HTML内容
        html_parts = []
        
        # 标题行
        if pinyin:
            pinyin_str = ', '.join(pinyin) if isinstance(pinyin, list) else pinyin
            html_parts.append(f'<h2>{char} [{pinyin_str}]</h2>')
        else:
            html_parts.append(f'<h2>{char}</h2>')
        
        # 基本信息
        if strokes > 0:
            html_parts.append(f'<p><strong>笔画:</strong> {strokes}画</p>')
        
        if radicals:
            html_parts.append(f'<p><strong>部首:</strong> {radicals}</p>')
        
        if structure:
            html_parts.append(f'<p><strong>结构:</strong> {structure}</p>')
        
        if frequency > 0:
            html_parts.append(f'<p><strong>使用频率:</strong> {frequency}</p>')
        
        # 繁体字
        if traditional and traditional != char:
            html_parts.append(f'<p><strong>繁体:</strong> {traditional}</p>')
        
        # 异体字
        if variant and variant != char:
            html_parts.append(f'<p><strong>异体:</strong> {variant}</p>')
        
        # 详细解释
        if explanations and isinstance(explanations, list):
            html_parts.append('<p><strong>详细解释:</strong></p>')
            for i, explanation in enumerate(explanations, 1):
                if isinstance(explanation, dict):
                    # 处理字典格式的解释
                    meaning = explanation.get('meaning', '')
                    examples = explanation.get('examples', [])
                    
                    if meaning:
                        html_parts.append(f'<p>{i}. {meaning}</p>')
                    
                    if examples and isinstance(examples, list):
                        for example in examples:
                            html_parts.append(f'<p style="margin-left: 20px; color: #666;">例: {example}</p>')
                else:
                    # 处理字符串格式的解释
                    html_parts.append(f'<p>{i}. {explanation}</p>')
        
        # 如果没有内容，提供默认信息
        if len(html_parts) <= 1:
            html_parts.append('<p>暂无详细解释</p>')
        
        return '\n'.join(html_parts)
        
    def format_merged_content(self, merged_data: Dict[str, Any]) -> str:
        """
        格式化合并后的数据内容
        
        Args:
            merged_data: 合并后的数据字典
            
        Returns:
            str: 格式化的HTML内容
        """
        word = merged_data.get('word', '')
        char_pinyin = merged_data.get('char_pinyin', '')
        char_explanation = merged_data.get('char_explanation', '')
        char_radicals = merged_data.get('char_radicals', '')
        char_strokes = merged_data.get('char_strokes', 0)
        char_frequency = merged_data.get('char_frequency', 0)
        
        word_pinyin = merged_data.get('word_pinyin', '')
        word_abbr = merged_data.get('word_abbr', '')
        word_explanation = merged_data.get('word_explanation', '')
        word_source = merged_data.get('word_source', '')
        word_quote = merged_data.get('word_quote', '')
        word_story = merged_data.get('word_story', '')
        word_similar = merged_data.get('word_similar', '')
        word_opposite = merged_data.get('word_opposite', '')
        word_example = merged_data.get('word_example', '')
        word_usage = merged_data.get('word_usage', '')
        word_notice = merged_data.get('word_notice', '')
        word_type = merged_data.get('word_type', '')
        
        html_parts = []
        
        # 标题行
        if char_pinyin:
            html_parts.append(f'<h2>{word} [{char_pinyin}]</h2>')
        else:
            html_parts.append(f'<h2>{word}</h2>')
        
        # 汉字信息
        if char_radicals:
            html_parts.append(f'<p><strong>部首:</strong> {char_radicals}</p>')
        if char_strokes > 0:
            html_parts.append(f'<p><strong>笔画:</strong> {char_strokes}画</p>')
        if char_frequency > 0:
            html_parts.append(f'<p><strong>使用频率:</strong> {char_frequency}</p>')
        
        # 词语信息
        if word_pinyin:
            html_parts.append(f'<p><strong>拼音:</strong> {word_pinyin}</p>')
        if word_abbr:
            html_parts.append(f'<p><strong>缩写:</strong> {word_abbr}</p>')
        if word_explanation:
            html_parts.append(f'<p><strong>解释:</strong> {word_explanation}</p>')
        
        # 其他字段
        fields = [
            ('word_source', '来源'),
            ('word_quote', '引用'),
            ('word_story', '典故'),
            ('word_similar', '近义词'),
            ('word_opposite', '反义词'),
            ('word_example', '例句'),
            ('word_usage', '用法'),
            ('word_notice', '注意')
        ]
        
        for field, label in fields:
            value = merged_data.get(field)
            if value:
                if isinstance(value, (list, dict)):
                    value = json.dumps(value, ensure_ascii=False)
                html_parts.append(f'<p><strong>{label}:</strong> {value}</p>')
        
        # 如果没有内容，提供默认信息
        if len(html_parts) <= 1:
            html_parts.append('<p>暂无详细解释</p>')
        
        return '\n'.join(html_parts)
        
    def process_data(self):
        """处理数据并生成StarDict格式文件"""
        print("开始处理数据...")
        
        # 连接数据库
        source_conn = sqlite3.connect(self.source_db)
        source_cursor = source_conn.cursor()
        
        target_conn = sqlite3.connect(self.dict_db_path)
        target_cursor = target_conn.cursor()
        
        # 打开文件
        dict_file = open(self.dict_file_path, 'wb')
        idx_file = open(self.idx_file_path, 'wb')
        
        try:
            # 第一步：收集所有数据并合并
            print("第一步：收集和合并数据...")
            
            # 收集汉字数据
            source_cursor.execute('''
                SELECT char, pinyin, explanations, radicals, strokes, frequency
                FROM characters
                ORDER BY char
            ''')
            characters = source_cursor.fetchall()
            print(f"找到 {len(characters)} 个汉字")
            
            # 收集词语数据
            source_cursor.execute('''
                SELECT word, pinyin, abbr, explanation, source, quote, story,
                       similar, opposite, example, usage, notice, word_type
                FROM words
                ORDER BY word
            ''')
            words = source_cursor.fetchall()
            print(f"找到 {len(words)} 个词语")
            
            # 合并数据：使用字典来避免重复
            merged_data = {}
            
            # 处理汉字数据
            for char_data in characters:
                char = char_data[0]
                char_dict = {
                    'type': 'character',
                    'char': char,
                    'pinyin': char_data[1],
                    'explanation': char_data[2],
                    'radicals': char_data[3],
                    'strokes': char_data[4],
                    'frequency': char_data[5]
                }
                merged_data[char] = char_dict
            
            # 处理词语数据，如果与汉字重复则合并
            for word_data in words:
                word = word_data[0]
                word_dict = {
                    'type': 'word',
                    'word': word,
                    'pinyin': word_data[1],
                    'abbr': word_data[2],
                    'explanation': word_data[3],
                    'source': word_data[4],
                    'quote': word_data[5],
                    'story': word_data[6],
                    'similar': word_data[7],
                    'opposite': word_data[8],
                    'example': word_data[9],
                    'usage': word_data[10],
                    'notice': word_data[11],
                    'word_type': word_data[12]
                }
                
                if word in merged_data:
                    # 如果词语与汉字重复，合并数据
                    existing = merged_data[word]
                    if existing['type'] == 'character':
                        # 将汉字数据转换为合并数据
                        merged_dict = {
                            'type': 'merged',
                            'word': word,
                            'char_pinyin': existing['pinyin'],
                            'char_explanation': existing['explanation'],
                            'char_radicals': existing['radicals'],
                            'char_strokes': existing['strokes'],
                            'char_frequency': existing['frequency'],
                            'word_pinyin': word_dict['pinyin'],
                            'word_abbr': word_dict['abbr'],
                            'word_explanation': word_dict['explanation'],
                            'word_source': word_dict['source'],
                            'word_quote': word_dict['quote'],
                            'word_story': word_dict['story'],
                            'word_similar': word_dict['similar'],
                            'word_opposite': word_dict['opposite'],
                            'word_example': word_dict['example'],
                            'word_usage': word_dict['usage'],
                            'word_notice': word_dict['notice'],
                            'word_type': word_dict['word_type']
                        }
                        merged_data[word] = merged_dict
                        print(f"合并数据: {word} (汉字+词语)")
                else:
                    # 如果词语不重复，直接添加
                    merged_data[word] = word_dict
            
            print(f"合并后共有 {len(merged_data)} 个条目")
            
            # 第二步：按顺序处理合并后的数据
            print("第二步：处理合并后的数据...")
            
            current_offset = 0
            total_processed = 0
            
            # 按字符顺序排序
            sorted_items = sorted(merged_data.items(), key=lambda x: x[0])
            
            for word, data in sorted_items:
                # 根据数据类型格式化内容
                if data['type'] == 'character':
                    content = self.format_character_content(data)
                elif data['type'] == 'word':
                    content = self.format_word_content(data)
                elif data['type'] == 'merged':
                    content = self.format_merged_content(data)
                else:
                    continue
                
                content_bytes = content.encode('utf-8')
                content_length = len(content_bytes)
                
                # 调试信息：对于"札记"这个词
                if word == '札记':
                    print(f"🔍 调试札记:")
                    print(f"   数据类型: {data['type']}")
                    print(f"   当前偏移量: {current_offset}")
                    print(f"   内容长度: {content_length}")
                    print(f"   格式化内容: {content[:100]}...")
                
                # 写入dict文件
                dict_file.write(content_bytes)
                
                # 写入idx文件：词语 + null终止符 + 偏移量(4字节) + 长度(4字节)
                word_bytes = word.encode('utf-8')
                idx_file.write(word_bytes)
                idx_file.write(b'\0')  # null终止符
                idx_file.write(struct.pack('>I', current_offset))  # 偏移量，大端序
                idx_file.write(struct.pack('>I', content_length))  # 长度，大端序
                
                # 插入数据库（统一转小写）
                target_cursor.execute('''
                    INSERT INTO wordIndex(word, offset, length)
                    VALUES (?, ?, ?)
                ''', (word.lower(), current_offset, content_length))
                
                # 调试信息：对于"札记"这个词
                if word == '札记':
                    print(f"   数据库插入成功: {word.lower()}, {current_offset}, {content_length}")
                
                # 更新偏移量
                current_offset += content_length
                total_processed += 1
                
                # 显示进度
                if total_processed % 1000 == 0:
                    print(f"处理进度: {total_processed}/{len(sorted_items)} ({total_processed/len(sorted_items)*100:.1f}%)")
            
            print(f"数据处理完成，共处理 {total_processed} 个条目")
            
            # 提交数据库更改
            target_conn.commit()
            
        finally:
            dict_file.close()
            idx_file.close()
            source_conn.close()
            target_conn.close()
        
    def create_ifo_file(self):
        """创建StarDict格式的.ifo信息文件"""
        print("创建.ifo信息文件...")
        
        # 获取文件信息
        dict_size = self.dict_file_path.stat().st_size
        idx_size = self.idx_file_path.stat().st_size
        
        # 计算词语数量（每个条目：词语 + null + 4字节偏移量 + 4字节长度）
        # 需要从idx文件计算实际条目数
        conn = sqlite3.connect(self.dict_db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM wordIndex')
        word_count = cursor.fetchone()[0]
        conn.close()
        
        # 创建.ifo文件内容
        ifo_content = f"""StarDict's dict ifo file
version=2.4.2
bookname=Chinese Dictionary
wordcount={word_count}
idxfilesize={idx_size}
sametypesequence=h
"""
        
        with open(self.ifo_file_path, 'w', encoding='utf-8') as f:
            f.write(ifo_content)
        
        print(f".ifo文件创建完成: {self.ifo_file_path}")
        
    def build(self):
        """执行完整的构建流程"""
        print("开始构建StarDict兼容的数据库...")
        
        try:
            # 1. 创建数据库表结构
            self.create_database_schema()
            
            # 2. 处理数据并生成文件
            self.process_data()
            
            # 3. 创建.ifo文件
            self.create_ifo_file()
            
            print("\n🎉 构建完成！")
            print(f"📁 输出目录: {self.output_dir}")
            print(f"🗄️  数据库: {self.dict_db_path}")
            print(f"📖 字典文件: {self.dict_file_path}")
            print(f"🔍 索引文件: {self.idx_file_path}")
            print(f"ℹ️  信息文件: {self.ifo_file_path}")
            
            # 显示文件大小
            print(f"\n📊 文件大小:")
            print(f"   .db: {self.dict_db_path.stat().st_size / 1024 / 1024:.2f} MB")
            print(f"   .dict: {self.dict_file_path.stat().st_size / 1024 / 1024:.2f} MB")
            print(f"   .idx: {self.idx_file_path.stat().st_size / 1024:.2f} KB")
            print(f"   .ifo: {self.ifo_file_path.stat().st_size} bytes")
            
        except Exception as e:
            print(f"❌ 构建失败: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        return True


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='创建与现有app兼容的StarDict格式数据库')
    parser.add_argument('--db', required=True, help='源数据库路径（chinese_dictionary.db）')
    parser.add_argument('--output', required=True, help='输出目录路径')
    
    args = parser.parse_args()
    
    # 检查源数据库是否存在
    if not Path(args.db).exists():
        print(f"❌ 源数据库不存在: {args.db}")
        sys.exit(1)
    
    # 创建构建器并执行构建
    builder = StarDictCompatibleBuilder(args.db, args.output)
    success = builder.build()
    
    if success:
        print("\n✅ 现在您可以将生成的文件用于现有的app了！")
        print("   数据库文件可以直接替换现有的数据库文件")
        print("   .dict, .idx, .ifo文件可以用于StarDict兼容的字典软件")
    else:
        print("\n❌ 构建失败，请检查错误信息")
        sys.exit(1)


if __name__ == '__main__':
    main()
