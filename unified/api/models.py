#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API数据模型（Pydantic）

定义API的请求和响应模型
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union, Generic, TypeVar

# 定义泛型类型变量
T = TypeVar('T')


class PronunciationModel(BaseModel):
    """发音信息"""
    ipa: Optional[str] = None
    region: str = "general"
    audio_file: Optional[str] = None


class ExampleModel(BaseModel):
    """例句"""
    text: str
    translation: Optional[str] = None
    source: Optional[str] = None


class SenseModel(BaseModel):
    """释义"""
    definition: str
    definition_lang: str = "zh"
    pos: Optional[str] = None
    sense_number: Optional[str] = None
    examples: List[ExampleModel] = []
    domain: Optional[str] = None
    register: Optional[str] = None  # 语域 (formal/informal/literary/slang) - 警告可忽略，不影响功能
    grammar_note: Optional[str] = None
    synonyms: List[str] = []
    antonyms: List[str] = []


class RelatedPhraseModel(BaseModel):
    """相关短语"""
    phrase: str
    meaning: Optional[str] = None
    phrase_type: str = "phrase"


class DictionaryQueryResponse(BaseModel):
    """词典查询响应"""
    id: Optional[int] = None
    headword: str
    source_id: str
    entry_id: Optional[str] = None
    
    # JSONB字段解析后的对象
    pronunciations: List[PronunciationModel] = []
    senses: List[SenseModel] = []
    forms: Optional[Dict[str, str]] = None
    related_phrases: List[RelatedPhraseModel] = []
    
    # 中文词典特有字段
    pinyin: Optional[str] = None
    pinyin_abbr: Optional[str] = None
    strokes: Optional[int] = None
    radical: Optional[str] = None
    
    # 词源/典故
    etymology: Optional[str] = None
    story: Optional[str] = None
    source_book: Optional[str] = None
    
    # 元信息
    frequency: Optional[int] = None
    level: Optional[str] = None
    tags: List[str] = []


class DictionaryNavigationResponse(BaseModel):
    """词典导航响应（上一个/下一个）"""
    headword: str
    source_id: str
    has_next: bool = False
    has_prev: bool = False
    entry: Optional[DictionaryQueryResponse] = None


class ApiResponse(BaseModel, Generic[T]):
    """API统一响应格式（支持泛型）"""
    code: int = 200
    message: str = "success"
    data: Optional[T] = None

