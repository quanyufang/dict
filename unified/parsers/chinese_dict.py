#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
汉语拼音词典解析器 (chinese_dict)

格式特点（基于样例分析）：
1. HTML格式：使用 <h2>, <p>, <strong> 标签
2. 词头和拼音：<h2>词头 [[拼音]]</h2> 或 <h2>词头 [拼音]</h2>
   - 单字词：拼音用双重方括号 [[\"yī\"]]，可能是JSON数组格式
   - 多字词：拼音用单方括号 [xué xí]
3. 字段（都在 <p><strong>字段名:</strong> 值</p> 中）：
   - 笔画：X画
   - 部首：X
   - 缩写：xx（拼音缩写）
   - 解释：文本内容
   - 近义词：JSON数组格式 ["词1", "词2"]
   - 反义词：JSON数组格式 ["词1", "词2"]
   - 来源：JSON对象格式 {"text": "...", "book": "..."}
   - 典故：JSON数组格式 ["..."]
   - 例句：JSON对象格式 {"text": "...", "book": "..."}
   - 用法：文本内容

样例：
<h2>一 [[\"yī\"]]</h2>
<p><strong>笔画:</strong> 1画</p>
<p><strong>部首:</strong> 一</p>

<h2>学习 [xué xí]</h2>
<p><strong>缩写:</strong> xx</p>
<p><strong>解释:</strong> 个体由经验或练习引起的...</p>
<p><strong>近义词:</strong> [\"劳动\", \"劳作\"]</p>
<p><strong>反义词:</strong> [\"休息\"]</p>
"""

import re
import json
from typing import Optional, List
from html.parser import HTMLParser
from ..models.entry import (
    DictionaryEntry, Pronunciation, Sense, Example,
    PartOfSpeech, RelatedPhrase
)
from .base import BaseParser


class ChineseDictHTMLParser(HTMLParser):
    """HTML内容解析器，提取结构化数据"""
    
    def __init__(self):
        super().__init__()
        self.headword = None
        self.pinyins = []
        self.strokes = None
        self.radical = None
        self.pinyin_abbr = None
        self.definition = None
        self.synonyms = []
        self.antonyms = []
        self.source = None  # {"text": "...", "book": "..."}
        self.story = None  # 典故（数组）
        self.examples = []  # [{"text": "...", "book": "..."}]
        self.usage = None
        
        self.current_tag = None
        self.current_attr = None
        self.current_data = ""
        self.in_strong = False
        self.in_p = False
        self.current_field = None
        self.strong_before_data = ""
    
    def handle_starttag(self, tag, attrs):
        self.current_tag = tag
        if tag == 'h2':
            self.current_data = ""
        elif tag == 'p':
            self.current_data = ""
            self.current_field = None
            self.in_p = True
        elif tag == 'strong':
            self.in_strong = True
            # 保存strong标签之前的数据（作为字段值的前缀，通常为空）
            self.strong_before_data = self.current_data
            self.current_data = ""
    
    def handle_endtag(self, tag):
        if tag == 'h2':
            # 解析词头和拼音
            content = self.current_data.strip()
            self._parse_headword_and_pinyin(content)
            self.current_data = ""
        elif tag == 'strong':
            self.in_strong = False
            # 提取字段名
            field_name = self.current_data.strip().rstrip(':').rstrip('：')
            self.current_field = field_name
            # 恢复strong标签之前的数据，准备接收字段值
            self.current_data = self.strong_before_data
        elif tag == 'p':
            # 解析字段值
            if self.current_field:
                value = self.current_data.strip()
                self._parse_field(self.current_field, value)
            self.current_data = ""
            self.current_field = None
            self.in_p = False
        if tag != 'strong':  # strong标签结束后，current_tag仍然是p
            if tag == 'p':
                self.current_tag = None
            elif tag == 'h2':
                self.current_tag = None
    
    def handle_data(self, data):
        # 在h2、p标签内，或者在p标签内的strong标签后，都收集数据
        if self.current_tag in ('h2', 'p') or (self.in_p and not self.in_strong):
            self.current_data += data
        elif self.current_tag == 'strong':
            self.current_data += data
    
    def _parse_headword_and_pinyin(self, content: str):
        """解析词头和拼音"""
        # 匹配格式：词头 [[\"拼音\"]] 或 词头 [拼音]
        # 单字词：一 [[\"yī\"]]
        # 多字词：学习 [xué xí]
        
        # 尝试匹配双重方括号（JSON数组格式，可能是单个或多个拼音）
        # 格式：词头 [["拼音"]] 或 词头 [["拼音1", "拼音2", ...]]
        match1 = re.match(r'^(.+?)\s*\[\[(.+?)\]\]$', content)
        if match1:
            self.headword = match1.group(1).strip()
            pinyin_part = match1.group(2).strip()
            # 尝试解析JSON数组
            try:
                self.pinyins = json.loads('[' + pinyin_part + ']')
            except:
                # 如果JSON解析失败，尝试简单解析
                # 移除引号，按逗号分割
                pinyin_part = pinyin_part.strip('"').strip("'")
                if ',' in pinyin_part:
                    self.pinyins = [p.strip().strip('"').strip("'") for p in pinyin_part.split(',')]
                else:
                    self.pinyins = [pinyin_part]
            return
        
        # 匹配单个方括号（可能有多个拼音，用逗号分隔）
        match2 = re.match(r'^(.+?)\s*\["(.+?)"\]$', content)
        if match2:
            self.headword = match2.group(1).strip()
            # 尝试解析JSON数组
            pinyin_part = match2.group(2)
            try:
                # 如果包含逗号，可能是JSON数组
                if ',' in pinyin_part:
                    pinyin_json = '["' + pinyin_part + '"]'
                    self.pinyins = json.loads(pinyin_json.replace('"', '"'))
                else:
                    self.pinyins = [pinyin_part.strip('"')]
            except:
                self.pinyins = [pinyin_part.strip('"')]
            return
        
        # 匹配普通方括号格式：词头 [拼音]
        match3 = re.match(r'^(.+?)\s*\[(.+?)\]$', content)
        if match3:
            self.headword = match3.group(1).strip()
            pinyin_text = match3.group(2).strip()
            # 多个拼音用空格分隔
            self.pinyins = [p.strip() for p in pinyin_text.split() if p.strip()]
            return
        
        # 如果没有匹配到，整个内容就是词头
        self.headword = content.strip()
    
    def _parse_field(self, field_name: str, value: str):
        """解析字段值"""
        field_name = field_name.strip()
        value = value.strip()
        
        if not value:
            return
        
        if field_name == '笔画':
            # 提取数字
            match = re.search(r'(\d+)', value)
            if match:
                self.strokes = int(match.group(1))
        elif field_name == '部首':
            self.radical = value
        elif field_name == '缩写':
            self.pinyin_abbr = value
        elif field_name == '解释':
            self.definition = value
        elif field_name == '近义词':
            self.synonyms = self._parse_json_array(value)
        elif field_name == '反义词':
            self.antonyms = self._parse_json_array(value)
        elif field_name == '来源':
            self.source = self._parse_json_object(value)
        elif field_name == '典故':
            self.story = self._parse_json_array(value)
        elif field_name == '例句':
            example_obj = self._parse_json_object(value)
            if example_obj:
                self.examples.append(example_obj)
        elif field_name == '用法':
            self.usage = value
    
    def _parse_json_array(self, value: str) -> List:
        """解析JSON数组"""
        try:
            return json.loads(value)
        except:
            # 如果解析失败，尝试手动解析简单格式
            # 移除方括号，按逗号分割
            value = value.strip('[]')
            items = []
            for item in value.split(','):
                item = item.strip().strip('"').strip("'")
                if item:
                    items.append(item)
            return items
    
    def _parse_json_object(self, value: str) -> Optional[dict]:
        """解析JSON对象"""
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            # JSON解析失败，尝试修复常见的格式问题
            # 问题：字符串值中包含未转义的引号（如 "text": "... "一盂酒" ..."）
            try:
                # 尝试修复：转义text字段值中的未转义引号
                def escape_text_quotes(match):
                    prefix = match.group(1)  # "text": "
                    content = match.group(2)  # 文本内容
                    suffix = match.group(3)  # 结尾的 " 或 ", 或 "}
                    # 转义内容中的引号（但跳过已经是转义的 \"）
                    content_escaped = re.sub(r'(?<!\\)"', r'\\"', content)
                    return prefix + content_escaped + suffix
                
                # 匹配 "text": "..." 模式（支持多行）
                pattern = r'("text":\s*")(.*?)("(?:,|\}))'
                fixed_value = re.sub(pattern, escape_text_quotes, value, flags=re.DOTALL)
                return json.loads(fixed_value)
            except:
                # 修复失败，返回None
                return None
        except:
            return None


class ChineseDictParser(BaseParser):
    """汉语拼音词典解析器"""
    
    @property
    def source_id(self) -> str:
        return "chinese_dict"
    
    @property
    def name(self) -> str:
        return "汉语拼音词典"
    
    @property
    def index_language(self) -> str:
        return "zh"
    
    @property
    def explanation_language(self) -> str:
        return "zh"
    
    def parse(self, word: str, raw_content: str) -> Optional[DictionaryEntry]:
        """解析汉语拼音词典条目"""
        if not raw_content or not raw_content.strip():
            return None
        
        # 使用HTML解析器提取数据
        html_parser = ChineseDictHTMLParser()
        try:
            html_parser.feed(raw_content)
        except Exception as e:
            # HTML解析失败，尝试简单文本解析
            return self._parse_simple(word, raw_content)
        
        # 构建字典条目
        entry = DictionaryEntry(
            headword=word,
            source_id=self.source_id,
            raw_content=raw_content,
        )
        
        # 拼音
        if html_parser.pinyins:
            for pinyin in html_parser.pinyins:
                entry.pronunciations.append(Pronunciation(
                    ipa=pinyin,
                    region="general"
                ))
        
        # 笔画和部首
        if html_parser.strokes:
            entry.strokes = html_parser.strokes
        if html_parser.radical:
            entry.radical = html_parser.radical
        if html_parser.pinyin_abbr:
            entry.pinyin_abbr = html_parser.pinyin_abbr
        
        # 词源和典故
        if html_parser.source:
            source_text = html_parser.source.get('text', '')
            if source_text:
                entry.etymology = source_text
        if html_parser.story:
            # 典故可能是数组，合并为文本
            if isinstance(html_parser.story, list):
                entry.story = ' '.join(html_parser.story)
            else:
                entry.story = str(html_parser.story)
        
        # 构建senses（释义）
        # 如果有解释，创建sense
        if html_parser.definition:
            sense = Sense(
                definition=html_parser.definition,
                definition_lang="zh",
                pos=None,  # 汉语拼音词典通常不标注词性
                sense_number="1"
            )
            
            # 添加例句
            if html_parser.examples:
                for ex in html_parser.examples:
                    if isinstance(ex, dict):
                        example_text = ex.get('text', '')
                        if example_text:
                            example = Example(
                                text=example_text,
                                translation=None,
                                source=ex.get('book')
                            )
                            sense.examples.append(example)
            
            # 添加同义词和反义词
            if html_parser.synonyms:
                sense.synonyms = html_parser.synonyms
            if html_parser.antonyms:
                sense.antonyms = html_parser.antonyms
            
            # 用法作为grammar_note
            if html_parser.usage:
                sense.grammar_note = html_parser.usage
            
            entry.senses.append(sense)
        elif html_parser.source:
            # 如果只有来源字段（没有解释），将来源的text作为定义
            source_text = html_parser.source.get('text', '')
            if source_text:
                sense = Sense(
                    definition=source_text,
                    definition_lang="zh",
                    pos=None,
                    sense_number="1"
                )
                entry.senses.append(sense)
        elif html_parser.strokes or html_parser.radical:
            # 如果有笔画或部首，创建一个空的sense
            sense = Sense(
                definition="",  # 单字词可能只有笔画部首信息
                definition_lang="zh",
                pos=None,
                sense_number="1"
            )
            entry.senses.append(sense)
        elif html_parser.synonyms or html_parser.antonyms or html_parser.pinyin_abbr:
            # 如果只有近义词、反义词或缩写等元数据，也创建一个sense（即使定义为空）
            # 这样可以保留这些有用信息，避免解析失败
            sense = Sense(
                definition="",  # 没有解释，定义为空
                definition_lang="zh",
                pos=None,
                sense_number="1"
            )
            # 添加同义词和反义词
            if html_parser.synonyms:
                sense.synonyms = html_parser.synonyms
            if html_parser.antonyms:
                sense.antonyms = html_parser.antonyms
            entry.senses.append(sense)
        
        # 必须至少有一个sense
        if not entry.senses:
            return None
        
        return entry
    
    def _parse_simple(self, word: str, raw_content: str) -> Optional[DictionaryEntry]:
        """简单文本解析（当HTML解析失败时）"""
        # 尝试用正则表达式提取基本信息
        entry = DictionaryEntry(
            headword=word,
            source_id=self.source_id,
            raw_content=raw_content,
        )
        
        # 提取拼音
        pinyin_match = re.search(r'\[(.*?)\]', raw_content)
        if pinyin_match:
            pinyin_text = pinyin_match.group(1).strip()
            # 尝试解析JSON数组格式
            try:
                pinyins = json.loads('[' + pinyin_text + ']')
            except:
                pinyins = [p.strip() for p in pinyin_text.split() if p.strip()]
            
            for pinyin in pinyins:
                entry.pronunciations.append(Pronunciation(
                    ipa=pinyin.strip('"').strip("'"),
                    region="general"
                ))
        
        # 提取笔画
        strokes_match = re.search(r'笔画[：:]\s*(\d+)', raw_content)
        if strokes_match:
            entry.strokes = int(strokes_match.group(1))
        
        # 提取部首
        radical_match = re.search(r'部首[：:]\s*([^\s<]+)', raw_content)
        if radical_match:
            entry.radical = radical_match.group(1)
        
        # 提取解释
        definition_match = re.search(r'解释[：:]\s*([^<]+)', raw_content)
        if definition_match:
            definition = definition_match.group(1).strip()
            sense = Sense(
                definition=definition,
                definition_lang="zh",
                pos=None,
                sense_number="1"
            )
            entry.senses.append(sense)
        
        if not entry.senses:
            # 如果还是没有sense，至少创建一个空的
            sense = Sense(
                definition="",
                definition_lang="zh",
                pos=None,
                sense_number="1"
            )
            entry.senses.append(sense)
        
        return entry

