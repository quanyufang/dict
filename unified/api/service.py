#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
词典查询服务

实现数据库查询逻辑
"""

import json
import logging
import asyncpg
from typing import List, Optional

logger = logging.getLogger(__name__)
try:
    # 作为模块导入
    from unified.api.database import get_db
    from unified.api.models import (
        DictionaryQueryResponse, DictionaryNavigationResponse,
        PronunciationModel, SenseModel, ExampleModel, RelatedPhraseModel
    )
except ImportError:
    # 直接运行时的相对导入
    import sys
    from pathlib import Path
    # 从 service.py 位置: api -> unified -> src
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from unified.api.database import get_db
    from unified.api.models import (
        DictionaryQueryResponse, DictionaryNavigationResponse,
        PronunciationModel, SenseModel, ExampleModel, RelatedPhraseModel
    )


class DictionaryService:
    """词典查询服务"""
    
    async def query(
        self, 
        key: str, 
        sources: Optional[List[str]] = None,
        fuzzy: bool = False,
        limit: int = 10
    ) -> List[DictionaryQueryResponse]:
        """
        查询词条
        
        Args:
            key: 查询词头
            sources: 词典来源列表（可选）
            fuzzy: 是否模糊查询
            limit: 返回结果数量限制
            
        Returns:
            查询结果列表
        """
        try:
            logger.info(f"开始查询数据库: key={key}, sources={sources}, fuzzy={fuzzy}")
            async with get_db() as conn:
                logger.info("数据库连接成功")
                if fuzzy:
                    # 模糊查询
                    if sources:
                        # 指定词典来源
                        placeholders = ','.join([f"${i+2}" for i in range(len(sources))])
                        query = f"""
                            SELECT * FROM dictionary_entries 
                            WHERE headword LIKE $1 
                              AND source_id IN ({placeholders})
                            ORDER BY headword
                            LIMIT ${len(sources) + 2}
                        """
                        params = [f"{key}%"] + list(sources) + [limit]
                    else:
                        # 所有词典
                        query = """
                            SELECT * FROM dictionary_entries 
                            WHERE headword LIKE $1
                            ORDER BY headword
                            LIMIT $2
                        """
                        params = [f"{key}%", limit]
                else:
                    # 精确查询
                    if sources:
                        # 指定词典来源
                        placeholders = ','.join([f"${i+2}" for i in range(len(sources))])
                        query = f"""
                            SELECT * FROM dictionary_entries 
                            WHERE headword = $1 
                              AND source_id IN ({placeholders})
                            ORDER BY source_id
                        """
                        params = [key] + list(sources)
                    else:
                        # 所有词典
                        query = """
                            SELECT * FROM dictionary_entries 
                            WHERE headword = $1
                            ORDER BY source_id
                        """
                        params = [key]
                
                logger.info(f"执行SQL查询: {query[:100]}... 参数: {params}")
                rows = await conn.fetch(query, *params)
                logger.info(f"查询返回 {len(rows)} 行数据")
                
                # 转换为响应模型
                results = []
                for row in rows:
                    try:
                        results.append(self._row_to_response(row))
                    except Exception as e:
                        logger.error(f"转换行数据失败: {str(e)}, row: {dict(row)}", exc_info=True)
                        continue
                
                logger.info(f"成功转换 {len(results)} 条结果")
                return results
        except asyncpg.exceptions.PostgresError as e:
            logger.error(f"数据库错误: {str(e)}", exc_info=True)
            raise Exception(f"数据库查询错误: {str(e)}")
        except Exception as e:
            logger.error(f"查询服务错误: {str(e)}", exc_info=True)
            raise
    
    async def get_next(self, key: str, source_id: str) -> DictionaryNavigationResponse:
        """
        获取下一个词条
        
        Args:
            key: 当前词头
            source_id: 词典来源ID
            
        Returns:
            导航响应（包含下一个词条）
        """
        async with get_db() as conn:
            # 查询下一个索引（使用表别名避免字段冲突）
            next_query = """
                SELECT 
                    e.id, e.headword, e.source_id, e.entry_id,
                    e.pronunciations, e.senses, e.forms, e.related_phrases,
                    e.pinyin, e.pinyin_abbr, e.strokes, e.radical,
                    e.etymology, e.story, e.source_book,
                    e.frequency, e.level, e.tags,
                    e.raw_content, e.parse_quality, e.parse_notes,
                    e.created_at, e.updated_at
                FROM dictionary_index i
                JOIN dictionary_entries e ON i.entry_id = e.id
                WHERE i.source_id = $1 
                  AND i.sort_key > (
                      SELECT sort_key FROM dictionary_index 
                      WHERE headword = $2 AND source_id = $1
                  )
                ORDER BY i.sort_key
                LIMIT 1
            """
            next_row = await conn.fetchrow(next_query, source_id, key)
            
            # 检查是否有上一个和下一个
            has_next_query = """
                SELECT COUNT(*) > 0 as has_next FROM dictionary_index 
                WHERE source_id = $1 
                  AND sort_key > (
                      SELECT sort_key FROM dictionary_index 
                      WHERE headword = $2 AND source_id = $1
                  )
            """
            has_prev_query = """
                SELECT COUNT(*) > 0 as has_prev FROM dictionary_index 
                WHERE source_id = $1 
                  AND sort_key < (
                      SELECT sort_key FROM dictionary_index 
                      WHERE headword = $2 AND source_id = $1
                  )
            """
            
            has_next_result = await conn.fetchrow(has_next_query, source_id, key)
            has_prev_result = await conn.fetchrow(has_prev_query, source_id, key)
            
            has_next = has_next_result['has_next'] if has_next_result else False
            has_prev = has_prev_result['has_prev'] if has_prev_result else False
            
            # 构建响应
            result = DictionaryNavigationResponse(
                headword=key,
                source_id=source_id,
                has_next=has_next,
                has_prev=has_prev,
                entry=None
            )
            
            # 如果有下一个词条，返回词条信息
            if next_row:
                result.entry = self._row_to_response(next_row)
                result.headword = next_row['headword']
            
            return result
    
    async def get_prev(self, key: str, source_id: str) -> DictionaryNavigationResponse:
        """
        获取上一个词条
        
        Args:
            key: 当前词头
            source_id: 词典来源ID
            
        Returns:
            导航响应（包含上一个词条）
        """
        async with get_db() as conn:
            # 查询上一个索引（使用表别名避免字段冲突）
            prev_query = """
                SELECT 
                    e.id, e.headword, e.source_id, e.entry_id,
                    e.pronunciations, e.senses, e.forms, e.related_phrases,
                    e.pinyin, e.pinyin_abbr, e.strokes, e.radical,
                    e.etymology, e.story, e.source_book,
                    e.frequency, e.level, e.tags,
                    e.raw_content, e.parse_quality, e.parse_notes,
                    e.created_at, e.updated_at
                FROM dictionary_index i
                JOIN dictionary_entries e ON i.entry_id = e.id
                WHERE i.source_id = $1 
                  AND i.sort_key < (
                      SELECT sort_key FROM dictionary_index 
                      WHERE headword = $2 AND source_id = $1
                  )
                ORDER BY i.sort_key DESC
                LIMIT 1
            """
            prev_row = await conn.fetchrow(prev_query, source_id, key)
            
            # 检查是否有上一个和下一个
            has_next_query = """
                SELECT COUNT(*) > 0 as has_next FROM dictionary_index 
                WHERE source_id = $1 
                  AND sort_key > (
                      SELECT sort_key FROM dictionary_index 
                      WHERE headword = $2 AND source_id = $1
                  )
            """
            has_prev_query = """
                SELECT COUNT(*) > 0 as has_prev FROM dictionary_index 
                WHERE source_id = $1 
                  AND sort_key < (
                      SELECT sort_key FROM dictionary_index 
                      WHERE headword = $2 AND source_id = $1
                  )
            """
            
            has_next_result = await conn.fetchrow(has_next_query, source_id, key)
            has_prev_result = await conn.fetchrow(has_prev_query, source_id, key)
            
            has_next = has_next_result['has_next'] if has_next_result else False
            has_prev = has_prev_result['has_prev'] if has_prev_result else False
            
            # 构建响应
            result = DictionaryNavigationResponse(
                headword=key,
                source_id=source_id,
                has_next=has_next,
                has_prev=has_prev,
                entry=None
            )
            
            # 如果有上一个词条，返回词条信息
            if prev_row:
                result.entry = self._row_to_response(prev_row)
                result.headword = prev_row['headword']
            
            return result
    
    def _row_to_response(self, row) -> DictionaryQueryResponse:
        """将数据库行转换为响应模型"""
        # 解析JSONB字段
        pronunciations = []
        if row.get('pronunciations'):
            try:
                if isinstance(row['pronunciations'], str):
                    pron_data = json.loads(row['pronunciations'])
                else:
                    pron_data = row['pronunciations']
                if isinstance(pron_data, list):
                    for p in pron_data:
                        pronunciations.append(PronunciationModel(**p))
            except Exception:
                pass
        
        senses = []
        if row.get('senses'):
            try:
                if isinstance(row['senses'], str):
                    sense_data = json.loads(row['senses'])
                else:
                    sense_data = row['senses']
                if isinstance(sense_data, list):
                    for s in sense_data:
                        examples = []
                        if s.get('examples'):
                            for e in s['examples']:
                                examples.append(ExampleModel(**e))
                        # 处理 pos 字段：如果是 -1 或无效值，转换为 None
                        pos_value = s.get('pos')
                        if pos_value == -1 or pos_value == '-1':
                            pos_value = None
                        elif pos_value is not None:
                            pos_value = str(pos_value)
                        
                        sense = SenseModel(
                            definition=s.get('definition', ''),
                            definition_lang=s.get('definition_lang', 'zh'),
                            pos=pos_value,
                            sense_number=s.get('sense_number'),
                            examples=examples,
                            domain=s.get('domain'),
                            register=s.get('register'),
                            grammar_note=s.get('grammar_note'),
                            synonyms=s.get('synonyms', []),
                            antonyms=s.get('antonyms', [])
                        )
                        senses.append(sense)
            except Exception as e:
                print(f"Error parsing senses: {e}")
                # 如果解析失败，至少保留定义
                senses.append(SenseModel(
                    definition=str(row.get('senses', '')),
                    definition_lang='zh'
                ))
        
        related_phrases = []
        if row.get('related_phrases'):
            try:
                if isinstance(row['related_phrases'], str):
                    phrase_data = json.loads(row['related_phrases'])
                else:
                    phrase_data = row['related_phrases']
                if isinstance(phrase_data, list):
                    for p in phrase_data:
                        related_phrases.append(RelatedPhraseModel(**p))
            except Exception:
                pass
        
        forms = None
        if row.get('forms'):
            try:
                if isinstance(row['forms'], str):
                    forms = json.loads(row['forms'])
                else:
                    forms = row['forms']
            except Exception:
                pass
        
        tags = []
        if row.get('tags'):
            try:
                if isinstance(row['tags'], str):
                    tags = json.loads(row['tags'])
                else:
                    tags = row['tags']
                if not isinstance(tags, list):
                    tags = []
            except Exception:
                pass
        
        return DictionaryQueryResponse(
            id=row.get('id'),
            headword=row['headword'],
            source_id=row['source_id'],
            entry_id=row.get('entry_id'),
            pronunciations=pronunciations,
            senses=senses,
            forms=forms,
            related_phrases=related_phrases,
            pinyin=row.get('pinyin'),
            pinyin_abbr=row.get('pinyin_abbr'),
            strokes=row.get('strokes'),
            radical=row.get('radical'),
            etymology=row.get('etymology'),
            story=row.get('story'),
            source_book=row.get('source_book'),
            frequency=row.get('frequency'),
            level=row.get('level'),
            tags=tags
        )

