#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import struct

def verify_offsets():
    """验证偏移量计算的正确性"""
    
    # 连接数据库
    conn = sqlite3.connect("../output/stardict_complete/chinese_dict.db")
    cursor = conn.cursor()
    
    # 查询一些条目的偏移量
    cursor.execute("""
        SELECT word, offset, length 
        FROM wordIndex 
        WHERE word IN ('札', '札记', '中', '中国')
        ORDER BY word
    """)
    
    results = cursor.fetchall()
    
    print("🔍 验证偏移量计算:")
    print("=" * 50)
    
    for word, offset, length in results:
        print(f"词语: {word}")
        print(f"偏移量: {offset}")
        print(f"长度: {length}")
        
        # 读取内容
        try:
            with open("../output/stardict_complete/chinese_dict.dict", 'rb') as f:
                f.seek(offset)
                content_bytes = f.read(length)
                
                # 尝试解码
                try:
                    content_str = content_bytes.decode('utf-8')
                    print(f"内容: {content_str[:100]}...")
                    
                    # 检查内容是否包含正确的词语
                    if word in content_str:
                        print("✅ 内容正确包含词语")
                    else:
                        print("❌ 内容中没有找到词语")
                        
                except UnicodeDecodeError as e:
                    print(f"❌ UTF-8解码失败: {e}")
                    print(f"原始字节: {content_bytes[:50]}...")
                    
        except Exception as e:
            print(f"❌ 读取文件失败: {e}")
            
        print("-" * 30)
    
    conn.close()

if __name__ == "__main__":
    verify_offsets()
