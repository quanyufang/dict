#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GCIDE (GNU Collaborative International Dictionary of English) 解析器

格式特点（基于样例分析）：
1. 词头标记: \\Word\\
2. 词性: a., n., v. t., v. i., adv. 等
3. 词源信息: [AS. ...] [1913 Webster]（可能跨多行）
4. 引用来源: --Shak. (Shakespeare), --Gen. i. 31. 等
5. 词根引用: {Better}, {Best}, {Gather} (花括号)
6. 数字释义: 1. ..., 2. ..., 等（4个空格缩进）
7. 例句: 大量缩进（12+空格），后面跟引用标记 --Author.
8. 标记: [1913 Webster] 出现在释义和例句之间

样例：
Good \Good\, a. [Compar. {Better}; superl. {Best}. ...]
   [AS. G[=o]d, akin to D. goed, ...] [1913 Webster]
   1. Possessing desirable qualities; ...
      [1913 Webster]
            And God saw everything... --Gen. i. 31.
      [1913 Webster]
"""

import re
from typing import Optional, List, Tuple, Dict
from ..models.entry import (
    DictionaryEntry, Pronunciation, Sense, Example, 
    RelatedPhrase, PartOfSpeech
)
from .base import BaseParser


class GcideParser(BaseParser):
    """GCIDE词典解析器"""
    
    # 词性映射
    POS_MAP = {
        'a.': 'adj',
        'adj.': 'adj',
        'n.': 'n',
        'v. t.': 'v.t.',
        'v. i.': 'v.i.',
        'vt.': 'v.t.',
        'vi.': 'v.i.',
        'v.': 'v',
        'adv.': 'adv',
        'prep.': 'prep',
        'conj.': 'conj',
        'pron.': 'pron',
        'interj.': 'interj',
        'art.': 'art',
    }
    
    @property
    def source_id(self) -> str:
        return "gcide"
    
    @property
    def name(self) -> str:
        return "GCIDE英英词典"
    
    @property
    def index_language(self) -> str:
        return "en"
    
    @property
    def explanation_language(self) -> str:
        return "en"  # 英英词典
    
    def _extract_etymology(self, content: str) -> Tuple[Optional[str], int]:
        """
        提取词源信息
        
        Returns:
            (词源文本, 词源结束位置)
        """
        # 词源信息在第一个独立的 [1913 Webster] 行之前
        # 格式：[...词源内容...] 后面跟着 [1913 Webster]
        # 查找第一个 [1913 Webster] 标记
        webster_match = re.search(r'^\s*\[1913\s+Webster\]\s*$', content, re.MULTILINE)
        if not webster_match:
            return None, 0
        
        # 在 [1913 Webster] 之前查找最近的方括号块
        before_webster = content[:webster_match.start()]
        
        # 查找最后一个完整的方括号块（可能跨多行）
        # 使用反向查找，找到最后一个 [ 开始的内容
        bracket_start = before_webster.rfind('[')
        if bracket_start == -1:
            return None, webster_match.end()
        
        # 找到对应的 ]（需要处理嵌套）
        bracket_end = before_webster.find(']', bracket_start)
        if bracket_end == -1:
            # 方括号块可能跨多行，包含到 [1913 Webster] 之前的所有内容
            etymology_text = before_webster[bracket_start:].strip()
            return etymology_text, webster_match.end()
        
        etymology_text = before_webster[bracket_start+1:bracket_end].strip()
        return etymology_text, webster_match.end()
    
    def _clean_text(self, text: str) -> str:
        """清理文本：移除标记和引用"""
        # 移除 [1913 Webster] 标记
        text = re.sub(r'\[1913\s+Webster\]', '', text)
        # 移除词根引用标记 {word}
        text = re.sub(r'\{([^}]+)\}', r'\1', text)
        # 移除年份标记
        text = re.sub(r'\[\d{4}\s+\w+\]', '', text)
        # 清理多余空格
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def parse(self, word: str, raw_content: str) -> Optional[DictionaryEntry]:
        """解析GCIDE词典条目"""
        if not raw_content or not raw_content.strip():
            return None
        
        entry = DictionaryEntry(
            headword=word,
            source_id=self.source_id,
            raw_content=raw_content,
        )
        
        content = raw_content.strip()
        lines = content.split('\n')
        
        # 1. 解析标题行（包含词头和词性）
        title_line = lines[0] if lines else ""
        
        # 提取词性（可能有多个，先取第一个）
        pos_match = re.search(r'\\[^\\]+\\,\s+([a-z.]+(?:\s+[a-z.]+)?)', title_line)
        current_pos = None
        if pos_match:
            pos_abbr = pos_match.group(1).strip()
            current_pos = self.POS_MAP.get(pos_abbr, pos_abbr)
        
        # 2. 提取词源信息
        etymology_text, etymology_end = self._extract_etymology(content)
        if etymology_text:
            entry.etymology = self._clean_text(etymology_text)
        
        # 3. 找到第一个数字释义的开始位置
        first_sense_match = re.search(r'^\s*(\d+)\.\s+', content, re.MULTILINE)
        if not first_sense_match:
            # 没有数字释义，尝试简单处理
            return self._parse_simple(entry, content, current_pos)
        
        # 从第一个释义开始处理
        main_content = content[etymology_end:first_sense_match.start()] + content[first_sense_match.start():]
        processing_lines = main_content.split('\n')
        
        # 跳过词源部分的行
        start_idx = 0
        for i, line in enumerate(processing_lines):
            if re.search(r'^\s*\d+\.\s+', line):
                start_idx = i
                break
        
        processing_lines = processing_lines[start_idx:]
        
        # 4. 解析释义和例句
        current_sense = None
        current_sense_num = None
        current_definition = []
        current_examples = []
        pending_example = None
        
        for line in processing_lines:
            line_rstrip = line.rstrip()
            
            # 跳过空行
            if not line_rstrip.strip():
                # 如果有待处理的例句，保存它
                if pending_example:
                    current_examples.append(pending_example)
                    pending_example = None
                continue
            
            # 跳过单独的 [1913 Webster] 标记行
            if re.match(r'^\s*\[1913\s+Webster\]\s*$', line_rstrip):
                # 如果有待处理的例句，保存它
                if pending_example:
                    current_examples.append(pending_example)
                    pending_example = None
                continue
            
            # 检测数字释义开始（如 "   1. " 或 "1. "）
            sense_match = re.match(r'^\s*(\d+)\.\s+(.+)$', line_rstrip)
            if sense_match:
                # 保存上一个sense
                if current_sense is not None:
                    sense_def = ' '.join(current_definition).strip()
                    if sense_def:
                        sense_def = self._clean_text(sense_def)
                        sense = Sense(
                            definition=sense_def,
                            definition_lang="en",
                            pos=current_pos,
                            sense_number=str(current_sense_num),
                            examples=current_examples
                        )
                        entry.senses.append(sense)
                
                # 开始新的sense
                current_sense_num = int(sense_match.group(1))
                definition_start = sense_match.group(2).strip()
                current_definition = [definition_start]
                current_examples = []
                pending_example = None
                current_sense = current_sense_num
                continue
            
            # 检测例句（大量缩进，通常12+空格）
            # 例句通常有大量缩进，且可能跨行
            indent_match = re.match(r'^(\s{10,})(.+)$', line_rstrip)
            if indent_match and current_sense is not None:
                example_text = indent_match.group(2).strip()
                
                # 检查是否有引用标记（在行末或下一行）
                citation_match = re.search(r'--([A-Z][a-zA-Z.]+(?:\s+[a-zA-Z0-9.]+)?)\.\s*$', example_text)
                if citation_match:
                    # 移除引用标记
                    example_text = re.sub(r'\s+--[A-Z][a-zA-Z.]+(?:\s+[a-zA-Z0-9.]+)?\.\s*$', '', example_text).strip()
                
                if example_text and len(example_text) > 8:  # 合理的例句长度
                    # 检查是否是完整的句子（以句号、问号、感叹号结尾）
                    if re.match(r'^[A-Z].*[.!?]$', example_text):
                        # 完整句子，直接添加
                        example = Example(text=example_text, translation=None)
                        current_examples.append(example)
                        pending_example = None
                    else:
                        # 可能是跨行的句子，暂存
                        if pending_example:
                            pending_example = Example(
                                text=pending_example.text + ' ' + example_text,
                                translation=None
                            )
                        else:
                            pending_example = Example(text=example_text, translation=None)
                continue
            
            # 检测单独的引用标记行（如 "      --Shak."）
            citation_only_match = re.match(r'^\s+--([A-Z][a-zA-Z.]+(?:\s+[a-zA-Z0-9.]+)?)\.\s*$', line_rstrip)
            if citation_only_match and pending_example:
                # 引用标记完成上一个例句
                current_examples.append(pending_example)
                pending_example = None
                continue
            
            # 其他内容添加到当前释义（中等缩进，2-8个空格）
            if current_sense is not None:
                indent_match = re.match(r'^(\s{0,8})(.+)$', line_rstrip)
                if indent_match:
                    definition_text = indent_match.group(2).strip()
                    # 移除年份标记
                    definition_text = re.sub(r'\[1913\s+Webster\]', '', definition_text)
                    definition_text = definition_text.strip()
                    if definition_text:
                        current_definition.append(definition_text)
        
        # 保存最后一个sense
        if current_sense is not None:
            if pending_example:
                current_examples.append(pending_example)
            sense_def = ' '.join(current_definition).strip()
            if sense_def:
                sense_def = self._clean_text(sense_def)
                sense = Sense(
                    definition=sense_def,
                    definition_lang="en",
                    pos=current_pos,
                    sense_number=str(current_sense_num),
                    examples=current_examples
                )
                entry.senses.append(sense)
        
        # 必须至少有一个释义
        if not entry.senses:
            return self._parse_simple(entry, content, current_pos)
        
        return entry
    
    def _parse_simple(self, entry: DictionaryEntry, content: str, pos: Optional[str]) -> Optional[DictionaryEntry]:
        """简单解析模式（当无法识别数字释义时）"""
        lines = content.strip().split('\n')
        if not lines:
            return None
        
        # 跳过标题行（第一行）
        content_lines = lines[1:] if len(lines) > 1 else []
        
        # 收集定义内容（在[1913 Webster]之前，或者整个内容如果没有[1913 Webster]）
        definition_lines = []
        found_webster = False
        
        for line in content_lines:
            line_stripped = line.strip()
            
            # 遇到[1913 Webster]标记，停止收集
            if re.match(r'^\[1913\s+Webster\]$', line_stripped):
                found_webster = True
                break
            
            # 跳过单独的引用标记行
            if re.match(r'^--[A-Z]', line_stripped):
                continue
            
            # 跳过空行
            if not line_stripped:
                continue
            
            # 保留定义内容（保留原始缩进，但去掉过度的空白）
            definition_lines.append(line_stripped)
        
        # 如果没有找到[1913 Webster]且没有收集到内容，尝试提取词源后的内容
        if not definition_lines and not found_webster:
            etymology_text, etymology_end = self._extract_etymology(content)
            if etymology_end > 0:
                content_after_etymology = content[etymology_end:].strip()
                if content_after_etymology:
                    # 重新处理词源后的内容
                    after_lines = content_after_etymology.split('\n')
                    for line in after_lines[1:] if len(after_lines) > 1 else after_lines:
                        line_stripped = line.strip()
                        if re.match(r'^\[1913\s+Webster\]$', line_stripped):
                            break
                        if re.match(r'^--[A-Z]', line_stripped):
                            continue
                        if line_stripped:
                            definition_lines.append(line_stripped)
        
        # 合并定义内容
        cleaned_content = ' '.join(definition_lines)
        cleaned_content = self._clean_text(cleaned_content)
        
        if cleaned_content:
            sense = Sense(
                definition=cleaned_content[:1000],  # 限制长度
                definition_lang="en",
                pos=pos,
                sense_number="1"
            )
            entry.senses.append(sense)
            return entry
        
        return None
