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
        'abbr': 'abbr',
        'symb': 'symb',
        'def art': 'art',  # def art = definite article
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
        
        # 1. 识别格式类型
        pattern_type = self._identify_pattern(content)
        parse_notes.append(f"格式类型: {pattern_type}")
        
        # 2. 解析音标和词性（开头部分）
        # 先清理HTML标记以便解析
        content_for_parse = re.sub(r'<i>([^<]+)</i>', r'\1', content)
        
        # 改进音标解析：先匹配整个音标部分（包括强读式）
        phonetic_match = re.match(r'^/([^/]+)/', content_for_parse)
        
        pos_str = None
        content_start = 0
        
        if phonetic_match:
            phonetic_text = phonetic_match.group(1).strip()
            
            # 解析音标：处理UK/US/强读式
            # 格式可能是：UK; US; strong form 强读式 SF
            # 或者：UK; US
            
            # 先检查是否有强读式
            strong_form_match = re.search(r'strong form[^;]*?([^;]+?)(?:;|$)', phonetic_text)
            
            if strong_form_match:
                # 有强读式，分离各部分
                strong_form_start = strong_form_match.start()
                main_phonetic = phonetic_text[:strong_form_start].strip()
                strong_form_raw = strong_form_match.group(1).strip()
                # 提取强读式音标（移除可能的说明文字）
                # 格式：强读式 ðiː; ði 或 强读式 ðiː
                strong_form_ipa = re.sub(r'强读式\s*', '', strong_form_raw).strip()
                # 如果还有分号，取第一个作为强读式
                if ';' in strong_form_ipa:
                    strong_form_ipa = strong_form_ipa.split(';')[0].strip()
                
                # 解析主音标部分（UK和US）
                # 格式：UK; US 或 UK; US（如果有多个分号）
                phonetic_parts = re.split(r';\s*', main_phonetic)
                uk_ipa = phonetic_parts[0].strip() if phonetic_parts else main_phonetic
                # 查找US音标（在强读式之前的部分）
                # 如果有多于1个部分，第二个通常是US
                us_ipa = phonetic_parts[1].strip() if len(phonetic_parts) > 1 else None
                # 如果US音标和UK相同，可能没有US，设置为None
                if us_ipa and us_ipa == uk_ipa:
                    us_ipa = None
                
                # 添加UK音标
                entry.pronunciations.append(Pronunciation(
                    ipa=uk_ipa,
                    region="uk"
                ))
                
                # 添加US音标（如果有且不同于UK）
                if us_ipa and us_ipa != uk_ipa:
                    entry.pronunciations.append(Pronunciation(
                        ipa=us_ipa,
                        region="us"
                    ))
                
                # 添加强读式
                entry.pronunciations.append(Pronunciation(
                    ipa=strong_form_ipa,
                    region="uk"
                ))
            else:
                # 没有强读式，按标准格式解析
                phonetic_parts = re.split(r';\s*', phonetic_text)
                uk_ipa = phonetic_parts[0].strip()
                us_ipa = phonetic_parts[1].strip() if len(phonetic_parts) > 1 else None
                
                # 添加UK音标
                entry.pronunciations.append(Pronunciation(
                    ipa=uk_ipa,
                    region="uk"
                ))
                
                # 添加US音标（如果有）
                if us_ipa and us_ipa != uk_ipa:
                    entry.pronunciations.append(Pronunciation(
                        ipa=us_ipa,
                        region="us"
                    ))
            
            # 查找词性（在音标后）
            # 注意：需要在原始content中查找，因为需要准确的位置
            content_after_phonetic = content[phonetic_match.end():].strip()
            pos_match_in_content = re.search(r'\b(def\s+art|adj|n|v|aux\s+v|prep|adv|conj|pron|interj|det|aux|modal|art|abbr|symb)\b', content_after_phonetic, re.I)
            
            if pos_match_in_content:
                pos_raw = pos_match_in_content.group(1).strip()
                # 处理词性（支持def art和aux v等复合词性）
                if pos_raw.lower() == 'def art':
                    pos_str = 'art'  # def art = definite article
                elif pos_raw.lower() == 'aux v':
                    pos_str = 'aux'  # aux v = auxiliary verb
                else:
                    pos_str = pos_raw.lower()
                
                # 更新content_start到词性后
                # content_after_phonetic是trimmed的，所以需要找到词性结束后的位置
                pos_end_in_content = phonetic_match.end() + len(content_after_phonetic) - len(content_after_phonetic[pos_match_in_content.end():].lstrip())
                content_start = pos_end_in_content
            else:
                # 没找到词性，使用默认位置
                content_start = phonetic_match.end()
            
            # 解析词形变化（在词性后面，格式通常是 (better /音标/, best /音标/)）
            # 词形变化应该在第一个数字序号之前，且包含音标或常见词形变化格式
            forms_match = re.search(
                r'\(([^)]*(?:/\d|better|best|worse|worst|more|most|er|est|ing|ed)[^)]*)\)',
                content[content_start:content_start+200]
            )
            
            if forms_match:
                # 确认这确实是词形变化（在数字序号之前）
                before_forms = content[content_start:content_start+forms_match.start()]
                if re.search(r'(?:^|\s)\d+\s+', before_forms):
                    # 数字序号在词形变化之前，这不是词形变化
                    forms_match = None
                else:
                    content_start = content.find(')', content_start) + 1
            
            # 跳过空白，找到第一个数字序号或字母序号
            # 使用更灵活的模式：可以匹配行首或空格后的数字
            match = re.search(r'(?:^|\s)(\d+)\s+', content[content_start:], re.MULTILINE)
            if match:
                # 如果匹配到的是空格开头，需要跳过这个空格
                if match.group(0).startswith(' '):
                    content_start = content_start + match.start() + 1
                else:
                    content_start = content_start + match.start()
        else:
            # 没有标准音标格式（/音标/），尝试查找词性
            # 可能格式：词性 定义（没有音标）
            pos_match = re.match(r'^([a-z]+(?:\.\s*[a-z]+)?\.?)\s+', content)
            if pos_match:
                pos_raw = pos_match.group(1).strip().rstrip('.')
                if pos_raw in self.POS_MAP:
                    pos_str = self.POS_MAP[pos_raw]
                    content_start = pos_match.end()
                else:
                    # 可能是词性但不在映射中，尝试提取
                    pos_str = pos_raw.lower()
                    content_start = pos_match.end()
            else:
                # 既没有音标也没有词性标记，从头开始
                content_start = 0
        
        # 3. 检查是否有多词性（通过独立音标+词性组合识别）
        # "have"词条格式：/həv/ aux v ... /hæv/ v ... /hæv/ v ...
        # 需要识别独立的音标+词性组合，即使它们之间只有单换行符
        # 在整个content中查找所有音标+词性组合
        multiple_pos_pattern = re.compile(
            r'/([^/]+)/[^\n]*?\b(aux\s+v|v|n|adj|adv|prep|conj|pron|interj|det|aux|modal|art|abbr|symb|def\s+art)\b',
            re.I
        )
        pos_with_phonetic_matches = list(multiple_pos_pattern.finditer(content))
        
        # 如果有多个独立音标+词性组合，使用多词性解析
        if len(pos_with_phonetic_matches) > 1:
            # 使用_parse_without_cross_ref来处理多词性
            # 但需要先处理第一个音标（已经在开头解析过了，需要合并）
            multi_pos_entry = self._parse_without_cross_ref(content, word)
            if multi_pos_entry:
                # 优先使用multi_pos_entry的音标（如果已解析）
                if multi_pos_entry.pronunciations:
                    entry.pronunciations = multi_pos_entry.pronunciations
                entry.senses.extend(multi_pos_entry.senses)
            
            # 多词性解析完成，跳过后续标准解析
            entry.parse_quality = 0.9 if entry.senses else 0.3
            entry.parse_notes = parse_notes
            return entry
        
        # 4. 解析主体内容（释义部分）- 单词性情况
        main_content = content[content_start:].strip()
        
        # 分离IDM和PHR V部分（仅在非多词性情况下，或处理多词性后的剩余部分）
        # 支持多种IDM标记：IDM, (idm 习语), (习语)
        # 注意：需要区分独立的IDM部分和义项内的IDM标记
        # - 独立的IDM：如 "(idm 习语) be the making of sb..."
        # - 义项内的IDM：如 "11 (idm 习语) the more..."
        idm_match = re.search(r'\bIDM\b|\(idm\s+习语\)|\(习语\)', main_content, re.I)
        phr_v_match = re.search(r'\bPHR V\b', main_content)
        
        # 提取IDM和PHR V部分
        idm_content = None
        phr_v_content = None
        
        if idm_match:
            # 检查是否是义项内的IDM标记（前面有数字序号）
            # 检查IDM标记前是否有数字序号（如 "11 (idm 习语)"）
            # 需要检查IDM标记前的内容，而不是整个main_content
            before_idm_start = max(0, idm_match.start() - 20)
            before_idm_context = main_content[before_idm_start:idm_match.start() + 20]
            sense_number_before_idm = re.search(r'(\d+)\s+(?:\(idm\s+习语\)|\(习语\))', before_idm_context, re.I)
            
            if sense_number_before_idm:
                # 这是义项内的IDM标记，不分离，让它作为义项的一部分
                # IDM习语会由_parse_main_senses中的_parse_sense_with_letters或_parse_single_sense处理
                idm_match = None
            else:
                # 这是独立的IDM部分，需要分离
                if phr_v_match:
                    if idm_match.start() < phr_v_match.start():
                        # IDM在前
                        main_content, idm_content = main_content[:idm_match.start()], main_content[idm_match.start():phr_v_match.start()]
                        phr_v_content = main_content[phr_v_match.start():]
                    else:
                        # PHR V在前
                        main_content, phr_v_content = main_content[:phr_v_match.start()], main_content[phr_v_match.start():idm_match.start()]
                        idm_content = main_content[idm_match.start():]
                else:
                    main_content, idm_content = main_content[:idm_match.start()], main_content[idm_match.start():]
        
        if phr_v_match and not idm_content:
            # 只有在没有独立的IDM部分时才分离PHR V
            main_content, phr_v_content = main_content[:phr_v_match.start()], main_content[phr_v_match.start():]
        
        # 4. 根据格式类型选择解析策略
        if pattern_type == "cross_reference":
            # 交叉引用，如 => have. 或 pt of go1.（纯交叉引用，无后续定义）
            sense = Sense(
                definition=main_content,
                definition_lang="en",
                sense_number=None
            )
            entry.senses.append(sense)
        elif pattern_type == "mixed_cross_ref":
            # 混合格式：交叉引用开头 + 完整定义
            # 分离交叉引用部分和后续内容
            # 支持多种交叉引用格式：=>, =>Usage, =>Usage at, pt of, pp of
            cross_ref_match = re.match(r'^(=>|(pt|pp)\s+of\s+[^.]+\.|=>Usage(?:\s+at\s+\w+)?[^.]*\.?)', content)
            if cross_ref_match:
                cross_ref_text = cross_ref_match.group(0).strip()
                remaining_content = content[cross_ref_match.end():].strip()
                
                # 注意：交叉引用通常只是说明文字，不是真正的sense
                # 如果剩余内容为空，才添加交叉引用sense
                # 否则，直接解析剩余内容（跳过交叉引用）
                if remaining_content.strip():
                    # 继续解析剩余内容（调用主解析逻辑，但跳过交叉引用检测）
                    remaining_entry = self._parse_without_cross_ref(remaining_content, word)
                    if remaining_entry:
                        # 使用remaining_entry的音标（如果已解析）
                        if remaining_entry.pronunciations:
                            entry.pronunciations = remaining_entry.pronunciations
                        entry.senses.extend(remaining_entry.senses)
                else:
                    # 只有交叉引用，没有剩余内容
                    cross_ref_sense = Sense(
                        definition=cross_ref_text,
                        definition_lang="en",
                        sense_number=None
                    )
                    entry.senses.append(cross_ref_sense)
        elif pattern_type == "direct_letter_numbered" or self._is_come_up_pattern(word, main_content):
            # come up 类型：直接字母序号开始
            senses = self._parse_come_up_case(main_content, pos_str)
            entry.senses.extend(senses)
        elif pattern_type == "phrase_heading" or self._is_give_up_pattern(word, main_content):
            # give up 类型：冒号分隔，短语标题+子sense
            senses = self._parse_give_up_case(main_content, pos_str)
            entry.senses.extend(senses)
        elif pattern_type == "numbered_sense" or phonetic_match:
            # 标准数字序号模式
            # 检查是否有多词性（main_content中是否有第二个词性标记）
            # main_content已经跳过了第一个词性，如果还有词性标记，说明是多词性
            
            # 先检查是否有多个独立词条段（用\n\n分隔）
            segments = re.split(r'\n\n+', main_content)
            has_multiple_segments = len(segments) > 1
            
            # 检查是否有第二个词性标记（包括abbr, symb等）
            pos_pattern = r'\b(adj|n|v|prep|adv|conj|pron|interj|det|aux|modal|art|abbr|symb|def\s+art)\b'
            pos_matches = list(re.finditer(pos_pattern, main_content, re.I))
            
            # 检查是否有第二个词性（通常在换行后，或在独立段中）
            has_multiple_pos = False
            if has_multiple_segments:
                # 有多个独立段，检查第二个段是否有词性标记
                if len(segments) > 1:
                    second_segment = segments[1]
                    second_pos_match = re.search(pos_pattern, second_segment, re.I)
                    if second_pos_match:
                        has_multiple_pos = True
            else:
                # 单个段，检查是否有第二个词性（在换行后）
                for match in pos_matches:
                    # 检查这个词性前是否有换行（说明是新词性开始）
                    before_pos = main_content[:match.start()].rstrip()
                    if before_pos.endswith('\n') or (len(before_pos) > 0 and before_pos[-1] == '\n'):
                        has_multiple_pos = True
                        break
            
            if has_multiple_pos and (len(pos_matches) > 1 or has_multiple_segments):
                # 有多个词性，使用多词性解析（传入从音标后的内容，包含第一个词性）
                # content_start已经跳过了音标，但我们需要包含第一个词性
                # 所以从音标匹配结束位置开始（如果有音标）
                if phonetic_match:
                    multi_pos_content = content[phonetic_match.end():].strip()
                else:
                    multi_pos_content = content[content_start:].strip()
                
                multi_pos_entry = self._parse_without_cross_ref(multi_pos_content, word)
                if multi_pos_entry:
                    # 优先使用multi_pos_entry的音标（如果已解析）
                    if multi_pos_entry.pronunciations:
                        entry.pronunciations = multi_pos_entry.pronunciations
                    entry.senses.extend(multi_pos_entry.senses)
            else:
                # 单词性，标准解析
                senses = self._parse_main_senses(main_content, pos_str)
                entry.senses.extend(senses)
        else:
            # 通用解析（fallback）
            senses = self._parse_generic_case(main_content, pos_str)
            entry.senses.extend(senses)
        
        # 5. 解析IDM部分
        if idm_content:
            idm_senses = self._parse_idm_section(idm_content)
            entry.senses.extend(idm_senses)
        
        # 6. 解析PHR V部分
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
            entry.parse_quality = 0.9
        
        entry.parse_notes = parse_notes
        return entry
    
    def _parse_without_cross_ref(self, content: str, word: str) -> Optional[DictionaryEntry]:
        """
        解析不含交叉引用的内容（用于混合格式）
        
        这个方法和parse类似，但不检测交叉引用，支持多词性解析
        """
        if not content or not content.strip():
            return None
        
        entry = DictionaryEntry(
            headword=word,
            source_id=self.source_id,
            raw_content=content,
        )
        
        # 1. 处理HTML标记（如<i>US</i>），先清理
        # 保留标记信息但简化解析
        content_clean = re.sub(r'<i>([^<]+)</i>', r'\1', content)
        
        # 2. 解析音标（改进版，处理US标记）
        # 格式: /gɒn; <i>US</i> gɔːn; ˇɔn/ 或 /gɒn; gɔːn/
        phonetic_match = re.search(r'/([^/]+)/', content_clean)
        if phonetic_match:
            phonetic_text = phonetic_match.group(1).strip()
            # 分割多个音标（用分号分隔）
            phonetic_parts = re.split(r';\s*', phonetic_text)
            
            # 查找US标记
            us_marked = '<i>US</i>' in content or 'US' in phonetic_text
            
            # 解析第一个音标（通常是UK）
            if phonetic_parts:
                uk_ipa = phonetic_parts[0].strip()
                entry.pronunciations.append(Pronunciation(
                    ipa=uk_ipa,
                    region="uk"
                ))
            
            # 解析其他音标
            for i, part in enumerate(phonetic_parts[1:], 1):
                part = part.strip()
                # 检查是否有US标记或特定标记（如ˇ）
                if 'US' in part or 'ˇ' in part or us_marked:
                    entry.pronunciations.append(Pronunciation(
                        ipa=part.replace('ˇ', '').replace('US', '').strip(),
                        region="us"
                    ))
                else:
                    entry.pronunciations.append(Pronunciation(
                        ipa=part,
                        region="general"
                    ))
        
        # 3. 支持多词性解析（adj, prep, abbr, symb等）
        # 找到所有词性位置（包括abbr, symb等）
        # 注意：abbr和symb可能是独立的词条段（在换行后，且有独立的音标）
        
        # 检查是否有多词性（通过独立音标+词性组合识别）
        # 格式：/音标/ 词性 ... /音标/ 词性 ...
        multiple_pos_pattern = re.compile(
            r'/([^/]+)/[^\n]*?\b(aux\s+v|v|n|adj|adv|prep|conj|pron|interj|det|aux|modal|art|abbr|symb|def\s+art)\b',
            re.I
        )
        pos_with_phonetic_matches = list(multiple_pos_pattern.finditer(content_clean))
        
        # 如果有多个独立音标+词性组合，分别解析每个部分
        has_multiple_entries = len(pos_with_phonetic_matches) > 1
        
        # 如果有多词性，使用音标+词性组合分割
        if has_multiple_entries:
            # 多个独立词性部分，分别解析
            for i, match in enumerate(pos_with_phonetic_matches):
                phonetic_text = match.group(1).strip()
                pos_raw = match.group(2).strip()
                match_start = match.start()
                
                # 找到下一个音标+词性组合的位置，或结尾
                if i + 1 < len(pos_with_phonetic_matches):
                    next_match_start = pos_with_phonetic_matches[i + 1].start()
                else:
                    next_match_start = len(content_clean)
                
                # 提取这个词性部分的内容（从当前音标+词性后到下一个音标前）
                # 需要找到词性结束的位置
                match_end = match.end()
                after_match = content_clean[match_end:match_end+100].strip()
                
                # 查找词性后的第一个有效内容位置（跳过交叉引用等）
                # 查找第一个数字序号、字母序号或分类标题
                content_start_pattern = re.search(
                    r'(?:^|\s)(\d+)\s+|\([a-z]\)\s+|\* [A-Z]',
                    after_match,
                    re.MULTILINE
                )
                
                if content_start_pattern:
                    pos_content_start = match_end + content_start_pattern.start()
                    if content_start_pattern.group(0).startswith(' '):
                        pos_content_start += 1
                else:
                    # 没找到明确的起始标记，使用词性后
                    pos_content_start = match_end
                
                pos_content = content_clean[pos_content_start:next_match_start].strip()
                
                # 解析音标（改进：清理音标文本，只提取真正的IPA音标）
                # 先移除"strong form 强读式"等说明文字
                phonetic_text_clean = phonetic_text
                
                # 提取强读式（如果有）
                strong_form_match = re.search(r'strong form[^;]*?([^;]+?)(?:;|$)', phonetic_text_clean)
                strong_form_ipa = None
                if strong_form_match:
                    strong_form_raw = strong_form_match.group(1).strip()
                    # 移除"强读式"文字，只保留音标
                    strong_form_ipa = re.sub(r'强读式\s*', '', strong_form_raw).strip()
                    # 如果还有分号，取第一个
                    if ';' in strong_form_ipa:
                        strong_form_ipa = strong_form_ipa.split(';')[0].strip()
                    # 移除音标文本中的强读式部分
                    phonetic_text_clean = phonetic_text_clean[:strong_form_match.start()].strip()
                
                # 分割主音标部分（UK和US）
                phonetic_parts = re.split(r';\s*', phonetic_text_clean)
                if phonetic_parts:
                    uk_ipa = phonetic_parts[0].strip()
                    # 清理音标：移除可能的非音标字符（如中文字符）
                    uk_ipa = re.sub(r'[^\x00-\x7F\s/\[\]()]', '', uk_ipa).strip()
                    
                    # 如果有强读式，添加弱读式和强读式
                    if strong_form_ipa:
                        strong_form_ipa_clean = re.sub(r'[^\x00-\x7F\s/\[\]()]', '', strong_form_ipa).strip()
                        if uk_ipa and uk_ipa != strong_form_ipa_clean:
                            entry.pronunciations.append(Pronunciation(
                                ipa=uk_ipa,
                                region="uk"
                            ))
                        if strong_form_ipa_clean:
                            entry.pronunciations.append(Pronunciation(
                                ipa=strong_form_ipa_clean,
                                region="uk"
                            ))
                    else:
                        # 没有强读式，添加主音标
                        if uk_ipa:
                            entry.pronunciations.append(Pronunciation(
                                ipa=uk_ipa,
                                region="uk"
                            ))
                        # 检查是否有US音标
                        if len(phonetic_parts) > 1:
                            us_ipa = phonetic_parts[1].strip()
                            us_ipa = re.sub(r'[^\x00-\x7F\s/\[\]()]', '', us_ipa).strip()
                            if us_ipa and us_ipa != uk_ipa:
                                entry.pronunciations.append(Pronunciation(
                                    ipa=us_ipa,
                                    region="us"
                                ))
                
                # 处理词性
                if pos_raw.lower() == 'aux v':
                    pos_str_section = 'aux'
                elif pos_raw.lower() == 'def art':
                    pos_str_section = 'art'
                else:
                    pos_str_section = pos_raw.lower()
                
                # 解析这个词性部分
                senses_section = self._parse_main_senses(pos_content, pos_str_section)
                entry.senses.extend(senses_section)
            
            return entry
        
        # 如果没有多词性，使用原有逻辑（双换行符分割或标准多词性解析）
        # 先按换行分割，检查是否有独立的词条段（每个段可能有独立的音标和词性）
        segments = re.split(r'\n\n+', content_clean)
        
        # 如果只有一个段，或者所有段都有音标，说明是多个独立的词条段
        has_multiple_entries_legacy = len(segments) > 1
        
        if has_multiple_entries_legacy:
            # 多个独立词条段，分别解析
            for segment in segments:
                segment = segment.strip()
                if not segment:
                    continue
                
                # 检查是否有音标和词性（独立词条段的特征）
                # 格式: /音标/ 词性 或 词性（如abbr 缩写 =）
                phonetic_match = re.search(r'/([^/]+)/', segment)
                pos_match = None
                
                # 查找词性标记
                # 模式1: 音标后跟词性（如 `/eɪ; e/ symb`）
                if phonetic_match:
                    after_phonetic = segment[phonetic_match.end():].strip()
                    pos_match = re.search(r'\b(n|v|aux\s+v|adj|adv|prep|conj|pron|interj|det|aux|modal|art|abbr|symb|def\s+art)\b', after_phonetic, re.I)
                else:
                    # 模式2: 直接词性（如 `abbr 缩写 =`）
                    pos_match = re.search(r'^\s*(abbr|symb)\s+', segment, re.I)
                
                if pos_match:
                    if phonetic_match:
                        # 有音标，提取音标
                        phonetic_text = phonetic_match.group(1).strip()
                        phonetic_parts = re.split(r';\s*', phonetic_text)
                        if phonetic_parts:
                            uk_ipa = phonetic_parts[0].strip()
                            entry.pronunciations.append(Pronunciation(
                                ipa=uk_ipa,
                                region="uk"
                            ))
                            if len(phonetic_parts) > 1:
                                us_ipa = phonetic_parts[1].strip()
                                entry.pronunciations.append(Pronunciation(
                                    ipa=us_ipa,
                                    region="us"
                                ))
                        
                        pos = pos_match.group(1).strip().lower()
                        if pos == 'def art':
                            pos = 'art'
                        elif pos == 'aux v':
                            pos = 'aux'  # aux v = auxiliary verb
                        pos_start = pos_match.end()
                    else:
                        # 没有音标，词性在开头
                        pos = pos_match.group(1).strip().lower()
                        pos_start = pos_match.end()
                    
                    # 提取这个词性的内容
                    pos_content = segment[pos_start:].strip()
                    
                    # 解析这个词性下的senses
                    senses = self._parse_main_senses(pos_content, self.POS_MAP.get(pos, pos))
                    entry.senses.extend(senses)
                else:
                    # 没找到词性，尝试解析整个段
                    sense = self._parse_single_sense(segment, None, None)
                    if sense:
                        entry.senses.append(sense)
        else:
            # 单个段，使用标准多词性解析
            # 支持aux v（助动词）
            pos_pattern = r'\b(adj|n|v|aux\s+v|prep|adv|conj|pron|interj|det|aux|modal|art|abbr|symb|def\s+art)\b'
            pos_matches = list(re.finditer(pos_pattern, content_clean, re.I))
            
            if not pos_matches:
                # 没有找到词性，尝试解析整个内容
                sense = self._parse_single_sense(content_clean, None, None)
                if sense:
                    entry.senses.append(sense)
                return entry
            
            # 处理每个词性及其内容
            for i, pos_match in enumerate(pos_matches):
                pos = pos_match.group(1).strip().lower()
                if pos == 'def art':
                    pos = 'art'
                pos_start = pos_match.end()
                
                # 找到下一个词性或结尾
                if i + 1 < len(pos_matches):
                    pos_end = pos_matches[i + 1].start()
                else:
                    pos_end = len(content_clean)
                
                pos_content = content_clean[pos_start:pos_end].strip()
                
                # 解析这个词性下的senses
                senses = self._parse_main_senses(pos_content, self.POS_MAP.get(pos, pos))
                entry.senses.extend(senses)
        
        return entry
    
    def _identify_pattern(self, content: str) -> str:
        """识别内容格式类型"""
        # 1. 检查交叉引用（但后面可能还有完整定义）
        # 支持多种交叉引用格式：
        # - =>Usage at a2
        # - =>Usage
        # - => have.
        # - pt of go1.
        # - pp of go.
        cross_ref_match = re.match(r'^(=>|(pt|pp)\s+of\s+[^.]+\.|=>Usage(?:\s+at\s+\w+)?)', content)
        if cross_ref_match:
            # 检查交叉引用后是否还有音标和定义
            cross_ref_end = cross_ref_match.end()
            remaining = content[cross_ref_end:].strip()
            # 如果后面有音标（/开头）或词性，说明是混合格式
            # 支持的词性：adj, n, v, aux v, prep, adv, def art, art等
            if re.search(r'^/[^/]+/', remaining) or re.search(r'^\b(adj|n|v|aux\s+v|prep|adv|conj|pron|interj|det|aux|modal|art|def\s+art|abbr|symb)\b', remaining, re.I):
                return "mixed_cross_ref"  # 混合格式：交叉引用+完整定义
            return "cross_reference"
        
        # 2. 检查音标/词性（标准格式）
        if re.match(r'^/[^/]+/', content):
            return "numbered_sense"
        
        # 3. 检查直接字母序号开始
        if re.match(r'^\s*\([a-z]\)\s+', content):
            return "direct_letter_numbered"
        
        # 4. 检查短语标题模式
        if re.search(r'\b\w+\s+(?:sb|sth|oneself|\w+)\s+\w+\s+\([a-z]\)', content):
            return "phrase_heading"
        
        # 5. 检查冒号分隔
        colon_count = content.count(': ')
        if colon_count > 3:
            return "colon_separated"
        
        return "generic"
    
    def _is_come_up_pattern(self, word: str, content: str) -> bool:
        """判断是否是come up类型（直接字母序号开始）"""
        # come up, go on 等短语词，直接以 (a) 开始
        return bool(re.match(r'^\s*\([a-z]\)\s+', content))
    
    def _is_give_up_pattern(self, word: str, content: str) -> bool:
        """判断是否是give up类型（冒号分隔，短语标题）"""
        # give up 类型：有短语标题 + 子sense，使用冒号分隔
        has_phrase = bool(re.search(r'\b\w+\s+(?:sb|sth)\s+\w+', content))
        has_letters = bool(re.search(r'\([a-z]\)', content))
        has_colons = content.count(': ') > 2
        return has_phrase and has_letters and has_colons
    
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
            # 没有数字序号，检查是否有字母序号
            letter_pattern = r'\(([a-z])\)\s+'
            letter_matches = list(re.finditer(letter_pattern, content))
            
            if letter_matches:
                # 有字母序号，检查是否后面有新词性
                last_letter_end = letter_matches[-1].end()
                remaining = content[last_letter_end:].strip()
                
                # 检查是否有新词性（通常在换行后）
                next_pos_match = re.search(r'\n\s*\b(adj|n|v|prep|adv|conj|pron|interj|det|aux|modal|art)\b\s+', remaining)
                
                if next_pos_match:
                    # 有新词性，只处理到新词性之前
                    letter_content_end = last_letter_end + next_pos_match.start()
                    letter_content = content[:letter_content_end]
                    # 解析字母序号部分
                    sub_senses = self._parse_sense_with_letters(letter_content, default_pos, None)
                    senses.extend(sub_senses)
                    # 注意：新词性部分应该由上级调用者处理（多词性解析）
                    # 这里返回，让上级继续处理剩余内容
                else:
                    # 没有新词性，解析所有字母序号
                    sub_senses = self._parse_sense_with_letters(content, default_pos, None)
                    senses.extend(sub_senses)
                return senses
            else:
                # 没有数字序号也没有字母序号，尝试解析整个内容作为一个释义
                # 遵循"不丢失内容"原则：即使解析失败，也保留原始内容
                sense = self._parse_single_sense(content, default_pos, None)
                if sense:
                    senses.append(sense)
                else:
                    # 如果解析失败，创建一个包含原始内容的sense（遵循"不丢失内容"原则）
                    fallback_sense = Sense(
                        definition=content,
                        definition_lang="zh-en",
                        pos=default_pos,
                        sense_number=None,
                        examples=[],
                        grammar_note=None
                    )
                    if hasattr(fallback_sense, 'raw_content'):
                        fallback_sense.raw_content = content
                    senses.append(fallback_sense)
                return senses
        
        # 处理每个数字序号之间的内容
        for i, match in enumerate(matches):
            sense_num = match.group(1)
            start_pos = match.end()
            
            # 找到下一个数字序号的位置（或结尾，或新词性）
            if i + 1 < len(matches):
                next_match_start = matches[i + 1].start()
            else:
                next_match_start = len(content)
            
            # 检查到下一个数字序号之间是否有新词性
            segment = content[start_pos:next_match_start]
            next_pos_match = re.search(r'\n\s*\b(adj|n|v|prep|adv|conj|pron|interj|det|aux|modal|art)\b\s+', segment)
            
            if next_pos_match:
                # 有新词性，只处理到新词性之前
                end_pos = start_pos + next_pos_match.start()
            else:
                end_pos = next_match_start
            
            sense_content = content[start_pos:end_pos].strip()
            
            if not sense_content:
                continue
            
            # 跳过分类标题（如 `* POSSESSING 有`）
            # 分类标题格式：* 大写英文单词 中文翻译
            category_title_pattern = r'^\*\s+[A-Z][A-Z\s]+\s+[\u4e00-\u9fff]+'
            if re.match(category_title_pattern, sense_content):
                # 这是分类标题，跳过
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
        # 注意：字母序号前可能有空格或换行
        letter_pattern = r'\(([a-z])\)\s+'
        letter_matches = list(re.finditer(letter_pattern, content))
        
        if not letter_matches:
            # 没有字母序号，检查是否有新词性
            # 如果内容中有换行后的新词性，应该在上级处理，这里先整个作为释义
            sense = self._parse_single_sense(content, pos, sense_num)
            if sense:
                senses.append(sense)
        else:
            # 有字母序号，分割处理
            # 先检查最后一个字母序号后是否有新词性
            last_letter_end = letter_matches[-1].end()
            remaining_after_letters = content[last_letter_end:].strip()
            
            # 检查剩余内容中是否有新词性标记（通常在换行后）
            next_pos_match = re.search(r'\n\s*\b(adj|n|v|prep|adv|conj|pron|interj|det|aux|modal|art)\b\s+', remaining_after_letters)
            
            if next_pos_match:
                # 有新词性，只处理到新词性之前的内容
                letter_end_pos = last_letter_end + next_pos_match.start()
            else:
                letter_end_pos = len(content)
            
            for i, match in enumerate(letter_matches):
                letter = match.group(1)
                start_pos = match.end()
                
                # 找到下一个字母序号或结尾（或新词性）
                if i + 1 < len(letter_matches):
                    next_match_start = letter_matches[i + 1].start()
                    end_pos = min(next_match_start, letter_end_pos)
                else:
                    end_pos = letter_end_pos
                
                sub_content = content[start_pos:end_pos].strip()
                sense_number = f"{sense_num}{letter}"
                
                sense = self._parse_single_sense(sub_content, pos, sense_number)
                if sense:
                    senses.append(sense)
        
        return senses
    
    def _parse_single_sense(self, content: str, pos: Optional[str], sense_number: Optional[str]) -> Optional[Sense]:
        """
        解析单个释义（提取定义、例句、语法说明等）
        
        原则：不丢失内容。即使解析失败，也保留原始内容。
        """
        original_content = content  # 保存原始内容，确保不丢失
        
        if not content.strip():
            # 即使为空，也返回包含原始内容的sense（遵循"不丢失内容"原则）
            sense = Sense(
                definition=original_content,
                definition_lang="zh-en",
                pos=pos,
                sense_number=sense_number,
                examples=[],
                grammar_note=None
            )
            # 如果Sense类有raw_content字段，保存原始内容
            if hasattr(sense, 'raw_content'):
                sense.raw_content = original_content
            return sense
        
        # 检查是否有IDM习语标记（义项内的IDM）
        idm_match = re.search(r'\(idm\s+习语\)|\(习语\)', content, re.I)
        idiom_title = None
        
        if idm_match:
            # 有IDM标记，提取习语短语标题和定义
            # 格式: (idm 习语) phrase_title definition: example
            idm_start = idm_match.end()
            idm_content = content[idm_start:].strip()
            
            # 查找习语短语标题（通常在IDM标记后，定义前）
            # 习语标题可能是短语（如 "the more, less, etc...the more, less, etc..."）
            # 或者简单的短语模式
            
            # 尝试识别习语标题（到冒号或定义开始）
            colon_pos = idm_content.find(': ')
            if colon_pos > 0:
                # 有冒号，标题可能在冒号前
                before_colon = idm_content[:colon_pos].strip()
                # 尝试提取习语标题（通常是短语）
                # 如果before_colon很长，可能是标题+定义
                # 查找定义开始位置（通常有中文或特定格式）
                definition_start_match = re.search(r'\([^)]*[\u4e00-\u9fff]', before_colon)
                if definition_start_match:
                    # 有定义，提取标题和定义
                    idiom_title = before_colon[:definition_start_match.start()].strip()
                    definition_text = before_colon[definition_start_match.start():].strip()
                else:
                    # 没有找到定义，整个作为标题
                    idiom_title = before_colon.strip()
                    definition_text = idm_content[colon_pos+2:].strip()
                
                # 如果标题为空，尝试提取第一个短语作为标题
                if not idiom_title:
                    # 提取到第一个括号或冒号
                    first_paren = before_colon.find('(')
                    if first_paren > 0:
                        idiom_title = before_colon[:first_paren].strip()
                        definition_text = before_colon[first_paren:].strip()
                    else:
                        # 没有括号，整个作为标题
                        idiom_title = before_colon.strip()
                        definition_text = idm_content[colon_pos+2:].strip()
            else:
                # 没有冒号，整个内容可能是标题+定义
                # 查找定义开始位置
                definition_start_match = re.search(r'\([^)]*[\u4e00-\u9fff]', idm_content)
                if definition_start_match:
                    idiom_title = idm_content[:definition_start_match.start()].strip()
                    definition_text = idm_content[definition_start_match.start():].strip()
                else:
                    # 没有找到定义，整个作为标题
                    idiom_title = idm_content.strip()
                    definition_text = ""
            
            # 将IDM标记和标题合并到内容开头
            if idiom_title:
                content = f"{idiom_title} {content[:idm_match.start()].strip()} {definition_text}".strip()
            else:
                content = content[:idm_match.start()].strip() + ' ' + definition_text
        
        # 提取语法说明 [xxx]
        grammar_note = None
        grammar_matches = re.findall(r'\[([^\]]+)\]', content)
        if grammar_matches:
            # 取第一个或合并
            grammar_note = grammar_matches[0]
            # 移除语法说明标记（只移除确认已提取的标记，遵循"不丢失内容"原则）
            # 注意：这里移除标记是合理的，因为语法说明已经提取到grammar_note字段中
            content = re.sub(r'\[([^\]]+)\]', '', content)
        
        # 提取例句
        # 1. * 开头的例句
        # 2. 冒号后的直接例句（无*标记）
        examples = []
        
        # 先识别并跳过分类标题（如 `* POSSESSING 有`、`* EXPERIENCING 体验或经历`）
        # 分类标题格式：* 大写英文单词 中文翻译（通常是单一英文单词或短语，后面是中文）
        category_title_pattern = r'\*\s+([A-Z][A-Z\s]+)\s+[\u4e00-\u9fff]+'
        category_title_match = re.search(category_title_pattern, content)
        if category_title_match:
            # 找到分类标题，从定义中移除（分类标题不是sense的一部分）
            category_title_text = category_title_match.group(0)
            content = content.replace(category_title_text, '', 1).strip()
        
        # 先提取*开头的例句（但跳过分类标题）
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
        
        # 如果没有找到*开头的例句，尝试提取冒号后的直接例句
        # 格式: 定义: 例句. 或 定义: 例句 翻译
        # 改进：更精确地识别定义后的冒号（区分定义后的冒号vs例句中的冒号）
        if not examples:
            # 查找所有冒号位置
            colon_positions = []
            pos = 0
            while True:
                pos = content.find(': ', pos)
                if pos == -1:
                    break
                colon_positions.append(pos)
                pos += 1
            
            # 找到定义后的冒号（冒号后是大写字母开头的例句）
            for col_pos in colon_positions:
                # 检查冒号前的内容（应该是定义）
                before_colon = content[:col_pos].strip()
                
                # 检查冒号后的内容
                after_colon = content[col_pos+2:].strip()
                
                # 定义后的冒号特征：
                # 1. 冒号后以大写字母开头（例句），或者以反引号+大写字母开头（如 `Ann'）
                # 2. 冒号后包含中文字符（翻译）
                # 3. 冒号前不是 ie/eg/cf/viz 等缩写（这些是例句中的冒号）
                if after_colon and (re.match(r'^[A-Z]', after_colon) or re.match(r'^[`\'"][A-Z]', after_colon)):
                    # 检查冒号前是否是缩写（避免误判例句中的冒号）
                    before_short = content[max(0, col_pos-20):col_pos].strip()
                    if re.search(r'\b(ie|eg|cf|viz)\s*$', before_short, re.I):
                        # 这是例句中的冒号（如 "13A, eg on a fuse"），跳过
                        continue
                    
                    # 提取例句（从冒号后到下一个义项或句号）
                    # 查找例句结束位置（下一个义项序号或段落结束）
                    next_sense_match = re.search(
                        r'\s+(\d+|\([a-z]\)|\w+\s+(?:sb|sth|oneself)\s+\w+)',
                        after_colon,
                        re.MULTILINE
                    )
                    
                    if next_sense_match:
                        # 找到下一个义项，例句到义项前结束
                        example_text = after_colon[:next_sense_match.start()].strip()
                    else:
                        # 没有找到下一个义项，提取到句号或段落结束
                        # 查找第一个完整的句子（包含中文字符的句号，或英文句号）
                        # 匹配模式：英文句子（可能包含反引号）+ 中文翻译 + 句号
                        sentence_end_match = re.search(
                            r'[A-Z`\'"][^.]*?[\u4e00-\u9fff][^.]*?\.|[A-Z`\'"][^.]*?\.(?=\s*[\u4e00-\u9fff]|[A-Z]|$)',
                            after_colon,
                            re.MULTILINE
                        )
                        if sentence_end_match:
                            example_text = after_colon[:sentence_end_match.end()].strip()
                            # 如果后面还有更多句子（用*分隔），也包含进来
                            remaining = after_colon[sentence_end_match.end():].strip()
                            if remaining.startswith('*'):
                                # 找到下一个*开头的例句
                                next_example_match = re.search(
                                    r'\*\s+[A-Z`\'"][^.]*?[\u4e00-\u9fff][^.]*?\.|[A-Z`\'"][^.]*?\.',
                                    remaining,
                                    re.MULTILINE
                                )
                                if next_example_match:
                                    example_text += ' ' + remaining[:next_example_match.end()].strip()
                        else:
                            # 如果没有找到完整句子，尝试提取到第一个句号
                            first_period = after_colon.find('.')
                            if first_period > 0:
                                example_text = after_colon[:first_period+1].strip()
                            else:
                                # 最后手段：取前500个字符（避免太长）
                                example_text = after_colon[:500].strip()
                    
                    # 跳过太短的（可能是定义的一部分）
                    if len(example_text) < 10:
                        continue
                    
                    # 尝试分离中英文
                    if any('\u4e00' <= c <= '\u9fff' for c in example_text):
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
                        
                        if en_text:
                            examples.append(Example(
                                text=en_text,
                                translation=zh_text if zh_text else None
                            ))
                            # 记录整个例句部分（包括冒号）
                            example_texts.append(content[col_pos:col_pos+2+len(example_text)])
                    else:
                        examples.append(Example(text=example_text))
                        example_texts.append(content[col_pos:col_pos+2+len(example_text)])
                    
                    # 只处理第一个定义后的冒号（一个sense通常只有一个定义后的冒号）
                    break
        
        # 移除例句标记，得到纯释义文本
        # 原则：只移除确认已提取的例句，对于无法确认的内容保留在定义中
        definition_text = content
        for ex_text in example_texts:
            # 验证ex_text确实存在于definition_text中（避免移除错误的内容）
            if ex_text in definition_text:
                definition_text = definition_text.replace(ex_text, '', 1).strip()
            # 如果不存在，说明提取可能有问题，保留原始内容（遵循"不丢失内容"原则）
        
        # 清理定义文本（保守策略：只移除明显的格式标记）
        # 1. 移除末尾的冒号（如果确实是定义后的冒号）
        definition_text = re.sub(r':\s*$', '', definition_text).strip()
        
        # 2. 保守地清理定义中残留的例句片段
        # 只移除确认是例句的内容（格式: 定义 例句. 翻译.）
        # 匹配模式：空格+大写字母+...句子+中文+句号（在末尾）
        # 注意：这个正则可能误匹配，所以更保守的策略是只移除确认已提取的例句
        # definition_text = re.sub(r'\s+[A-Z][^.]*?\s+[\u4e00-\u9fff][^.]*?\.\s*$', '', definition_text)
        
        # 3. 移除冒号后残留的内容（保守策略：只移除确认是例句的内容）
        # 查找定义后的冒号，如果冒号后还有内容，检查是否是已提取的例句
        colon_pos = definition_text.rfind(': ')
        if colon_pos > 0:
            after_colon = definition_text[colon_pos+2:].strip()
            # 如果冒号后是大写字母开头，可能是残留的例句
            if after_colon and re.match(r'^[A-Z]', after_colon):
                # 检查是否是缩写后的冒号
                before_short = definition_text[max(0, colon_pos-20):colon_pos].strip()
                if not re.search(r'\b(ie|eg|cf|viz)\s*$', before_short, re.I):
                    # 检查这个内容是否已经在examples中（确认是例句）
                    is_extracted_example = any(
                        after_colon[:50] in ex.text or ex.text[:50] in after_colon 
                        for ex in examples
                    )
                    if is_extracted_example:
                        # 确认是已提取的例句，可以移除
                        definition_text = definition_text[:colon_pos].strip()
                    # 如果不是已提取的例句，保留在定义中（遵循"不丢失内容"原则）
        
        # 4. 移除末尾的标点和多余内容（保守策略：只移除明显的格式标记）
        definition_text = re.sub(r'\s*,\s*$', '', definition_text)
        definition_text = re.sub(r'\s+', ' ', definition_text).strip()
        
        # 5. 移除开头的 ~ 符号（代表词头，这是格式标记，可以安全移除）
        definition_text = re.sub(r'^~\s*', '', definition_text)
        
        # 6. 再次清理末尾的标点（保守策略：只移除明显的格式标记）
        definition_text = re.sub(r'[:，。、]$', '', definition_text).strip()
        
        # 确保至少保留原始内容（遵循"不丢失内容"原则）
        if not definition_text:
            definition_text = original_content
        
        # 即使解析失败，也返回sense（遵循"不丢失内容"原则）
        return Sense(
            definition=definition_text if definition_text else original_content,
            definition_lang="zh-en",
            pos=pos,
            sense_number=sense_number,
            examples=examples,
            grammar_note=grammar_note,
            raw_content=original_content  # 保存原始内容，便于调试和恢复
        )
    
    def _parse_come_up_case(self, content: str, default_pos: Optional[str] = None) -> List[Sense]:
        """
        解析 come up 类型：直接以字母序号开始
        
        格式: (a) 定义: 例句 (b) 定义: 例句 ... come up (to...) 定义: 例句
        """
        senses = []
        
        if not content.strip():
            return senses
        
        # 1. 先处理字母序号系列 (a)-(g)
        letter_pattern = r'\(([a-z])\)\s+'
        letter_matches = list(re.finditer(letter_pattern, content))
        
        # 找到字母序号系列的结束位置（第一个变体短语标题）
        # 注意：变体短语也是 "come up" 开头，但后面有更多内容
        phrase_pattern = r'\bcome\s+up\s+(?:`)?(?:\([^)]+\)\s*)*\b(?:to|against|for|with)\b'
        phrase_match = re.search(phrase_pattern, content)
        letter_end_pos = phrase_match.start() if phrase_match else len(content)
        
        # 处理字母序号系列
        if letter_matches:
            for i, match in enumerate(letter_matches):
                # 只处理在字母序号系列范围内的
                if match.start() > letter_end_pos:
                    break
                
                letter = match.group(1)
                start_pos = match.end()
                
                # 找到下一个字母序号或短语标题
                next_letter_pos = None
                if i + 1 < len(letter_matches):
                    next_match = letter_matches[i + 1]
                    if next_match.start() <= letter_end_pos:
                        next_letter_pos = next_match.start()
                
                if next_letter_pos:
                    end_pos = next_letter_pos
                elif phrase_match:
                    end_pos = phrase_match.start()
                else:
                    end_pos = len(content)
                
                sense_content = content[start_pos:end_pos].strip()
                sense = self._parse_single_sense(sense_content, default_pos, letter)  # 无主编号
                if sense:
                    senses.append(sense)
        
        # 2. 处理变体短语部分
        if phrase_match:
            phrase_content = content[phrase_match.start():].strip()
            phrase_senses = self._parse_variant_phrases(phrase_content, default_pos, len(senses))
            senses.extend(phrase_senses)
        
        return senses
    
    def _parse_give_up_case(self, content: str, default_pos: Optional[str] = None) -> List[Sense]:
        """
        解析 give up 类型：冒号分隔，短语标题+子sense
        
        格式: 定义: 例句 give sb up (a) 定义: 例句 (b) 定义: 例句 ...
        """
        senses = []
        
        if not content.strip():
            return senses
        
        # 策略：先识别短语标题，然后按短语标题分割
        # 找到所有短语标题的位置
        phrase_pattern = r'\b(give\s+(?:sb|sth|oneself)\s+\w+)\s+'
        phrase_matches = list(re.finditer(phrase_pattern, content))
        
        if not phrase_matches:
            # 没有短语标题，尝试按冒号分割
            sense_parts = self._split_by_definition_colon(content)
            for i, part in enumerate(sense_parts):
                sense = self._parse_single_sense(part.strip(), default_pos, str(i+1) if i > 0 else None)
                if sense:
                    senses.append(sense)
            return senses
        
        # 处理第一个sense（短语标题之前）
        first_phrase_pos = phrase_matches[0].start()
        first_part = content[:first_phrase_pos].strip()
        if first_part:
            sense = self._parse_single_sense(first_part, default_pos, None)
            if sense:
                senses.append(sense)
        
        # 处理每个短语标题及其内容
        for i, match in enumerate(phrase_matches):
            phrase_title = match.group(1).strip()
            start_pos = match.end()
            
            # 找到下一个短语标题或结尾
            if i + 1 < len(phrase_matches):
                end_pos = phrase_matches[i + 1].start()
            else:
                end_pos = len(content)
            
            phrase_content = content[start_pos:end_pos].strip()
            
            # 检查是否有子sense (a), (b)
            if re.search(r'\([a-z]\)\s+', phrase_content):
                # 有子sense
                sense_num = str(len(senses) + 1)
                sub_senses = self._parse_sub_senses(phrase_content, default_pos, phrase_title, sense_num)
                senses.extend(sub_senses)
            else:
                # 无子sense，直接解析
                sense = self._parse_single_sense(phrase_content, default_pos, str(len(senses) + 1))
                if sense:
                    # 将短语标题加入定义
                    if sense.definition:
                        sense.definition = f"{phrase_title} {sense.definition}"
                    else:
                        sense.definition = phrase_title
                    senses.append(sense)
        
        return senses
    
    def _parse_variant_phrases(self, content: str, default_pos: Optional[str], start_index: int) -> List[Sense]:
        """
        解析变体短语部分
        
        格式: come up (to...) (Brit) 定义: 例句 come up to sth (a) 定义 (b) 定义
        """
        senses = []
        
        # 识别短语标题（以 come up 开头的变体）
        # 模式：come up + 可选重音 + 可选括号参数 + 关键词（to/against/for/with/sb/sth等）
        phrase_pattern = r'come\s+up\s+(?:`)?(?:\([^)]+\)\s*)*(?:to|against|for|with|sb|sth|oneself|\w+)'
        
        # 找到所有可能的短语标题开始位置
        # 更精确的模式：come up 后跟特定关键词
        phrase_keywords = [
            r'come\s+up\s+(?:`)?(?:\([^)]+\)\s*)*(?:\([^)]+\)\s*)*(?:Brit|US)',
            r'come\s+up\s+(?:`)?(?:\([^)]+\)\s*)*(?:to|against|for|with)\b',
            r'come\s+up\s+(?:`)?(?:\([^)]+\)\s*)*to\s+sth',
        ]
        
        phrase_matches = []
        for pattern in phrase_keywords:
            matches = list(re.finditer(pattern, content))
            phrase_matches.extend(matches)
        
        # 去重并按位置排序
        phrase_matches = sorted(set(phrase_matches), key=lambda m: m.start())
        
        if not phrase_matches:
            # 没有识别到短语，尝试按冒号分割
            colon_parts = self._split_by_definition_colon(content)
            for i, part in enumerate(colon_parts):
                sense = self._parse_single_sense(part.strip(), default_pos, str(start_index + i + 1))
                if sense:
                    senses.append(sense)
            return senses
        
        # 处理每个短语标题
        for i, match in enumerate(phrase_matches):
            # 提取短语标题（到第一个空格或括号后的内容之前）
            match_end = match.end()
            # 找到短语标题的结束位置（通常是空格或括号前的关键词）
            title_end_match = re.search(r'\s+(?:\([^)]+\)|\([A-Z][a-z]+\)|begin|be|come|find)', content[match_end:match_end+100])
            if title_end_match:
                phrase_title = content[match.start():match_end + title_end_match.start()].strip()
                start_pos = match_end + title_end_match.start()
            else:
                # 简化：取匹配的前50个字符作为标题
                phrase_title = content[match.start():match.end()].strip()
                start_pos = match.end()
            
            # 找到下一个短语标题或结尾
            if i + 1 < len(phrase_matches):
                end_pos = phrase_matches[i + 1].start()
            else:
                end_pos = len(content)
            
            phrase_content = content[start_pos:end_pos].strip()
            
            # 检查是否有子sense (a), (b)
            if re.search(r'\([a-z]\)\s+', phrase_content):
                # 有子sense
                sense_num = str(start_index + len(senses) + 1)
                sub_senses = self._parse_sub_senses(phrase_content, default_pos, phrase_title, sense_num)
                senses.extend(sub_senses)
            else:
                # 无子sense，直接解析
                sense = self._parse_single_sense(phrase_content, default_pos, str(start_index + len(senses) + 1))
                if sense:
                    # 将短语标题加入定义
                    if sense.definition:
                        sense.definition = f"{phrase_title} {sense.definition}"
                    else:
                        sense.definition = phrase_title
                    senses.append(sense)
        
        return senses
    
    def _parse_sub_senses(self, content: str, pos: Optional[str], parent_title: Optional[str], parent_num: Optional[str]) -> List[Sense]:
        """
        解析子sense (a), (b) 等
        
        Args:
            content: 包含子sense的内容
            pos: 词性
            parent_title: 父标题（如 "give sb up"）
            parent_num: 父编号（如 "1"）
        """
        senses = []
        
        letter_pattern = r'\(([a-z])\)\s+'
        letter_matches = list(re.finditer(letter_pattern, content))
        
        if not letter_matches:
            # 没有字母序号，整个作为一个sense
            sense = self._parse_single_sense(content, pos, parent_num)
            if sense:
                if parent_title and not sense.definition.startswith(parent_title):
                    sense.definition = f"{parent_title} {sense.definition}" if sense.definition else parent_title
                senses.append(sense)
            return senses
        
        for i, match in enumerate(letter_matches):
            letter = match.group(1)
            start_pos = match.end()
            
            # 找到下一个字母序号或结尾
            if i + 1 < len(letter_matches):
                end_pos = letter_matches[i + 1].start()
            else:
                end_pos = len(content)
            
            sub_content = content[start_pos:end_pos].strip()
            
            # 构建sense_number
            if parent_num:
                sense_number = f"{parent_num}{letter}"
            elif parent_title:
                sense_number = f"{parent_title}({letter})"
            else:
                sense_number = letter
            
            sense = self._parse_single_sense(sub_content, pos, sense_number)
            if sense:
                # 如果父标题不在定义中，添加它
                if parent_title and parent_title not in sense.definition:
                    sense.definition = f"{parent_title} {sense.definition}"
                senses.append(sense)
        
        return senses
    
    def _split_by_definition_colon(self, content: str) -> List[str]:
        """
        使用智能冒号分割sense
        
        定义后的冒号通常在句子结尾，后面是例句
        例句中的冒号通常在句子中间
        
        策略：
        1. 找到所有冒号位置
        2. 判断哪些是定义后的冒号（sense分隔符）
        3. 根据冒号分割
        """
        parts = []
        
        # 策略：查找 "定义: " 模式，定义后通常跟着例句（大写字母开头）
        # 但例句中的冒号后面可能是小写或数字
        
        # 找到所有 ": " 的位置
        colon_positions = []
        pos = 0
        while True:
            pos = content.find(': ', pos)
            if pos == -1:
                break
            colon_positions.append(pos)
            pos += 1
        
        if not colon_positions:
            # 没有冒号，返回整个内容
            return [content]
        
        # 判断哪些冒号是sense分隔符
        sense_colons = []
        last_pos = 0
        
        for col_pos in colon_positions:
            # 检查冒号前的内容
            before_colon = content[last_pos:col_pos].strip()
            
            # 检查是否是短语标题或sense的开始
            # 如: "give sb up (a)" 或 "定义文本"
            if re.search(r'(?:^|\s)(\d+|\([a-z]\)|\w+\s+(?:sb|sth)\s+\w+)', before_colon) or last_pos == 0:
                # 检查冒号后的内容
                after_colon = content[col_pos+2:col_pos+50].strip()
                
                # 定义后的冒号通常跟着：
                # 1. 大写字母开头的句子（例句）
                # 2. 中文
                # 3. 不是指代符号的标记
                if re.match(r'[A-Z\u4e00-\u9fff]', after_colon):
                    # 不是指代符号
                    before_short = content[max(0, col_pos-10):col_pos].strip()
                    if not re.search(r'\b(ie|eg|cf|viz)\s*$', before_short, re.I):
                        sense_colons.append(col_pos)
            
            last_pos = col_pos + 2
        
        # 按sense分隔符分割
        if not sense_colons:
            # 没有找到sense分隔符，返回整个内容
            return [content]
        
        last_pos = 0
        for col_pos in sense_colons:
            # 找到下一个sense的开始位置（数字序号、字母序号、短语标题）
            next_sense_match = re.search(
                r'(?:^|\s)(\d+|\([a-z]\)|\w+\s+(?:sb|sth|oneself)\s+\w+)',
                content[col_pos+2:],
                re.MULTILINE
            )
            
            if next_sense_match:
                part_end = col_pos + 2 + next_sense_match.start()
            else:
                part_end = len(content)
            
            part = content[last_pos:part_end].strip()
            if part:
                parts.append(part)
            last_pos = part_end
        
        # 添加最后一部分
        if last_pos < len(content):
            parts.append(content[last_pos:].strip())
        
        return parts if parts else [content]
    
    def _parse_generic_case(self, content: str, default_pos: Optional[str] = None) -> List[Sense]:
        """通用解析（fallback）"""
        # 尝试多种策略
        senses = []
        
        # 策略1: 尝试按数字序号
        senses = self._parse_main_senses(content, default_pos)
        if senses:
            return senses
        
        # 策略2: 尝试按字母序号
        if re.search(r'\([a-z]\)', content):
            senses = self._parse_come_up_case(content, default_pos)
            if senses:
                return senses
        
        # 策略3: 尝试按冒号分隔
        if content.count(': ') > 1:
            senses = self._parse_give_up_case(content, default_pos)
            if senses:
                return senses
        
        # 策略4: 整个作为一个sense
        sense = self._parse_single_sense(content, default_pos, None)
        if sense:
            return [sense]
        
        return []
    
    def _parse_idm_section(self, content: str) -> List[Sense]:
        """
        解析IDM（习语）部分
        
        格式: (idm 习语) phrase_title definition: example phrase_title definition: example ...
        
        每个习语短语的结构：
        - 短语标题（如 `be the making of sb` 或 `A1`）
        - 可选音标（如 `/ 7eI 5wQn; e`wQn/`）
        - 定义（中英文）
        - 冒号
        - 例句（可能多个，用*分隔）
        
        策略：
        1. 识别每个习语短语的边界（通过短语标题模式）
        2. 提取短语标题、定义和例句
        3. 创建related_phrases
        """
        senses = []
        
        if not content.strip():
            return senses
        
        # 移除IDM标记
        content = re.sub(r'\bIDM\b|\(idm\s+习语\)|\(习语\)', '', content, flags=re.I).strip()
        
        # 策略1: 如果包含数字序号或字母序号，按序号分割
        if re.search(r'\s(\d+|\([a-z]\))\s+', content):
            # 有序号，使用标准解析
            return self._parse_main_senses(content, None)
        
        # 策略2: 识别习语短语（通过短语标题模式）
        # 习语短语的结构：短语标题 + 定义 + 冒号 + 例句
        # 每个习语短语之间没有明确的分隔符，需要通过短语标题来识别
        
        # 第一步：找到所有习语短语标题
        # 习语短语标题的特征：
        # 1. 以小写字母开头（如 `be the making of sb`, `have the makings of sth`）
        # 2. 介词短语（如 `in the making`, `from A to B`）
        # 3. 或大写字母开头（如 `A1`）
        
        # 找到所有可能的短语标题开始位置
        # 模式1: 动词短语（如 `be the making of sb`, `have the makings of sth`）
        # 模式2: 介词短语（如 `in the making`, `from A to B`）
        # 模式3: 单个单词（如 `A1`）
        
        # 先找到所有冒号位置（定义后的冒号）
        colon_positions = []
        pos = 0
        while True:
            pos = content.find(': ', pos)
            if pos == -1:
                break
            # 检查冒号后是否是大写字母开头的例句
            after_colon = content[pos+2:pos+50].strip()
            if after_colon and (re.match(r'^[A-Z`]', after_colon) or re.match(r'^[a-z][^:]*[\u4e00-\u9fff]', after_colon)):
                # 这是定义后的冒号
                # 检查冒号前是否是缩写（如 `ie`, `eg`）
                before_short = content[max(0, pos-20):pos].strip()
                if not re.search(r'\b(ie|eg|cf|viz)\s*$', before_short, re.I):
                    colon_positions.append(pos)
            pos += 1
        
        if not colon_positions:
            # 没有找到冒号，尝试按其他模式分割
            sense = self._parse_single_sense(content, None, "1")
            if sense:
                senses.append(sense)
            return senses
        
        # 第二步：对于每个冒号，向前查找短语标题，向后查找例句结束位置
        for i, col_pos in enumerate(colon_positions):
            # 确定查找范围：从上一个冒号后（或开头）到当前冒号前
            if i == 0:
                search_start = 0
            else:
                search_start = colon_positions[i-1] + 2
            
            before_colon = content[search_start:col_pos].strip()
            
            # 在冒号前查找短语标题（尝试多种模式）
            phrase_title = None
            title_start = None
            
            # 模式1: 动词短语（如 `be the making of sb`, `have the makings of sth`）
            title_match = re.search(
                r'\b(be\s+the\s+\w+\s+of\s+sb|have\s+the\s+\w+\s+of\s+sth|have\s+it\s+\w+|do\s+\w+\s+sth)\b',
                before_colon,
                re.I
            )
            
            # 模式2: 介词短语（如 `in the making`, `from A to B`）
            # 注意：要匹配 `in the `making`（带反引号）但不匹配例句中的 `in the making`
            if not title_match:
                # 查找 `in the` 后跟反引号+单词或直接跟单词
                title_match = re.search(
                    r'\b(in\s+the\s+`?\w+|from\s+\w+\s+to\s+\w+|on\s+the\s+\w+|at\s+the\s+\w+)\b',
                    before_colon,
                    re.I
                )
            
            # 模式3: 单个单词或短语（如 `A1`, `from A to B`）
            if not title_match:
                title_match = re.search(
                    r'\b([A-Z]\w*(?:\s+to\s+[A-Z]\w*)?)\b',
                    before_colon
                )
            
            if title_match:
                phrase_title = title_match.group(1).strip()
                title_start = title_match.start() + search_start
                # 定义在短语标题后，到冒号前
                definition_start = title_match.end() + search_start
                definition = content[definition_start:col_pos].strip()
            else:
                # 没找到标题，整个作为定义
                phrase_title = ""
                definition = before_colon.strip()
            
            # 提取冒号后的例句（到下一个习语短语开始或段落结束）
            after_colon = content[col_pos+2:].strip()
            
            # 找到例句结束位置（下一个习语短语开始或段落结束）
            # 策略：先提取例句（到句号），然后查找下一个习语短语标题
            if i + 1 < len(colon_positions):
                # 在下一个冒号前查找例句和下一个短语标题
                next_col_pos = colon_positions[i + 1]
                text_between_colons = content[col_pos+2:next_col_pos].strip()
                
                # 先提取例句（到句号或下一个短语标题）
                # 查找第一个完整的句子（包含中文字符的句号）
                sentence_end_match = re.search(
                    r'[A-Z`][^.]*?[\u4e00-\u9fff][^.]*?\.|^[A-Z`][^.]*?\.',
                    text_between_colons,
                    re.MULTILINE
                )
                
                if sentence_end_match:
                    # 找到第一个句子结束位置
                    first_sentence_end = sentence_end_match.end()
                    
                    # 检查第一个句子后是否有*（表示多个例句）
                    remaining = text_between_colons[first_sentence_end:].strip()
                    if remaining.startswith('*'):
                        # 有多个例句，继续查找
                        # 找到下一个*后的句子
                        next_example_match = re.search(
                            r'\*\s+[A-Z`][^.]*?[\u4e00-\u9fff][^.]*?\.|^[A-Z`][^.]*?\.',
                            remaining,
                            re.MULTILINE
                        )
                        if next_example_match:
                            example_end = first_sentence_end + next_example_match.end()
                        else:
                            example_end = first_sentence_end
                    else:
                        example_end = first_sentence_end
                    
                    # 检查例句后是否有下一个习语短语标题（小写字母开头）
                    after_examples = text_between_colons[example_end:].strip()
                    
                    # 查找下一个短语标题（不以大写字母开头的单个单词，除非是特定的习语模式）
                    next_title_match = re.search(
                        r'\b(be\s+the\s+\w+\s+of\s+sb|have\s+the\s+\w+\s+of\s+sth|have\s+it\s+\w+|do\s+\w+\s+sth|in\s+the\s+`?\w+|from\s+\w+\s+to\s+\w+|on\s+the\s+\w+|at\s+the\s+\w+)\b',
                        after_examples,
                        re.I
                    )
                    
                    if next_title_match:
                        # 找到下一个短语标题，例句只到example_end
                        example_text = text_between_colons[:example_end].strip()
                    else:
                        # 没找到，例句到example_end
                        example_text = text_between_colons[:example_end].strip()
                else:
                    # 没找到完整句子，尝试其他方式
                    # 查找下一个习语短语标题（不以大写字母开头的单个单词）
                    next_title_match = re.search(
                        r'\b(be\s+the\s+\w+\s+of\s+sb|have\s+the\s+\w+\s+of\s+sth|have\s+it\s+\w+|do\s+\w+\s+sth|in\s+the\s+`?\w+|from\s+\w+\s+to\s+\w+|on\s+the\s+\w+|at\s+the\s+\w+)\b',
                        text_between_colons,
                        re.I
                    )
                    
                    if next_title_match:
                        # 找到下一个短语标题，例句到标题前结束
                        example_text = text_between_colons[:next_title_match.start()].strip()
                    else:
                        # 没找到，例句到下一个冒号前
                        example_text = text_between_colons.strip()
            else:
                # 最后一个短语，例句到段落结束
                example_text = after_colon.strip()
            
            # 移除定义中的音标（如果有）
            phonetic_match = re.search(r'/\s*[^/]+\s*/\s*', definition)
            if phonetic_match:
                # 移除音标
                definition = definition[:phonetic_match.start()].strip() + ' ' + definition[phonetic_match.end():].strip()
            
            # 清理定义文本
            definition = definition.strip()
            
            # 创建sense（作为related_phrase）
            # 这里我们创建一个sense，但可以后续转换为related_phrase
            sense = Sense(
                definition=definition if definition else phrase_title,
                definition_lang="zh-en",
                pos=None,  # 习语通常继承父词性
                sense_number=str(i+1),
            )
            
            # 解析例句（可能多个，用*分隔）
            if example_text:
                # 分割多个例句（用*分隔）
                example_parts = re.split(r'\s*\*\s+', example_text)
                for ex_part in example_parts:
                    ex_part = ex_part.strip()
                    if not ex_part:
                        continue
                    
                    # 提取到句号结束（如果还没有提取到句号）
                    if '.' not in ex_part or not ex_part.strip().endswith('.'):
                        period_pos = ex_part.find('.')
                        if period_pos > 0:
                            ex_part = ex_part[:period_pos+1].strip()
                    
                    # 尝试分离中英文
                    if any('\u4e00' <= c <= '\u9fff' for c in ex_part):
                        parts = ex_part.split()
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
                        
                        if en_text:
                            from ..models.entry import Example
                            sense.examples.append(Example(
                                text=en_text,
                                translation=zh_text if zh_text else None
                            ))
                    else:
                        if ex_part:
                            from ..models.entry import Example
                            sense.examples.append(Example(text=ex_part))
            
            # 添加短语标题到定义的开始（如果存在）
            if phrase_title:
                sense.definition = f"{phrase_title} {sense.definition}".strip()
            
            senses.append(sense)
        
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

