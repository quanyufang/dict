#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一词典数据模型

基于实际词典样例分析设计，各词典独立存储但格式统一。
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Union
from enum import Enum
import json


class PartOfSpeech(Enum):
    """词性枚举 - 基于实际词典中出现的词性"""
    # 英文词性
    NOUN = "n"
    VERB = "v"
    VERB_INTRANS = "v.i."      # 不及物动词 (GCIDE)
    VERB_TRANS = "v.t."         # 及物动词 (GCIDE)
    ADJECTIVE = "adj"
    ADVERB = "adv"
    PRONOUN = "pron"
    PREPOSITION = "prep"
    CONJUNCTION = "conj"
    INTERJECTION = "interj"
    ARTICLE = "art"
    DETERMINER = "det"
    AUXILIARY = "aux"
    MODAL = "modal"
    
    # 中文词性 (现汉格式)
    MING = "名"                  # 名词
    DONG = "动"                  # 动词
    XING = "形"                  # 形容词
    FU = "副"                    # 副词
    LIANG = "量"                 # 量词
    DAI = "代"                   # 代词
    SHU = "数"                   # 数词
    ZHU = "助"                   # 助词
    
    # 特殊类型
    PHRASAL_VERB = "phr.v"       # 动词短语
    IDIOM = "idiom"              # 习语/成语
    PHRASE = "phrase"            # 短语
    PREFIX = "prefix"
    SUFFIX = "suffix"
    ABBREVIATION = "abbr"
    
    UNKNOWN = "unknown"


class Domain(Enum):
    """领域/学科 - 基于朗道词典的【】标签"""
    GENERAL = "general"          # 通用
    ECONOMICS = "经"             # 经济
    COMPUTING = "计"             # 计算机
    MEDICAL = "医"               # 医学
    MECHANICAL = "机"            # 机械
    LAW = "法"                   # 法律
    CHEMISTRY = "化"             # 化学
    BIOLOGY = "生"               # 生物
    PHYSICS = "物"               # 物理
    MILITARY = "军"              # 军事
    MUSIC = "音"                 # 音乐
    SPORTS = "体"                # 体育
    ARCHITECTURE = "建"          # 建筑


@dataclass
class Pronunciation:
    """发音信息"""
    ipa: Optional[str] = None           # IPA音标
    region: str = "general"              # 地区: us/uk/general
    audio_file: Optional[str] = None     # 音频文件名


@dataclass
class Example:
    """例句"""
    text: str                            # 例句原文
    translation: Optional[str] = None    # 译文
    source: Optional[str] = None         # 来源 (如 --Shak. from GCIDE)


@dataclass
class Sense:
    """
    单个释义
    
    这是统一格式的核心：无论来自哪个词典，每个释义都转换为此结构。
    """
    # 核心内容
    definition: str                      # 释义文本
    definition_lang: str = "zh"          # 释义语言: zh/en/zh-en
    
    # 结构信息
    pos: Optional[str] = None            # 词性
    sense_number: Optional[str] = None   # 序号 (如 "1", "2a", "①")
    
    # 例句
    examples: List[Example] = field(default_factory=list)
    
    # 扩展信息
    domain: Optional[str] = None         # 领域: 经/计/医...
    register: Optional[str] = None       # 语域: formal/informal/literary/slang
    grammar_note: Optional[str] = None   # 语法说明 (如 [attrib], [pred])
    
    # 关联词
    synonyms: List[str] = field(default_factory=list)
    antonyms: List[str] = field(default_factory=list)
    
    # 原始标记（保留用于调试）
    raw_markers: List[str] = field(default_factory=list)
    
    # 原始内容（遵循"不丢失内容"原则）
    raw_content: Optional[str] = None    # 原始内容，用于调试和恢复


@dataclass
class RelatedPhrase:
    """相关短语/词组"""
    phrase: str                          # 短语
    meaning: Optional[str] = None        # 含义
    phrase_type: str = "phrase"          # 类型: phrase/idiom/phr.v


@dataclass 
class DictionaryEntry:
    """
    统一词典条目
    
    设计原则：
    1. 各词典独立存储，但格式统一
    2. 保留原始数据用于回溯
    3. 结构清晰，便于客户端渲染
    """
    
    # ========== 基础信息 ==========
    headword: str                        # 词头
    source_id: str                       # 来源词典ID (oxford/gcide/langdao/xiandai/chinese_dict)
    entry_id: Optional[str] = None       # 条目唯一ID
    
    # ========== 发音 ==========
    pronunciations: List[Pronunciation] = field(default_factory=list)
    
    # ========== 释义列表 ==========
    # 按词性分组后的所有释义
    senses: List[Sense] = field(default_factory=list)
    
    # ========== 词形变化 (英文) ==========
    forms: Dict[str, str] = field(default_factory=dict)
    # 例: {"plural": "books", "past": "went", "pp": "gone", "ing": "going"}
    
    # ========== 相关短语/词组 ==========
    related_phrases: List[RelatedPhrase] = field(default_factory=list)
    
    # ========== 中文特有字段 ==========
    pinyin: Optional[str] = None         # 拼音（带声调）
    pinyin_abbr: Optional[str] = None    # 拼音缩写
    strokes: Optional[int] = None        # 笔画数
    radical: Optional[str] = None        # 部首
    
    # ========== 词源/典故 (GCIDE/成语) ==========
    etymology: Optional[str] = None      # 词源
    story: Optional[str] = None          # 典故（成语用）
    source_book: Optional[str] = None    # 出处书籍
    
    # ========== 元信息 ==========
    frequency: Optional[int] = None      # 词频等级 1-10
    level: Optional[str] = None          # 难度级别: basic/intermediate/advanced
    tags: List[str] = field(default_factory=list)
    
    # ========== 原始数据（调试用） ==========
    raw_content: Optional[str] = None    # 原始内容
    parse_quality: float = 1.0           # 解析质量分 0-1
    parse_notes: List[str] = field(default_factory=list)  # 解析备注
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典，用于JSON序列化"""
        return {
            "headword": self.headword,
            "source_id": self.source_id,
            "entry_id": self.entry_id,
            "pronunciations": [
                {"ipa": p.ipa, "region": p.region, "audio_file": p.audio_file}
                for p in self.pronunciations
            ],
            "senses": [
                {
                    "definition": s.definition,
                    "definition_lang": s.definition_lang,
                    "pos": s.pos,
                    "sense_number": s.sense_number,
                    "examples": [
                        {"text": e.text, "translation": e.translation, "source": e.source}
                        for e in s.examples
                    ],
                    "domain": s.domain,
                    "register": s.register,
                    "grammar_note": s.grammar_note,
                    "synonyms": s.synonyms,
                    "antonyms": s.antonyms,
                }
                for s in self.senses
            ],
            "forms": self.forms if self.forms else None,
            "related_phrases": [
                {"phrase": p.phrase, "meaning": p.meaning, "type": p.phrase_type}
                for p in self.related_phrases
            ] if self.related_phrases else None,
            "pinyin": self.pinyin,
            "pinyin_abbr": self.pinyin_abbr,
            "strokes": self.strokes,
            "radical": self.radical,
            "etymology": self.etymology,
            "story": self.story,
            "source_book": self.source_book,
            "frequency": self.frequency,
            "level": self.level,
            "tags": self.tags if self.tags else None,
        }
    
    def to_json(self, indent: int = 2) -> str:
        """转换为JSON字符串"""
        # 过滤掉None值
        data = {k: v for k, v in self.to_dict().items() if v is not None}
        return json.dumps(data, ensure_ascii=False, indent=indent)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DictionaryEntry':
        """从字典创建实例"""
        entry = cls(
            headword=data['headword'],
            source_id=data['source_id'],
            entry_id=data.get('entry_id'),
        )
        
        # 解析发音
        for p in data.get('pronunciations', []):
            entry.pronunciations.append(Pronunciation(
                ipa=p.get('ipa'),
                region=p.get('region', 'general'),
                audio_file=p.get('audio_file')
            ))
        
        # 解析释义
        for s in data.get('senses', []):
            sense = Sense(
                definition=s['definition'],
                definition_lang=s.get('definition_lang', 'zh'),
                pos=s.get('pos'),
                sense_number=s.get('sense_number'),
                domain=s.get('domain'),
                register=s.get('register'),
                grammar_note=s.get('grammar_note'),
                synonyms=s.get('synonyms', []),
                antonyms=s.get('antonyms', []),
            )
            # 解析例句
            for e in s.get('examples', []):
                sense.examples.append(Example(
                    text=e['text'],
                    translation=e.get('translation'),
                    source=e.get('source')
                ))
            entry.senses.append(sense)
        
        # 其他字段
        entry.forms = data.get('forms', {})
        entry.pinyin = data.get('pinyin')
        entry.pinyin_abbr = data.get('pinyin_abbr')
        entry.strokes = data.get('strokes')
        entry.radical = data.get('radical')
        entry.etymology = data.get('etymology')
        entry.story = data.get('story')
        entry.source_book = data.get('source_book')
        entry.frequency = data.get('frequency')
        entry.level = data.get('level')
        entry.tags = data.get('tags', [])
        
        # 相关短语
        for p in data.get('related_phrases', []):
            entry.related_phrases.append(RelatedPhrase(
                phrase=p['phrase'],
                meaning=p.get('meaning'),
                phrase_type=p.get('type', 'phrase')
            ))
        
        return entry


# ========== JSON Schema (用于验证和文档) ==========

UNIFIED_ENTRY_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "UnifiedDictionaryEntry",
    "description": "统一词典条目格式 - 基于实际词典样例设计",
    "type": "object",
    "required": ["headword", "source_id", "senses"],
    "properties": {
        "headword": {
            "type": "string",
            "description": "词头/词条"
        },
        "source_id": {
            "type": "string",
            "description": "来源词典",
            "enum": ["oxford", "gcide", "langdao", "xiandaihanyucidian", "chinese_dict"]
        },
        "entry_id": {
            "type": "string",
            "description": "条目唯一ID"
        },
        "pronunciations": {
            "type": "array",
            "description": "发音列表",
            "items": {
                "type": "object",
                "properties": {
                    "ipa": {"type": "string", "description": "IPA音标"},
                    "region": {"type": "string", "enum": ["uk", "us", "general"]},
                    "audio_file": {"type": "string"}
                }
            }
        },
        "senses": {
            "type": "array",
            "description": "释义列表",
            "items": {
                "type": "object",
                "required": ["definition"],
                "properties": {
                    "definition": {"type": "string", "description": "释义"},
                    "definition_lang": {"type": "string", "enum": ["zh", "en", "zh-en"]},
                    "pos": {"type": "string", "description": "词性"},
                    "sense_number": {"type": "string", "description": "序号如1/2a/①"},
                    "examples": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": ["text"],
                            "properties": {
                                "text": {"type": "string"},
                                "translation": {"type": "string"},
                                "source": {"type": "string"}
                            }
                        }
                    },
                    "domain": {"type": "string", "description": "领域如经/计/医"},
                    "register": {"type": "string", "description": "语域"},
                    "grammar_note": {"type": "string", "description": "语法说明"},
                    "synonyms": {"type": "array", "items": {"type": "string"}},
                    "antonyms": {"type": "array", "items": {"type": "string"}}
                }
            }
        },
        "forms": {
            "type": "object",
            "description": "词形变化",
            "additionalProperties": {"type": "string"}
        },
        "related_phrases": {
            "type": "array",
            "description": "相关短语",
            "items": {
                "type": "object",
                "properties": {
                    "phrase": {"type": "string"},
                    "meaning": {"type": "string"},
                    "type": {"type": "string"}
                }
            }
        },
        "pinyin": {"type": "string", "description": "拼音"},
        "pinyin_abbr": {"type": "string", "description": "拼音缩写"},
        "strokes": {"type": "integer", "description": "笔画数"},
        "radical": {"type": "string", "description": "部首"},
        "etymology": {"type": "string", "description": "词源"},
        "story": {"type": "string", "description": "典故"},
        "source_book": {"type": "string", "description": "出处"},
        "frequency": {"type": "integer", "description": "词频1-10"},
        "level": {"type": "string", "description": "难度级别"},
        "tags": {"type": "array", "items": {"type": "string"}}
    }
}


# ========== 格式对照表（基于实际分析）==========

FORMAT_MAPPING = """
格式对照表 - 各词典格式 → 统一格式

┌──────────────────┬──────────────────────┬───────────────────┐
│ 词典             │ 原始格式              │ 统一格式字段       │
├──────────────────┼──────────────────────┼───────────────────┤
│ Oxford           │ /英; 美/              │ pronunciations    │
│                  │ n, v, adj...          │ sense.pos         │
│                  │ 1 2 3 (a)(b)(c)       │ sense.sense_number│
│                  │ * example             │ sense.examples    │
│                  │ [attrib][pred]        │ sense.grammar_note│
│                  │ IDM / PHR V           │ related_phrases   │
├──────────────────┼──────────────────────┼───────────────────┤
│ GCIDE            │ \\Word\\               │ headword          │
│                  │ n., v. i., v. t.      │ sense.pos         │
│                  │ [1913 Webster]        │ (metadata)        │
│                  │ --Shak.               │ example.source    │
│                  │ {word}                │ (cross-reference) │
│                  │ Syn:                  │ sense.synonyms    │
├──────────────────┼──────────────────────┼───────────────────┤
│ Langdao          │ *[ipa]                │ pronunciations    │
│                  │ n. v. a. ad.          │ sense.pos         │
│                  │ 【经】【计】           │ sense.domain      │
│                  │ 相关词组:              │ related_phrases   │
├──────────────────┼──────────────────────┼───────────────────┤
│ 现汉             │ yī (拼音)             │ pinyin            │
│                  │ BS 一 BH 0            │ radical, strokes  │
│                  │ ◎                     │ (multi-reading)   │
│                  │ 〈名〉〈动〉            │ sense.pos         │
│                  │ ①②③                  │ sense.sense_number│
│                  │ ～                    │ (placeholder)     │
├──────────────────┼──────────────────────┼───────────────────┤
│ 汉语拼音         │ <h2>词 [pinyin]</h2>  │ headword, pinyin  │
│                  │ 缩写:                  │ pinyin_abbr       │
│                  │ 解释:                  │ senses            │
│                  │ 近义词/反义词:         │ synonyms/antonyms │
│                  │ 来源/典故:             │ story, source_book│
│                  │ 用法:                  │ (usage note)      │
└──────────────────┴──────────────────────┴───────────────────┘
"""

if __name__ == "__main__":
    print(FORMAT_MAPPING)
    
    # 示例：创建一个统一格式的条目
    entry = DictionaryEntry(
        headword="good",
        source_id="langdao",
        pronunciations=[
            Pronunciation(ipa="gud", region="general")
        ],
        senses=[
            Sense(
                definition="善行, 好处, 利益",
                definition_lang="zh",
                pos="n",
            ),
            Sense(
                definition="好的, 优良的, 上等的",
                definition_lang="zh", 
                pos="adj",
            ),
            Sense(
                definition="货物; 好的",
                definition_lang="zh",
                domain="经",
            ),
        ],
        related_phrases=[
            RelatedPhrase(phrase="for good", meaning="永远"),
            RelatedPhrase(phrase="good for", meaning="对...有益"),
        ]
    )
    
    print("\n示例输出:")
    print(entry.to_json())
