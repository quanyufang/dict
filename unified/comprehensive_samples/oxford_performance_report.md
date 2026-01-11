# Oxford解析器性能分析报告

> 生成时间: 2026-01-08  
> 总样例数: 174

---

## 📊 解析统计

| 指标 | 数值 | 占比 |
|------|------|------|
| 总样例 | 174 | 100% |
| 解析成功 | 174 | 100.0% |
| 解析失败 | 0 | 0.0% |
| 平均释义数 | 9.6 | - |
| 平均例句数 | 17.6 | - |

---

## 📊 问题统计

| 问题类型 | 数量 | 占比 | 说明 |
|---------|------|------|------|
| 无音标 | 24 | 13.8% | 主要是交叉引用和短语词条 |
| 无释义 | 0 | 0.0% | 解析失败 |
| 质量分 < 0.8 | 24 | 13.8% | 解析质量较低 |
| 释义数 <= 1（可能漏解析） | 0 | 0.0% | **重点关注** |
| 无例句（长条目） | 0 | 0.0% | 可能例句提取失败 |
| 定义文本问题 | 48 | 27.6% | 定义中可能包含例句或冗余内容 |
| 超短条目 (<50字符) | 8 | 4.6% | 可能是交叉引用 |
| 超长条目 (>8000字符) | 24 | 13.8% | 可能需要特殊处理 |

---

## 🔴 Bad Cases 详细列表

### 1️⃣ 可能漏解析（释义数 <= 1，但内容长度 > 500）

**重点关注这些case，可能包含多个义项但只解析出1个。**


### 2️⃣ 定义文本问题（定义中可能包含例句或冗余内容）

#### 1. `a` (长度: 1126)

**原始数据**:
```
/eɪ; e/ n (pl A's, a's / eIz; ez/)  1 the first letter of the English alphabet 英语字母表的第一个字母: `Ann' begins with (an) A/`A'. Ann一字以A字母开始.  2 (music 音) the sixth note in the scale of C major  C大调音阶中的第六音或音符.  3 academic mark indicating the highest standard of work 学业成绩达最高标准的评价符号: get (an) A/`A' in biology 生物（学科）得A.  4 (used to designate a range of standard paper sizes 用以标明一系列标准纸张的规格): [attrib 作定语] an A...
```

**解析结果**:
- 释义数: 8
- 例句数: 2

**问题**: 定义文本可能包含例句片段或冗余内容

---

#### 2. `have` (长度: 13800)

**原始数据**:
```
/həv; həv; strong form 强读式 hæv; hæv/ 见词条使用详细说明6.2、6.3. aux v =>Usage at have3 用法见have3; (used with the past participle to form perfect tenses 与过去分词连用构成完成时态): I've finished my work. 我已经做完工作了. * He's gone home, hasn't he? 他已经回家去了, 是吗? * Have you seen it? Yes I have/No I haven't. 你看见了吗? 看见了[没看见]. * He'll have had the results by then. 他到时候会有结果的. * She may not have told him yet. 她可能还没有告诉他. * Had they l...
```

**解析结果**:
- 释义数: 37
- 例句数: 111

**问题**: 定义文本可能包含例句片段或冗余内容

---

#### 3. `good` (长度: 7026)

**原始数据**:
```
/gʊd; ˇᴜd/ adj (better / 5betE(r); `bZtL/, best /best; bZst/)  1 of high quality; of an acceptable standard; satisfactory 好的; 优质的; 符合标准的; 令人满意的: a good lecture, performance, harvest 好的演讲、表演、收成 * good pronunciation, behaviour, eyesight 好的发音、行为、视力 * a good (eg sharp) knife 快的刀 * Is the light good enough to take photographs? 光线适合照相吗? * The car has very good brakes. 这辆汽车的刹车很灵. * Her English is very go...
```

**解析结果**:
- 释义数: 12
- 例句数: 35

**问题**: 定义文本可能包含例句片段或冗余内容

---

#### 4. `bad` (长度: 2234)

**原始数据**:
```
/bæd; bæd/ adj (worse/ w\:s; w[s/, worst/ w\:st; w[st/)  1 (a) of poor quality; below an acceptable standard; faulty 坏的; 劣质的; 不合格的; 有错的: a bad lecture, harvest 很糟的演讲、收成 * bad pronunciation, eyesight 很差的发音、视力 * You can't take photographs if the light is bad. 光线不足, 就无法拍照. (b) (used with names of occupations or with ns derived from vs 与职业名称连用或与动词派生的名词连用) not competent; not able to perform satisfactor...
```

**解析结果**:
- 释义数: 8
- 例句数: 4

**问题**: 定义文本可能包含例句片段或冗余内容

---

#### 5. `big` (长度: 3151)

**原始数据**:
```
/bɪg; bɪˇ/ adj (-gger, -ggest)  1 large in size, extent or intensity （在体积、面积、范围、程度或强度方面）大的: a big garden, man, majority, defeat, explosion, argument 大花园[高大的人/大多数/大败/大爆炸/大辩论] * the big toe, ie the largest 大脚趾 * a big `g', ie a capital G 大写的g（大写字母G） * (infml 口) big money, ie a lot of money 大笔的钱 * The bigger (ie worse) the crime, the longer the gaol sentence. 犯的罪越大, 刑期越长. * He's the biggest liar (ie ...
```

**解析结果**:
- 释义数: 12
- 例句数: 19

**问题**: 定义文本可能包含例句片段或冗余内容

---

#### 6. `small` (长度: 3931)

**原始数据**:
```
/smɔːl; smɔl/ adj  1 not large in size, degree, number, value, etc （体积、程度、数量、价值等）小的, 少的: a small house, town, room, audience, sum of money 小房子、小镇、小房间、少数听众、一小笔钱 * This hat is too small for me. 这帽子我戴太小. * My influence over her is small, so she won't do as I say. 我对她起不了多大影响, 她不会按我的话去做. Cf 参看 big. =>Usage 见所附用法.  2 young 幼小的; 年幼的: Would a small child know that? 小孩能懂这种事吗? * I lived in the country when ...
```

**解析结果**:
- 释义数: 6
- 例句数: 11

**问题**: 定义文本可能包含例句片段或冗余内容

---

#### 7. `new` (长度: 4294)

**原始数据**:
```
/njuː; <i>US</i> nuː; nu/ adj (-er, -est)  1 not existing before; seen, introduced, made, invented, etc recently or for the first time 新的: a new school, idea, film, novel, invention, car 新的学校、想法、影片、小说、发明、汽车 * new clothes, furniture 新的衣服、家具 * new potatoes, ie ones dug from the soil early in the season 新下来的土豆 * new (ie freshly baked) bread 刚出炉的面包 * the newest (ie latest) fashions 最新款式. =>Usage 见所附用法...
```

**解析结果**:
- 释义数: 7
- 例句数: 16

**问题**: 定义文本可能包含例句片段或冗余内容

---

#### 8. `old` (长度: 6107)

**原始数据**:
```
NOTE ON USAGE 用法: The usual comparative and superlative forms of old are older and oldest *old通常的比较级和最高级形式是older和oldest: My brother is older than me. 我哥哥比我年龄大. *  The cathedral is the oldest building in the city. 这座大教堂是城里最古老的建筑. When comparing the ages of people, especially of members of a family, elder and eldest are often used, as adjectives and pronouns. 在比较人的年龄时, 特别是对于家庭成员, 经常使用elder和eldest, 用...
```

**解析结果**:
- 释义数: 23
- 例句数: 32

**问题**: 定义文本可能包含例句片段或冗余内容

---

#### 9. `long` (长度: 6139)

**原始数据**:
```
/lɒŋ; <i>US</i> lɔːŋ; lɔŋ/ adj (-er / -NgE(r); -N^L/, -est /-NgIst; -NgIst/)  1 having a great or specified extent in space （空间上）长的: How long is the River Nile? 尼罗河有多长? * Your hair is longer than mine. 你的头发比我的长. * Is it a long way (ie far) to your house? 到你家远吗? * These trousers are two inches too long. 这条裤子长出两英寸. Cf 参看 short1 1.  2 having a great or specified duration or extent in time （时间上）长的: He...
```

**解析结果**:
- 释义数: 16
- 例句数: 21

**问题**: 定义文本可能包含例句片段或冗余内容

---

#### 10. `go` (长度: 17744)

**原始数据**:
```
/gəʊ; ˇo/ v (3rd pers sing pres t goes / gEUz; ^oz/, pt went / went; wZnt/, pp gone / gCn; ?@ gR:n; ^Rn/). =>Usage at been 用法见been.

* MOVEMENT 动作 (Senses 1, 2, 3, 4, 5 and 6 refer esp to movement away from the place where the speaker or writer is or a place where he imagines himself to be. 1、2、3、4、5、6各义尤指从说话的人或书写的人所在之处离去的动作, 或从其想像所处之处离去的动作. )  1 (a) [I, Ipr, Ip] move or travel from one place to a...
```

**解析结果**:
- 释义数: 37
- 例句数: 98

**问题**: 定义文本可能包含例句片段或冗余内容

---


### 3️⃣ 无例句（长条目，长度 > 300）


## 📝 建议

1. **重点关注"可能漏解析"的case**：这些case内容较长但只解析出1个释义，可能包含多个义项
2. **检查定义文本问题**：定义中可能包含例句片段，需要改进文本分割逻辑
3. **优化例句提取**：长条目但无例句，可能是例句格式特殊，需要改进例句识别逻辑

---

## 📋 完整数据

完整数据已保存在JSON文件中，便于进一步分析。

