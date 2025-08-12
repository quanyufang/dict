#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整的汉语拼音辞典构建脚本

整合整个构建流程：
1. 构建SQLite数据库
2. 生成StarDict格式文件
3. 创建查询工具
"""

import os
import sys
import time
import argparse
from pathlib import Path
import subprocess


def run_command(cmd: str, description: str) -> bool:
    """运行命令并处理结果"""
    print(f"\n🔄 {description}...")
    print(f"执行命令: {cmd}")
    print(f"开始时间: {time.strftime('%H:%M:%S')}")
    
    try:
        # 使用实时输出，显示进展
        process = subprocess.Popen(
            cmd, 
            shell=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # 实时监控输出
        start_time = time.time()
        last_progress_time = start_time
        
        print(f"🔄 进程已启动，PID: {process.pid}")
        
        while True:
            # 检查进程是否还在运行
            if process.poll() is not None:
                break
                
            current_time = time.time()
            elapsed = current_time - start_time
            
            # 尝试读取输出
            try:
                # 非阻塞读取
                import select
                readable, _, _ = select.select([process.stdout, process.stderr], [], [], 1.0)
                
                for stream in readable:
                    if stream == process.stdout and process.stdout:
                        line = process.stdout.readline()
                        if line:
                            print(f"[{description}] {line.strip()}")
                    elif stream == process.stderr and process.stderr:
                        line = process.stderr.readline()
                        if line:
                            print(f"[{description} ERROR] {line.strip()}")
                            
            except Exception as e:
                print(f"[{description}] 读取输出时出错: {e}")
            
            # 显示进度（每30秒显示一次）
            if current_time - last_progress_time > 30:
                print(f"⏱️  {description}运行中... 已用时: {int(elapsed)}秒")
                last_progress_time = current_time
        
        # 获取最终结果
        stdout, stderr = process.communicate()
        return_code = process.returncode
        
        if return_code == 0:
            print(f"✅ {description}完成")
            print(f"结束时间: {time.strftime('%H:%M:%S')}")
            print(f"总用时: {int(time.time() - start_time)}秒")
            if stdout:
                print(f"最终输出: {stdout[-500:]}...")  # 只显示最后500字符
            return True
        else:
            print(f"❌ {description}失败")
            print(f"错误代码: {return_code}")
            print(f"结束时间: {time.strftime('%H:%M:%S')}")
            print(f"总用时: {int(time.time() - start_time)}秒")
            if stdout:
                print(f"标准输出: {stdout[-500:]}...")
            if stderr:
                print(f"错误输出: {stderr[-500:]}...")
            return False
            
    except Exception as e:
        print(f"❌ {description}执行异常: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_dependencies():
    """检查依赖项"""
    print("🔍 检查依赖项...")
    
    # 检查Python版本
    if sys.version_info < (3, 7):
        print("❌ 需要Python 3.7或更高版本")
        return False
    
    # 检查必要的模块
    required_modules = ['sqlite3', 'json', 'logging', 'pathlib', 'argparse']
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print(f"❌ 缺少必要的Python模块: {missing_modules}")
        return False
    
    print("✅ 依赖项检查通过")
    return True


def build_database(data_dir: str, output_dir: str) -> bool:
    """构建数据库"""
    cmd = f"python3 dict_builder.py --data-dir {data_dir} --output-dir {output_dir}"
    return run_command(cmd, "构建SQLite数据库")


def generate_stardict(db_path: str, output_dir: str) -> bool:
    """生成StarDict文件"""
    cmd = f"python3 stardict_generator.py --db {db_path} --output {output_dir}"
    return run_command(cmd, "生成StarDict格式文件")


def create_query_tool(output_dir: str):
    """创建查询工具"""
    print("\n🔧 创建查询工具...")
    
    # 创建简单的查询脚本
    query_script = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查询工具 - 汉语拼音辞典
"""

import sqlite3
import sys
from pathlib import Path

def query_character(db_path, query):
    """查询汉字"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    if len(query) == 1:
        cursor.execute('SELECT char, pinyin, strokes, radicals, frequency FROM characters WHERE char = ?', (query,))
    else:
        cursor.execute('SELECT char, pinyin, strokes, radicals, frequency FROM characters WHERE pinyin LIKE ?', (f'%{query}%',))
    
    results = cursor.fetchall()
    conn.close()
    
    if results:
        print(f"找到 {len(results)} 个汉字:")
        for char_data in results:
            char, pinyin, strokes, radicals, frequency = char_data
            print(f"汉字: {char}, 拼音: {pinyin}, 笔画: {strokes}, 部首: {radicals}")
    else:
        print(f"未找到匹配的汉字: {query}")

def query_word(db_path, query):
    """查询词语"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('SELECT word, pinyin, explanation FROM words WHERE word LIKE ? OR pinyin LIKE ?', 
                   (f'%{query}%', f'%{query}%'))
    
    results = cursor.fetchall()
    conn.close()
    
    if results:
        print(f"找到 {len(results)} 个词语:")
        for word_data in results:
            word, pinyin, explanation = word_data
            print(f"词语: {word}, 拼音: {pinyin}")
            if explanation:
                print(f"解释: {explanation[:100]}...")
    else:
        print(f"未找到匹配的词语: {query}")

def main():
    if len(sys.argv) < 3:
        print("使用方法: python query_tool.py <数据库路径> <查询类型> <查询内容>")
        print("查询类型: char <汉字> 或 word <词语>")
        return
    
    db_path = sys.argv[1]
    query_type = sys.argv[2]
    query_content = sys.argv[3] if len(sys.argv) > 3 else ""
    
    if not Path(db_path).exists():
        print(f"数据库文件不存在: {db_path}")
        return
    
    if query_type == 'char':
        query_character(db_path, query_content)
    elif query_type == 'word':
        query_word(db_path, query_content)
    else:
        print(f"不支持的查询类型: {query_type}")

if __name__ == '__main__':
    main()
'''
    
    query_tool_path = Path(output_dir) / "query_tool.py"
    with open(query_tool_path, 'w', encoding='utf-8') as f:
        f.write(query_script)
    
    # 设置执行权限
    os.chmod(query_tool_path, 0o755)
    
    print(f"✅ 查询工具创建完成: {query_tool_path}")


def create_readme(output_dir: str, stats: dict):
    """创建README文件"""
    print("\n📝 创建README文件...")
    
    readme_content = f"""# 汉语拼音辞典 - 构建完成

## 📊 构建统计

- **汉字总数**: {stats.get('total_chars', 0)}
- **词语总数**: {stats.get('total_words', 0)}
- **构建时间**: {time.strftime('%Y-%m-%d %H:%M:%S')}

## 📁 文件结构

```
{output_dir}/
├── chinese_dictionary.db          # SQLite数据库文件
├── chinese-characters.ifo         # 汉字StarDict信息文件
├── chinese-characters.idx         # 汉字StarDict索引文件
├── chinese-characters.dict        # 汉字StarDict数据文件
├── chinese-words.ifo              # 词语StarDict信息文件
├── chinese-words.idx              # 词语StarDict索引文件
├── chinese-words.dict             # 词语StarDict数据文件
├── chinese-dictionary.ifo         # 完整版StarDict信息文件
├── chinese-dictionary.idx         # 完整版StarDict索引文件
├── chinese-dictionary.dict        # 完整版StarDict数据文件
├── query_tool.py                  # 查询工具
├── statistics.txt                 # 详细统计信息
├── dict_builder.log               # 构建日志
└── stardict_generator.log         # StarDict生成日志
```

## 🚀 使用方法

### 1. 查询工具

```bash
# 查询汉字
python query_tool.py chinese_dictionary.db char 一

# 查询词语
python query_tool.py chinese_dictionary.db word 一帆风顺
```

### 2. StarDict格式

生成的StarDict文件可以在支持StarDict的应用程序中使用，如：
- GoldenDict
- StarDict
- 各种移动端词典应用

### 3. 数据库查询

```bash
# 使用SQLite命令行工具
sqlite3 chinese_dictionary.db

# 查看表结构
.schema

# 查询示例
SELECT * FROM characters WHERE char = '一';
SELECT * FROM words WHERE word LIKE '%一帆风顺%';
```

## 🔧 技术特点

- **分层构建**: 按频率和类型分层处理，提高构建效率
- **数据完整性**: 支持汉字、词语、成语等多种数据类型
- **格式兼容**: 支持SQLite和StarDict两种格式
- **查询优化**: 建立多种索引，支持快速查询
- **错误处理**: 完善的错误处理和日志记录

## 📈 性能指标

- **构建速度**: 支持大数据量快速构建
- **存储效率**: 优化的数据库结构和索引
- **查询性能**: 毫秒级查询响应
- **内存使用**: 优化的内存管理，支持大文件处理

## 🆘 故障排除

如果遇到问题，请检查：
1. 日志文件中的错误信息
2. 数据库文件是否完整
3. 输入数据格式是否正确
4. 系统资源是否充足

## 📞 支持

如有问题或建议，请查看日志文件或联系开发团队。
"""
    
    readme_path = Path(output_dir) / "README.md"
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"✅ README文件创建完成: {readme_path}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='完整的汉语拼音辞典构建脚本',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python build_complete_dictionary.py --data-dir chinese-dictionary-main --output output
  
参数说明:
  --data-dir: 数据源目录路径（包含character、word、idiom子目录）
  --output: 输出目录路径
  --skip-db: 跳过数据库构建（如果数据库已存在）
  --skip-stardict: 跳过StarDict生成（如果只需要数据库）
        """
    )
    
    parser.add_argument('--data-dir', required=True, help='数据源目录路径')
    parser.add_argument('--output', required=True, help='输出目录路径')
    parser.add_argument('--skip-db', action='store_true', help='跳过数据库构建')
    parser.add_argument('--skip-stardict', action='store_true', help='跳过StarDict生成')
    
    args = parser.parse_args()
    
    print("🏗️  汉语拼音辞典完整构建脚本")
    print("=" * 50)
    print(f"开始时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"数据源目录: {args.data_dir}")
    print(f"输出目录: {args.output}")
    print("=" * 50)
    
    # 检查依赖项
    print("\n🔍 检查依赖项...")
    if not check_dependencies():
        print("❌ 依赖项检查失败，退出构建")
        sys.exit(1)
    
    # 检查数据源目录
    print(f"\n🔍 检查数据源目录: {args.data_dir}")
    data_dir = Path(args.data_dir)
    if not data_dir.exists():
        print(f"❌ 数据源目录不存在: {args.data_dir}")
        sys.exit(1)
    
    # 检查必要的数据文件
    required_files = [
        "character/char_base.json",
        "character/char_detail.json",
        "word/word.json",
        "idiom/idiom.json"
    ]
    
    for file_path in required_files:
        full_path = data_dir / file_path
        if not full_path.exists():
            print(f"❌ 缺少必要的数据文件: {file_path}")
            sys.exit(1)
        else:
            size = full_path.stat().st_size
            print(f"  ✅ {file_path} ({size:,} 字节)")
    
    # 确保输出目录存在
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"\n📁 输出目录: {output_dir}")
    
    start_time = time.time()
    
    try:
        # 第一步：构建数据库
        if not args.skip_db:
            print(f"\n🚀 开始第一步：构建SQLite数据库")
            if not build_database(args.data_dir, args.output):
                print("❌ 数据库构建失败，退出构建")
                sys.exit(1)
            print(f"✅ 第一步完成：数据库构建成功")
        else:
            print("⏭️  跳过数据库构建")
        
        # 第二步：生成StarDict文件
        if not args.skip_stardict:
            print(f"\n🚀 开始第二步：生成StarDict格式文件")
            db_path = output_dir / "chinese_dictionary.db"
            if not db_path.exists():
                print("❌ 数据库文件不存在，无法生成StarDict文件")
                sys.exit(1)
            
            if not generate_stardict(str(db_path), args.output):
                print("❌ StarDict文件生成失败，退出构建")
                sys.exit(1)
            print(f"✅ 第二步完成：StarDict文件生成成功")
        else:
            print("⏭️  跳过StarDict生成")
        
        # 第三步：创建查询工具
        print(f"\n🚀 开始第三步：创建查询工具")
        create_query_tool(args.output)
        print(f"✅ 第三步完成：查询工具创建成功")
        
        # 第四步：创建README文件
        print(f"\n🚀 开始第四步：创建文档")
        stats = {'total_chars': '待统计', 'total_words': '待统计'}
        create_readme(args.output, stats)
        print(f"✅ 第四步完成：文档创建成功")
        
        # 计算构建时间
        build_time = time.time() - start_time
        
        print(f"\n🎉 汉语拼音辞典构建完成！")
        print("=" * 50)
        print(f"⏱️  总构建时间: {build_time:.2f} 秒")
        print(f"📁 输出目录: {args.output}")
        print(f"🔍 使用查询工具: python3 {args.output}/query_tool.py")
        print(f"📊 查看统计信息: {args.output}/statistics.txt")
        print(f"📝 查看构建日志: {args.output}/dict_builder.log")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ 构建过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
