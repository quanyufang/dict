# PostgreSQL数据库设置指南

## 1. 安装PostgreSQL

如果还没有安装PostgreSQL，请先安装：

```bash
# macOS
brew install postgresql
brew services start postgresql

# Ubuntu
sudo apt-get install postgresql postgresql-contrib

# CentOS
sudo yum install postgresql postgresql-server
```

## 2. 创建数据库

```bash
# 连接到PostgreSQL
psql postgres

# 创建数据库
CREATE DATABASE fishenglish_dict;

# 创建用户（如果需要）
CREATE USER fishenglish WITH PASSWORD 'your_password_here';
GRANT ALL PRIVILEGES ON DATABASE fishenglish_dict TO fishenglish;

# 退出
\q
```

## 3. 导入表结构

```bash
# 连接到目标数据库
psql -d fishenglish_dict -U fishenglish

# 或者使用postgres用户
psql -d fishenglish_dict

# 导入表结构
\i postgresql_schema.sql
```

或者直接执行SQL文件：

```bash
psql -d fishenglish_dict -f postgresql_schema.sql
```

## 4. 验证表结构

```bash
# 连接到数据库
psql -d fishenglish_dict

# 查看所有表
\dt

# 查看表结构
\d dictionary_entries
\d dictionary_index

# 退出
\q
```

## 5. 配置Spring Boot数据源

更新 `application-dict.yml` 或 `application-dev.yml` 中的PostgreSQL配置：

```yaml
dict:
  datasource:
    url: jdbc:postgresql://localhost:5432/fishenglish_dict
    username: fishenglish
    password: your_password_here
    driver-class-name: org.postgresql.Driver
```

**注意**：如果使用多数据源，需要配置数据源Bean。当前实现假设PostgreSQL是主数据源或使用相同的配置。

## 6. 测试连接

```bash
# 使用psql测试连接
psql -h localhost -U fishenglish -d fishenglish_dict
```

## 7. 导入词典数据

使用数据导入工具导入词典数据：

```bash
cd /Users/fangyu/work/fishenglish/Daemon/dict/src
python3 -m unified.scripts.import_to_postgresql
```

## 常见问题

### 1. 连接被拒绝

检查PostgreSQL服务是否运行：

```bash
# macOS
brew services list | grep postgresql

# Linux
sudo systemctl status postgresql
```

### 2. 认证失败

检查 `pg_hba.conf` 文件，确保允许密码认证：

```bash
# 找到pg_hba.conf位置
psql -U postgres -c "SHOW hba_file"

# 编辑文件，添加：
host    all             all             127.0.0.1/32            md5
```

### 3. JSONB类型支持

确保PostgreSQL版本 >= 9.4（JSONB支持）：

```sql
SELECT version();
```

