#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
解析质量评估工具

从PostgreSQL数据库中统计和评估词典解析质量

使用方法：
    # 评估所有词典
    python evaluate_quality.py
    
    # 评估特定词典
    python evaluate_quality.py --source oxford
    
    # 输出JSON报告
    python evaluate_quality.py --format json
    
    # 输出HTML报告
    python evaluate_quality.py --format html
"""

import sys
import asyncio
import argparse
import logging
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from collections import defaultdict

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from unified.api.database import get_db, create_pool, close_pool
from unified.api.config import config

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def evaluate_source(source_id: str) -> Dict:
    """
    评估单个词典源的解析质量
    
    Returns:
        评估结果字典
    """
    async with get_db() as conn:
        # 1. 基础统计
        total_entries = await conn.fetchval("""
            SELECT COUNT(*) FROM dictionary_entries WHERE source_id = $1
        """, source_id)
        
        if total_entries == 0:
            return {
                'source_id': source_id,
                'total_entries': 0,
                'error': 'No entries found'
            }
        
        # 2. 质量指标统计
        # 有音标/拼音的词条数
        entries_with_pronunciation = await conn.fetchval("""
            SELECT COUNT(*) 
            FROM dictionary_entries 
            WHERE source_id = $1 
            AND (pronunciations IS NOT NULL AND jsonb_array_length(pronunciations) > 0)
        """, source_id)
        
        # 有例句的senses数量
        senses_with_examples = await conn.fetchval("""
            SELECT COUNT(*)
            FROM dictionary_entries,
                 jsonb_array_elements(senses) AS sense
            WHERE source_id = $1
            AND jsonb_array_length(sense->'examples') > 0
        """, source_id)
        
        # 总senses数量
        total_senses = await conn.fetchval("""
            SELECT SUM(jsonb_array_length(senses))
            FROM dictionary_entries
            WHERE source_id = $1
        """, source_id)
        
        # 总例句数量
        total_examples = await conn.fetchval("""
            SELECT COUNT(*)
            FROM dictionary_entries,
                 jsonb_array_elements(senses) AS sense,
                 jsonb_array_elements(sense->'examples') AS example
            WHERE source_id = $1
        """, source_id)
        
        # 有词性的senses数量
        senses_with_pos = await conn.fetchval("""
            SELECT COUNT(*)
            FROM dictionary_entries,
                 jsonb_array_elements(senses) AS sense
            WHERE source_id = $1
            AND (sense->>'pos') IS NOT NULL
            AND (sense->>'pos') != ''
            AND (sense->>'pos') != 'null'
        """, source_id)
        
        # 空释义数量（定义为空或仅包含空格）
        empty_definitions = await conn.fetchval("""
            SELECT COUNT(*)
            FROM dictionary_entries,
                 jsonb_array_elements(senses) AS sense
            WHERE source_id = $1
            AND (
                (sense->>'definition') IS NULL 
                OR TRIM(sense->>'definition') = ''
            )
        """, source_id)
        
        # 平均senses数量
        avg_senses = total_senses / total_entries if total_entries > 0 else 0
        
        # 平均例句数量
        avg_examples = total_examples / total_entries if total_entries > 0 else 0
        
        # 平均每个sense的例句数
        avg_examples_per_sense = total_examples / total_senses if total_senses > 0 else 0
        
        # 3. 数据完整性指标（百分比）
        pronunciation_coverage = (entries_with_pronunciation / total_entries * 100) if total_entries > 0 else 0
        example_coverage = (senses_with_examples / total_senses * 100) if total_senses > 0 else 0
        pos_coverage = (senses_with_pos / total_senses * 100) if total_senses > 0 else 0
        
        # 4. 解析质量分数（parse_quality字段统计）
        quality_stats = await conn.fetchrow("""
            SELECT 
                AVG(parse_quality) as avg_quality,
                MIN(parse_quality) as min_quality,
                MAX(parse_quality) as max_quality,
                COUNT(*) FILTER (WHERE parse_quality >= 0.8) as high_quality_count,
                COUNT(*) FILTER (WHERE parse_quality < 0.5) as low_quality_count
            FROM dictionary_entries
            WHERE source_id = $1
        """, source_id)
        
        # 5. 词条长度分布（按senses数量）
        sense_distribution = await conn.fetch("""
            SELECT 
                jsonb_array_length(senses) as sense_count,
                COUNT(*) as entry_count
            FROM dictionary_entries
            WHERE source_id = $1
            GROUP BY jsonb_array_length(senses)
            ORDER BY sense_count
        """, source_id)
        
        return {
            'source_id': source_id,
            'total_entries': total_entries,
            'total_senses': total_senses,
            'total_examples': total_examples,
            'avg_senses': round(avg_senses, 2),
            'avg_examples': round(avg_examples, 2),
            'avg_examples_per_sense': round(avg_examples_per_sense, 2),
            'entries_with_pronunciation': entries_with_pronunciation,
            'senses_with_examples': senses_with_examples,
            'senses_with_pos': senses_with_pos,
            'empty_definitions': empty_definitions,
            'pronunciation_coverage': round(pronunciation_coverage, 2),
            'example_coverage': round(example_coverage, 2),
            'pos_coverage': round(pos_coverage, 2),
            'quality_stats': {
                'avg_quality': round(float(quality_stats['avg_quality'] or 0), 3),
                'min_quality': round(float(quality_stats['min_quality'] or 0), 3),
                'max_quality': round(float(quality_stats['max_quality'] or 0), 3),
                'high_quality_count': quality_stats['high_quality_count'],
                'low_quality_count': quality_stats['low_quality_count'],
            },
            'sense_distribution': [
                {'sense_count': row['sense_count'], 'entry_count': row['entry_count']}
                for row in sense_distribution
            ]
        }


async def evaluate_all_sources() -> Dict:
    """
    评估所有词典源
    
    Returns:
        所有源的评估结果
    """
    async with get_db() as conn:
        # 获取所有源ID
        sources = await conn.fetch("""
            SELECT DISTINCT source_id 
            FROM dictionary_entries 
            ORDER BY source_id
        """)
        
        all_results = {}
        summary = {
            'total_sources': len(sources),
            'total_entries_all': 0,
            'total_senses_all': 0,
            'total_examples_all': 0,
        }
        
        for row in sources:
            source_id = row['source_id']
            logger.info(f"评估词典: {source_id}")
            result = await evaluate_source(source_id)
            all_results[source_id] = result
            
            if 'total_entries' in result:
                summary['total_entries_all'] += result['total_entries']
                summary['total_senses_all'] += result.get('total_senses', 0)
                summary['total_examples_all'] += result.get('total_examples', 0)
        
        return {
            'summary': summary,
            'by_source': all_results,
            'evaluated_at': datetime.now().isoformat()
        }


def format_json_report(results: Dict) -> str:
    """格式化为JSON报告"""
    return json.dumps(results, indent=2, ensure_ascii=False)


def format_text_report(results: Dict) -> str:
    """格式化为文本报告"""
    lines = []
    lines.append("=" * 80)
    lines.append("词典解析质量评估报告")
    lines.append("=" * 80)
    lines.append(f"评估时间: {results.get('evaluated_at', 'N/A')}")
    lines.append("")
    
    summary = results.get('summary', {})
    lines.append("总体统计:")
    lines.append(f"  词典数量: {summary.get('total_sources', 0)}")
    lines.append(f"  总词条数: {summary.get('total_entries_all', 0):,}")
    lines.append(f"  总释义数: {summary.get('total_senses_all', 0):,}")
    lines.append(f"  总例句数: {summary.get('total_examples_all', 0):,}")
    lines.append("")
    
    by_source = results.get('by_source', {})
    for source_id, stats in by_source.items():
        if 'error' in stats:
            continue
        
        lines.append("-" * 80)
        lines.append(f"词典: {source_id}")
        lines.append("-" * 80)
        lines.append(f"  总词条数: {stats.get('total_entries', 0):,}")
        lines.append(f"  总释义数: {stats.get('total_senses', 0):,}")
        lines.append(f"  总例句数: {stats.get('total_examples', 0):,}")
        lines.append(f"  平均释义数/词条: {stats.get('avg_senses', 0):.2f}")
        lines.append(f"  平均例句数/词条: {stats.get('avg_examples', 0):.2f}")
        lines.append(f"  平均例句数/释义: {stats.get('avg_examples_per_sense', 0):.2f}")
        lines.append("")
        lines.append("  数据完整性:")
        lines.append(f"    有音标/拼音的词条: {stats.get('entries_with_pronunciation', 0):,} ({stats.get('pronunciation_coverage', 0):.1f}%)")
        lines.append(f"    有例句的释义: {stats.get('senses_with_examples', 0):,} ({stats.get('example_coverage', 0):.1f}%)")
        lines.append(f"    有词性的释义: {stats.get('senses_with_pos', 0):,} ({stats.get('pos_coverage', 0):.1f}%)")
        lines.append(f"    空释义数量: {stats.get('empty_definitions', 0):,}")
        lines.append("")
        
        quality_stats = stats.get('quality_stats', {})
        lines.append("  解析质量:")
        lines.append(f"    平均质量分: {quality_stats.get('avg_quality', 0):.3f}")
        lines.append(f"    高质量(≥0.8): {quality_stats.get('high_quality_count', 0):,}")
        lines.append(f"    低质量(<0.5): {quality_stats.get('low_quality_count', 0):,}")
        lines.append("")
        
        # 释义数量分布（前10个）
        distribution = stats.get('sense_distribution', [])[:10]
        if distribution:
            lines.append("  释义数量分布 (前10):")
            for dist in distribution:
                lines.append(f"    {dist['sense_count']} 个释义: {dist['entry_count']:,} 词条")
            lines.append("")
    
    lines.append("=" * 80)
    return "\n".join(lines)


async def main():
    parser = argparse.ArgumentParser(description='评估词典解析质量')
    parser.add_argument('--source', type=str, help='评估特定词典源')
    parser.add_argument('--format', type=str, choices=['text', 'json', 'html'], default='text', 
                       help='输出格式 (默认: text)')
    parser.add_argument('--output', type=str, help='输出文件路径（可选）')
    
    args = parser.parse_args()
    
    # 初始化数据库连接池
    await create_pool()
    
    try:
        if args.source:
            # 评估单个源
            result = await evaluate_source(args.source)
            results = {
                'by_source': {args.source: result},
                'evaluated_at': datetime.now().isoformat()
            }
        else:
            # 评估所有源
            results = await evaluate_all_sources()
        
        # 格式化输出
        if args.format == 'json':
            output = format_json_report(results)
        elif args.format == 'html':
            output = "HTML格式暂未实现，请使用text或json格式"
            logger.warning(output)
            output = format_text_report(results)
        else:
            output = format_text_report(results)
        
        # 输出
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(output)
            logger.info(f"报告已保存到: {output_path}")
        else:
            print(output)
    
    finally:
        await close_pool()


if __name__ == "__main__":
    asyncio.run(main())

