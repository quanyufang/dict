# Oxford解析器问题案例汇总（已更新）

> 生成时间: 2026-01-08（已改进）  
> 总样例数: 174  
> 解析成功率: 174/174 (100.0%)

---

## 📊 解析统计

| 指标 | 数值 |
|------|------|
| 总样例 | 174 |
| 解析成功 | 174 (100.0%) |
| 解析失败 | 0 |
| 平均释义数 | 9.1 |
| 平均例句数 | 16.6 |

---

## 📊 问题分类统计

| 问题类型 | 数量 | 占比 |
|---------|------|------|
| 无音标 | 24 | 13.8% |
| 无释义 | 0 | 0.0% |
| 质量分 < 0.8 | 0 | 0.0% |
| 释义数 <= 1（可能漏解析） | 1 | 0.6% |
| 无例句（长条目） | 1 | 0.6% |
| 超短条目 (<50字符) | 8 | 4.6% |
| 超长条目 (>8000字符) | 24 | 13.8% |

---

## 1️⃣ 无音标案例 (24个)

### `is` (长度: 117)

**原始数据**:
```
abbr 缩写 = Island(s); Isle(s): (the) Windward Is, ie Islands 向风群岛 * (the) British Is, ie Isles 不列颠群岛. Cf 参看 I abbr 缩写.
```

**解析结果**: 质量分 0.7, 释义数 1, 格式类型: generic

**备注**: 格式类型: generic, 未解析到音标

---

### `has` (长度: 8)

**原始数据**:
```
=> have.
```

**解析结果**: 质量分 0.7, 释义数 1, 格式类型: cross_reference

**备注**: 格式类型: cross_reference, 未解析到音标

---

### `had` (长度: 15)

**原始数据**:
```
pt, pp of have.
```

**解析结果**: 质量分 0.7, 释义数 1, 格式类型: generic

**备注**: 格式类型: generic, 未解析到音标

---

### `does` (长度: 6)

**原始数据**:
```
=> do.
```

**解析结果**: 质量分 0.7, 释义数 1, 格式类型: cross_reference

**备注**: 格式类型: cross_reference, 未解析到音标

---

### `did` (长度: 9)

**原始数据**:
```
pt of do.
```

**解析结果**: 质量分 0.7, 释义数 1, 格式类型: cross_reference

**备注**: 格式类型: cross_reference, 未解析到音标

---

### `went` (长度: 10)

**原始数据**:
```
pt of go1.
```

**解析结果**: 质量分 0.7, 释义数 1, 格式类型: cross_reference

**备注**: 格式类型: cross_reference, 未解析到音标

---

### `database` (长度: 80)

**原始数据**:
```
n large store of computerized data, esp lists or abstracts of reports, etc 数据单元.
```

**解析结果**: 质量分 0.7, 释义数 1, 格式类型: generic

**备注**: 格式类型: generic, 未解析到音标

---

### `ashtray` (长度: 86)

**原始数据**:
```
n small dish or container into which smokers put tobacco ash, cigarette ends, etc 烟灰缸.
```

**解析结果**: 质量分 0.7, 释义数 1, 格式类型: generic

**备注**: 格式类型: generic, 未解析到音标

---

### `taps` (长度: 10)

**原始数据**:
```
=> tap2 2.
```

**解析结果**: 质量分 0.7, 释义数 1, 格式类型: cross_reference

**备注**: 格式类型: cross_reference, 未解析到音标

---

### `balance sheet` (长度: 125)

**原始数据**:
```
written record of money received and paid out, showing the difference between the two total amounts 资产负债表, 资金平衡表（显示收支总差额的记录）.
```

**解析结果**: 质量分 0.7, 释义数 1, 格式类型: generic

**备注**: 格式类型: generic, 未解析到音标

---

### `blow-dry` (长度: 222)

**原始数据**:
```
v (pt, pp -dried) [Tn] style (the hair) while drying it with a hand-held drier 用手持吹风机把（头发）吹乾并定型.  n act of drying and styling the hair in this way 用上述方法将头发吹乾并定型的作业: ask the hairdresser for a wash and blow-dry 要求理发师洗头并吹乾定型.
```

**解析结果**: 质量分 0.7, 释义数 1, 格式类型: generic

**备注**: 格式类型: generic, 未解析到音标

---

### `steerage-way` (长度: 118)

**原始数据**:
```
n [U] (nautical 海) forward movement needed by a ship, boat, etc to allow it to be steered or controlled properly 舵效航速.
```

**解析结果**: 质量分 0.7, 释义数 1, 格式类型: generic

**备注**: 格式类型: generic, 未解析到音标

---

### `hay fever` (长度: 100)

**原始数据**:
```
allergic illness affecting the nose and throat, caused by pollen or dust 枯草热（由花粉或尘埃引起鼻部和咽喉发炎的变态反应症）.
```

**解析结果**: 质量分 0.7, 释义数 1, 格式类型: generic

**备注**: 格式类型: generic, 未解析到音标

---

### `soft-hearted` (长度: 150)

**原始数据**:
```
adj sympathetic and kind, sometimes to too great an extent 有同情心的, 心肠软的（有时过分）: He's always lending her money; he's too soft-hearted. 他老是把钱借给她, 心肠也太软了. 
```

**解析结果**: 质量分 0.7, 释义数 1, 格式类型: generic

**备注**: 格式类型: generic, 未解析到音标

---

### `wildfowl` (长度: 141)

**原始数据**:
```
n (pl unchanged 复数不变) any of the types of bird that are shot or hunted as game, eg ducks, geese, pheasants, quail, etc （视为猎物的）野禽（如野鸭、雁、雉、鹑等）.
```

**解析结果**: 质量分 0.7, 释义数 1, 格式类型: generic

**备注**: 格式类型: generic, 未解析到音标

---

### `public transport` (长度: 131)

**原始数据**:
```
buses, trains, etc available to the public according to a published timetable 公共交通工具（公共汽车、火车等）: travel by public transport 乘公共车辆旅行.
```

**解析结果**: 质量分 0.7, 释义数 1, 格式类型: generic

**备注**: 格式类型: generic, 未解析到音标

---

### `set sb up` (长度: 1785)

**原始数据**:
```
(infml 口) (a) make sb healthier, stronger, more lively, etc 使某人更健康、强壮、活跃等: A hot drink will soon set you up. 你喝杯热饮料马上就精神了. * A week in the country will set her up nicely after her operation. 她手术後在郊外住上一个星期一定能复原. (b) provide sb with the money to start a business, buy a house, etc 使某人有钱创业、买房子等: Her father set her up in business. 她父亲出钱帮她创业. * His father set him up as a bookseller. 他父亲资助他做了书商. * Winning all that money on the pools set her up for life. 她赢得足球普尔的那些彩金已够她一生花用不尽. set sth up (a) place sth i...
```

**解析结果**: 质量分 0.7, 释义数 8, 格式类型: phrase_heading

**备注**: 格式类型: phrase_heading, 未解析到音标

---

### `junk food` (长度: 128)

**原始数据**:
```
(infml derog 口, 贬) food (eg potato crisps) eaten as a snack and usu thought to be not good for one's health 通常认为不利健康的小吃（如炸马铃薯条）.
```

**解析结果**: 质量分 0.7, 释义数 1, 格式类型: generic

**备注**: 格式类型: generic, 未解析到音标

---

### `pack-ice` (长度: 107)

**原始数据**:
```
n [U] large mass of ice floating in the sea, formed from smaller pieces which have frozen together 海上的大堆浮冰.
```

**解析结果**: 质量分 0.7, 释义数 1, 格式类型: generic

**备注**: 格式类型: generic, 未解析到音标

---

### `merely` (长度: 105)

**原始数据**:
```
adv only; simply 仅; 只; 不过: I merely asked his name. 我只问了他的名字. * I meant it merely as a joke. 我原意只不过是开个玩笑.
```

**解析结果**: 质量分 0.7, 释义数 1, 格式类型: generic

**备注**: 格式类型: generic, 未解析到音标

---


## 2️⃣ 可能漏解析的案例 (1个)

### `making` (长度: 561, 释义数: 1)

**原始数据**:
```
/ˈmeɪkɪŋ; `mekɪŋ/ n (idm 习语) be the making of sb make sb succeed or develop well 使某人成功或顺利: These two years of hard work will be the making of him. 这两年的艰苦工作能把他造就成材. have the makings of sth have the qualities needed to become sth 有条件成为某事物: She has the makings of a good lawyer. 她具备当个好律师的素质. in the `making in the course of being made, formed or developed 在制造、形成或发展的过程中: This first novel is the work of a writer in the making, ie not yet an expert writer. 这第一本小说是作者正在成长锻炼中的作品. * This model was two years in the making, ie took two years to make. 这一型号的产品是用了两年时间制成的.
```

**解析结果**: 格式类型: numbered_sense, 例句数: 1

---


## 3️⃣ 格式类型分布

| 格式类型 | 数量 | 占比 |
|---------|------|------|
| numbered_sense | 141 | 81.0% |
| generic | 18 | 10.3% |
| cross_reference | 7 | 4.0% |
| direct_letter_numbered | 3 | 1.7% |
| colon_separated | 2 | 1.1% |
| phrase_heading | 2 | 1.1% |
| mixed_cross_ref | 1 | 0.6% |

---


## 4️⃣ 需要review的特殊case

### give up (测试用例)
- 格式类型: phrase_heading
- 预期: 多个sense，包括短语标题+子sense
- 实际: 已识别格式类型，但需要验证sense分割是否正确

### come up (测试用例)
- 格式类型: direct_letter_numbered
- 预期: 字母序号系列 (a)-(g) + 变体短语
- 实际: 已识别格式类型，但需要验证变体短语分割是否正确

---
