#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
牛津英汉词典解析器

格式特点（基于样例分析）：
1. 音标: /英式; 美式/ 或 /单一音标/
2. 词性: n, v, adj, adv, prep, conj, pron, interj, det, aux, modal, art
3. 词形变化: (better /音标/, best /音标/)
4. 义项: 数字序号 1, 2, 3... 表示主要释义
5. 细分: 字母序号 (a), (b), (c)... 表示释义细分
6. 例句: * 开头
7. 语法说明: [attrib], [pred], [esp passive] 等
8. 习语: IDM 标记
9. 动词短语: PHR V 标记
10. 交叉引用: =>

样例：
/gʊd; ˇᴜd/ adj (better / 5betE(r); `bZtL/, best /best; bZst/)  1 of high quality...
"""

import re
from typing import Optional, List, Tuple, Dict
from ..models.entry import (
    DictionaryEntry, Pronunciation, Sense, Example, 
    RelatedPhrase
)
from .base import BaseParser


class OxfordParser(BaseParser):
    """牛津英汉词典解析器"""
    
    # 词性映射
    POS_MAP = {
        'n': 'n',
        'v': 'v',
        'adj': 'adj',
        'adv': 'adv',
        'prep': 'prep',
        'conj': 'conj',
        'pron': 'pron',
        'interj': 'interj',
        'det': 'det',
        'aux': 'aux',
        'modal': 'modal',
        'art': 'art',
    }
    
    @property
    def source_id(self) -> str:
        return "oxford"
    
    @property
    def name(self) -> str:
        return "牛津英汉词典"
    
    @property
    def index_language(self) -> str:
        return "en"
    
    @property
    def explanation_language(self) -> str:
        return "zh-en"  # 中英混合
    
    def parse(self, word: str, raw_content: str) -> Optional[DictionaryEntry]:
        """解析Oxford词典条目"""
        if not raw_content or not raw_content.strip():
            return None
        
        entry = DictionaryEntry(
            headword=word,
            source_id=self.source_id,
            raw_content=raw_content,
        )
        
        parse_notes = []
        content = raw_content.strip()
        
        # 1. 解析音标和词性（开头部分）
        phonetic_pos_match = re.match(
            r'^/([^/;]+)(?:;\s*([^/]+))?/\s*([a-z]+)',
            content
        )
        
        if phonetic_pos_match:
            uk_ipa = phonetic_pos_match.group(1).strip()
            us_ipa = phonetic_pos_match.group(2).strip() if phonetic_pos_match.group(2) else None
            pos_str = phonetic_pos_match.group(3)
            
            # 添加音标
            entry.pronunciations.append(Pronunciation(
                ipa=uk_ipa,
                region="uk"
            ))
            if us_ipa:
                entry.pronunciations.append(Pronunciation(
                    ipa=us_ipa,
                    region="us"
                ))
            
            # 解析词形变化（在词性后面）
            forms_match = re.search(
                r'\(([^)]+)\)',
                content[phonetic_pos_match.end():phonetic_pos_match.end()+200]
            )
            if forms_match:
                forms_text = forms_match.group(1)
                # 简单提取词形变化（后续可以更精细）
                # 例如: better / 5betE(r); `bZtL/, best /best; bZst/
                # 这里先提取词形，音标后续处理
                pass  # TODO: 解析词形变化
            
            # 找到释义开始位置（跳过音标、词性、词形变化）
            content_start = phonetic_pos_match.end()
            if forms_match:
                content_start = content.find(')', content_start) + 1
            
            # 跳过空白，找到第一个数字序号
            match = re.search(r'\s+(\d+)\s+', content[content_start:])
            if match:
                content_start = content_start + match.start()
        else:
            # 没有标准格式，尝试只解析音标
            phonetic_match = re.search(r'/([^/]+)/', content)
            if phonetic_match:
                ipa = phonetic_match.group(1).split(';')[0].strip()
                entry.pronunciations.append(Pronunciation(
                    ipa=ipa,
                    region="general"
                ))
            content_start = 0
        
        # 2. 解析主体内容（释义部分）
        main_content = content[content_start:].strip()
        
        # 分离IDM和PHR V部分
        idm_match = re.search(r'\bIDM\b', main_content)
        phr_v_match = re.search(r'\bPHR V\b', main_content)
        
        # 提取IDM和PHR V部分
        idm_content = None
        phr_v_content = None
        
        if idm_match and phr_v_match:
            if idm_match.start() < phr_v_match.start():
                # IDM在前
                main_content, idm_content = main_content[:idm_match.start()], main_content[idm_match.start():phr_v_match.start()]
                phr_v_content = main_content[phr_v_match.start():]
            else:
                # PHR V在前
                main_content, phr_v_content = main_content[:phr_v_match.start()], main_content[phr_v_match.start():idm_match.start()]
                idm_content = main_content[idm_match.start():]
        elif idm_match:
            main_content, idm_content = main_content[:idm_match.start()], main_content[idm_match.start():]
        elif phr_v_match:
            main_content, phr_v_content = main_content[:phr_v_match.start()], main_content[phr_v_match.start():]
        
        # 3. 解析主要释义（数字序号）
        senses = self._parse_main_senses(main_content, pos_str if phonetic_pos_match else None)
        entry.senses.extend(senses)
        
        # 4. 解析IDM部分
        if idm_content:
            idm_senses = self._parse_idm_section(idm_content)
            entry.senses.extend(idm_senses)
        
        # 5. 解析PHR V部分
        if phr_v_content:
            phr_v_phrases = self._parse_phr_v_section(phr_v_content)
            entry.related_phrases.extend(phr_v_phrases)
        
        # 设置解析质量
        if not entry.senses:
            entry.parse_quality = 0.3
            parse_notes.append("未解析到释义")
        elif not entry.pronunciations:
            entry.parse_quality = 0.7
            parse_notes.append("未解析到音标")
        else:
            entry.parse_quality = 0.9  # Oxford复杂，先给0.9，后续优化
        
        entry.parse_notes = parse_notes
        return entry
    
    def _parse_main_senses(self, content: str, default_pos: Optional[str] = None) -> List[Sense]:
        """
        解析主要释义部分
        
        格式: 1 释义文本 * 例句 * 例句 2 (a) 释义 (b) 释义...
        """
        senses = []
        
        if not content.strip():
            return senses
        
        current_pos = default_pos
        
        # 使用更精确的正则来匹配数字序号（考虑行首和空格）
        # 匹配模式: 空格+数字+空格 或 行首+数字+空格
        pattern = r'(?:^|\s)(\d+)\s+'
        
        # 找到所有数字序号的位置
        matches = list(re.finditer(pattern, content))
        
        if not matches:
            # 没有数字序号，尝试解析整个内容作为一个释义
            sense = self._parse_single_sense(content, default_pos, None)
            if sense:
                senses.append(sense)
            return senses
        
        # 处理每个数字序号之间的内容
        for i, match in enumerate(matches):
            sense_num = match.group(1)
            start_pos = match.end()
            
            # 找到下一个数字序号的位置（或结尾）
            if i + 1 < len(matches):
                end_pos = matches[i + 1].start()
            else:
                end_pos = len(content)
            
            sense_content = content[start_pos:end_pos].strip()
            
            if not sense_content:
                continue
            
            # 检查词性变化（在释义开头）
            pos_match = re.match(r'^([a-z]+)\s+', sense_content)
            if pos_match and pos_match.group(1) in self.POS_MAP:
                current_pos = self.POS_MAP[pos_match.group(1)]
                sense_content = sense_content[pos_match.end():].strip()
            
            # 解析这个义项（可能包含字母序号 (a), (b)）
            sub_senses = self._parse_sense_with_letters(sense_content, current_pos, sense_num)
            senses.extend(sub_senses)
        
        return senses
    
    def _parse_sense_with_letters(self, content: str, pos: Optional[str], sense_num: str) -> List[Sense]:
        """解析可能包含字母序号的义项"""
        senses = []
        
        # 检查是否有字母序号 (a), (b) 等
        letter_pattern = r'\(([a-z])\)\s+'
        letter_matches = list(re.finditer(letter_pattern, content))
        
        if not letter_matches:
            # 没有字母序号，整个作为一个释义
            sense = self._parse_single_sense(content, pos, sense_num)
            if sense:
                senses.append(sense)
        else:
            # 有字母序号，分割处理
            for i, match in enumerate(letter_matches):
                letter = match.group(1)
                start_pos = match.end()
                
                # 找到下一个字母序号的位置（或结尾）
                if i + 1 < len(letter_matches):
                    end_pos = letter_matches[i + 1].start()
                else:
                    end_pos = len(content)
                
                sub_content = content[start_pos:end_pos].strip()
                sense_number = f"{sense_num}{letter}"
                
                sense = self._parse_single_sense(sub_content, pos, sense_number)
                if sense:
                    senses.append(sense)
        
        return senses
    
    def _parse_single_sense(self, content: str, pos: Optional[str], sense_number: Optional[str]) -> Optional[Sense]:
        """解析单个释义（提取定义、例句、语法说明等）"""
        if not content.strip():
            return None
        
        # 提取语法说明 [xxx]
        grammar_note = None
        grammar_matches = re.findall(r'\[([^\]]+)\]', content)
        if grammar_matches:
            # 取第一个或合并
            grammar_note = grammar_matches[0]
            # 移除语法说明标记
            content = re.sub(r'\[([^\]]+)\]', '', content)
        
        # 提取例句（* 开头，直到下一个*或结尾）
        examples = []
        example_pattern = r'\*\s+([^*]+?)(?=\s*\*|$)'
        example_matches = re.finditer(example_pattern, content)
        
        example_texts = []
        for match in example_matches:
            example_text = match.group(1).strip()
            # 尝试分离中英文
            if any('\u4e00' <= c <= '\u9fff' for c in example_text):
                # 包含中文，尝试分离
                # 简单策略：中文通常在英文后面，用空格或标点分隔
                parts = example_text.split()
                en_parts = []
                zh_parts = []
                in_zh = False
                
                for part in parts:
                    has_chinese = any('\u4e00' <= c <= '\u9fff' for c in part)
                    if has_chinese:
                        in_zh = True
                        zh_parts.append(part)
                    elif in_zh:
                        zh_parts.append(part)
                    else:
                        en_parts.append(part)
                
                en_text = ' '.join(en_parts).strip()
                zh_text = ' '.join(zh_parts).strip()
                
                examples.append(Example(
                    text=en_text if en_text else example_text,
                    translation=zh_text if zh_text else None
                ))
            else:
                examples.append(Example(text=example_text))
            
            example_texts.append(match.group(0))
        
        # 移除例句标记，得到纯释义文本
        definition_text = content
        for ex_text in example_texts:
            definition_text = definition_text.replace(ex_text, '').strip()
        
        # 清理定义文本
        definition_text = re.sub(r'\s+', ' ', definition_text).strip()
        
        # 移除开头的 ~ 符号（代表词头）
        definition_text = re.sub(r'^~\s*', '', definition_text)
        
        if definition_text or examples:
            return Sense(
                definition=definition_text if definition_text else "(见例句)",
                definition_lang="zh-en",
                pos=pos,
                sense_number=sense_number,
                examples=examples,
                grammar_note=grammar_note
            )
        
        return None
    
    def _parse_idm_section(self, content: str) -> List[Sense]:
        """解析IDM（习语）部分"""
        senses = []
        # TODO: 实现IDM解析
        # IDM部分通常格式: IDM phrase 释义 * 例句
        return senses
    
    def _parse_phr_v_section(self, content: str) -> List[RelatedPhrase]:
        """解析PHR V（动词短语）部分"""
        phrases = []
        # TODO: 实现PHR V解析
        # PHR V部分通常格式: PHR V phrase 释义 * 例句
        return phrases


# 测试代码
if __name__ == "__main__":
    import sys
    from pathlib import Path
    
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    
    # 测试样例
    test_content = """/gʊd; ˇᴜd/ adj (better / 5betE(r); `bZtL/, best /best; bZst/)  1 of high quality; of an acceptable standard; satisfactory 好的; 优质的; 符合标准的; 令人满意的: a good lecture, performance, harvest 好的演讲、表演、收成 * good pronunciation, behaviour, eyesight 好的发音、行为、视力 * a good (eg sharp) knife 快的刀 * Is the light good enough to take photographs? 光线适合照相吗? * The car has very good brakes. 这辆汽车的刹车很灵. * Her English is very good. 她的英语很好.  2 (a) ~ (at sth) (often used with names of occupations or with ns derived from vs 常与职业名称或动词派生的名词连用) able to perform satisfactorily; competent 表现令人满意的; 有能力的: a good teacher, hairdresser, poet, etc 优秀的教师、理发师、诗人等 * good at mathematics, languages, describing things 擅长数学、语言、叙事 * a good loser, ie one who doesn't complain when he loses 输得起的人. (b) [pred 作表语] ~ with sth/sb capable when using, dealing with, etc sth/sb 善于使用某物、处事、待人或用人: good with one's hands, eg able to draw, make things, etc 手巧（如会画、会做东西等） * He's very good with children, ie can look after them well, amuse them, etc. 他很会照看孩子."""

    parser = OxfordParser()
    entry = parser.parse("good", test_content)
    
    if entry:
        print("解析结果:")
        print(f"音标: {[f'{p.region}: {p.ipa}' for p in entry.pronunciations]}")
        print(f"释义数: {len(entry.senses)}")
        for i, sense in enumerate(entry.senses[:5]):
            print(f"\n[{i+1}] {sense.pos or '-'} {sense.sense_number or ''}")
            print(f"    定义: {sense.definition[:100]}...")
            if sense.grammar_note:
                print(f"    语法: {sense.grammar_note}")
            if sense.examples:
                print(f"    例句: {len(sense.examples)}个")
        print(f"\n解析质量: {entry.parse_quality}")
        print(f"解析备注: {entry.parse_notes}")
    else:
        print("解析失败!")

