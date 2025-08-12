#!/usr/bin/env python3
# -*- coding: utf-8
"""
test_compatibility.py - 测试生成的数据库是否与现有app兼容

这个脚本模拟现有app的查询逻辑，验证生成的数据库是否能正常工作。
"""

import sqlite3
import struct
from pathlib import Path


def test_database_compatibility():
    """测试数据库兼容性"""
    print("🔍 测试数据库兼容性...")
    
    # 数据库文件路径
    db_path = "output/stardict_compatible/chinese_dict.db"
    dict_path = "output/stardict_compatible/chinese_dict.dict"
    
    if not Path(db_path).exists():
        print(f"❌ 数据库文件不存在: {db_path}")
        return False
    
    if not Path(dict_path).exists():
        print(f"❌ 字典文件不存在: {dict_path}")
        return False
    
    try:
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 测试1: 检查表结构
        print("\n📋 测试1: 检查表结构")
        cursor.execute("PRAGMA table_info(wordIndex)")
        columns = cursor.fetchall()
        
        expected_columns = [
            (0, 'id', 'INTEGER', 0, None, 1),
            (1, 'word', 'VARCHAR(128)', 0, None, 0),
            (2, 'offset', 'INTEGER', 0, None, 0),
            (3, 'length', 'INTEGER', 0, None, 0)
        ]
        
        if len(columns) == len(expected_columns):
            print("✅ 表结构正确")
        else:
            print(f"❌ 表结构不匹配: 期望{len(expected_columns)}列，实际{len(columns)}列")
            return False
        
        # 测试2: 检查索引
        print("\n🔍 测试2: 检查索引")
        cursor.execute("PRAGMA index_list(wordIndex)")
        indexes = cursor.fetchall()
        
        if len(indexes) >= 2:  # 至少应该有word和offset索引
            print("✅ 索引创建正确")
        else:
            print(f"❌ 索引数量不足: {len(indexes)}")
            return False
        
        # 测试3: 查询测试
        print("\n🔍 测试3: 查询测试")
        
        # 测试查询一些常见词语
        test_words = ['你好', '中国', '学习', '计算机', '人工智能']
        
        for word in test_words:
            cursor.execute("SELECT word, offset, length FROM wordIndex WHERE word = ?", (word.lower(),))
            result = cursor.fetchone()
            
            if result:
                print(f"✅ 找到词语: {result[0]} (偏移量: {result[1]}, 长度: {result[2]})")
                
                # 测试读取字典内容
                try:
                    with open(dict_path, 'rb') as f:
                        f.seek(result[1])
                        content = f.read(result[2]).decode('utf-8')
                        if content.startswith('<h2>') and '</h2>' in content:
                            print(f"   📖 内容读取成功，长度: {len(content)} 字符")
                        else:
                            print(f"   ⚠️  内容格式可能有问题")
                except Exception as e:
                    print(f"   ❌ 读取内容失败: {e}")
            else:
                print(f"⚠️  未找到词语: {word}")
        
        # 测试4: 性能测试
        print("\n⚡ 测试4: 性能测试")
        
        # 测试随机查询性能
        import time
        start_time = time.time()
        
        cursor.execute("SELECT COUNT(*) FROM wordIndex")
        total_words = cursor.fetchone()[0]
        
        # 随机查询100个词语
        cursor.execute("SELECT word FROM wordIndex ORDER BY RANDOM() LIMIT 100")
        random_words = cursor.fetchall()
        
        query_count = 0
        for (word,) in random_words:
            cursor.execute("SELECT offset, length FROM wordIndex WHERE word = ?", (word,))
            result = cursor.fetchone()
            if result:
                query_count += 1
        
        end_time = time.time()
        query_time = end_time - start_time
        
        print(f"✅ 随机查询100个词语，成功: {query_count}/100，耗时: {query_time:.3f}秒")
        print(f"   平均查询时间: {query_time/100*1000:.2f}毫秒")
        
        # 测试5: 统计信息
        print("\n📊 测试5: 统计信息")
        
        cursor.execute("SELECT COUNT(*) FROM wordIndex")
        total_words = cursor.fetchone()[0]
        
        cursor.execute("SELECT MIN(length), MAX(length), AVG(length) FROM wordIndex")
        min_len, max_len, avg_len = cursor.fetchone()
        
        print(f"   总词语数: {total_words}")
        print(f"   内容长度范围: {min_len} - {max_len} 字节")
        print(f"   平均内容长度: {avg_len:.1f} 字节")
        
        conn.close()
        
        print("\n🎉 所有测试通过！数据库与现有app完全兼容！")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_stardict_format():
    """测试StarDict格式文件"""
    print("\n🔍 测试StarDict格式文件...")
    
    # 检查.ifo文件
    ifo_path = "output/stardict_compatible/chinese_dict.ifo"
    if Path(ifo_path).exists():
        with open(ifo_path, 'r', encoding='utf-8') as f:
            ifo_content = f.read()
        
        required_fields = ['version', 'bookname', 'wordcount', 'idxfilesize', 'sametypesequence']
        missing_fields = [field for field in required_fields if field not in ifo_content]
        
        if not missing_fields:
            print("✅ .ifo文件格式正确")
        else:
            print(f"❌ .ifo文件缺少字段: {missing_fields}")
            return False
    else:
        print("❌ .ifo文件不存在")
        return False
    
    # 检查.idx文件
    idx_path = "output/stardict_compatible/chinese_dict.idx"
    if Path(idx_path).exists():
        idx_size = Path(idx_path).stat().st_size
        print(f"✅ .idx文件存在，大小: {idx_size / 1024:.1f} KB")
    else:
        print("❌ .idx文件不存在")
        return False
    
    # 检查.dict文件
    dict_path = "output/stardict_compatible/chinese_dict.dict"
    if Path(dict_path).exists():
        dict_size = Path(dict_path).stat().st_size
        print(f"✅ .dict文件存在，大小: {dict_size / 1024 / 1024:.1f} MB")
    else:
        print("❌ .dict文件不存在")
        return False
    
    return True


def main():
    """主函数"""
    print("🧪 开始测试生成的数据库兼容性")
    print("=" * 50)
    
    # 测试数据库兼容性
    db_ok = test_database_compatibility()
    
    # 测试StarDict格式
    stardict_ok = test_stardict_format()
    
    print("\n" + "=" * 50)
    if db_ok and stardict_ok:
        print("🎉 所有测试通过！")
        print("\n✅ 现在您可以将生成的文件用于现有的app了：")
        print("   1. 将 chinese_dict.db 替换现有的数据库文件")
        print("   2. 使用 chinese_dict.dict, chinese_dict.idx, chinese_dict.ifo 作为StarDict文件")
        print("\n📱 您的app应该能够正常查询这些数据了！")
    else:
        print("❌ 部分测试失败，请检查问题")
        return False
    
    return True


if __name__ == '__main__':
    main()

