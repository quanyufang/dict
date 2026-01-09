#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
词典解析器基类
"""

from abc import ABC, abstractmethod
from typing import Optional
from ..models.entry import DictionaryEntry


class BaseParser(ABC):
    """词典解析器基类"""
    
    @property
    @abstractmethod
    def source_id(self) -> str:
        """词典标识"""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """词典名称"""
        pass
    
    @property
    @abstractmethod
    def index_language(self) -> str:
        """索引语言: en/zh/fr/ja"""
        pass
    
    @property
    @abstractmethod
    def explanation_language(self) -> str:
        """解释语言: en/zh/zh-en"""
        pass
    
    @abstractmethod
    def parse(self, word: str, raw_content: str) -> Optional[DictionaryEntry]:
        """
        解析原始词典内容
        
        Args:
            word: 词头
            raw_content: 原始内容（从.dictcontent读取的文本）
            
        Returns:
            解析后的词典条目，解析失败返回None
        """
        pass
    
    def parse_safe(self, word: str, raw_content: str) -> Optional[DictionaryEntry]:
        """
        安全解析，捕获异常
        """
        try:
            return self.parse(word, raw_content)
        except Exception as e:
            print(f"解析错误 [{self.source_id}] {word}: {e}")
            return None

