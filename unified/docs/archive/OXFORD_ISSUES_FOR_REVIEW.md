# Oxford解析器问题案例 - 待Review

> 生成时间: 2026-01-08  
> 总样例数: 174

---

## 📊 问题统计概览

| 问题类型 | 数量 | 占比 | 说明 |
|---------|------|------|------|
| **无音标** | 24 | 13.8% | 这些词条可能格式特殊或需要特殊处理 |
| **可能漏解析** | 7 | 4.0% | 长条目但只有1个释义，可能包含多个义项 |
| **无例句（长条目）** | 7 | 4.0% | 长条目但没有提取到例句 |
| **超短条目** | 8 | 4.6% | <50字符，可能是交叉引用 |
| **超长条目** | 24 | 13.8% | >8000字符，可能是多词条合并 |

**无释义**: 0 ✅  
**质量分 < 0.8**: 0 ✅

---

## 1️⃣ 无音标案例 (24个)

这些词条的原始数据格式可能不符合标准格式（无 `/音标/` 开头）：

1. **`is`** - 长度117
   - 内容: `abbr 缩写 = Island(s); Isle(s): ...`
   - 特点: 是缩写词，直接是 `abbr` 开头

2. **`has`, `had`, `does`, `did`, `went`** - 动词变形
   - 内容: `=> have.` 或 `pt of go1.`
   - 特点: 交叉引用或词形说明，指向主词条

3. **`database`, `ashtray`, `steerage-way`, `hay fever`, `soft-hearted`** 等
   - 特点: 短语词或多词词条，可能格式不同

4. **`balance sheet`, `blow-dry`, `public transport`, `junk food`, `pack-ice`** 等
   - 特点: 复合词或短语

**需要检查**: 这些格式是否正常？是否需要特殊处理？

---

## 2️⃣ 可能漏解析的案例 (7个)

这些是长条目但只解析出1个释义，可能包含多个义项：

1. **`give up`** - 长度1231, 释义数1
2. **`go on`** - 长度3063, 释义数1  
3. **`come up`** - 长度2044, 释义数1
4. **`important`** - 长度742, 释义数1
5. **`making`** - 长度561, 释义数1
6. **`management`** - 长度659, 释义数1
7. **`eternal`** - 长度563, 释义数1

**需要检查**: 这些长条目是否真的只有一个释义？还是解析器漏掉了其他义项？

---

## 3️⃣ 无例句的长条目 (7个)

这些条目长度 >300字符，但解析出的例句数为0：

- 可能是定义格式特殊，例句标记不是 `*` 开头
- 或者例句被包含在定义文本中

---

## 📋 详细数据位置

完整的问题案例数据已保存在：

1. **详细报告**: `comprehensive_samples/oxford_issues_report.md`
   - 包含每个问题case的原始数据和解析结果
   - 便于逐个review

2. **JSON数据**: `comprehensive_samples/oxford_issues_data.json`
   - 包含所有case的完整结构化数据
   - 包含解析后的JSON格式数据

3. **原始样例**: `comprehensive_samples/oxford_comprehensive.json`
   - 包含所有174个样例的原始数据

---

## 🔍 建议Review重点

1. **无音标的24个case** - 检查这些格式是否正常，是否需要特殊处理
2. **可能漏解析的7个case** - 重点检查 `give up`, `go on`, `come up` 这三个超长条目
3. **查看详细报告** - `oxford_issues_report.md` 中包含每个case的完整原始数据

---

## 📝 如何查看详细数据

```bash
# 查看详细报告
cat comprehensive_samples/oxford_issues_report.md

# 查看JSON数据（格式化）
python3 -m json.tool comprehensive_samples/oxford_issues_data.json | less

# 查看特定词的原始数据
python3 -c "
import json
with open('comprehensive_samples/oxford_comprehensive.json') as f:
    data = json.load(f)
word = 'give up'
sample = next((s for s in data['samples'] if s['word'] == word), None)
if sample:
    print(sample['raw_content'])
"
```

