#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import sys

def test_zha_ji():
    """测试查询'札记'这个词"""
    db_path = "../output/stardict_complete/chinese_dict.db"
    dict_path = "../output/stardict_complete/chinese_dict.dict"
    
    try:
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 查询札记
        cursor.execute("SELECT word, offset, length FROM wordIndex WHERE word = '札记'")
        result = cursor.fetchone()
        
        if result:
            word, offset, length = result
            print(f"✅ 找到词语: {word}")
            print(f"   偏移量: {offset}")
            print(f"   长度: {length}")
            
            # 读取内容
            try:
                with open(dict_path, 'rb') as f:
                    f.seek(offset)
                    content = f.read(length)
                    content_str = content.decode('utf-8')
                    print(f"\n📖 词语内容:")
                    print(f"{'='*50}")
                    print(content_str)
                    print(f"{'='*50}")
                    
                    # 检查内容是否包含"札记"
                    if "札记" in content_str:
                        print("✅ 内容正确包含'札记'")
                    else:
                        print("❌ 内容中没有找到'札记'")
                        
            except Exception as e:
                print(f"❌ 读取内容失败: {e}")
                
        else:
            print("❌ 未找到'札记'")
            
        # 查询"札"字
        print(f"\n🔍 查询汉字'札':")
        cursor.execute("SELECT word, offset, length FROM wordIndex WHERE word = '札'")
        result = cursor.fetchone()
        
        if result:
            word, offset, length = result
            print(f"✅ 找到汉字: {word}")
            print(f"   偏移量: {offset}")
            print(f"   长度: {length}")
            
            # 读取内容
            try:
                with open(dict_path, 'rb') as f:
                    f.seek(offset)
                    content = f.read(length)
                    content_str = content.decode('utf-8')
                    print(f"\n📖 汉字内容:")
                    print(f"{'='*50}")
                    print(content_str)
                    print(f"{'='*50}")
                    
            except Exception as e:
                print(f"❌ 读取内容失败: {e}")
                
        conn.close()
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    test_zha_ji()
