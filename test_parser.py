#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本：验证StarDict解析器的修复
"""

import os
import sys

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from convertDictToXml import StarDictParser

def test_parser():
    """测试解析器的基本功能"""
    print("测试StarDict解析器...")
    
    # 检查测试文件是否存在
    test_files = [
        'xiandaihanyucidian.dictcontent',
        'xiandaihanyucidian.idx'
    ]
    
    for file in test_files:
        if not os.path.exists(file):
            print(f"测试文件不存在: {file}")
            return False
    
    try:
        # 创建解析器实例
        parser = StarDictParser(
            'xiandaihanyucidian.dictcontent',
            'xiandaihanyucidian.idx',
            'test_output.xml',
            debug=True
        )
        
        # 测试文件验证
        parser.validate_files()
        print("✓ 文件验证通过")
        
        # 测试索引文件解析
        entries = parser.parse_index_file()
        print(f"✓ 索引文件解析完成，找到 {len(entries)} 个条目")
        
        if entries:
            # 测试第一个条目的内容读取
            key, offset, length = entries[0]
            print(f"第一个条目: key='{key}', offset={offset}, length={length}")
            
            content = parser.read_dict_content(offset, length)
            print(f"内容预览: {content[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_parser()
    if success:
        print("\n🎉 所有测试通过！")
    else:
        print("\n❌ 测试失败！")
        sys.exit(1)
