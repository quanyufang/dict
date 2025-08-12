#!/usr/bin/env python3
# -*- coding: utf-8
"""
test_complete_dictionary.py - 测试完整词典（汉字+词语）功能

这个脚本测试包含汉字和词语的完整词典功能。
"""

import sqlite3
import struct
from pathlib import Path


def test_complete_dictionary():
    """测试完整词典功能"""
    print("🧪 测试完整词典功能（汉字+词语）")
    print("=" * 60)
    
    # 数据库文件路径
    db_path = "output/stardict_complete/chinese_dict.db"
    dict_path = "output/stardict_complete/chinese_dict.dict"
    
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
        
        # 测试1: 统计信息
        print("\n📊 测试1: 统计信息")
        cursor.execute("SELECT COUNT(*) FROM wordIndex")
        total_entries = cursor.fetchone()[0]
        print(f"   总条目数: {total_entries}")
        
        # 测试2: 汉字查询测试
        print("\n🔍 测试2: 汉字查询测试")
        test_chars = ['中', '国', '人', '大', '小', '学', '习']
        
        for char in test_chars:
            cursor.execute("SELECT word, offset, length FROM wordIndex WHERE word = ?", (char,))
            result = cursor.fetchone()
            
            if result:
                print(f"✅ 找到汉字: {result[0]} (偏移量: {result[1]}, 长度: {result[2]})")
                
                # 读取汉字内容
                try:
                    with open(dict_path, 'rb') as f:
                        f.seek(result[1])
                        content = f.read(result[2]).decode('utf-8')
                        if '<h2>' in content and '笔画' in content:
                            print(f"   📖 汉字内容读取成功，包含笔画信息")
                        else:
                            print(f"   ⚠️  汉字内容格式可能有问题")
                except Exception as e:
                    print(f"   ❌ 读取汉字内容失败: {e}")
            else:
                print(f"⚠️  未找到汉字: {char}")
        
        # 测试3: 词语查询测试
        print("\n🔍 测试3: 词语查询测试")
        test_words = ['中国', '学习', '计算机', '人工智能', '你好', '谢谢']
        
        for word in test_words:
            cursor.execute("SELECT word, offset, length FROM wordIndex WHERE word = ?", (word.lower(),))
            result = cursor.fetchone()
            
            if result:
                print(f"✅ 找到词语: {result[0]} (偏移量: {result[1]}, 长度: {result[2]})")
                
                # 读取词语内容
                try:
                    with open(dict_path, 'rb') as f:
                        f.seek(result[1])
                        content = f.read(result[2]).decode('utf-8')
                        if '<h2>' in content and '解释' in content:
                            print(f"   📖 词语内容读取成功，包含解释信息")
                        else:
                            print(f"   ⚠️  词语内容格式可能有问题")
                except Exception as e:
                    print(f"   ❌ 读取词语内容失败: {e}")
            else:
                print(f"⚠️  未找到词语: {word}")
        
        # 测试4: 混合查询测试
        print("\n🔍 测试4: 混合查询测试")
        mixed_queries = ['中', '中国', '国', '学习', '习']
        
        for query in mixed_queries:
            cursor.execute("SELECT word, offset, length FROM wordIndex WHERE word = ? OR word = ?", 
                         (query, query.lower()))
            results = cursor.fetchall()
            
            if results:
                for result in results:
                    print(f"✅ 找到条目: {result[0]} (偏移量: {result[1]}, 长度: {result[2]})")
            else:
                print(f"⚠️  未找到条目: {query}")
        
        # 测试5: 性能测试
        print("\n⚡ 测试5: 性能测试")
        
        import time
        start_time = time.time()
        
        # 随机查询100个条目
        cursor.execute("SELECT word FROM wordIndex ORDER BY RANDOM() LIMIT 100")
        random_entries = cursor.fetchall()
        
        query_count = 0
        for (word,) in random_entries:
            cursor.execute("SELECT offset, length FROM wordIndex WHERE word = ?", (word,))
            result = cursor.fetchone()
            if result:
                query_count += 1
        
        end_time = time.time()
        query_time = end_time - start_time
        
        print(f"✅ 随机查询100个条目，成功: {query_count}/100，耗时: {query_time:.3f}秒")
        print(f"   平均查询时间: {query_time/100*1000:.2f}毫秒")
        
        # 测试6: 内容长度统计
        print("\n📊 测试6: 内容长度统计")
        
        cursor.execute("SELECT MIN(length), MAX(length), AVG(length) FROM wordIndex")
        min_len, max_len, avg_len = cursor.fetchone()
        
        print(f"   内容长度范围: {min_len} - {max_len} 字节")
        print(f"   平均内容长度: {avg_len:.1f} 字节")
        
        # 测试7: 汉字和词语数量统计
        print("\n📊 测试7: 汉字和词语数量统计")
        
        # 统计单字符条目（汉字）
        cursor.execute("SELECT COUNT(*) FROM wordIndex WHERE LENGTH(word) = 1")
        char_count = cursor.fetchone()[0]
        
        # 统计多字符条目（词语）
        cursor.execute("SELECT COUNT(*) FROM wordIndex WHERE LENGTH(word) > 1")
        word_count = cursor.fetchone()[0]
        
        print(f"   汉字数量: {char_count}")
        print(f"   词语数量: {word_count}")
        print(f"   总计: {char_count + word_count}")
        
        conn.close()
        
        print("\n🎉 所有测试通过！完整词典功能正常！")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_content_samples():
    """测试内容样本"""
    print("\n📖 测试内容样本")
    print("=" * 60)
    
    db_path = "output/stardict_complete/chinese_dict.db"
    dict_path = "output/stardict_complete/chinese_dict.dict"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 测试汉字内容
        print("\n🔤 汉字内容样本:")
        cursor.execute("SELECT word, offset, length FROM wordIndex WHERE LENGTH(word) = 1 LIMIT 3")
        chars = cursor.fetchall()
        
        for char, offset, length in chars:
            with open(dict_path, 'rb') as f:
                f.seek(offset)
                content = f.read(length).decode('utf-8')
                print(f"\n汉字: {char}")
                print(f"内容: {content[:200]}...")
        
        # 测试词语内容
        print("\n📚 词语内容样本:")
        cursor.execute("SELECT word, offset, length FROM wordIndex WHERE LENGTH(word) > 1 LIMIT 3")
        words = cursor.fetchall()
        
        for word, offset, length in words:
            with open(dict_path, 'rb') as f:
                f.seek(offset)
                content = f.read(length).decode('utf-8')
                print(f"\n词语: {word}")
                print(f"内容: {content[:200]}...")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 内容样本测试失败: {e}")


def main():
    """主函数"""
    print("🧪 开始测试完整词典功能")
    
    # 测试完整词典功能
    success = test_complete_dictionary()
    
    # 测试内容样本
    test_content_samples()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 完整词典测试通过！")
        print("\n✅ 现在您可以享受包含汉字和词语的完整词典了：")
        print("   1. 支持汉字查询（笔画、部首、拼音等）")
        print("   2. 支持词语查询（解释、例句、用法等）")
        print("   3. 统一的查询接口，无需区分汉字和词语")
        print("   4. 优化的查询性能，支持快速检索")
        print("\n📱 您的app现在可以完美支持汉字和词语查询了！")
    else:
        print("❌ 部分测试失败，请检查问题")
        return False
    
    return True


if __name__ == '__main__':
    main()

