import sys
import struct
import sqlite3
from os import stat


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print('Usage:')
        print('\tpython ', sys.argv[0], ' dictFilename indexFilename sqliteDbName')
        exit(-1)
    dictFilename = sys.argv[1]
    idxFilename  = sys.argv[2]
    sqliteDbName = sys.argv[3]

    print(f"开始处理索引文件: {idxFilename}")
    print(f"目标数据库: {sqliteDbName}")

    try:
        db     = sqlite3.connect(sqliteDbName)
        cursor = db.cursor()
        cursor.execute('create table wordIndex(`id` integer primary key, `word` varchar(128), `offset` integer, `length` integer)');
        print("数据库表创建成功")

        statResult = stat(idxFilename)
        idxFilesize = statResult[6]
        print(f"索引文件大小: {idxFilesize} 字节")
        
        with open(idxFilename, 'rb') as f:
            word_count = 0
            processed_bytes = 0
            
            while f.tell() < idxFilesize:
                current_pos = f.tell()
                if word_count % 1000 == 0:  # 每1000个单词打印一次进度
                    progress = (current_pos / idxFilesize) * 100
                    print(f"进度: {progress:.2f}% ({current_pos}/{idxFilesize}), 已处理单词数: {word_count}")
                
                # 读取单词字符串，直到遇到null终止符
                word_bytes = b''
                while True:
                    byte = f.read(1)
                    if not byte:  # 文件结束
                        print("到达文件末尾")
                        break
                    if byte == b'\0':  # 遇到null终止符
                        break
                    word_bytes += byte
                
                # 检查是否到达文件末尾
                if not word_bytes:
                    print("没有更多单词数据，退出循环")
                    break
                
                # 将字节转换为UTF-8字符串
                try:
                    key = word_bytes.decode('utf-8').lower()
                except UnicodeDecodeError:
                    print(f"Warning: 无法解码单词: {word_bytes}")
                    continue
                
                # 读取偏移量和长度（4字节，大端序）
                offset_bytes = f.read(4)
                length_bytes = f.read(4)
                
                if len(offset_bytes) < 4 or len(length_bytes) < 4:
                    print(f"文件数据不足，退出循环。offset_bytes长度: {len(offset_bytes)}, length_bytes长度: {len(length_bytes)}")
                    break  # 文件结束
                
                offset = struct.unpack('>I', offset_bytes)[0]  # 使用无符号整数
                length = struct.unpack('>I', length_bytes)[0]  # 使用无符号整数
                
                #if word_count < 10:  # 只打印前10个单词的详细信息
                #print(f'处理单词: key={key}, offset={offset}, length={length}')

                sql = 'INSERT INTO wordIndex(word, offset, length) VALUES (?, ?, ?)'
                param = (key, offset, length)
                try:
                    cursor.execute(sql, param)
                    db.commit()
                    word_count += 1
                except sqlite3.IntegrityError as msg:
                    print(f"\n=== 发现重复单词: {key} ===")
                    
                    # 获取已存在的单词信息
                    cursor.execute('SELECT offset, length FROM wordIndex WHERE word = ?', (key,))
                    existing_data = cursor.fetchone()
                    if existing_data:
                        existing_offset, existing_length = existing_data
                        print(f"已存在的单词 - offset: {existing_offset}, length: {existing_length}")
                        
                        # 读取已存在单词的词义
                        try:
                            with open(dictFilename, 'rb') as dict_file:
                                dict_file.seek(existing_offset)
                                existing_definition = dict_file.read(existing_length).decode('utf-8', errors='ignore')
                                print(f"已存在的词义: {existing_definition[:200]}{'...' if len(existing_definition) > 200 else ''}")
                        except Exception as e:
                            print(f"读取已存在词义失败: {e}")
                    
                    print(f"当前单词 - offset: {offset}, length: {length}")
                    
                    # 读取当前单词的词义
                    try:
                        with open(dictFilename, 'rb') as dict_file:
                            dict_file.seek(offset)
                            current_definition = dict_file.read(length).decode('utf-8', errors='ignore')
                            print(f"当前的词义: {current_definition[:200]}{'...' if len(current_definition) > 200 else ''}")
                    except Exception as e:
                        print(f"读取当前词义失败: {e}")
                    
                    print("=" * 50)

        cursor.close()
        db.close()
        print(f"索引创建完成！总共处理了 {word_count} 个单词")
            
    except sqlite3.OperationalError as msg:
        print(f"数据库操作错误: {msg}")
    except Exception as e:
        print(f"发生未知错误: {e}")
        import traceback
        traceback.print_exc()
