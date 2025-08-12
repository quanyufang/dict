#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
StarDict格式生成器

将构建好的汉语拼音辞典数据库转换为StarDict格式文件
支持多种查询方式和优化索引
"""

import os
import sqlite3
import json
import struct
import logging
from pathlib import Path
from typing import List, Tuple, Dict, Optional
import argparse


class StarDictGenerator:
    """StarDict格式生成器"""
    
    def __init__(self, db_path: str, output_dir: str):
        """
        初始化StarDict生成器
        
        Args:
            db_path: SQLite数据库路径
            output_dir: 输出目录路径
        """
        self.db_path = Path(db_path)
        self.output_dir = Path(output_dir)
        
        # 确保输出目录存在
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 设置日志
        self.setup_logging()
        
        # 验证数据库
        self.validate_database()
        
    def setup_logging(self):
        """设置日志配置"""
        log_file = self.output_dir / "stardict_generator.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def validate_database(self):
        """验证数据库文件"""
        if not self.db_path.exists():
            raise FileNotFoundError(f"数据库文件不存在: {self.db_path}")
            
        # 测试数据库连接
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 检查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        required_tables = ['characters', 'words']
        missing_tables = [table for table in required_tables if table not in tables]
        
        if missing_tables:
            raise ValueError(f"数据库缺少必要的表: {missing_tables}")
            
        conn.close()
        self.logger.info("数据库验证通过")
        
    def generate_character_stardict(self):
        """生成汉字StarDict文件"""
        self.logger.info("生成汉字StarDict文件...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 查询所有汉字数据
        cursor.execute('''
            SELECT char, pinyin, strokes, radicals, frequency, structure, 
                   traditional, variant, explanations
            FROM characters 
            ORDER BY frequency, strokes, char
        ''')
        
        characters = cursor.fetchall()
        conn.close()
        
        if not characters:
            self.logger.warning("没有找到汉字数据")
            return
            
        # 生成StarDict文件
        dict_name = "chinese-characters"
        self._generate_stardict_files(
            dict_name=dict_name,
            entries=characters,
            entry_formatter=self._format_character_entry,
            bookname="汉语拼音辞典 - 汉字",
            description="收录常用汉字、拼音、笔画、部首、结构等信息"
        )
        
        self.logger.info(f"汉字StarDict文件生成完成: {len(characters)} 个汉字")
        
    def generate_word_stardict(self):
        """生成词语StarDict文件"""
        self.logger.info("生成词语StarDict文件...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 查询所有词语数据
        cursor.execute('''
            SELECT word, pinyin, abbr, explanation, source, quote, story,
                   similar, opposite, example, usage, notice, word_type
            FROM words 
            ORDER BY word_type, word
        ''')
        
        words = cursor.fetchall()
        conn.close()
        
        if not words:
            self.logger.warning("没有找到词语数据")
            return
            
        # 生成StarDict文件
        dict_name = "chinese-words"
        self._generate_stardict_files(
            dict_name=dict_name,
            entries=words,
            entry_formatter=self._format_word_entry,
            bookname="汉语拼音辞典 - 词语",
            description="收录常用词语、成语、拼音、解释、例句等信息"
        )
        
        self.logger.info(f"词语StarDict文件生成完成: {len(words)} 个词语")
        
    def generate_combined_stardict(self):
        """生成合并的StarDict文件（汉字+词语）"""
        self.logger.info("生成合并的StarDict文件...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 查询汉字数据
        cursor.execute('''
            SELECT char, pinyin, strokes, radicals, frequency, structure, 
                   traditional, variant, explanations
            FROM characters 
            ORDER BY frequency, strokes, char
        ''')
        characters = cursor.fetchall()
        
        # 查询词语数据
        cursor.execute('''
            SELECT word, pinyin, abbr, explanation, source, quote, story,
                   similar, opposite, example, usage, notice, word_type
            FROM words 
            ORDER BY word_type, word
        ''')
        words = cursor.fetchall()
        
        conn.close()
        
        if not characters and not words:
            self.logger.warning("没有找到任何数据")
            return
            
        # 合并数据
        combined_entries = []
        
        # 添加汉字条目
        for char_data in characters:
            combined_entries.append(('char', char_data))
            
        # 添加词语条目
        for word_data in words:
            combined_entries.append(('word', word_data))
            
        # 按条目名称排序
        combined_entries.sort(key=lambda x: x[1][0] if x[0] == 'char' else x[1][0])
        
        # 生成StarDict文件
        dict_name = "chinese-dictionary"
        self._generate_stardict_files(
            dict_name=dict_name,
            entries=combined_entries,
            entry_formatter=self._format_combined_entry,
            bookname="汉语拼音辞典 - 完整版",
            description="收录汉字、词语、成语等完整信息，支持多种查询方式"
        )
        
        self.logger.info(f"合并StarDict文件生成完成: {len(combined_entries)} 个条目")
        
    def _format_character_entry(self, char_data) -> str:
        """格式化汉字条目"""
        char, pinyin, strokes, radicals, frequency, structure, traditional, variant, explanations = char_data
        
        # 解析拼音
        try:
            pinyin_list = json.loads(pinyin) if pinyin else []
        except:
            pinyin_list = [pinyin] if pinyin else []
            
        # 解析解释
        try:
            explanations_data = json.loads(explanations) if explanations else []
        except:
            explanations_data = []
            
        # 构建HTML格式的内容
        content = f"""
<div class="character-entry">
    <h1 class="char">{char}</h1>
    
    <div class="basic-info">
        <p><strong>拼音:</strong> {', '.join(pinyin_list) if pinyin_list else '无'}</p>
        <p><strong>笔画:</strong> {strokes}</p>
        <p><strong>部首:</strong> {radicals}</p>
        <p><strong>结构:</strong> {structure}</p>
        <p><strong>频率:</strong> {self._get_frequency_name(frequency)}</p>
    </div>
    
    {f'<p><strong>繁体:</strong> {traditional}</p>' if traditional else ''}
    {f'<p><strong>异体:</strong> {variant}</p>' if variant else ''}
    
    {self._format_explanations(explanations_data) if explanations_data else ''}
</div>
        """
        
        return content.strip()
        
    def _format_word_entry(self, word_data) -> str:
        """格式化词语条目"""
        word, pinyin, abbr, explanation, source, quote, story, similar, opposite, example, usage, notice, word_type = word_data
        
        # 解析JSON字段
        source_data = json.loads(source) if source else None
        quote_data = json.loads(quote) if quote else None
        story_data = json.loads(story) if story else []
        similar_data = json.loads(similar) if similar else []
        opposite_data = json.loads(opposite) if opposite else []
        
        # 构建HTML格式的内容
        content = f"""
<div class="word-entry">
    <h1 class="word">{word}</h1>
    <p class="pinyin">{pinyin}</p>
    <p class="abbr">拼音缩写: {abbr}</p>
    <p class="type">类型: {self._get_word_type_name(word_type)}</p>
    
    <div class="explanation">
        <h3>解释</h3>
        <p>{explanation}</p>
    </div>
    
    {f'''
    <div class="source">
        <h3>出处</h3>
        <p>{source_data.get('text', '')}</p>
        <p class="book">——《{source_data.get('book', '')}》</p>
    </div>
    ''' if source_data else ''}
    
    {f'''
    <div class="quote">
        <h3>引用</h3>
        <p>{quote_data.get('text', '')}</p>
        <p class="book">——《{quote_data.get('book', '')}》</p>
    </div>
    ''' if quote_data else ''}
    
    {f'''
    <div class="story">
        <h3>典故</h3>
        {''.join([f'<p>{story_item}</p>' for story_item in story_data])}
    </div>
    ''' if story_data else ''}
    
    {f'''
    <div class="similar">
        <h3>近义词</h3>
        <p>{', '.join(similar_data)}</p>
    </div>
    ''' if similar_data else ''}
    
    {f'''
    <div class="opposite">
        <h3>反义词</h3>
        <p>{', '.join(opposite_data)}</p>
    </div>
    ''' if opposite_data else ''}
    
    {f'''
    <div class="example">
        <h3>例句</h3>
        <p>{example}</p>
    </div>
    ''' if example else ''}
    
    {f'''
    <div class="usage">
        <h3>用法</h3>
        <p>{usage}</p>
    </div>
    ''' if usage else ''}
    
    {f'''
    <div class="notice">
        <h3>注意事项</h3>
        <p>{notice}</p>
    </div>
    ''' if notice else ''}
</div>
        """
        
        return content.strip()
        
    def _format_combined_entry(self, entry_data) -> str:
        """格式化合并条目"""
        entry_type, data = entry_data
        
        if entry_type == 'char':
            return self._format_character_entry(data)
        else:
            return self._format_word_entry(data)
            
    def _get_frequency_name(self, frequency: int) -> str:
        """获取频率名称"""
        freq_names = {
            0: "最常用",
            1: "较常用", 
            2: "次常用",
            3: "二级字",
            4: "三级字",
            5: "生僻字"
        }
        return freq_names.get(frequency, f"频率{frequency}")
        
    def _get_word_type_name(self, word_type: str) -> str:
        """获取词语类型名称"""
        type_names = {
            'idiom': '成语',
            'word': '词语'
        }
        return type_names.get(word_type, word_type)
        
    def _format_explanations(self, explanations: List[Dict]) -> str:
        """格式化解释信息"""
        if not explanations:
            return ""
            
        content = '<div class="explanations"><h3>详细解释</h3>'
        
        for i, pronunciation in enumerate(explanations):
            pinyin = pronunciation.get('pinyin', '')
            explanations_list = pronunciation.get('explanations', [])
            
            content += f'<div class="pronunciation"><h4>读音: {pinyin}</h4>'
            
            for j, explanation in enumerate(explanations_list):
                content += f'<div class="explanation-item"><p>{explanation.get("content", "")}</p>'
                
                # 添加例句
                if 'example' in explanation:
                    content += f'<p class="example">例句: {explanation["example"]}</p>'
                    
                # 添加文献引用
                if 'detail' in explanation:
                    content += '<div class="references">'
                    for detail in explanation['detail']:
                        content += f'<p class="reference">"{detail.get("text", "")}" ——《{detail.get("book", "")}》</p>'
                    content += '</div>'
                    
                content += '</div>'
                
            content += '</div>'
            
        content += '</div>'
        return content
        
    def _generate_stardict_files(self, dict_name: str, entries: List, 
                                entry_formatter, bookname: str, description: str):
        """生成StarDict格式文件"""
        # 文件路径
        ifo_file = self.output_dir / f"{dict_name}.ifo"
        idx_file = self.output_dir / f"{dict_name}.idx"
        dict_file = self.output_dir / f"{dict_name}.dict"
        
        # 生成.ifo文件
        self._generate_ifo_file(ifo_file, dict_name, bookname, description, len(entries))
        
        # 生成.idx和.dict文件
        self._generate_idx_dict_files(idx_file, dict_file, entries, entry_formatter)
        
        self.logger.info(f"StarDict文件生成完成: {dict_name}")
        
    def _generate_ifo_file(self, ifo_file: Path, dict_name: str, bookname: str, 
                           description: str, wordcount: int):
        """生成.ifo文件"""
        ifo_content = f"""StarDict's dict ifo file
version=2.4.2
bookname={bookname}
wordcount={wordcount}
idxfilesize=0
sametypesequence=h
description={description}
date={self._get_current_date()}
author=汉语拼音辞典构建程序
website=https://github.com/chinese-dictionary
        """
        
        with open(ifo_file, 'w', encoding='utf-8') as f:
            f.write(ifo_content)
            
    def _generate_idx_dict_files(self, idx_file: Path, dict_file: Path, 
                                entries: List, entry_formatter):
        """生成.idx和.dict文件"""
        with open(idx_file, 'wb') as idx_f, open(dict_file, 'wb') as dict_f:
            offset = 0
            
            for entry in entries:
                # 获取条目名称
                if isinstance(entry, tuple):
                    entry_name = entry[1][0]  # (type, data) -> data[0]
                else:
                    entry_name = entry[0]
                    
                # 格式化条目内容
                content = entry_formatter(entry)
                content_bytes = content.encode('utf-8')
                
                # 写入.idx文件：条目名 + 偏移量 + 长度
                idx_f.write(entry_name.encode('utf-8'))
                idx_f.write(b'\0')  # null结尾
                idx_f.write(struct.pack('>I', offset))  # 4字节偏移量（大端序）
                idx_f.write(struct.pack('>I', len(content_bytes)))  # 4字节长度（大端序）
                
                # 写入.dict文件
                dict_f.write(content_bytes)
                
                offset += len(content_bytes)
                
        # 更新.ifo文件中的idxfilesize
        idx_size = idx_file.stat().st_size
        ifo_file = self.output_dir / f"{dict_file.stem}.ifo"
        
        with open(ifo_file, 'r', encoding='utf-8') as f:
            ifo_content = f.read()
            
        ifo_content = ifo_content.replace('idxfilesize=0', f'idxfilesize={idx_size}')
        
        with open(ifo_file, 'w', encoding='utf-8') as f:
            f.write(ifo_content)
            
    def _get_current_date(self) -> str:
        """获取当前日期"""
        from datetime import datetime
        return datetime.now().strftime('%Y.%m.%d')
        
    def generate_all(self):
        """生成所有StarDict文件"""
        try:
            self.logger.info("开始生成StarDict文件...")
            
            # 生成汉字StarDict
            self.generate_character_stardict()
            
            # 生成词语StarDict
            self.generate_word_stardict()
            
            # 生成合并StarDict
            self.generate_combined_stardict()
            
            self.logger.info("所有StarDict文件生成完成！")
            
        except Exception as e:
            self.logger.error(f"生成StarDict文件失败: {e}")
            raise


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='StarDict格式生成器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python stardict_generator.py --db chinese_dictionary.db --output output
  
参数说明:
  --db: SQLite数据库文件路径
  --output: 输出目录路径
        """
    )
    
    parser.add_argument('--db', required=True, help='SQLite数据库文件路径')
    parser.add_argument('--output', required=True, help='输出目录路径')
    
    args = parser.parse_args()
    
    try:
        # 创建StarDict生成器并执行
        generator = StarDictGenerator(args.db, args.output)
        generator.generate_all()
        print(f"\n🎉 StarDict文件生成完成！")
        print(f"输出目录: {args.output}")
        
    except Exception as e:
        print(f"\n❌ StarDict文件生成失败: {e}")
        import sys
        sys.exit(1)


if __name__ == '__main__':
    main()
