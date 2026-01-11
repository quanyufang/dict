# 词典解析系统 - 项目待办列表

> **更新日期**: 2026-01-XX
> **当前阶段**: 解析器开发 + 网站开发

---

## 📋 项目概述

本项目旨在将多种格式的词典数据解析成统一JSON结构，并开发Web查询界面，支持词典数据的查询和浏览。

---

## ✅ 已完成

### 解析器开发
- ✅ **Oxford解析器** (oxford.py) - 基本完成，待批量检查效果
  - 支持多词性分离
  - 支持子义项结构（1a, 1b等）
  - 分类标题正确处理
  - 音标解析、例句提取等功能
  - ⚠️ 已知问题：音标解析、助动词识别等需要后续批量检查时修复

- ✅ **Langdao解析器** (langdao.py) - 已完成

- ✅ **Chinese Dict解析器** (chinese_dict.py) - 已完成

---

## 🚧 进行中

### 解析器开发
- ✅ **现代汉语词典解析器** (xiandaihanyucidian.py) - 基本完成
  - 优先级：高（词典ID: xiandaihanyucidian）
  - 格式特点：
    - 拼音标注：`yī`、`rén`
    - 部首笔画：`BS 一 | BH 0`
    - 序号标记：`①`、`②`、`③`
    - 词性标记：`〈名〉`、`〈动〉`
    - 多读音支持

- ⏳ **GCIDE解析器** (gcide.py) - 待开发
  - 优先级：中（词典ID: gcide）
  - 格式特点：
    - 词头标记：`\Word\`
    - 词性标记：`n.`、`v. i.`、`v. t.`
    - 词源信息：`[1913 Webster]`
    - 例句来源：`--Shak.`
    - 交叉引用：`{word}`

---

## 📝 待办任务

### 阶段一：完成剩余解析器

#### 1. 实现现代汉语词典解析器
- [ ] 分析格式样例，设计解析逻辑
- [ ] 实现拼音解析（带声调）
- [ ] 实现部首和笔画提取（`BS`、`BH`）
- [ ] 实现序号解析（`①②③`）
- [ ] 实现词性解析（`〈名〉`、`〈动〉`等）
- [ ] 实现多读音支持（如"一"有yī、yí、yì）
- [ ] 实现交叉引用解析（`见'一'（yī）`）
- [ ] 创建测试用例
- [ ] 编写文档

#### 2. 实现GCIDE解析器
- [ ] 分析格式样例，设计解析逻辑
- [ ] 实现词头提取（`\Word\`）
- [ ] 实现词性解析（`n.`、`v. i.`、`v. t.`等）
- [ ] 实现词源信息提取（`[1913 Webster]`）
- [ ] 实现例句来源标记（`--Shak.`等）
- [ ] 实现交叉引用解析（`{word}`）
- [ ] 创建测试用例
- [ ] 编写文档

---

### 阶段二：数据库设计

#### 3. 设计PostgreSQL数据库表结构
- [ ] 设计词典条目主表（dictionary_entries）
  - 字段：headword, source_id, entry_id, pronunciations (JSONB), senses (JSONB), etc.
- [ ] 设计索引表（dictionary_index）
  - 支持快速key查询
  - 支持遍历查询（按字母顺序）
- [ ] 设计辅助表（可选）
  - 词频表、标签表等
- [ ] 创建数据库迁移脚本
- [ ] 编写表结构文档

---

### 阶段三：数据导入工具

#### 4. 实现数据导入工具
- [ ] 设计导入脚本（import_to_postgresql.py）
- [ ] 实现批量解析词典数据
- [ ] 实现数据转换（统一格式 → PostgreSQL）
- [ ] 实现批量插入（使用批量插入优化性能）
- [ ] 实现进度显示和错误处理
- [ ] 创建导入配置文件
- [ ] 测试导入功能

---

### 阶段四：网站后端开发

#### 5. 开发查询API后端
**技术栈**: Python FastAPI（已完成）

- ✅ 创建FastAPI服务（`api/`模块）
- ✅ 实现key查询API
  - ✅ `GET /api/dict/query?key={word}&sources={source1,source2}&fuzzy={true/false}&limit={number}`
  - ✅ 支持模糊查询、精确查询
- ✅ 实现遍历查询API
  - ✅ `GET /api/dict/next?key={word}&source={source_id}`
  - ✅ `GET /api/dict/prev?key={word}&source={source_id}`
  - ✅ 返回相邻的key（按字母顺序）
- ✅ 实现多词典查询
  - ✅ 支持同时查询多个词典
  - ✅ 返回结果合并和排序
- ⏳ 实现缓存机制（Redis）（可选，后续优化）
- ✅ 添加API文档（FastAPI自动生成Swagger UI）
- ⏳ 单元测试（待测试）

---

### 阶段五：网站前端开发

#### 6. 开发查询页面
**技术栈**: 建议使用 React 或 Vue.js

- [ ] 设计页面布局
  - 查询输入框
  - 词典选择（多选）
  - 结果显示区域
- [ ] 实现key查询功能
  - 搜索框输入
  - 实时搜索建议
  - 结果展示（释义、例句等）
- [ ] 实现遍历功能
  - "上一个"按钮
  - "下一个"按钮
  - 键盘快捷键支持（← →）
- [ ] 实现结果渲染
  - 词头、音标显示
  - 释义列表展示
  - 例句展示
  - 相关短语展示
- [ ] 响应式设计
- [ ] 性能优化（虚拟滚动等）

---

### 阶段六：测试和优化

#### 7. 测试和优化
- [ ] 功能测试
  - 所有解析器测试
  - API测试
  - 前端功能测试
- [ ] 性能测试
  - 查询性能
  - 大数据量测试
- [ ] 批量检查Oxford解析器效果
  - 导入所有Oxford词条
  - 检查解析质量
  - 修复发现的问题
- [ ] 优化
  - 数据库索引优化
  - 查询优化
  - 前端性能优化

---

## 📊 优先级排序

1. **P0 (最高优先级)**
   - 实现现代汉语词典解析器
   - 实现GCIDE解析器

2. **P1 (高优先级)**
   - 设计PostgreSQL数据库表结构
   - 实现数据导入工具

3. **P2 (中优先级)**
   - 开发查询API后端
   - 开发查询页面前端

4. **P3 (低优先级)**
   - 测试和优化
   - 批量检查Oxford解析器

---

## 📁 文件结构

```
Daemon/dict/src/unified/
├── parsers/
│   ├── oxford.py          ✅ 已完成
│   ├── langdao.py         ✅ 已完成
│   ├── xiandaihanyucidian.py  ⏳ 待开发
│   └── gcide.py           ⏳ 待开发
├── scripts/
│   └── import_to_postgresql.py  ⏳ 待开发
└── ...

unified/api/              ✅ FastAPI服务
├── main.py               ✅ FastAPI主应用
├── config.py             ✅ 配置管理
├── database.py           ✅ 数据库连接
├── models.py             ✅ Pydantic模型
├── service.py            ✅ 业务逻辑
└── requirements.txt      ✅ 依赖列表

feweb/                     ⏳ 新建或更新
├── dict-query/           # 词典查询页面
└── ...
```

---

## 🔗 相关文档

- [项目总体规划](../Docs/PROJECT_OVERVIEW_AND_PLANNING.md)
- [词典架构讨论](../Docs/DICTIONARY_ARCHITECTURE_DISCUSSION.md)
- [统一数据模型](models/entry.py)
- [Oxford解析器文档](docs/OXFORD_PARSER.md)

---

## 📝 备注

- Oxford解析器虽然已基本完成，但仍有一些已知问题，等待网站开发完成后批量检查效果再统一修复
- 数据库选择PostgreSQL是因为其JSONB支持，便于存储灵活的词典数据结构
- 网站功能需要支持key查询和遍历查询两种模式，便于用户浏览词典

