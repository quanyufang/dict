# 词典生成转换工具
## lookupDict.py
lookupDict.py 根据索引文件读取字典解释，并把数据输出到XML

## createDictSqliteDbIndex.py
createDictSqliteDbIndex.py 根据字典索引，创建使用sqlite3作为存储的索引
    createDictSqliteDbIndex.py xiandaihanyucidian.dict xiandaihanyucidian.idx xiandaihanyucidian.db

# 解压从网络上词典文件：
mv oxford-gb.dict.dz oxford-gb.dict.gz
gunzip oxford-gb.dict.gz

# 处理app需要的数据，主要注意把默认的dict文件后缀修改一下
7z a xiandaihanyucidian.dictcontent.7z xiandaihanyucidian.dictcontent
7z a chinese_dict.dictcontent.7z chinese_dict.dictcontent
7z a chinese_dict.db.7z chinese_dict.db