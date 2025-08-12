#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import struct

def debug_zha_ji():
    """调试'札记'这个词的问题"""
    
    # 检查中间数据库
    print("🔍 检查中间数据库...")
    source_conn = sqlite3.connect("../output/chinese_dictionary.db")
    source_cursor = source_conn.cursor()
    
    # 查询札记
    source_cursor.execute("SELECT id, word, pinyin, abbr, explanation FROM words WHERE word = '札记'")
    word_data = source_cursor.fetchone()
    
    if word_data:
        print("✅ 中间数据库中找到'札记':")
        print(f"   id: {word_data[0]}")
        print(f"   word: {word_data[1]}")
        print(f"   pinyin: {word_data[2]}")
        print(f"   abbr: {word_data[3]}")
        print(f"   explanation: {word_data[4]}")
        
        # 格式化内容
        word_dict = {
            'word': word_data[1],
            'pinyin': word_data[2],
            'abbr': word_data[3],
            'explanation': word_data[4]
        }
        
        # 模拟格式化
        content = format_word_content_debug(word_dict)
        print(f"\n📖 格式化后的内容:")
        print(f"{'='*50}")
        print(content)
        print(f"{'='*50}")
        print(f"内容长度: {len(content)} 字符")
        print(f"UTF-8字节长度: {len(content.encode('utf-8'))} 字节")
        
    else:
        print("❌ 中间数据库中未找到'札记'")
    
    source_conn.close()
    
    # 检查最终数据库
    print(f"\n🔍 检查最终数据库...")
    target_conn = sqlite3.connect("../output/stardict_complete/chinese_dict.db")
    target_cursor = target_conn.cursor()
    
    target_cursor.execute("SELECT word, offset, length FROM wordIndex WHERE word = '札记'")
    result = target_cursor.fetchone()
    
    if result:
        word, offset, length = result
        print(f"✅ 最终数据库中找到'札记':")
        print(f"   word: {word}")
        print(f"   offset: {offset}")
        print(f"   length: {length}")
        
        # 检查dict文件中的内容
        try:
            with open("../output/stardict_complete/chinese_dict.dict", 'rb') as f:
                f.seek(offset)
                content_bytes = f.read(length)
                print(f"\n📖 从dict文件读取的内容:")
                print(f"{'='*50}")
                print(f"原始字节: {content_bytes[:100]}...")
                print(f"{'='*50}")
                
                # 尝试解码
                try:
                    content_str = content_bytes.decode('utf-8')
                    print(f"✅ UTF-8解码成功:")
                    print(content_str)
                except UnicodeDecodeError as e:
                    print(f"❌ UTF-8解码失败: {e}")
                    
                    # 尝试其他编码
                    try:
                        content_str = content_bytes.decode('gbk')
                        print(f"✅ GBK解码成功:")
                        print(content_str)
                    except:
                        print("❌ GBK解码也失败")
                        
        except Exception as e:
            print(f"❌ 读取dict文件失败: {e}")
    
    target_conn.close()

def format_word_content_debug(word_data):
    """格式化词语内容（调试版本）"""
    word = word_data.get('word', '')
    pinyin = word_data.get('pinyin', '')
    explanation = word_data.get('explanation', '')
    abbr = word_data.get('abbr', '')
    
    # 构建HTML内容
    html_parts = []
    
    # 标题行
    if pinyin:
        html_parts.append(f'<h2>{word} [{pinyin}]</h2>')
    else:
        html_parts.append(f'<h2>{word}</h2>')
    
    # 缩写
    if abbr:
        html_parts.append(f'<p><strong>缩写:</strong> {abbr}</p>')
    
    # 解释
    if explanation:
        html_parts.append(f'<p><strong>解释:</strong> {explanation}</p>')
    
    # 如果没有内容，提供默认信息
    if len(html_parts) <= 1:
        html_parts.append('<p>暂无详细解释</p>')
    
    return '\n'.join(html_parts)

if __name__ == "__main__":
    debug_zha_ji()
