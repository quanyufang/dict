#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从原始词典文件（.db + .dictcontent）全量导入数据到PostgreSQL

使用方法：
    # 导入单个词典
    python import_from_dictfiles.py --source oxford
    
    # 导入所有词典
    python import_from_dictfiles.py --all
    
    # 指定批量大小
    python import_from_dictfiles.py --source oxford --batch-size 500
"""

import sys
import asyncio
import argparse
import logging
import sqlite3
from pathlib import Path
from typing import List, Optional, Tuple, Dict
from datetime import datetime
import time

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from unified.models.entry import DictionaryEntry
from unified.api.database import get_db, create_pool, close_pool
from unified.api.config import config

# 导入解析器
try:
    from unified.parsers.oxford import OxfordParser
    from unified.parsers.langdao import LangdaoParser
    from unified.parsers.xiandaihanyucidian import XiandaihanyucidianParser
    from unified.parsers.gcide import GcideParser
    from unified.parsers.chinese_dict import ChineseDictParser
    PARSERS_AVAILABLE = True
except ImportError:
    PARSERS_AVAILABLE = False

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 词典文件目录
# 从 scripts/import_from_dictfiles.py 到 dict/app_dictfiles
# scripts -> unified -> src -> dict -> app_dictfiles
DICT_BASE_PATH = Path(__file__).parent.parent.parent.parent / "app_dictfiles"

# 词典配置
DICT_CONFIGS = {
    'oxford': {
        'db': 'oxford-gb.db',
        'content': 'oxford-gb.dictcontent',
        'name': '牛津英汉词典',
        'parser_class': 'OxfordParser' if PARSERS_AVAILABLE else None
    },
    'langdao': {
        'db': 'langdao-ec-gb.db',
        'content': 'langdao-ec-gb.dictcontent',
        'name': '朗道英汉词典',
        'parser_class': 'LangdaoParser' if PARSERS_AVAILABLE else None
    },
    'gcide': {
        'db': 'gcide.db',
        'content': 'gcide.dictcontent',
        'name': 'GCIDE英英词典',
        'parser_class': 'GcideParser' if PARSERS_AVAILABLE else None
    },
    'xiandaihanyucidian': {
        'db': 'xiandaihanyucidian.db',
        'content': 'xiandaihanyucidian.dictcontent',
        'name': '现代汉语词典',
        'parser_class': 'XiandaihanyucidianParser' if PARSERS_AVAILABLE else None
    },
    'chinese_dict': {
        'db': 'chinese_dict.db',
        'content': 'chinese_dict.dictcontent',
        'name': '汉语拼音词典',
        'parser_class': 'ChineseDictParser' if PARSERS_AVAILABLE else None
    },
}


def get_parser(source_id: str):
    """获取解析器实例"""
    if not PARSERS_AVAILABLE:
        return None
    
    parser_map = {
        'oxford': OxfordParser,
        'langdao': LangdaoParser,
        'gcide': GcideParser,
        'xiandaihanyucidian': XiandaihanyucidianParser,
        'chinese_dict': ChineseDictParser,
    }
    
    parser_class = parser_map.get(source_id)
    if parser_class:
        return parser_class()
    return None


def read_word_from_dict(db_path: Path, content_path: Path, word: str) -> Optional[str]:
    """
    从词典文件读取单个词条的内容
    
    Args:
        db_path: 索引数据库路径
        content_path: 正文文件路径
        word: 词头
        
    Returns:
        词条原始内容，如果未找到返回None
    """
    if not db_path.exists() or not content_path.exists():
        return None
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # 尝试精确匹配
        cursor.execute('SELECT offset, length FROM wordIndex WHERE word = ?', (word.lower(),))
        result = cursor.fetchone()
        
        # 如果没找到，尝试原始大小写
        if not result and word != word.lower():
            cursor.execute('SELECT offset, length FROM wordIndex WHERE word = ?', (word,))
            result = cursor.fetchone()
        
        conn.close()
        
        if not result:
            return None
        
        offset, length = result
        
        # 从dictcontent文件读取内容
        with open(content_path, 'rb') as f:
            f.seek(offset)
            raw_bytes = f.read(length)
            try:
                return raw_bytes.decode('utf-8')
            except UnicodeDecodeError:
                return raw_bytes.decode('utf-8', errors='replace')
    except Exception as e:
        logger.error(f"读取词条失败 {word}: {e}")
        return None


def get_all_words(db_path: Path) -> List[str]:
    """
    获取词典中所有词条列表
    
    Args:
        db_path: 索引数据库路径
        
    Returns:
        所有词头的列表
    """
    if not db_path.exists():
        logger.error(f"索引文件不存在: {db_path}")
        return []
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT word FROM wordIndex ORDER BY word')
        words = [row[0] for row in cursor.fetchall()]
        conn.close()
        return words
    except Exception as e:
        logger.error(f"读取词条列表失败: {e}")
        return []


async def insert_entry_batch(conn, entries: List[DictionaryEntry]) -> Tuple[int, int]:
    """
    批量插入词典条目
    
    Returns:
        (成功数, 失败数)
    """
    if not entries:
        return 0, 0
    
    import json
    
    success_count = 0
    fail_count = 0
    
    for entry in entries:
        try:
            entry_dict = entry.to_dict()
            
            # 准备JSONB数据
            pronunciations_json = json.dumps(entry_dict.get('pronunciations', []), ensure_ascii=False) if entry_dict.get('pronunciations') else None
            senses_json = json.dumps(entry_dict.get('senses', []), ensure_ascii=False) if entry_dict.get('senses') else None
            forms_json = json.dumps(entry_dict.get('forms'), ensure_ascii=False) if entry_dict.get('forms') else None
            related_phrases_json = json.dumps(entry_dict.get('related_phrases', []), ensure_ascii=False) if entry_dict.get('related_phrases') else None
            tags_json = json.dumps(entry_dict.get('tags', []), ensure_ascii=False) if entry_dict.get('tags') else None
            parse_notes_json = json.dumps(entry.parse_notes, ensure_ascii=False) if entry.parse_notes else None
            
            # 使用ON CONFLICT处理重复
            insert_query = """
                INSERT INTO dictionary_entries (
                    headword, source_id, entry_id,
                    pronunciations, senses, forms, related_phrases,
                    pinyin, pinyin_abbr, strokes, radical,
                    etymology, story, source_book,
                    frequency, level, tags,
                    raw_content, parse_quality, parse_notes
                ) VALUES (
                    $1, $2, $3,
                    $4::jsonb, $5::jsonb, $6::jsonb, $7::jsonb,
                    $8, $9, $10, $11,
                    $12, $13, $14,
                    $15, $16, $17::jsonb,
                    $18, $19, $20::jsonb
                )
                ON CONFLICT (headword, source_id) 
                DO UPDATE SET
                    pronunciations = EXCLUDED.pronunciations,
                    senses = EXCLUDED.senses,
                    forms = EXCLUDED.forms,
                    related_phrases = EXCLUDED.related_phrases,
                    pinyin = EXCLUDED.pinyin,
                    pinyin_abbr = EXCLUDED.pinyin_abbr,
                    strokes = EXCLUDED.strokes,
                    radical = EXCLUDED.radical,
                    etymology = EXCLUDED.etymology,
                    story = EXCLUDED.story,
                    source_book = EXCLUDED.source_book,
                    frequency = EXCLUDED.frequency,
                    level = EXCLUDED.level,
                    tags = EXCLUDED.tags,
                    raw_content = EXCLUDED.raw_content,
                    parse_quality = EXCLUDED.parse_quality,
                    parse_notes = EXCLUDED.parse_notes,
                    updated_at = CURRENT_TIMESTAMP
            """
            
            await conn.execute(
                insert_query,
                entry.headword,
                entry.source_id,
                entry.entry_id,
                pronunciations_json,
                senses_json,
                forms_json,
                related_phrases_json,
                entry.pinyin,
                entry.pinyin_abbr,
                entry.strokes,
                entry.radical,
                entry.etymology,
                entry.story,
                entry.source_book,
                entry.frequency,
                entry.level,
                tags_json,
                entry.raw_content,
                entry.parse_quality or 1.0,
                parse_notes_json
            )
            
            success_count += 1
        except Exception as e:
            logger.error(f"插入词条失败 {entry.headword}: {e}")
            fail_count += 1
    
    return success_count, fail_count


async def import_dict_source(source_id: str, batch_size: int = 100, limit: Optional[int] = None) -> Dict:
    """
    导入单个词典源的所有数据
    
    Args:
        source_id: 词典ID
        batch_size: 批量处理大小
        limit: 限制导入数量（用于测试），None表示导入全部
        
    Returns:
        导入统计信息
    """
    if source_id not in DICT_CONFIGS:
        logger.error(f"未知的词典ID: {source_id}")
        return {'success': False, 'error': f'未知的词典ID: {source_id}'}
    
    config_dict = DICT_CONFIGS[source_id]
    db_path = DICT_BASE_PATH / config_dict['db']
    content_path = DICT_BASE_PATH / config_dict['content']
    
    logger.info(f"\n{'='*60}")
    logger.info(f"开始导入: {config_dict['name']} ({source_id})")
    logger.info(f"索引文件: {db_path}")
    logger.info(f"正文文件: {content_path}")
    logger.info(f"{'='*60}")
    
    # 检查文件是否存在
    if not db_path.exists():
        logger.error(f"索引文件不存在: {db_path}")
        return {'success': False, 'error': f'索引文件不存在: {db_path}'}
    
    if not content_path.exists():
        logger.error(f"正文文件不存在: {content_path}")
        return {'success': False, 'error': f'正文文件不存在: {content_path}'}
    
    # 获取解析器
    parser = get_parser(source_id)
    if not parser:
        logger.error(f"无法获取解析器: {source_id}")
        return {'success': False, 'error': f'无法获取解析器: {source_id}'}
    
    # 获取所有词条列表
    logger.info("正在读取词条列表...")
    all_words = get_all_words(db_path)
    total_words = len(all_words)
    
    if limit:
        all_words = all_words[:limit]
        logger.info(f"限制导入数量: {limit} (总词条数: {total_words})")
    else:
        logger.info(f"总词条数: {total_words}")
    
    if not all_words:
        logger.warning("未找到任何词条")
        return {'success': False, 'error': '未找到任何词条'}
    
    # 统计信息
    stats = {
        'source_id': source_id,
        'total_words': len(all_words),
        'parsed': 0,
        'failed_parse': 0,
        'imported': 0,
        'failed_import': 0,
        'start_time': datetime.now(),
    }
    
    # 批量处理
    batch = []
    start_time = time.time()
    
    async with get_db() as conn:
        for i, word in enumerate(all_words, 1):
            try:
                # 读取原始内容
                raw_content = read_word_from_dict(db_path, content_path, word)
                if not raw_content:
                    logger.warning(f"[{i}/{len(all_words)}] 未找到内容: {word}")
                    stats['failed_parse'] += 1
                    continue
                
                # 解析
                entry = None
                parse_error = None
                try:
                    entry = parser.parse_safe(word, raw_content)
                except Exception as e:
                    parse_error = str(e)
                    logger.debug(f"[{i}/{len(all_words)}] 解析异常 {word}: {e}", exc_info=True)
                
                if not entry:
                    # 详细日志：解析失败
                    logger.warning(f"[{i}/{len(all_words)}] 解析失败: {word}")
                    logger.warning(f"  原始内容长度: {len(raw_content)} 字符")
                    logger.warning(f"  原始内容预览 (前200字符): {raw_content[:200]}")
                    if parse_error:
                        logger.warning(f"  解析错误: {parse_error}")
                    stats['failed_parse'] += 1
                    continue
                
                # 检查是否有senses（数据库要求senses不能为空）
                if not entry.senses or len(entry.senses) == 0:
                    # 详细日志：解析后无senses - 用于分析如何增强解析器
                    logger.warning("=" * 80)
                    logger.warning(f"[{i}/{len(all_words)}] 解析后无senses: {word}")
                    logger.warning(f"词典: {source_id} ({config_dict['name']})")
                    logger.warning(f"原始内容长度: {len(raw_content)} 字符")
                    logger.warning(f"原始内容 (完整):")
                    logger.warning(f"{raw_content}")
                    logger.warning(f"解析结果摘要:")
                    logger.warning(f"  - headword: {entry.headword}")
                    logger.warning(f"  - source_id: {entry.source_id}")
                    logger.warning(f"  - pronunciations: {len(entry.pronunciations) if entry.pronunciations else 0} 个")
                    if entry.pronunciations:
                        for idx, pron in enumerate(entry.pronunciations):
                            logger.warning(f"    [{idx+1}] {pron}")
                    logger.warning(f"  - senses: {len(entry.senses) if entry.senses else 0} 个")
                    logger.warning(f"  - forms: {len(entry.forms) if entry.forms else 0} 个")
                    if entry.forms:
                        logger.warning(f"    {entry.forms}")
                    logger.warning(f"  - related_phrases: {len(entry.related_phrases) if entry.related_phrases else 0} 个")
                    logger.warning(f"  - etymology: {entry.etymology[:100] if entry.etymology else 'None'}...")
                    if entry.parse_notes:
                        logger.warning(f"  - 解析备注: {entry.parse_notes}")
                    if entry.parse_quality:
                        logger.warning(f"  - 解析质量分: {entry.parse_quality}")
                    logger.warning("=" * 80)
                    stats['failed_parse'] += 1
                    continue
                
                stats['parsed'] += 1
                batch.append(entry)
                
                # 批量插入
                if len(batch) >= batch_size:
                    success, fail = await insert_entry_batch(conn, batch)
                    stats['imported'] += success
                    stats['failed_import'] += fail
                    batch = []
                    
                    elapsed = time.time() - start_time
                    rate = stats['imported'] / elapsed if elapsed > 0 else 0
                    logger.info(
                        f"进度: {i}/{len(all_words)} "
                        f"已解析: {stats['parsed']} "
                        f"已导入: {stats['imported']} "
                        f"失败: {stats['failed_parse'] + stats['failed_import']} "
                        f"速度: {rate:.1f} 条/秒"
                    )
                    
            except Exception as e:
                logger.error(f"[{i}/{len(all_words)}] 处理失败 {word}: {e}", exc_info=True)
                stats['failed_parse'] += 1
        
        # 处理剩余批次
        if batch:
            success, fail = await insert_entry_batch(conn, batch)
            stats['imported'] += success
            stats['failed_import'] += fail
    
    # 更新索引表
    logger.info("正在更新索引表...")
    try:
        async with get_db() as conn:
            await conn.execute("""
                DELETE FROM dictionary_index WHERE source_id = $1
            """, source_id)
            
            await conn.execute("""
                INSERT INTO dictionary_index (headword, source_id, sort_key, entry_id)
                SELECT DISTINCT ON (headword, source_id) 
                    headword, source_id, LOWER(headword) as sort_key, id as entry_id
                FROM dictionary_entries
                WHERE source_id = $1
                ORDER BY headword, source_id, id DESC
                ON CONFLICT (source_id, headword)
                DO UPDATE SET
                    sort_key = EXCLUDED.sort_key,
                    entry_id = EXCLUDED.entry_id
            """, source_id)
            
            count = await conn.fetchval("""
                SELECT COUNT(*) FROM dictionary_index WHERE source_id = $1
            """, source_id)
            
            logger.info(f"索引表已更新: {source_id} (共 {count} 条索引)")
    except Exception as e:
        logger.error(f"更新索引表失败: {e}", exc_info=True)
    
    # 完成统计
    stats['end_time'] = datetime.now()
    stats['duration'] = (stats['end_time'] - stats['start_time']).total_seconds()
    stats['success'] = True
    
    logger.info(f"\n{'='*60}")
    logger.info(f"导入完成: {config_dict['name']}")
    logger.info(f"总词条数: {stats['total_words']}")
    logger.info(f"解析成功: {stats['parsed']}")
    logger.info(f"解析失败: {stats['failed_parse']}")
    logger.info(f"导入成功: {stats['imported']}")
    logger.info(f"导入失败: {stats['failed_import']}")
    logger.info(f"耗时: {stats['duration']:.1f} 秒")
    logger.info(f"{'='*60}\n")
    
    return stats


async def main():
    parser = argparse.ArgumentParser(description='从原始词典文件导入数据到PostgreSQL')
    parser.add_argument('--source', type=str, help='词典ID (oxford/langdao/gcide/xiandaihanyucidian)')
    parser.add_argument('--all', action='store_true', help='导入所有词典')
    parser.add_argument('--batch-size', type=int, default=100, help='批量处理大小 (默认: 100)')
    parser.add_argument('--limit', type=int, help='限制导入数量（用于测试）')
    
    args = parser.parse_args()
    
    if not args.source and not args.all:
        parser.print_help()
        return
    
    # 初始化数据库连接池
    await create_pool()
    
    try:
        if args.all:
            # 导入所有词典
            all_stats = []
            for source_id in DICT_CONFIGS.keys():
                stats = await import_dict_source(source_id, args.batch_size, args.limit)
                all_stats.append(stats)
            
            # 汇总统计
            logger.info("\n" + "="*60)
            logger.info("全部导入完成 - 汇总统计")
            logger.info("="*60)
            for stats in all_stats:
                if stats.get('success'):
                    logger.info(
                        f"{stats['source_id']:20s} "
                        f"总数: {stats['total_words']:6d} "
                        f"解析: {stats['parsed']:6d} "
                        f"导入: {stats['imported']:6d} "
                        f"失败: {stats['failed_parse'] + stats['failed_import']:6d}"
                    )
        else:
            # 导入单个词典
            await import_dict_source(args.source, args.batch_size, args.limit)
    
    finally:
        await close_pool()


if __name__ == "__main__":
    asyncio.run(main())

