-- 授予数据库用户权限
-- 使用方法：
--   psql -U postgres -d fishenglish_dict -f grant_permissions.sql
--   或者交互式执行：
--   \i grant_permissions.sql

-- 注意：请将 'fishenglish' 替换为你的实际用户名

-- 授予用户对表的 SELECT, INSERT, UPDATE, DELETE 权限
GRANT SELECT, INSERT, UPDATE, DELETE ON dictionary_entries TO fishenglish;
GRANT SELECT, INSERT, UPDATE, DELETE ON dictionary_index TO fishenglish;
GRANT SELECT, INSERT, UPDATE, DELETE ON dictionary_stats TO fishenglish;

-- 授予用户对序列的 USAGE 权限（用于主键自增）
GRANT USAGE, SELECT ON SEQUENCE dictionary_entries_id_seq TO fishenglish;
GRANT USAGE, SELECT ON SEQUENCE dictionary_index_id_seq TO fishenglish;
GRANT USAGE, SELECT ON SEQUENCE dictionary_stats_id_seq TO fishenglish;

-- 授予用户对表的权限（用于未来的表）
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO fishenglish;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO fishenglish;

-- 显示当前权限（验证）
SELECT 
    grantee, 
    table_name, 
    privilege_type 
FROM information_schema.table_privileges 
WHERE table_schema = 'public' 
  AND grantee = 'fishenglish'
ORDER BY table_name, privilege_type;

