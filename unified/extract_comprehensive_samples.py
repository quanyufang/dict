#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全面词典样例提取工具

提取更多样例词汇，包含原始数据，用于详细分析和人工review。
"""

import os
import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import random

# 词典文件目录
DICT_BASE_PATH = Path(__file__).parent.parent.parent / "app_dictfiles"
OUTPUT_PATH = Path(__file__).parent / "comprehensive_samples"


# 扩展的英文样例词汇 - 覆盖各种类型
ENGLISH_SAMPLES_EXTENDED = [
    # ========== 常用基础词 ==========
    "a", "the", "is", "are", "be", "have", "has", "had",
    "do", "does", "did", "will", "would", "can", "could",
    "good", "bad", "big", "small", "new", "old", "long", "short",
    "go", "come", "make", "take", "get", "put", "give", "keep",
    "say", "tell", "ask", "see", "look", "find", "know", "think",
    
    # ========== 多义词（释义多的词）==========
    "run", "set", "take", "get", "put", "turn", "break", "fall",
    "hold", "stand", "sit", "lie", "cut", "draw", "play", "work",
    "call", "point", "hand", "face", "head", "back", "part", "side",
    
    # ========== 名词 ==========
    "book", "water", "time", "people", "world", "day", "year", "life",
    "man", "woman", "child", "house", "school", "company", "system",
    "problem", "question", "answer", "idea", "fact", "reason", "case",
    
    # ========== 形容词 ==========
    "beautiful", "important", "different", "possible", "available",
    "great", "little", "high", "low", "large", "young", "right", "wrong",
    "public", "private", "local", "national", "international",
    
    # ========== 动词变形测试 ==========
    "running", "taken", "went", "gone", "better", "best", "worse", "worst",
    "being", "having", "doing", "saying", "going", "coming", "making",
    
    # ========== 专业词汇 ==========
    "algorithm", "database", "philosophy", "psychology", "economy",
    "technology", "environment", "government", "development", "management",
    "computer", "software", "hardware", "network", "internet",
    "science", "research", "analysis", "theory", "method",
    
    # ========== 短语/习语相关 ==========
    "give up", "look for", "come up", "go on", "take off",
    
    # ========== 生僻/难词 ==========
    "serendipity", "ephemeral", "ubiquitous", "paradigm", "synergy",
    "ameliorate", "exacerbate", "facilitate", "implement", "constitute",
    
    # ========== 易混淆词 ==========
    "affect", "effect", "accept", "except", "advice", "advise",
    "lose", "loose", "than", "then", "their", "there", "they're",
    
    # ========== 缩写/特殊 ==========
    "etc", "eg", "ie", "vs", "ok",
]

# 扩展的中文样例词汇
CHINESE_SAMPLES_EXTENDED = [
    # ========== 常用单字 ==========
    "一", "二", "三", "四", "五", "六", "七", "八", "九", "十",
    "人", "大", "中", "小", "上", "下", "左", "右", "前", "后",
    "天", "地", "日", "月", "年", "时", "分", "秒",
    "东", "西", "南", "北",
    
    # ========== 多音字 ==========
    "行", "了", "着", "的", "得", "地", "长", "乐", "重", "数",
    "干", "发", "还", "好", "会", "几", "教", "觉", "空", "累",
    
    # ========== 常用词语 ==========
    "学习", "工作", "朋友", "时间", "问题", "方法", "情况", "关系",
    "发展", "经济", "社会", "文化", "教育", "科学", "技术", "环境",
    "生活", "健康", "安全", "质量", "效率", "水平", "能力", "条件",
    
    # ========== 成语 ==========
    "一帆风顺", "画龙点睛", "守株待兔", "亡羊补牢", "刻舟求剑",
    "掩耳盗铃", "自相矛盾", "叶公好龙", "井底之蛙", "杯弓蛇影",
    "狐假虎威", "愚公移山", "塞翁失马", "滥竽充数", "对牛弹琴",
    
    # ========== 词组 ==========
    "中国人", "计算机", "互联网", "手机", "电脑", "电视", "电影",
]


def get_random_words_from_db(db_path: Path, count: int = 100) -> List[str]:
    """从数据库随机抽取单词"""
    if not db_path.exists():
        return []
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # 获取总词数
    cursor.execute('SELECT COUNT(*) FROM wordIndex')
    total = cursor.fetchone()[0]
    
    # 随机抽取
    cursor.execute(f'SELECT word FROM wordIndex ORDER BY RANDOM() LIMIT {count}')
    words = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    return words


def query_word(db_path: Path, content_path: Path, word: str) -> Optional[Tuple[str, int, int]]:
    """从词典查询单词，返回 (内容, offset, length)"""
    if not db_path.exists() or not content_path.exists():
        return None
        
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
    
    with open(content_path, 'rb') as f:
        f.seek(offset)
        raw_bytes = f.read(length)
        try:
            content = raw_bytes.decode('utf-8')
        except UnicodeDecodeError:
            content = raw_bytes.decode('utf-8', errors='replace')
    
    return (content, offset, length)


def extract_langdao_comprehensive():
    """全面提取朗道词典样例"""
    db_path = DICT_BASE_PATH / "langdao-ec-gb.db"
    content_path = DICT_BASE_PATH / "langdao-ec-gb.dictcontent"
    
    print("=" * 60)
    print("朗道英汉词典 - 全面样例提取")
    print("=" * 60)
    
    # 1. 指定词汇
    samples = []
    found_count = 0
    not_found = []
    
    for word in ENGLISH_SAMPLES_EXTENDED:
        result = query_word(db_path, content_path, word)
        if result:
            content, offset, length = result
            samples.append({
                "word": word,
                "raw_content": content,
                "offset": offset,
                "length": length,
                "source": "specified"
            })
            found_count += 1
        else:
            not_found.append(word)
    
    print(f"指定词汇: 找到 {found_count}/{len(ENGLISH_SAMPLES_EXTENDED)}")
    if not_found:
        print(f"未找到: {not_found[:20]}{'...' if len(not_found) > 20 else ''}")
    
    # 2. 随机抽样补充
    random_words = get_random_words_from_db(db_path, 50)
    random_found = 0
    
    for word in random_words:
        # 跳过已有的
        if any(s['word'].lower() == word.lower() for s in samples):
            continue
        
        result = query_word(db_path, content_path, word)
        if result:
            content, offset, length = result
            samples.append({
                "word": word,
                "raw_content": content,
                "offset": offset,
                "length": length,
                "source": "random"
            })
            random_found += 1
    
    print(f"随机抽样: 添加 {random_found} 个")
    print(f"总计样例: {len(samples)}")
    
    return samples


def analyze_langdao_format(samples: List[Dict]) -> Dict:
    """详细分析朗道词典格式"""
    import re
    
    analysis = {
        "total_samples": len(samples),
        "format_patterns": {},
        "statistics": {},
        "special_cases": [],
        "samples_by_category": {}
    }
    
    # 统计数据
    stats = {
        "has_phonetic": 0,
        "has_pos": 0,
        "has_domain": 0,
        "has_related_phrases": 0,
        "avg_length": 0,
        "max_length": 0,
        "min_length": float('inf'),
        "pos_distribution": {},
        "domain_distribution": {},
    }
    
    # 格式模式检测
    patterns_found = {
        "phonetic_star_bracket": 0,      # *[ipa]
        "phonetic_slash": 0,              # /ipa/
        "pos_with_dot": 0,                # n. v. a.
        "domain_bracket": 0,              # 【经】【计】
        "related_phrases_section": 0,     # 相关词组:
        "multiline": 0,                   # 多行内容
        "single_line": 0,                 # 单行内容
    }
    
    # 特殊案例收集
    special_cases = []
    
    for sample in samples:
        content = sample['raw_content']
        word = sample['word']
        length = len(content)
        
        # 长度统计
        stats['avg_length'] += length
        stats['max_length'] = max(stats['max_length'], length)
        stats['min_length'] = min(stats['min_length'], length)
        
        # 行数统计
        lines = content.strip().split('\n')
        if len(lines) > 1:
            patterns_found['multiline'] += 1
        else:
            patterns_found['single_line'] += 1
        
        # 音标检测
        if re.search(r'\*\[([^\]]+)\]', content):
            stats['has_phonetic'] += 1
            patterns_found['phonetic_star_bracket'] += 1
        elif re.search(r'/[^/]+/', content):
            patterns_found['phonetic_slash'] += 1
        
        # 词性检测
        pos_matches = re.findall(r'\b(n\.|v\.|vt\.|vi\.|a\.|ad\.|adj\.|adv\.|prep\.|conj\.|pron\.|int\.|interj\.|num\.|abbr\.)', content)
        if pos_matches:
            stats['has_pos'] += 1
            patterns_found['pos_with_dot'] += 1
            for pos in pos_matches:
                stats['pos_distribution'][pos] = stats['pos_distribution'].get(pos, 0) + 1
        
        # 领域标签检测
        domain_matches = re.findall(r'【([^】]+)】', content)
        if domain_matches:
            stats['has_domain'] += 1
            patterns_found['domain_bracket'] += 1
            for domain in domain_matches:
                stats['domain_distribution'][domain] = stats['domain_distribution'].get(domain, 0) + 1
        
        # 相关词组检测
        if '相关词组' in content:
            stats['has_related_phrases'] += 1
            patterns_found['related_phrases_section'] += 1
        
        # 特殊案例检测
        if length < 20:
            special_cases.append({
                "type": "very_short",
                "word": word,
                "content": content,
                "note": "内容极短"
            })
        elif length > 2000:
            special_cases.append({
                "type": "very_long",
                "word": word,
                "length": length,
                "note": "内容极长"
            })
        
        # 检测异常格式
        if not re.search(r'\*\[', content) and not any(content.startswith(p) for p in ['n.', 'v.', 'a.', 'ad.']):
            if not content.startswith('【'):
                special_cases.append({
                    "type": "unusual_start",
                    "word": word,
                    "content": content[:100],
                    "note": "开头格式异常"
                })
    
    # 计算平均值
    stats['avg_length'] = stats['avg_length'] / len(samples) if samples else 0
    
    analysis['statistics'] = stats
    analysis['format_patterns'] = patterns_found
    analysis['special_cases'] = special_cases[:20]  # 限制数量
    
    # 按类别分组样例
    categories = {
        "basic_words": [],      # 基础词
        "multi_sense": [],      # 多义词
        "with_domain": [],      # 有领域标签
        "with_phrases": [],     # 有相关词组
        "short_entries": [],    # 短条目
        "long_entries": [],     # 长条目
    }
    
    for sample in samples:
        content = sample['raw_content']
        length = len(content)
        
        if length < 100:
            categories['short_entries'].append(sample)
        elif length > 500:
            categories['long_entries'].append(sample)
        
        if '【' in content:
            categories['with_domain'].append(sample)
        
        if '相关词组' in content:
            categories['with_phrases'].append(sample)
        
        # 多义词判断（多个词性或很长）
        pos_count = len(re.findall(r'\b(n\.|v\.|a\.|ad\.)', content))
        if pos_count >= 3 or length > 800:
            categories['multi_sense'].append(sample)
    
    # 每类只保留5个示例
    for cat in categories:
        categories[cat] = categories[cat][:5]
    
    analysis['samples_by_category'] = categories
    
    return analysis


def main():
    """主函数"""
    OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
    
    # 提取朗道样例
    langdao_samples = extract_langdao_comprehensive()
    
    # 保存完整样例（包含原始数据）
    output_file = OUTPUT_PATH / "langdao_comprehensive.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "dictionary_id": "langdao",
            "dictionary_name": "朗道英汉词典",
            "total_samples": len(langdao_samples),
            "samples": langdao_samples
        }, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 样例数据已保存: {output_file}")
    
    # 详细分析
    analysis = analyze_langdao_format(langdao_samples)
    
    analysis_file = OUTPUT_PATH / "langdao_detailed_analysis.json"
    with open(analysis_file, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)
    print(f"✅ 分析结果已保存: {analysis_file}")
    
    # 生成人工review报告
    generate_review_report(langdao_samples, analysis, OUTPUT_PATH / "langdao_review_report.md")
    print(f"✅ Review报告已生成: {OUTPUT_PATH / 'langdao_review_report.md'}")
    
    return langdao_samples, analysis


def generate_review_report(samples: List[Dict], analysis: Dict, output_path: Path):
    """生成人工review报告"""
    
    report = f"""# 朗道英汉词典 - 详细分析报告

> 生成时间: 2026-01-08  
> 样例总数: {len(samples)}

---

## 📊 统计概览

| 指标 | 数值 |
|------|------|
| 样例总数 | {analysis['statistics'].get('total_samples', len(samples))} |
| 有音标 | {analysis['statistics']['has_phonetic']} ({analysis['statistics']['has_phonetic']/len(samples)*100:.1f}%) |
| 有词性 | {analysis['statistics']['has_pos']} ({analysis['statistics']['has_pos']/len(samples)*100:.1f}%) |
| 有领域标签 | {analysis['statistics']['has_domain']} ({analysis['statistics']['has_domain']/len(samples)*100:.1f}%) |
| 有相关词组 | {analysis['statistics']['has_related_phrases']} ({analysis['statistics']['has_related_phrases']/len(samples)*100:.1f}%) |
| 平均长度 | {analysis['statistics']['avg_length']:.0f} 字符 |
| 最大长度 | {analysis['statistics']['max_length']} 字符 |
| 最小长度 | {analysis['statistics']['min_length']} 字符 |

---

## 📝 格式模式统计

| 模式 | 出现次数 | 说明 |
|------|----------|------|
| `*[ipa]` 音标 | {analysis['format_patterns']['phonetic_star_bracket']} | 星号方括号格式 |
| `/ipa/` 音标 | {analysis['format_patterns']['phonetic_slash']} | 斜杠格式 |
| `n. v. a.` 词性 | {analysis['format_patterns']['pos_with_dot']} | 带点缩写 |
| `【领域】` 标签 | {analysis['format_patterns']['domain_bracket']} | 中文方括号 |
| `相关词组:` | {analysis['format_patterns']['related_phrases_section']} | 词组部分 |
| 多行条目 | {analysis['format_patterns']['multiline']} | 换行分隔 |
| 单行条目 | {analysis['format_patterns']['single_line']} | 无换行 |

---

## 📖 词性分布

| 词性 | 出现次数 |
|------|----------|
"""
    
    for pos, count in sorted(analysis['statistics']['pos_distribution'].items(), key=lambda x: -x[1]):
        report += f"| `{pos}` | {count} |\n"
    
    report += """
---

## 🏷️ 领域标签分布

| 领域 | 出现次数 |
|------|----------|
"""
    
    for domain, count in sorted(analysis['statistics']['domain_distribution'].items(), key=lambda x: -x[1]):
        report += f"| 【{domain}】 | {count} |\n"
    
    report += """
---

## ⚠️ 特殊案例

"""
    
    for case in analysis['special_cases'][:10]:
        report += f"### {case['type']}: `{case['word']}`\n"
        report += f"- 说明: {case['note']}\n"
        if 'content' in case:
            report += f"- 内容: `{case['content'][:200]}`\n"
        if 'length' in case:
            report += f"- 长度: {case['length']} 字符\n"
        report += "\n"
    
    report += """
---

## 📋 样例展示（按类别）

### 短条目示例

"""
    
    for sample in analysis['samples_by_category'].get('short_entries', [])[:5]:
        report += f"#### `{sample['word']}`\n```\n{sample['raw_content']}\n```\n\n"
    
    report += """
### 长条目示例

"""
    
    for sample in analysis['samples_by_category'].get('long_entries', [])[:3]:
        content = sample['raw_content']
        if len(content) > 1000:
            content = content[:1000] + "\n... (truncated)"
        report += f"#### `{sample['word']}` ({len(sample['raw_content'])} 字符)\n```\n{content}\n```\n\n"
    
    report += """
### 含领域标签示例

"""
    
    for sample in analysis['samples_by_category'].get('with_domain', [])[:5]:
        report += f"#### `{sample['word']}`\n```\n{sample['raw_content']}\n```\n\n"
    
    report += """
### 含相关词组示例

"""
    
    for sample in analysis['samples_by_category'].get('with_phrases', [])[:3]:
        content = sample['raw_content']
        if len(content) > 800:
            content = content[:800] + "\n... (truncated)"
        report += f"#### `{sample['word']}`\n```\n{content}\n```\n\n"
    
    report += """
---

## 🔍 全部样例原始数据

以下是所有样例的原始数据，供详细review:

"""
    
    # 按字母顺序排列
    sorted_samples = sorted(samples, key=lambda x: x['word'].lower())
    
    for sample in sorted_samples:
        word = sample['word']
        content = sample['raw_content']
        source = sample.get('source', 'unknown')
        
        # 对于很长的内容，截断显示
        display_content = content
        if len(content) > 1500:
            display_content = content[:1500] + "\n\n... [内容过长，已截断，完整内容请查看JSON文件]"
        
        report += f"### `{word}` (来源: {source}, 长度: {len(content)})\n\n"
        report += f"```\n{display_content}\n```\n\n---\n\n"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)


if __name__ == '__main__':
    main()

