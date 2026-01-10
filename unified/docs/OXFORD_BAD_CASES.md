# Oxford解析器Bad Case记录

> 记录解析器遇到的特殊case和修复方案  
> 最后更新: 2026-01-08

---

## 📋 原则

- ✅ **通用规则优先**：尽量通过规则改进解决问题，而不是针对单个单词的特殊处理
- ✅ **记录所有case**：遇到的所有bad case都要记录，便于后续统一测试
- ✅ **测试验证**：修复后统一测试所有记录的case，确保都解决

---

## 🔴 Bad Cases 列表

### Case 1: `important` - 词形变化误匹配

**问题描述**：
- 只解析出1个sense（#2），遗漏了第一个sense（#1）
- 原因：词形变化匹配逻辑错误，将释义中的`(to sb/sth)`误判为词形变化

**原始数据**：
```
/ɪmˈpɔːtnt; ɪm`pɔrtnt/ 
adj  
1 ~ (to sb/sth) very serious and significant; of great value or concern 重要的; 重大的; 非常有价值的: 
an important decision, announcement, meeting 重要的决定、宣布、会议 
* It is vitally important to cancel the order immediately. 最重要的是要立即取消这一定单. 
...
2 (of a person) having great influence or authority; influential （指人）有很大影响或权威的: ...
```

**预期结果**：
- 2个sense（#1, #2）
- 每个sense都有正确的定义和例句

**修复方案**：
- ✅ 改进词形变化匹配逻辑：仅在数字序号之前，且包含音标或常见词形变化格式时才匹配
- ✅ 添加验证：如果数字序号在括号之前，则不视为词形变化
- ✅ **通用规则**：适用于所有包含括号的释义

**修复状态**：✅ 已修复  
**测试状态**：✅ 已验证（平均释义数从8.2提升到8.4）

---

### Case 2: `gone` - 混合格式（交叉引用+完整定义）

**问题描述**：
- 只解析出1个sense（交叉引用），遗漏了后续的完整定义
- 原因：交叉引用检测后直接返回，没有继续解析后续内容

**原始数据**：
```
pp of go.
/gɒn; <i>US</i> gɔːn; ˇɔn/ 
adj  
1 [pred 作表语] past; departed 过去; 离去: 
Gone are the days when you could buy a three-course meal for under 1. 一顿饭吃三道菜不到1英镑, 这日子一去不复返了.  
2 (used after a phrase expressing time in weeks or months 用于表示星期或月的时间短语之後) having been pregnant for the specified period of time 已怀孕一段时间的: 
She's seven months gone. 她已有七个月的身孕.  
3 (idm 习语) be gone on sb (infml 口) be very much in love with sb; be infatuated with sb 与某人热恋; 迷恋某人: 
It's a pity Peter's so gone on Jane. 彼得如此迷恋简, 真遗憾. 
,going, ,going, `gone (said by an auctioneer to show that bidding must stop because an item has been sold 拍卖商用语, 表示某物售出而停止出价).
prep 
later than; past (in time) 晚于; （时间上）已过:
It's gone six o'clock already. 现在已过了六点钟.
```

**预期结果**：
- 1个交叉引用sense（`pp of go.`）
- 3个adj词性的sense（#1, #2, #3）
- 1个prep词性的sense
- 正确的音标解析（包含HTML标记）

**修复方案**：
- ✅ 新增`mixed_cross_ref`格式类型：检测交叉引用后是否还有完整定义
- ✅ 实现`_parse_without_cross_ref`方法：处理交叉引用后的内容
- ✅ 改进音标解析：处理HTML标记（`<i>US</i>`）
- ✅ 支持多词性解析：分别处理adj和prep词性
- ✅ 改进例句提取：支持冒号后直接例句（无`*`标记）
- ✅ **通用规则**：适用于所有混合格式的条目

**修复状态**：✅ 已修复  
**测试状态**：✅ 已验证（5个sense全部解析成功）

---

## 📊 修复统计

| Case | 单词 | 问题类型 | 修复方案 | 状态 | 影响范围 |
|------|------|----------|----------|------|----------|
| 1 | `important` | 词形变化误匹配 | 改进匹配逻辑 | ✅ | 通用规则 |
| 2 | `gone` | 混合格式识别 | 新增格式类型 | ✅ | 通用规则 |
| 3 | `making` | IDM习语解析 | 改进IDM解析逻辑 | ⏳ | 通用规则 |
| 4 | `christ` | 字母序号+多词性 | 改进字母序号识别和多词性检测 | ⏳ | 通用规则 |

## 📊 改进效果统计

### 关键指标对比

| 指标 | 改进前 | 改进后 | 提升 |
|------|--------|--------|------|
| 平均释义数 | 1.6 | **9.1** | **+466%** ⬆️ |
| 平均例句数 | 15.3 | **16.6** | **+8%** ⬆️ |
| 可能漏解析 | 7个 | **1个** | **-86%** ⬇️ |

### 当前问题分布

| 问题类型 | 数量 | 占比 | 优先级 |
|---------|------|------|--------|
| 定义文本问题 | 115 | 66.1% | 🔴 **高** |
| 无音标 | 24 | 13.8% | 🟡 中 |
| 可能漏解析 | 1 | 0.6% | 🔴 **高** |
| 无例句（长条目） | 1 | 0.6% | 🟡 中 |

---

## 🧪 统一测试

### 测试脚本

创建`test_bad_cases.py`来统一测试所有记录的bad case。

### 测试标准

每个case应该：
- ✅ 解析成功（不为None）
- ✅ sense数量符合预期
- ✅ 音标解析正确（如果有）
- ✅ 例句提取正确（如果有）
- ✅ 定义文本完整清晰

---

## 📝 添加新Case的步骤

1. **记录**：在本文档中添加新的bad case
2. **分析**：分析问题原因，确定是单个单词问题还是规则问题
3. **修复**：优先使用通用规则，避免针对单个单词的特殊处理
4. **测试**：修复后运行统一测试，验证所有case
5. **更新**：更新本文档的修复状态和测试状态

---

## 🔍 待解决的Case

### Case 3: `making` - IDM习语短语解析

**问题描述**：
- 预期1个sense（n词性），包含3个习语短语
- 实际解析出6个sense，习语短语被拆分过细
- 原因：IDM解析逻辑没有正确识别习语短语的边界

**原始数据**：
```
/ˈmeɪkɪŋ; mekɪŋ/ 
n 
(idm 习语) be the making of sb make sb succeed or develop well 使某人成功或顺利: 
These two years of hard work will be the making of him. 这两年的艰苦工作能把他造就成材. 

have the makings of sth have the qualities needed to become sth 有条件成为某事物: 
She has the makings of a good lawyer. 她具备当个好律师的素质. 

in the making in the course of being made, formed or developed 在制造、形成或发展的过程中: 
This first novel is the work of a writer in the making, ie not yet an expert writer. 这第一本小说是作者正在成长锻炼中的作品. 
* This model was two years in the making, ie took two years to make. 这一型号的产品是用了两年时间制成的.
```

**预期结果**：
- 1个sense（n词性）
- 包含3个习语短语（作为related_phrases或独立的sense）

**修复方案**：
- ⏳ 改进IDM解析逻辑，正确识别习语短语的边界
- ⏳ 习语短语应该作为一个整体，包含短语标题、定义和例句
- ⏳ **通用规则**：适用于所有包含习语的条目

**修复状态**：⏳ 待修复  
**测试状态**：⏳ 待测试

---

### Case 4: `christ` - 字母序号+多词性解析

**问题描述**：
- 预期3个sense（2个n词性：(a), (b) + 1个interj词性）
- 实际只解析出2个sense（#a, #b），interj词性没有被识别
- 原因1：字母序号(a)中的括号内容`(also Jesus, Jesus Christ/...)`影响了字母序号的识别
- 原因2：字母序号后出现新词性(interj)没有被正确分离处理

**原始数据**：
```
/kraɪst; kraɪst/ 
n 
(a) (also Jesus, Jesus Christ/ 9dVi:zEs 5kraIst; 9dVizEs 5raIst/) the founder of the Christian religion 基督. (b) image or picture of Christ 基督的图像.

interj (also Jesus, Jesus Christ) (<!> infml 讳, 口) (expressing anger, annoyance, surprise, etc 表示愤怒、烦恼、惊讶等): 
Christ! We're running out of petrol. 天哪! 我们的汽油要用完了.
```

**预期结果**：
- 2个n词性的sense：(a), (b)
- 1个interj词性的sense

**修复方案**：
- ⏳ 改进字母序号识别，正确处理括号内的内容
- ⏳ 改进多词性检测，确保在字母序号后能识别到新词性
- ⏳ **通用规则**：适用于所有字母序号+多词性的条目

**修复状态**：⏳ 待修复  
**测试状态**：⏳ 待测试

---

## ✅ 已解决的Case

1. ✅ `important` - 词形变化误匹配（已修复并验证）
2. ✅ `gone` - 混合格式识别（已修复并验证）

