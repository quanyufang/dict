#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
朗道英汉词典解析器

格式特点（基于样例分析）：
1. 音标: *[ipa]
2. 词性: n. v. a. ad. 等
3. 释义: 中文，逗号分隔
4. 领域: 【经】【计】【医】等
5. 相关词组: "相关词组:" 后列出

样例：
*[gud]
n. 善行, 好处, 利益
a. 好的, 优良的, 上等的, 愉快的, 有益的, 好心的, 慈善的, 虔诚的
【经】 货物; 好的
相关词组:
  for good
  for good or for evil
  ...
"""

import re
from typing import Optional, List, Tuple
from ..models.entry import (
    DictionaryEntry, Pronunciation, Sense, Example, 
    RelatedPhrase, PartOfSpeech
)
from .base import BaseParser


class LangdaoParser(BaseParser):
    """朗道英汉词典解析器"""
    
    # 词性映射
    POS_MAP = {
        'n.': 'n',
        'v.': 'v',
        'vt.': 'v',
        'vi.': 'v',
        'a.': 'adj',
        'ad.': 'adv',
        'adj.': 'adj',
        'adv.': 'adv',
        'prep.': 'prep',
        'conj.': 'conj',
        'pron.': 'pron',
        'int.': 'interj',
        'interj.': 'interj',
        'art.': 'art',
        'num.': 'num',
        'abbr.': 'abbr',
    }
    
    # 领域标签映射
    DOMAIN_MAP = {
        '经': 'economics',
        '计': 'computing',
        '医': 'medical',
        '机': 'mechanical',
        '法': 'law',
        '化': 'chemistry',
        '生': 'biology',
        '物': 'physics',
        '军': 'military',
        '音': 'music',
        '体': 'sports',
        '建': 'architecture',
        '数': 'mathematics',
        '电': 'electronics',
        '农': 'agriculture',
        '地': 'geography',
        '矿': 'mining',
    }
    
    @property
    def source_id(self) -> str:
        return "langdao"
    
    @property
    def name(self) -> str:
        return "朗道英汉词典"
    
    @property
    def index_language(self) -> str:
        return "en"
    
    @property
    def explanation_language(self) -> str:
        return "zh"
    
    def parse(self, word: str, raw_content: str) -> Optional[DictionaryEntry]:
        """解析朗道词典条目"""
        if not raw_content or not raw_content.strip():
            return None
        
        entry = DictionaryEntry(
            headword=word,
            source_id=self.source_id,
            raw_content=raw_content,
        )
        
        lines = raw_content.strip().split('\n')
        parse_notes = []
        
        # 1. 解析音标 (第一行通常是 *[ipa])
        phonetic = self._parse_phonetic(lines[0] if lines else "")
        if phonetic:
            entry.pronunciations.append(Pronunciation(
                ipa=phonetic,
                region="general"
            ))
        
        # 2. 解析主体内容
        in_related_phrases = False
        
        for line in lines[1:]:  # 跳过音标行
            line = line.strip()
            if not line:
                continue
            
            # 检测相关词组部分
            if line.startswith('相关词组') or line.startswith('相关词组:') or line.startswith('相关词组：'):
                in_related_phrases = True
                continue
            
            if in_related_phrases:
                # 解析词组
                phrase = line.strip()
                if phrase:
                    entry.related_phrases.append(RelatedPhrase(
                        phrase=phrase,
                        phrase_type="phrase"
                    ))
            else:
                # 解析释义行
                senses = self._parse_definition_line(line)
                entry.senses.extend(senses)
        
        # 设置解析质量
        if not entry.senses:
            entry.parse_quality = 0.5
            parse_notes.append("未解析到释义")
        elif not entry.pronunciations:
            entry.parse_quality = 0.8
            parse_notes.append("未解析到音标")
        else:
            entry.parse_quality = 1.0
        
        entry.parse_notes = parse_notes
        return entry
    
    def _parse_phonetic(self, line: str) -> Optional[str]:
        """解析音标行: *[ipa]"""
        match = re.search(r'\*\[([^\]]+)\]', line)
        if match:
            return match.group(1)
        return None
    
    def _parse_definition_line(self, line: str) -> List[Sense]:
        """
        解析释义行
        
        格式示例:
        - "n. 善行, 好处, 利益"
        - "a. 好的, 优良的"
        - "【经】 货物; 好的"
        - "run的过去式和过去分词"
        """
        senses = []
        
        # 检查领域标签 【xxx】
        domain = None
        domain_match = re.search(r'【([^】]+)】', line)
        if domain_match:
            domain_char = domain_match.group(1)
            domain = self.DOMAIN_MAP.get(domain_char, domain_char)
            # 移除领域标签，继续解析
            line = re.sub(r'【[^】]+】\s*', '', line)
        
        # 检查词性
        pos = None
        for pos_abbr in sorted(self.POS_MAP.keys(), key=len, reverse=True):
            if line.startswith(pos_abbr) or line.startswith(pos_abbr.replace('.', '. ')):
                pos = self.POS_MAP[pos_abbr]
                line = line[len(pos_abbr):].strip()
                break
        
        # 剩余内容作为释义
        if line:
            sense = Sense(
                definition=line,
                definition_lang="zh",
                pos=pos,
                domain=domain
            )
            senses.append(sense)
        
        return senses


# 测试代码
if __name__ == "__main__":
    import json
    
    # 测试样例
    test_content = """*[gud]
n. 善行, 好处, 利益
a. 好的, 优良的, 上等的, 愉快的, 有益的, 好心的, 慈善的, 虔诚的
【经】 货物; 好的
相关词组:
  for good
  for good or for evil
  good and
  good for"""

    parser = LangdaoParser()
    entry = parser.parse("good", test_content)
    
    if entry:
        print("解析结果:")
        print(entry.to_json())
        print(f"\n解析质量: {entry.parse_quality}")
        print(f"解析备注: {entry.parse_notes}")

