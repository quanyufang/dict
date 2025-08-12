#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
convertDictToXml.py - StarDict格式字典文件解析器

根据索引文件读取字典解释，并将数据输出到XML格式。
支持错误处理、输入验证和安全的XML生成。

使用方法:
    python convertDictToXml.py <字典文件> <索引文件> <输出XML文件>

示例:
    python convertDictToXml.py xiandaihanyucidian.dictcontent xiandaihanyucidian.idx xiandaihanyucidian.xml
"""

import sys
import os
import logging
from array import array
import socket
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom
import argparse


class StarDictParser:
    """StarDict格式字典文件解析器"""
    
    def __init__(self, dict_filename, idx_filename, output_filename, debug=False):
        """
        初始化解析器
        
        Args:
            dict_filename (str): 字典内容文件路径
            idx_filename (str): 索引文件路径
            output_filename (str): 输出XML文件路径
            debug (bool): 是否启用调试模式
        """
        self.dict_filename = dict_filename
        self.idx_filename = idx_filename
        self.output_filename = output_filename
        self.debug = debug
        self.setup_logging()
        
    def setup_logging(self):
        """设置日志配置"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def validate_files(self):
        """验证输入文件是否存在且可读"""
        files_to_check = [
            (self.dict_filename, "字典文件"),
            (self.idx_filename, "索引文件")
        ]
        
        for filepath, description in files_to_check:
            if not os.path.exists(filepath):
                raise FileNotFoundError(f"{description}不存在: {filepath}")
            if not os.access(filepath, os.R_OK):
                raise PermissionError(f"无法读取{description}: {filepath}")
                
        # 检查输出目录是否可写
        output_dir = os.path.dirname(self.output_filename)
        if output_dir and not os.access(output_dir, os.W_OK):
            raise PermissionError(f"无法写入输出目录: {output_dir}")
            
    def escape_xml_text(self, text):
        """
        转义XML文本中的特殊字符
        
        Args:
            text (str): 需要转义的文本
            
        Returns:
            str: 转义后的文本
        """
        if isinstance(text, bytes):
            try:
                text = text.decode('utf-8', errors='replace')
            except UnicodeDecodeError:
                text = text.decode('latin-1', errors='replace')
                
        # XML特殊字符转义
        xml_escapes = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&apos;'
        }
        
        for char, escape in xml_escapes.items():
            text = text.replace(char, escape)
            
        return text
        
    def parse_index_file(self):
        """
        解析索引文件，提取键值对和偏移量信息
        
        Returns:
            list: 包含(键, 偏移量, 长度)元组的列表
        """
        self.logger.info(f"开始解析索引文件: {self.idx_filename}")
        
        entries = []
        try:
            with open(self.idx_filename, 'rb') as idx_file:
                idx_size = os.path.getsize(self.idx_filename)
                self.logger.info(f"索引文件大小: {idx_size} 字节")
                position = 0
                
                while position < idx_size:
                    # 读取键（以null结尾的字符串）
                    key_bytes = bytearray()
                    key_start_pos = idx_file.tell()
                    max_key_length = 1024  # 限制键的最大长度，防止无限循环
                    
                    while len(key_bytes) < max_key_length:
                        byte = idx_file.read(1)
                        if not byte:
                            self.logger.warning(f"文件意外结束，位置: {key_start_pos}")
                            break
                        if byte == b'\0':
                            break
                        key_bytes.extend(byte)
                        position += 1
                    
                    if not key_bytes:
                        if key_start_pos >= idx_size - 8:  # 接近文件末尾，正常结束
                            break
                        else:
                            self.logger.warning(f"跳过空的键条目，位置: {key_start_pos}")
                            continue
                    
                    if len(key_bytes) >= max_key_length:
                        self.logger.warning(f"键过长，跳过: {key_bytes[:50]}...")
                        continue
                        
                    # 读取偏移量和长度（每个4字节，网络字节序）
                    # 使用更安全的方式读取，避免32位整数溢出
                    try:
                        # 读取8字节数据（4字节偏移量 + 4字节长度）
                        data_bytes = idx_file.read(8)
                        if len(data_bytes) < 8:
                            self.logger.warning(f"索引文件格式错误，位置: {position}")
                            break
                        
                        # 手动解析偏移量和长度，避免32位整数限制
                        offset = int.from_bytes(data_bytes[0:4], byteorder='big', signed=False)
                        length = int.from_bytes(data_bytes[4:8], byteorder='big', signed=False)
                        
                        if self.debug:
                            self.logger.debug(f"解析条目: key='{key_bytes.decode('latin-1', errors='replace')}', offset={offset}, length={length}")
                        
                        # 验证偏移量和长度的合理性
                        if offset < 0 or length < 0:
                            self.logger.warning(f"无效的偏移量或长度: offset={offset}, length={length}")
                            continue
                            
                        # 检查是否超过文件大小限制（防止异常大的值）
                        if offset > 10 * 1024 * 1024 * 1024:  # 10GB
                            self.logger.warning(f"偏移量过大，跳过: offset={offset}")
                            continue
                        if length > 100 * 1024 * 1024:  # 100MB
                            self.logger.warning(f"长度过大，跳过: length={length}")
                            continue
                            
                    except Exception as e:
                        self.logger.warning(f"解析偏移量和长度时出错: {e}")
                        continue
                        
                    # 尝试解码键
                    try:
                        key = key_bytes.decode('utf-8')
                    except UnicodeDecodeError:
                        key = key_bytes.decode('latin-1', errors='replace')
                        
                    entries.append((key, offset, length))
                    position = idx_file.tell()
                    
        except Exception as e:
            self.logger.error(f"解析索引文件时出错: {e}")
            raise
            
        self.logger.info(f"索引文件解析完成，共找到 {len(entries)} 个条目")
        return entries
        
    def read_dict_content(self, offset, length):
        """
        从字典文件中读取指定位置和长度的内容
        
        Args:
            offset (int): 内容在文件中的偏移量
            length (int): 内容的长度
            
        Returns:
            str: 读取的内容
        """
        try:
            with open(self.dict_filename, 'rb') as dict_file:
                # 检查文件大小，确保偏移量不超出文件范围
                file_size = os.path.getsize(self.dict_filename)
                if offset >= file_size:
                    self.logger.warning(f"偏移量超出文件范围: offset={offset}, file_size={file_size}")
                    return f"[偏移量超出文件范围: {offset}]"
                
                # 确保不会读取超出文件末尾的数据
                actual_length = min(length, file_size - offset)
                if actual_length <= 0:
                    self.logger.warning(f"无效的读取长度: offset={offset}, length={length}, file_size={file_size}")
                    return f"[无效的读取长度: {length}]"
                
                dict_file.seek(offset)
                content_bytes = dict_file.read(actual_length)
                
                if len(content_bytes) != actual_length:
                    self.logger.warning(f"读取内容长度不匹配: 期望{actual_length}, 实际{len(content_bytes)}")
                    
                # 尝试解码内容
                try:
                    content = content_bytes.decode('utf-8')
                except UnicodeDecodeError:
                    content = content_bytes.decode('latin-1', errors='replace')
                    
                return content
                
        except Exception as e:
            self.logger.error(f"读取字典内容时出错: {e}")
            return f"[读取错误: {e}]"
            
    def generate_xml(self, entries):
        """
        生成XML格式的输出
        
        Args:
            entries (list): 包含(键, 偏移量, 长度)元组的列表
        """
        self.logger.info("开始生成XML文件")
        
        # 创建XML根元素
        root = Element('dictionary')
        root.set('version', '1.0')
        root.set('encoding', 'utf-8')
        
        # 添加字典信息
        info = SubElement(root, 'info')
        SubElement(info, 'dict_file').text = os.path.basename(self.dict_filename)
        SubElement(info, 'index_file').text = os.path.basename(self.idx_filename)
        SubElement(info, 'total_entries').text = str(len(entries))
        
        # 添加条目
        items = SubElement(root, 'items')
        
        for i, (key, offset, length) in enumerate(entries):
            if i % 1000 == 0:
                self.logger.info(f"处理进度: {i}/{len(entries)}")
                
            # 读取字典内容
            content = self.read_dict_content(offset, length)
            
            # 创建条目元素
            item = SubElement(items, 'item')
            
            key_elem = SubElement(item, 'key')
            key_elem.text = self.escape_xml_text(key)
            
            content_elem = SubElement(item, 'content')
            content_elem.text = self.escape_xml_text(content)
            
        # 格式化XML并写入文件
        xml_string = tostring(root, encoding='unicode')
        dom = minidom.parseString(xml_string)
        pretty_xml = dom.toprettyxml(indent='  ', encoding='utf-8')
        
        with open(self.output_filename, 'wb') as xml_file:
            xml_file.write(pretty_xml)
            
        self.logger.info(f"XML文件生成完成: {self.output_filename}")
        
    def process(self):
        """执行完整的解析和转换流程"""
        try:
            self.logger.info("开始处理字典文件")
            
            # 验证文件
            self.validate_files()
            
            # 解析索引文件
            entries = self.parse_index_file()
            
            if not entries:
                self.logger.warning("索引文件中没有找到有效条目")
                return
                
            # 生成XML
            self.generate_xml(entries)
            
            self.logger.info("处理完成")
            
        except Exception as e:
            self.logger.error(f"处理过程中出错: {e}")
            raise


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='StarDict格式字典文件解析器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python convertDictToXml.py xiandaihanyucidian.dictcontent xiandaihanyucidian.idx xiandaihanyudidian.xml
  
调试模式:
  python convertDictToXml.py --debug xiandaihanyucidian.dictcontent xiandaihanyucidian.idx xiandaihanyudidian.xml
        """
    )
    
    parser.add_argument('dict_file', help='字典内容文件路径')
    parser.add_argument('index_file', help='索引文件路径')
    parser.add_argument('output_file', help='输出XML文件路径')
    parser.add_argument('--debug', action='store_true', help='启用调试模式')
    
    args = parser.parse_args()
    
    try:
        # 创建解析器并执行
        parser = StarDictParser(args.dict_file, args.index_file, args.output_file, debug=args.debug)
        parser.process()
        print(f"转换完成！输出文件: {args.output_file}")
        
    except KeyboardInterrupt:
        print("\n用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
            

            
