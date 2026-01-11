# 解析器设计原则

> 更新时间: 2026-01-08

---

## 核心原则：不丢失内容

**原则**：尝试拆解，但不会消除内容。也就是说，如果没有拆解出来的内容，不会不见了，只是没有正确拆解。

**具体要求**：
1. 所有原始内容必须保留在`raw_content`字段中
2. 即使解析失败，也返回包含原始内容的sense，而不是返回None
3. 提取的内容（例句、语法说明等）不应从原始内容中移除，除非明确知道它们已经被正确提取
4. 清理定义文本时，只移除确认是格式标记的内容，对于无法确认的内容保留在定义中

### 具体要求

1. **所有原始内容必须保留**：即使无法正确解析，原始内容也应该保留在某个字段中（通常是`definition`字段）
2. **提取的内容不应从原始内容中移除**：提取的例句、语法说明等应该保留在原始内容中，除非明确知道它们已经被正确提取
3. **解析失败时保留原始内容**：如果解析失败，应该返回包含原始内容的sense，而不是返回None

---

## 当前代码检查

### ✅ 符合原则的地方

1. **语法说明提取**（第812-819行）
   - ✅ 语法说明提取到`grammar_note`字段
   - ✅ 从content中移除`[xxx]`标记，但这是合理的，因为标记已经提取
   - ⚠️ 注意：如果提取失败，标记会被移除但内容可能丢失

2. **例句提取**（第821-975行）
   - ✅ 例句提取到`examples`列表
   - ⚠️ 问题：例句从`definition_text`中移除（第980行），但如果提取错误，原始内容会丢失

3. **Sense创建**（第1013-1021行）
   - ✅ 如果`definition_text`为空但`examples`不为空，会创建sense（定义="(见例句)"）
   - ✅ 如果`definition_text`不为空，会创建sense
   - ⚠️ 问题：如果两者都为空，返回None，可能导致内容丢失

---

### ⚠️ 可能违反原则的地方

#### 1. 例句提取后从定义中移除（第977-980行）

```python
# 移除例句标记，得到纯释义文本
definition_text = content
for ex_text in example_texts:
    definition_text = definition_text.replace(ex_text, '', 1).strip()
```

**问题**：
- 如果例句提取错误（例如，提取了不应该提取的内容），原始内容会丢失
- 如果某些例句没有被提取到（例如，格式不匹配），这些例句会从定义中移除

**建议**：
- 只移除**确认已提取**的例句
- 对于无法确认的例句，保留在定义中

---

#### 2. 清理定义文本时可能移除内容（第985-1001行）

```python
# 1. 移除末尾的例句片段
definition_text = re.sub(r'\s+[A-Z][^.]*?\s+[\u4e00-\u9fff][^.]*?\.\s*$', '', definition_text)

# 2. 移除冒号后残留的内容
colon_pos = definition_text.rfind(': ')
if colon_pos > 0:
    after_colon = definition_text[colon_pos+2:].strip()
    if after_colon and re.match(r'^[A-Z]', after_colon):
        # 检查是否是缩写后的冒号
        before_short = definition_text[max(0, colon_pos-20):colon_pos].strip()
        if not re.search(r'\b(ie|eg|cf|viz)\s*$', before_short, re.I):
            # 不是缩写后的冒号，移除冒号后的内容
            definition_text = definition_text[:colon_pos].strip()
```

**问题**：
- 正则匹配可能错误，导致移除不应该移除的内容
- 冒号后的内容判断可能不准确，导致丢失内容

**建议**：
- 更保守的清理策略：只移除**确认是例句**的内容
- 对于无法确认的内容，保留在定义中

---

#### 3. 返回None可能导致内容丢失（第1013-1023行）

```python
if definition_text or examples:
    return Sense(
        definition=definition_text if definition_text else "(见例句)",
        ...
    )

return None
```

**问题**：
- 如果`definition_text`为空且`examples`为空，返回None
- 这可能导致无法解析的内容完全丢失

**建议**：
- 即使两者都为空，也应该返回包含原始`content`的sense
- 或者，在调用`_parse_single_sense`之前，确保content不为空

---

#### 4. 空内容检查可能导致跳过（第748-749行）

```python
if not content.strip():
    return None
```

**问题**：
- 如果content为空，返回None
- 但空内容可能是有效的（例如，只有例句的sense）

**建议**：
- 空内容检查应该更宽松，或者保留原始content

---

#### 5. 语法说明移除（第819行）

```python
content = re.sub(r'\[([^\]]+)\]', '', content)
```

**问题**：
- 如果语法说明提取失败，标记会被移除但内容可能丢失
- 嵌套的括号可能导致匹配错误

**建议**：
- 只移除**确认已提取**的语法说明标记
- 对于无法确认的标记，保留在content中

---

## 改进建议

### 优先级1：保守的清理策略

**问题**：当前代码在清理定义文本时可能移除不应该移除的内容

**方案**：
1. 只移除**确认已提取**的例句（通过精确匹配）
2. 对于无法确认的内容，保留在定义中
3. 添加日志记录，标记可能丢失的内容

---

### 优先级2：确保不返回None

**问题**：如果解析失败，返回None会导致内容丢失

**方案**：
1. 即使解析失败，也返回包含原始content的sense
2. 在sense中添加`raw_content`字段，保存原始内容
3. 添加`parsing_status`字段，标记解析状态

---

### 优先级3：改进例句提取

**问题**：例句提取后从定义中移除，如果提取错误会丢失内容

**方案**：
1. 只移除**确认已提取**的例句（通过精确匹配example_texts）
2. 对于无法确认的例句，保留在定义中
3. 添加验证机制，确保提取的例句确实存在于原始内容中

---

## 代码修改建议

### 1. 改进`_parse_single_sense`方法

```python
def _parse_single_sense(self, content: str, pos: Optional[str], sense_number: Optional[str]) -> Optional[Sense]:
    """解析单个释义（提取定义、例句、语法说明等）"""
    original_content = content  # 保存原始内容
    
    if not content.strip():
        # 即使为空，也返回包含原始内容的sense
        return Sense(
            definition=original_content,
            definition_lang="zh-en",
            pos=pos,
            sense_number=sense_number,
            examples=[],
            grammar_note=None
        )
    
    # ... 提取逻辑 ...
    
    # 改进：只移除确认已提取的例句
    definition_text = content
    for ex_text in example_texts:
        # 验证ex_text确实存在于content中
        if ex_text in definition_text:
            definition_text = definition_text.replace(ex_text, '', 1).strip()
        else:
            # 如果不存在，记录警告但不移除
            # 可能提取错误，保留原始内容
            pass
    
    # 改进：更保守的清理策略
    # 只移除确认是例句的内容，对于无法确认的内容保留
    
    # 确保至少保留原始内容
    if not definition_text:
        definition_text = original_content
    
    # 即使解析失败，也返回sense
    return Sense(
        definition=definition_text,
        definition_lang="zh-en",
        pos=pos,
        sense_number=sense_number,
        examples=examples,
        grammar_note=grammar_note
    )
```

---

### 2. 添加原始内容字段

在`Sense` dataclass中添加`raw_content`字段：

```python
@dataclass
class Sense:
    # ... 现有字段 ...
    raw_content: Optional[str] = None  # 原始内容，用于调试和恢复
    parsing_status: str = "success"  # 解析状态：success/partial/failed
```

---

### 3. 改进清理逻辑

```python
# 改进：更保守的清理策略
# 只移除确认是例句的内容

# 1. 移除确认已提取的例句
for ex_text in example_texts:
    if ex_text in definition_text:
        definition_text = definition_text.replace(ex_text, '', 1).strip()

# 2. 保守地清理定义文本
# 只移除明显的格式标记，不移除可能的内容

# 3. 如果清理后内容为空，使用原始内容
if not definition_text:
    definition_text = original_content
```

---

## 测试建议

1. **测试用例**：创建包含各种格式的测试用例，确保所有内容都被保留
2. **验证机制**：添加验证逻辑，确保提取的内容确实存在于原始内容中
3. **日志记录**：记录所有可能丢失内容的情况，便于调试

---

## 总结

当前代码在以下方面可能违反"不丢失内容"原则：

1. ⚠️ 例句提取后从定义中移除（可能移除错误）
2. ⚠️ 清理定义文本时可能移除内容（正则匹配可能错误）
3. ⚠️ 返回None可能导致内容丢失（解析失败时）
4. ⚠️ 语法说明移除（如果提取失败，标记会被移除）

**建议优先修复**：
1. 确保不返回None（即使解析失败，也返回包含原始内容的sense）
2. 改进例句提取逻辑（只移除确认已提取的例句）
3. 更保守的清理策略（只移除确认是格式标记的内容）

