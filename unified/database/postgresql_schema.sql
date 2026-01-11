-- 词典数据PostgreSQL数据库表结构
-- 设计说明：
-- 1. 使用JSONB存储灵活的词典数据结构
-- 2. 使用索引支持快速key查询和遍历查询
-- 3. 支持多词典、多语言

-- ========================================
-- 词典条目主表
-- ========================================
CREATE TABLE dictionary_entries (
    id BIGSERIAL PRIMARY KEY,
    headword VARCHAR(255) NOT NULL,              -- 词头
    source_id VARCHAR(50) NOT NULL,              -- 词典来源ID (oxford/gcide/langdao/xiandai/chinese_dict)
    entry_id VARCHAR(255),                       -- 条目唯一ID（可选）
    
    -- JSONB字段存储灵活的数据结构
    pronunciations JSONB,                        -- 发音信息数组
    senses JSONB NOT NULL,                       -- 释义数组（必须）
    forms JSONB,                                 -- 词形变化（英文词典用）
    related_phrases JSONB,                       -- 相关短语/词组
    
    -- 中文词典特有字段
    pinyin VARCHAR(100),                         -- 拼音（带声调）
    pinyin_abbr VARCHAR(50),                     -- 拼音缩写
    strokes INTEGER,                             -- 笔画数
    radical VARCHAR(50),                         -- 部首
    
    -- 词源/典故（GCIDE/成语）
    etymology TEXT,                              -- 词源
    story TEXT,                                  -- 典故
    source_book VARCHAR(255),                    -- 出处书籍
    
    -- 元信息
    frequency INTEGER,                           -- 词频等级 1-10
    level VARCHAR(20),                           -- 难度级别: basic/intermediate/advanced
    tags JSONB,                                  -- 标签数组
    
    -- 元数据
    raw_content TEXT,                            -- 原始内容（用于调试）
    parse_quality DECIMAL(3,2) DEFAULT 1.0,      -- 解析质量分 0-1
    parse_notes JSONB,                           -- 解析备注
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 唯一约束：同一词典内词头唯一
    CONSTRAINT uk_entry_headword_source UNIQUE (headword, source_id)
);

-- 索引：支持key查询和排序
CREATE INDEX idx_entries_headword ON dictionary_entries(headword);
CREATE INDEX idx_entries_source ON dictionary_entries(source_id);
CREATE INDEX idx_entries_headword_source ON dictionary_entries(headword, source_id);

-- 索引：支持中文拼音查询
CREATE INDEX idx_entries_pinyin ON dictionary_entries(pinyin);
CREATE INDEX idx_entries_pinyin_abbr ON dictionary_entries(pinyin_abbr);

-- 索引：支持JSONB查询（如果需要）
CREATE INDEX idx_entries_senses ON dictionary_entries USING GIN(senses);
CREATE INDEX idx_entries_tags ON dictionary_entries USING GIN(tags);

-- 索引：支持遍历查询（按词头排序）
CREATE INDEX idx_entries_source_headword ON dictionary_entries(source_id, headword);

-- ========================================
-- 词典索引表（用于快速遍历查询）
-- ========================================
-- 这个表用于支持"上一个/下一个"遍历功能
-- 存储词典内词头的排序顺序
CREATE TABLE dictionary_index (
    id BIGSERIAL PRIMARY KEY,
    source_id VARCHAR(50) NOT NULL,              -- 词典来源ID
    headword VARCHAR(255) NOT NULL,              -- 词头
    sort_key VARCHAR(255) NOT NULL,              -- 排序键（用于排序，可能包含大小写、拼音等）
    entry_id BIGINT NOT NULL,                    -- 关联到dictionary_entries.id
    
    -- 元数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 外键约束
    CONSTRAINT fk_index_entry FOREIGN KEY (entry_id) 
        REFERENCES dictionary_entries(id) ON DELETE CASCADE,
    
    -- 唯一约束
    CONSTRAINT uk_index_source_headword UNIQUE (source_id, headword)
);

-- 索引：支持快速遍历查询（按source_id和sort_key排序）
CREATE INDEX idx_index_source_sort ON dictionary_index(source_id, sort_key);
CREATE INDEX idx_index_entry ON dictionary_index(entry_id);

-- ========================================
-- 词典统计表（可选）
-- ========================================
CREATE TABLE dictionary_stats (
    source_id VARCHAR(50) PRIMARY KEY,           -- 词典来源ID
    total_entries BIGINT DEFAULT 0,              -- 总条目数
    total_senses BIGINT DEFAULT 0,               -- 总释义数
    total_examples BIGINT DEFAULT 0,             -- 总例句数
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 统计信息JSONB（可存储更多统计信息）
    statistics JSONB
);

-- ========================================
-- 触发器：自动更新updated_at
-- ========================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_dictionary_entries_updated_at 
    BEFORE UPDATE ON dictionary_entries
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ========================================
-- 视图：词典条目视图（便于查询）
-- ========================================
CREATE VIEW v_dictionary_entries AS
SELECT 
    e.*,
    i.sort_key,
    (SELECT COUNT(*) FROM dictionary_index WHERE entry_id = e.id) as index_count
FROM dictionary_entries e
LEFT JOIN dictionary_index i ON e.id = i.entry_id AND e.headword = i.headword;

-- ========================================
-- 查询示例
-- ========================================

-- 1. Key查询（精确查询）
-- SELECT * FROM dictionary_entries 
-- WHERE headword = 'have' AND source_id = 'oxford';

-- 2. Key查询（模糊查询）
-- SELECT * FROM dictionary_entries 
-- WHERE headword LIKE 'have%' AND source_id = 'oxford'
-- ORDER BY headword LIMIT 20;

-- 3. 遍历查询（下一个）
-- SELECT e.* FROM dictionary_entries e
-- JOIN dictionary_index i ON e.id = i.entry_id
-- WHERE i.source_id = 'oxford' 
--   AND i.sort_key > (SELECT sort_key FROM dictionary_index WHERE headword = 'have' AND source_id = 'oxford')
-- ORDER BY i.sort_key
-- LIMIT 1;

-- 4. 遍历查询（上一个）
-- SELECT e.* FROM dictionary_entries e
-- JOIN dictionary_index i ON e.id = i.entry_id
-- WHERE i.source_id = 'oxford' 
--   AND i.sort_key < (SELECT sort_key FROM dictionary_index WHERE headword = 'have' AND source_id = 'oxford')
-- ORDER BY i.sort_key DESC
-- LIMIT 1;

-- 5. 多词典查询
-- SELECT * FROM dictionary_entries 
-- WHERE headword = 'have' 
--   AND source_id IN ('oxford', 'gcide', 'langdao')
-- ORDER BY source_id;

