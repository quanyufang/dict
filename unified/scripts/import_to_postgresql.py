#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将解析后的词典数据导入PostgreSQL数据库

支持从以下数据源导入：
1. JSON文件（解析器输出的JSON格式）
2. 字典对象列表（DictionaryEntry对象）
3. 字典文件目录（批量导入）

使用方法：
    # 导入单个JSON文件
    python import_to_postgresql.py --source oxford --file oxford_samples.json
    
    # 导入目录下所有JSON文件
    python import_to_postgresql.py --source oxford --dir samples/
    
    # 从解析器直接导入（需要实现）
    python import_to_postgresql.py --source oxford --parse --input raw_dict_file
"""

import sys
import json
import asyncio
import argparse
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
import unicodedata

# 添加项目路径（src目录）
# 从 scripts/import_to_postgresql.py 到 src: scripts -> unified -> src
src_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(src_dir))

from unified.models.entry import DictionaryEntry
from unified.api.database import get_db
from unified.api.config import config

# 导入解析器（可选，用于解析原始数据）
try:
    from unified.parsers.oxford import OxfordParser
    from unified.parsers.langdao import LangdaoParser
    from unified.parsers.xiandaihanyucidian import XiandaihanyucidianParser
    from unified.parsers.gcide import GcideParser
    PARSERS_AVAILABLE = True
except ImportError:
    PARSERS_AVAILABLE = False

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def normalize_for_sort(text: str) -> str:
    """
    生成排序键，用于字典顺序
    
    - 英文：转为小写，去除空格
    - 中文：使用Unicode排序
    """
    if not text:
        return ""
    
    # 去除首尾空格，转为小写（英文）
    normalized = text.strip().lower()
    
    # 使用NFD规范化（分离音调符号等）
    normalized = unicodedata.normalize('NFD', normalized)
    
    # 去除组合字符（如音调符号）
    normalized = ''.join(c for c in normalized if unicodedata.category(c) != 'Mn')
    
    return normalized


async def insert_entry(conn, entry: DictionaryEntry, batch_size: int = 100) -> Optional[int]:
    """
    插入单个词典条目
    
    Returns:
        插入的entry_id，如果失败返回None
    """
    try:
        # 转换为字典
        entry_dict = entry.to_dict()
        
        # 准备JSONB数据
        pronunciations_json = json.dumps(entry_dict.get('pronunciations', []), ensure_ascii=False) if entry_dict.get('pronunciations') else None
        senses_json = json.dumps(entry_dict.get('senses', []), ensure_ascii=False) if entry_dict.get('senses') else None
        forms_json = json.dumps(entry_dict.get('forms'), ensure_ascii=False) if entry_dict.get('forms') else None
        related_phrases_json = json.dumps(entry_dict.get('related_phrases', []), ensure_ascii=False) if entry_dict.get('related_phrases') else None
        tags_json = json.dumps(entry_dict.get('tags', []), ensure_ascii=False) if entry_dict.get('tags') else None
        parse_notes_json = json.dumps(entry.parse_notes, ensure_ascii=False) if entry.parse_notes else None
        
        # 使用ON CONFLICT处理重复（基于headword和source_id的唯一约束）
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
                entry_id = EXCLUDED.entry_id,
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
            RETURNING id
        """
        
        entry_id = await conn.fetchval(
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
            entry.parse_quality,
            parse_notes_json
        )
        
        return entry_id
        
    except Exception as e:
        logger.error(f"插入条目失败: {entry.headword} ({entry.source_id}): {str(e)}")
        return None


async def insert_index(conn, entry_id: int, entry: DictionaryEntry):
    """
    插入索引条目（用于遍历查询）
    """
    try:
        sort_key = normalize_for_sort(entry.headword)
        
        insert_query = """
            INSERT INTO dictionary_index (
                source_id, headword, sort_key, entry_id
            ) VALUES ($1, $2, $3, $4)
            ON CONFLICT (source_id, headword)
            DO UPDATE SET
                sort_key = EXCLUDED.sort_key,
                entry_id = EXCLUDED.entry_id
        """
        
        await conn.execute(
            insert_query,
            entry.source_id,
            entry.headword,
            sort_key,
            entry_id
        )
        
    except Exception as e:
        logger.error(f"插入索引失败: {entry.headword} ({entry.source_id}): {str(e)}")


async def update_stats(conn, source_id: str, total_entries: int, total_senses: int, total_examples: int):
    """
    更新统计信息
    """
    try:
        stats_json = json.dumps({
            "total_entries": total_entries,
            "total_senses": total_senses,
            "total_examples": total_examples,
            "last_import": datetime.now().isoformat()
        }, ensure_ascii=False)
        
        insert_query = """
            INSERT INTO dictionary_stats (
                source_id, total_entries, total_senses, total_examples, statistics
            ) VALUES ($1, $2, $3, $4, $5::jsonb)
            ON CONFLICT (source_id)
            DO UPDATE SET
                total_entries = EXCLUDED.total_entries,
                total_senses = EXCLUDED.total_senses,
                total_examples = EXCLUDED.total_examples,
                statistics = EXCLUDED.statistics,
                last_updated = CURRENT_TIMESTAMP
        """
        
        await conn.execute(
            insert_query,
            source_id,
            total_entries,
            total_senses,
            total_examples,
            stats_json
        )
        
    except Exception as e:
        logger.error(f"更新统计信息失败: {source_id}: {str(e)}")


def load_entries_from_json(file_path: Path) -> List[DictionaryEntry]:
    """
    从JSON文件加载词典条目
    """
    entries = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 支持多种JSON格式：
        # 1. 列表格式: [entry1, entry2, ...]  (已解析的DictionaryEntry)
        # 2. 对象格式: {"entries": [entry1, entry2, ...]}  (已解析的DictionaryEntry)
        # 3. 对象格式: {"samples": [{"word": "...", "raw_content": "..."}, ...]}  (原始数据，需要解析)
        if isinstance(data, list):
            entry_list = data
            needs_parsing = False
        elif isinstance(data, dict) and 'entries' in data:
            entry_list = data['entries']
            needs_parsing = False
        elif isinstance(data, dict) and 'samples' in data:
            # samples格式：包含原始数据，需要解析
            entry_list = data['samples']
            needs_parsing = True
            source_id_from_file = data.get('dictionary_id', None)
        else:
            logger.error(f"不支持的JSON格式: {file_path}")
            logger.error(f"期望格式: 列表、{{'entries': [...]}} 或 {{'samples': [...]}}")
            return entries
        
        if needs_parsing:
            # 需要解析原始数据
            if not PARSERS_AVAILABLE:
                logger.error("解析器不可用，无法解析原始数据。请先安装解析器模块。")
                return entries
            
            # 根据source_id选择解析器
            parser = None
            if source_id_from_file == 'oxford':
                parser = OxfordParser()
            elif source_id_from_file == 'langdao':
                parser = LangdaoParser()
            elif source_id_from_file == 'xiandaihanyucidian':
                parser = XiandaihanyucidianParser()
            elif source_id_from_file == 'gcide':
                parser = GcideParser()
            else:
                logger.error(f"未知的词典ID: {source_id_from_file}，无法选择解析器")
                return entries
            
            logger.info(f"使用 {parser.name} 解析器解析原始数据...")
            for sample_data in entry_list:
                try:
                    word = sample_data.get('word')
                    raw_content = sample_data.get('raw_content', '')
                    if not word or not raw_content:
                        logger.warning(f"跳过无效样本: {sample_data}")
                        continue
                    
                    entry = parser.parse_safe(word, raw_content)
                    if entry:
                        entries.append(entry)
                    else:
                        logger.warning(f"解析失败: {word}")
                except Exception as e:
                    logger.warning(f"解析样本失败: {str(e)}")
                    continue
        else:
            # 已解析的数据，直接加载
            for entry_data in entry_list:
                try:
                    entry = DictionaryEntry.from_dict(entry_data)
                    entries.append(entry)
                except Exception as e:
                    logger.warning(f"加载条目失败: {str(e)}")
                    continue
        
        logger.info(f"从 {file_path} 加载了 {len(entries)} 条条目")
        
    except Exception as e:
        logger.error(f"加载JSON文件失败: {file_path}: {str(e)}")
    
    return entries


async def import_entries(entries: List[DictionaryEntry], batch_size: int = 100, update_stats_flag: bool = True):
    """
    导入词典条目到数据库
    
    Args:
        entries: 词典条目列表
        batch_size: 批量大小
        update_stats_flag: 是否更新统计信息
    """
    if not entries:
        logger.warning("没有条目需要导入")
        return
    
    logger.info(f"开始导入 {len(entries)} 条条目...")
    
    # 统计信息
    stats_by_source: Dict[str, Dict[str, int]] = {}
    success_count = 0
    error_count = 0
    
    async with get_db() as conn:
        # 批量处理
        for i in range(0, len(entries), batch_size):
            batch = entries[i:i + batch_size]
            logger.info(f"处理批次 {i // batch_size + 1}/{(len(entries) + batch_size - 1) // batch_size} ({len(batch)} 条)...")
            
            for entry in batch:
                try:
                    # 插入条目
                    entry_id = await insert_entry(conn, entry)
                    
                    if entry_id:
                        # 插入索引
                        await insert_index(conn, entry_id, entry)
                        success_count += 1
                        
                        # 统计
                        source_id = entry.source_id
                        if source_id not in stats_by_source:
                            stats_by_source[source_id] = {
                                'entries': 0,
                                'senses': 0,
                                'examples': 0
                            }
                        
                        stats_by_source[source_id]['entries'] += 1
                        stats_by_source[source_id]['senses'] += len(entry.senses)
                        stats_by_source[source_id]['examples'] += sum(len(s.examples) for s in entry.senses)
                    else:
                        error_count += 1
                        
                except Exception as e:
                    logger.error(f"处理条目失败: {entry.headword}: {str(e)}")
                    error_count += 1
            
            # 每批提交一次（使用事务）
            # asyncpg 默认在连接关闭时自动提交，如果需要显式提交可以使用事务
    
    # 更新统计信息
    if update_stats_flag:
        async with get_db() as conn:
            for source_id, stats in stats_by_source.items():
                await update_stats(
                    conn,
                    source_id,
                    stats['entries'],
                    stats['senses'],
                    stats['examples']
                )
    
    logger.info("=" * 60)
    logger.info(f"导入完成！")
    logger.info(f"成功: {success_count} 条")
    logger.info(f"失败: {error_count} 条")
    logger.info(f"总计: {len(entries)} 条")
    logger.info("=" * 60)
    
    if stats_by_source:
        logger.info("\n按词典统计:")
        for source_id, stats in stats_by_source.items():
            logger.info(f"  {source_id}:")
            logger.info(f"    条目数: {stats['entries']}")
            logger.info(f"    释义数: {stats['senses']}")
            logger.info(f"    例句数: {stats['examples']}")


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='将词典数据导入PostgreSQL数据库')
    parser.add_argument('--file', '-f', type=str, help='JSON文件路径')
    parser.add_argument('--dir', '-d', type=str, help='JSON文件目录（批量导入）')
    parser.add_argument('--source', '-s', type=str, required=True, 
                       help='词典来源ID (oxford/langdao/gcide/xiandai/chinese_dict)')
    parser.add_argument('--batch-size', type=int, default=100, help='批量大小（默认100）')
    parser.add_argument('--no-stats', action='store_true', help='不更新统计信息')
    parser.add_argument('--dry-run', action='store_true', help='仅验证，不实际导入')
    
    args = parser.parse_args()
    
    # 检查参数
    if not args.file and not args.dir:
        parser.error("必须指定 --file 或 --dir")
    
    entries = []
    
    # 加载条目
    if args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            logger.error(f"文件不存在: {file_path}")
            return
        
        loaded_entries = load_entries_from_json(file_path)
        entries.extend(loaded_entries)
    
    elif args.dir:
        dir_path = Path(args.dir)
        if not dir_path.exists() or not dir_path.is_dir():
            logger.error(f"目录不存在: {dir_path}")
            return
        
        json_files = list(dir_path.glob('*.json'))
        if not json_files:
            logger.warning(f"目录中没有找到JSON文件: {dir_path}")
            return
        
        logger.info(f"找到 {len(json_files)} 个JSON文件")
        
        for json_file in json_files:
            loaded_entries = load_entries_from_json(json_file)
            entries.extend(loaded_entries)
    
    # 过滤指定来源
    if args.source:
        entries = [e for e in entries if e.source_id == args.source]
        logger.info(f"过滤后: {len(entries)} 条条目 (source={args.source})")
    
    if not entries:
        logger.warning("没有找到需要导入的条目")
        return
    
    # 干运行模式
    if args.dry_run:
        logger.info("=" * 60)
        logger.info("干运行模式 - 仅验证数据，不实际导入")
        logger.info("=" * 60)
        logger.info(f"将导入 {len(entries)} 条条目")
        for i, entry in enumerate(entries[:10], 1):
            logger.info(f"{i}. {entry.headword} ({entry.source_id}) - {len(entry.senses)} 个释义")
        if len(entries) > 10:
            logger.info(f"... 还有 {len(entries) - 10} 条")
        logger.info("验证通过，数据格式正确")
        return
    
    # 导入数据
    await import_entries(
        entries,
        batch_size=args.batch_size,
        update_stats_flag=not args.no_stats
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n\n操作已取消")
    except Exception as e:
        logger.error(f"\n❌ 错误: {str(e)}")
        import traceback
        traceback.print_exc()

