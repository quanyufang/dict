#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
现代汉语词典解析器

格式特点（基于样例分析）：
1. 拼音: yī, rén (第一行，带声调)
2. 部首笔画: BS 一 | BH 0 (BS=部首, BH=笔画)
3. 序号: ①②③ (圆圈数字)
4. 词性: 〈名〉〈动〉〈形〉〈副〉 (尖括号)
5. 波浪线: ～ (代表词头)
6. 多读音: 同一字可能有多个读音（如"一"有yī、yí、yì）
7. 交叉引用: 见'一'（yī）

样例：
yī
BS 一 | BH 0
一1
①数目，最小的正整数。参看〖数字〗。
②同一：～视同仁│咱们是～家人│你们～路走│这不是～码事。
...
"""

import re
from typing import Optional, List
from ..models.entry import (
    DictionaryEntry, Pronunciation, Sense, Example,
    PartOfSpeech
)
from .base import BaseParser


class XiandaihanyucidianParser(BaseParser):
    """现代汉语词典解析器"""
    
    # 词性映射（现代汉语词典使用的词性标记）
    POS_MAP = {
        '名': '名',      # 名词
        '动': '动',      # 动词
        '形': '形',      # 形容词
        '副': '副',      # 副词
        '量': '量',      # 量词
        '代': '代',      # 代词
        '数': '数',      # 数词
        '助': '助',      # 助词
        '介': 'prep',    # 介词
        '连': 'conj',    # 连词
        '叹': 'interj',  # 叹词
        '拟': 'interj',  # 拟声词
        '书': 'fml',     # 书面语标记
        '方': 'dial',    # 方言标记
        '古': 'arch',    # 古语标记
    }
    
    # 圆圈数字映射
    CIRCLED_NUMBERS = {
        '①': '1', '②': '2', '③': '3', '④': '4', '⑤': '5',
        '⑥': '6', '⑦': '7', '⑧': '8', '⑨': '9', '⑩': '10',
        '⑪': '11', '⑫': '12', '⑬': '13', '⑭': '14', '⑮': '15',
        '⑯': '16', '⑰': '17', '⑱': '18', '⑲': '19', '⑳': '20',
    }
    
    @property
    def source_id(self) -> str:
        return "xiandaihanyucidian"
    
    @property
    def name(self) -> str:
        return "现代汉语词典"
    
    @property
    def index_language(self) -> str:
        return "zh"
    
    @property
    def explanation_language(self) -> str:
        return "zh"
    
    def parse(self, word: str, raw_content: str) -> Optional[DictionaryEntry]:
        """解析现代汉语词典条目"""
        if not raw_content or not raw_content.strip():
            return None
        
        entry = DictionaryEntry(
            headword=word,
            source_id=self.source_id,
            raw_content=raw_content,
        )
        
        content = raw_content.strip()
        
        # 1. 解析拼音（第一行，通常是拼音，可能包含多个读音）
        lines = content.split('\n')
        first_line = lines[0].strip() if lines else ""
        
        # 检查是否是拼音（通常不包含中文字符或特殊标记）
        pinyin_line = first_line
        if 'BS' in first_line or 'BH' in first_line:
            # 第一行不是拼音，跳过
            pinyin_line = None
        elif any('\u4e00' <= c <= '\u9fff' for c in first_line):
            # 包含中文字符，不是纯拼音
            pinyin_line = None
        
        # 提取拼音（支持多个读音，用换行或空格分隔）
        if pinyin_line:
            # 拼音可能包含多个读音，如 "yī\nyí\nyì"
            pinyin_list = []
            for line in lines[:3]:  # 检查前3行，找到拼音
                line = line.strip()
                if not line or 'BS' in line or 'BH' in line:
                    break
                if not any('\u4e00' <= c <= '\u9fff' for c in line):
                    # 不包含中文字符，可能是拼音
                    # 检查是否是拼音格式（包含字母和声调符号）
                    if re.match(r'^[a-zāáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜ]+$', line, re.I):
                        pinyin_list.append(line)
            
            if pinyin_list:
                # 使用第一个读音作为主拼音
                entry.pinyin = pinyin_list[0]
                # 如果有多个读音，可以存储在某个字段中（当前模型没有多拼音字段，暂时忽略）
        
        # 2. 解析部首和笔画（BS 一 | BH 0）
        radical = None
        strokes = None
        bs_match = re.search(r'BS\s+([^\|]+?)\s*\|\s*BH\s+(\d+)', content)
        if bs_match:
            radical = bs_match.group(1).strip()
            strokes = int(bs_match.group(2))
            entry.radical = radical
            entry.strokes = strokes
        
        # 3. 查找多读音部分（如"◆ 一\nyí\nBS..."）
        # 如果有多个读音，会有"◆"标记分隔
        parts = re.split(r'\n\s*◆\s*\n', content)
        
        # 如果只有一个部分，直接解析
        if len(parts) == 1:
            senses = self._parse_senses(parts[0], entry.pinyin)
            entry.senses.extend(senses)
        else:
            # 多个读音部分，分别解析
            for i, part in enumerate(parts):
                part = part.strip()
                if not part:
                    continue
                
                # 提取这个读音的拼音
                part_lines = part.split('\n')
                part_pinyin = None
                if part_lines:
                    first_part_line = part_lines[0].strip()
                    # 检查是否是拼音
                    if not any('\u4e00' <= c <= '\u9fff' for c in first_part_line) and \
                       re.match(r'^[a-zāáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜ]+$', first_part_line, re.I):
                        part_pinyin = first_part_line
                
                # 解析这个读音的释义
                part_senses = self._parse_senses(part, part_pinyin)
                entry.senses.extend(part_senses)
                
                # 如果是第一个读音，更新主拼音
                if i == 0 and part_pinyin and not entry.pinyin:
                    entry.pinyin = part_pinyin
        
        # 4. 处理交叉引用（如"见'一'（yī）"）
        cross_ref_match = re.search(r"见['""]?([^'""（）]+)['""]?（([^）]+)）", content)
        if cross_ref_match and not entry.senses:
            # 只有交叉引用，没有释义
            sense = Sense(
                definition=f"见'{cross_ref_match.group(1)}'（{cross_ref_match.group(2)}）",
                definition_lang="zh",
                sense_number=None,
            )
            entry.senses.append(sense)
        
        # 设置解析质量
        if not entry.senses:
            entry.parse_quality = 0.3
            entry.parse_notes.append("未解析到释义")
        elif not entry.pinyin:
            entry.parse_quality = 0.7
            entry.parse_notes.append("未解析到拼音")
        else:
            entry.parse_quality = 0.9
        
        return entry
    
    def _parse_senses(self, content: str, default_pinyin: Optional[str] = None) -> List[Sense]:
        """解析释义部分"""
        senses = []
        
        if not content.strip():
            return senses
        
        # 移除拼音行和部首笔画行
        lines = content.split('\n')
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            # 跳过拼音行（如果已经提取过）
            if default_pinyin and line == default_pinyin:
                continue
            # 跳过部首笔画行
            if 'BS' in line or 'BH' in line:
                continue
            cleaned_lines.append(line)
        
        content = '\n'.join(cleaned_lines)
        
        # 查找所有圆圈数字序号（①②③等）
        circled_num_pattern = r'([①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳])'
        matches = list(re.finditer(circled_num_pattern, content))
        
        if not matches:
            # 没有序号，检查是否有词性标记或其他结构
            # 尝试解析整个内容作为一个释义
            sense = self._parse_single_sense(content, None, None, default_pinyin)
            if sense:
                senses.append(sense)
            return senses
        
        # 处理每个序号之间的内容
        for i, match in enumerate(matches):
            sense_num = match.group(1)
            sense_number = self.CIRCLED_NUMBERS.get(sense_num, sense_num)
            start_pos = match.end()
            
            # 找到下一个序号的位置
            if i + 1 < len(matches):
                next_match_start = matches[i + 1].start()
            else:
                next_match_start = len(content)
            
            sense_content = content[start_pos:next_match_start].strip()
            
            if not sense_content:
                continue
            
            # 解析单个释义
            sense = self._parse_single_sense(sense_content, None, sense_number, default_pinyin)
            if sense:
                senses.append(sense)
        
        return senses
    
    def _parse_single_sense(self, content: str, pos: Optional[str], 
                           sense_number: Optional[str], 
                           default_pinyin: Optional[str] = None) -> Optional[Sense]:
        """解析单个释义"""
        if not content.strip():
            return None
        
        original_content = content
        
        # 提取词性标记（〈名〉〈动〉等）
        pos_matches = re.findall(r'〈([^〉]+)〉', content)
        if pos_matches:
            # 使用第一个词性标记
            pos_marker = pos_matches[0]
            pos = self.POS_MAP.get(pos_marker, pos_marker)
            # 移除词性标记
            content = re.sub(r'〈[^〉]+〉', '', content).strip()
        
        # 提取例句（冒号后的内容）
        examples = []
        # 例句格式：释义：例句│例句
        if '：' in content or ':' in content:
            colon_pos = content.find('：') if '：' in content else content.find(':')
            definition = content[:colon_pos].strip()
            example_text = content[colon_pos+1:].strip()
            
            # 分割多个例句（用│分隔）
            example_parts = example_text.split('│')
            for ex_part in example_parts:
                ex_part = ex_part.strip()
                if ex_part:
                    # 替换～为词头
                    if '～' in ex_part:
                        # 需要知道词头才能替换，这里暂时保留～
                        pass
                    examples.append(Example(
                        text=ex_part,
                        translation=None
                    ))
        else:
            definition = content.strip()
        
        # 清理定义文本
        # 移除波浪线（暂时保留，后续可以替换为词头）
        definition = definition.strip()
        # 移除末尾的标点
        definition = re.sub(r'[。，、；：]$', '', definition).strip()
        
        # 检查是否有交叉引用
        cross_ref_match = re.search(r"见['""]?([^'""（）]+)['""]?（([^）]+)）", definition)
        if cross_ref_match:
            definition = f"见'{cross_ref_match.group(1)}'（{cross_ref_match.group(2)}）"
        
        # 提取特殊标记（〖数字〗等）
        # 这些是交叉引用标记，可以保留在定义中
        
        return Sense(
            definition=definition if definition else original_content,
            definition_lang="zh",
            pos=pos,
            sense_number=sense_number,
            examples=examples,
            raw_content=original_content
        )


# 测试代码
if __name__ == '__main__':
    import sys
    from pathlib import Path
    
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    
    parser = XiandaihanyucidianParser()
    
    # 测试样例
    test_content = """yī
BS 一 | BH 0
一1
①数目，最小的正整数。参看〖数字〗。
②同一：～视同仁│咱们是～家人│你们～路走│这不是～码事。
③另一：番茄～名西红柿。
④全；满：～冬│～生│～路平安│～屋子人│～身的汗。
⑤专一：～心～意。"""
    
    entry = parser.parse("一", test_content)
    
    if entry:
        print(f"词头: {entry.headword}")
        print(f"拼音: {entry.pinyin}")
        print(f"部首: {entry.radical}, 笔画: {entry.strokes}")
        print(f"释义数: {len(entry.senses)}")
        for i, sense in enumerate(entry.senses[:3]):
            print(f"\n[{i+1}] #{sense.sense_number} {sense.pos or '-'}")
            print(f"    定义: {sense.definition[:60]}...")
            if sense.examples:
                print(f"    例句: {len(sense.examples)}个")
    else:
        print("解析失败!")

