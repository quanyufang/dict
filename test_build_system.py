#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试构建系统的基本功能

验证各个组件是否正常工作
"""

import os
import sys
import json
from pathlib import Path


def test_data_files():
    """测试数据文件是否存在"""
    print("🔍 测试数据文件...")
    
    data_dir = Path("chinese-dictionary-main")
    required_files = [
        "character/char_base.json",
        "character/char_detail.json", 
        "word/word.json",
        "idiom/idiom.json"
    ]
    
    missing_files = []
    for file_path in required_files:
        full_path = data_dir / file_path
        if not full_path.exists():
            missing_files.append(file_path)
        else:
            # 检查文件大小
            size = full_path.stat().st_size
            print(f"  ✅ {file_path} ({size:,} 字节)")
    
    if missing_files:
        print(f"  ❌ 缺少文件: {missing_files}")
        return False
    
    print("  ✅ 所有数据文件检查通过")
    return True


def test_json_parsing():
    """测试JSON文件解析"""
    print("\n🔍 测试JSON文件解析...")
    
    data_dir = Path("chinese-dictionary-main")
    
    try:
        # 测试汉字基础数据
        char_base_path = data_dir / "character" / "char_base.json"
        with open(char_base_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 修复JSON格式问题：添加方括号，移除最后一个逗号
        if not content.strip().startswith('['):
            content = '[' + content
        if not content.strip().endswith(']'):
            # 移除最后一个逗号和换行符，然后添加 ]
            content = content.rstrip().rstrip(',').rstrip() + '\n]'
        
        # 尝试解析修复后的JSON
        char_data = json.loads(content)
        
        if not isinstance(char_data, list):
            print("  ❌ char_base.json 不是列表格式")
            return False
            
        print(f"  ✅ char_base.json 解析成功，包含 {len(char_data)} 个汉字")
        
        # 检查第一个汉字的结构
        if char_data:
            first_char = char_data[0]
            required_fields = ['char', 'pinyin', 'strokes', 'radicals', 'frequency']
            missing_fields = [field for field in required_fields if field not in first_char]
            
            if missing_fields:
                print(f"  ❌ 第一个汉字缺少字段: {missing_fields}")
                return False
                
            print(f"  ✅ 第一个汉字: {first_char['char']}, 拼音: {first_char['pinyin']}")
        
        # 测试词语数据
        word_path = data_dir / "word" / "word.json"
        with open(word_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 修复JSON格式问题
        if not content.strip().startswith('['):
            content = '[' + content
        if not content.strip().endswith(']'):
            content = content.rstrip().rstrip(',').rstrip() + '\n]'
        
        word_data = json.loads(content)
            
        if not isinstance(word_data, list):
            print("  ❌ word.json 不是列表格式")
            return False
            
        print(f"  ✅ word.json 解析成功，包含 {len(word_data)} 个词语")
        
        # 检查第一个词语的结构
        if word_data:
            first_word = word_data[0]
            required_fields = ['word', 'pinyin', 'abbr', 'explanation']
            missing_fields = [field for field in required_fields if field not in first_word]
            
            if missing_fields:
                print(f"  ❌ 第一个词语缺少字段: {missing_fields}")
                return False
                
            print(f"  ✅ 第一个词语: {first_word['word']}, 拼音: {first_word['pinyin']}")
        
        # 测试成语数据
        idiom_path = data_dir / "idiom" / "idiom.json"
        with open(idiom_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 修复JSON格式问题
        if not content.strip().startswith('['):
            content = '[' + content
        if not content.strip().endswith(']'):
            content = content.rstrip().rstrip(',').rstrip() + '\n]'
        
        idiom_data = json.loads(content)
            
        if not isinstance(idiom_data, list):
            print("  ❌ idiom.json 不是列表格式")
            return False
            
        print(f"  ✅ idiom.json 解析成功，包含 {len(idiom_data)} 个成语")
        
        return True
        
    except Exception as e:
        print(f"  ❌ JSON解析失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_python_modules():
    """测试Python模块导入"""
    print("\n🔍 测试Python模块导入...")
    
    required_modules = [
        'sqlite3',
        'json', 
        'logging',
        'pathlib',
        'argparse',
        'dataclasses'
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
            print(f"  ✅ {module}")
        except ImportError:
            print(f"  ❌ {module}")
            missing_modules.append(module)
    
    if missing_modules:
        print(f"  ❌ 缺少模块: {missing_modules}")
        return False
    
    print("  ✅ 所有Python模块导入成功")
    return True


def test_file_permissions():
    """测试文件权限"""
    print("\n🔍 测试文件权限...")
    
    # 测试当前目录是否可写
    current_dir = Path(".")
    if not os.access(current_dir, os.W_OK):
        print("  ❌ 当前目录不可写")
        return False
    
    # 测试是否可以创建测试文件
    test_file = current_dir / "test_permission.tmp"
    try:
        with open(test_file, 'w') as f:
            f.write("test")
        test_file.unlink()  # 删除测试文件
        print("  ✅ 文件权限正常")
        return True
    except Exception as e:
        print(f"  ❌ 文件权限测试失败: {e}")
        return False


def test_build_components():
    """测试构建组件"""
    print("\n🔍 测试构建组件...")
    
    # 检查构建脚本是否存在
    build_scripts = [
        "dict_builder.py",
        "stardict_generator.py", 
        "build_complete_dictionary.py"
    ]
    
    missing_scripts = []
    for script in build_scripts:
        if not Path(script).exists():
            missing_scripts.append(script)
        else:
            print(f"  ✅ {script}")
    
    if missing_scripts:
        print(f"  ❌ 缺少构建脚本: {missing_scripts}")
        return False
    
    print("  ✅ 所有构建组件检查通过")
    return True


def main():
    """主测试函数"""
    print("🧪 汉语拼音辞典构建系统测试")
    print("=" * 50)
    
    tests = [
        ("数据文件检查", test_data_files),
        ("JSON解析测试", test_json_parsing),
        ("Python模块测试", test_python_modules),
        ("文件权限测试", test_file_permissions),
        ("构建组件测试", test_build_components)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        try:
            if test_func():
                passed += 1
            else:
                print(f"  ❌ {test_name} 失败")
        except Exception as e:
            print(f"  ❌ {test_name} 异常: {e}")
    
    print(f"\n📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！构建系统准备就绪")
        print("\n🚀 可以开始构建字典:")
        print("  python build_complete_dictionary.py --data-dir chinese-dictionary-main --output output")
        return True
    else:
        print("❌ 部分测试失败，请检查问题后重试")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
