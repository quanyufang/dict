#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import sys
from pathlib import Path

def test_dictionary():
    """测试最终生成的字典"""
    
    db_path = Path("../output/stardict_complete/chinese_dict.db")
    dict_path = Path("../output/stardict_complete/chinese_dict.dictcontent")
    
    if not db_path.exists():
        print("❌ 数据库文件不存在")
        return False
    
    if not dict_path.exists():
        print("❌ 字典文件不存在")
        return False
    
    print("🧪 测试最终生成的字典")
    print("=" * 50)
    
    # 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 测试表结构
    cursor.execute("PRAGMA table_info(wordIndex)")
    columns = cursor.fetchall()
    print("📋 数据库表结构:")
    for col in columns:
        print(f"   {col[1]} ({col[2]})")
    
    # 统计信息
    cursor.execute("SELECT COUNT(*) FROM wordIndex")
    total_count = cursor.fetchone()[0]
    print(f"\n📊 总条目数: {total_count}")
    
    # 测试查询
    test_words = ['要', '札记', '中国', '中', '札']
    
    print(f"\n🔍 测试查询:")
    for word in test_words:
        cursor.execute("SELECT word, offset, length FROM wordIndex WHERE word = ?", (word,))
        result = cursor.fetchone()
        
        if result:
            word_name, offset, length = result
            print(f"✅ {word}: 偏移量={offset}, 长度={length}")
            
            # 读取内容
            try:
                with open(dict_path, 'rb') as f:
                    f.seek(offset)
                    content_bytes = f.read(length)
                    content = content_bytes.decode('utf-8')
                    print(f"   内容: {content[:100]}...")
            except Exception as e:
                print(f"   ❌ 读取内容失败: {e}")
        else:
            print(f"❌ {word}: 未找到")
    
    # 测试一些边界情况
    print(f"\n🔍 边界测试:")
    
    # 测试单字符
    cursor.execute("SELECT COUNT(*) FROM wordIndex WHERE LENGTH(word) = 1")
    single_char_count = cursor.fetchone()[0]
    print(f"   单字符数量: {single_char_count}")
    
    # 测试多字符
    cursor.execute("SELECT COUNT(*) FROM wordIndex WHERE LENGTH(word) > 1")
    multi_char_count = cursor.fetchone()[0]
    print(f"   多字符数量: {multi_char_count}")
    
    # 测试重复项
    cursor.execute("""
        SELECT word, COUNT(*) as count 
        FROM wordIndex 
        GROUP BY word 
        HAVING COUNT(*) > 1
    """)
    duplicates = cursor.fetchall()
    print(f"   重复条目: {len(duplicates)}")
    
    conn.close()
    
    print(f"\n✅ 测试完成！")
    return True

if __name__ == "__main__":
    test_dictionary()
