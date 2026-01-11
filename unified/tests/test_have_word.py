#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
"have"词条解析测试

测试Oxford解析器对复杂词条"have"的解析能力
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from unified.parsers.oxford import OxfordParser
from unified.models.entry import DictionaryEntry


# "have"词条的原始数据（来自用户提供）
HAVE_RAW_CONTENT = """/həv; həv; strong form 强读式 hæv; hæv/
见词条使用详细说明6.2、6.3.
aux v =>Usage at have3 用法见have3; (used with the past participle to form perfect tenses 与过去分词连用构成完成时态):
I've finished my work. 我已经做完工作了.
* He's gone home, hasn't he? 他已经回家去了, 是吗?
* Have you seen it? Yes I have/No I haven't. 你看见了吗? 看见了[没看见].
* He'll have had the results by then. 他到时候会有结果的.
* She may not have told him yet. 她可能还没有告诉他.
* Had they left before you got there? 你到达那里时他们已经离开了吗?
* She'd fallen asleep by that time, hadn't she? 那时她早已睡着了, 是吗?
* If I hadn't seen it with my own eyes I wouldn't have believed it. 我要不是亲眼看见, 还可能不相信呢.
* Had I known that (ie If I had known that), I would never have come. 我要是早知道, 我绝对不来.

/hæv; hæv/ v =>Usage at have2, 3 用法见have2,3. (Brit also have got) (not used in the continuous tenses 不用于进行时态).

* POSSESSING 有
1 (Cf 参看 my, your, his, her, its, our, their)
(a) [Tn] possess or own (sth) 有, 据有（某物）:
He has a house in London and a cottage near the sea. 他在伦敦有一所房子, 在海边还有一个小屋.
* Do you have any pets? 你有什么宠物吗? * They've got two cars. 他们有两辆小汽车. * How many glasses have we got? 我们有多少个玻璃杯?
* Do you have/Have you got a 50p piece? 你有没有一枚50便士的硬币?

(b) [Tn, Tn.pr, Cn.a] possess or display (a mental quality or physical feature) 有, 具有（某种精神素质或生理特点）:
You must have a lot of courage. 你可真有胆量.
* She has a good memory. 她的记性很好. * Giraffes have long necks. 长颈鹿的脖子很长.
* The house has (ie contains) three bedrooms. 这所房子有三间卧室.
* You've got a cut on your chin. 你下巴上有一道伤口.
* have a tooth loose/missing 有一颗牙齿松了[掉了].

2 [Tn] (indicating a relationship 表示某种关系):
I have two sisters. 我有两个姐姐.
* They have four children. 他们有四个孩子.
* Does he have any friends? 他有朋友吗?

3 [Tn] (be able to) make use of or exercise (sth) （有能力）利用或运用（某事物）:
She has no real power. 她没有实权.
* I don't have the authority to send them home. 我无法打发他们回家.
* I haven't as much responsibility as before. 我不再担负过去那样多的责任了.
* Have you got time to phone him? 你有时间给他打电话吗?

* EXPERIENCING 体验或经历
4 [Tn] experience or feel (sth); keep in the mind (used esp with the ns shown) 体验或感到（某事物）; 心存, 心怀（尤与下列名词连用）:
I have no doubt (ie I am sure) that you are right. 我肯定你说得对.
* She had the impression that she had seen him before. 她觉得以前见过他.
* Do you have any idea where he lives? 你知道他住在哪里吗?
* What reason have you (got) for thinking he's dishonest? 你凭什么认为他不诚实?

5 [Tng] experience the results of sb's actions 经受（某人的行动所产生的结果）:
We've got people phoning up from all over the world. 我们接到人们从世界各地打来的电话.
* They have orders coming in at the rate of 30 an hour. 他们每小时接到30份定单.

6 [Tn] suffer from (an illness or a disease) 患（病）; 遭受（病痛）:
She's got appendicitis. 她得了阑尾炎.
* He says he has a headache. 他说他头痛.
* Have you got problems at work? 你工作中有问题吗?
* How often do you have a bad back? 你多长时间腰痛一次?

* SHOWING OR DISPLAYING 表现或显示

7 [Tnt] show or demonstrate (a quality) by one's actions 以行动表现或显示（某种品性）:
He has the impudence to take things behind my back! 他背着我拿东西真不害臊!
* Surely she didn't have the nerve to say that to him? 她真的没有勇气对他说那件事吗?
* (fml 文) Would you have the goodness (ie Please be good or kind enough) to help me with my cases? 劳驾帮我拿拿箱子好吗?

* TAKING OR ACCEPTING SOMEBODY 吸收或接纳某人
8 [Tn] (sometimes in the -ing form to indicate an intention or arrangement for the future 有时以-ing的形式表示意向或打算) attend to the needs of (sb/sth) for a limited period; take care of; look after 满足（某人[某事物]）一时之需; 关照; 看管:
Are you having the children tomorrow afternoon? 明天下午你照料孩子吗?
* We've got the neighbours' dog while they're away. 邻居出门时把狗交给我们看管.
* We usually have my mother (ie staying in our house) for a month in the summer. 我们在夏天往往请母亲来住上一个月.

9 [Cn.n/a] take or accept (sb) in a specified function 吸收或接受（某人）担负某种责任:
We'll have Jones as our spokesman. 我们让琼斯做我们的代言人.
* Who can we have as treasurer? 我们能让谁掌管财务呢?

* OTHER MEANINGS 其他意义
10 [Tn, Tn.pr, Tn.p] be holding or displaying (sb/sth) in a specified way （以某种方式）抓住或展示（某人[某事物]）:
She's got him by the collar. 她抓住他的衣领.
* Why did you have your back to the camera? 你为什么背对着照相机?
* He had his head down as he walked out of the court. 他走出法庭时耷拉着脑袋.

11 [Tn, Tnt] be aware of (sth) as a duty or necessity 对（某事物）觉得有责任或有必要:
He has a lot of homework (to do) tonight. 他今晚有许多家庭作业（要做）.
* I must go  I have a bus to catch. 我该走了--我得赶上公共汽车.
* She's got a family to feed. 她要养活一家人.

12 (idm 习语)
`have it (that)... claim to be a fact that...; say that... 断言...; 说...:
Rumour has it that we'll have a new manager soon. 据说我们不久就要来一位新经理.

have (got) it/that `coming can expect unpleasant consequences to follow 注定; 活该:
It was no surprise when he was sent to prison  everyone knew he had it coming (to him). 果不其然他进了监狱--大家都清楚（他）得有这么一天.

have it `in for sb (infml 口) intend to punish or do sth unpleasant to sb 意图惩罚某人; 跟某人过不去:
She's had it in for him ever since he called her a fool in public. 自从他当众说她是蠢货以来, 她就一直想治治他.

have it `in one (to do sth) (infml 口) be capable (of sth); have the ability (to do sth) 有（某一方面）的能力; 有能力（做某事）:
Do you think she's got it in her to be a dancer? 你认为她是舞蹈家的材料吗?

13 (phr v)
have sth in have a stock of sth in one's home, etc 家里等存有某物:
Have we got enough food in? 我们存的食物够不够?

have sth on be wearing sth 穿着; 戴着:
She has a red jacket on. 她穿着一件红色的短上衣.
* He's got a tie on today. 他今天系着一条领带.
have sth on sb (infml 口) (no passive 不用于被动语态) have (evidence) to show that sb is guilty of a crime, etc 有（证据）表明某人有罪等:
Have the police got anything on him? 警方有证据证明他有罪吗?

have sb/sth to oneself be able to use, enjoy, etc sb/sth without others 可独自使用某人[某物]; 得以独享:
With my parents away I've got the house to myself. 由于我父母不在, 我可以独自使用这所房子.

NOTE ON USAGE 用法:
When indicating possession, the most commonly used verb in British English is have got (in present tense forms) 在表示｀有＇的意思时, 英式英语中最常用的动词是have got（用现在时态）:
`Have you got any pets?' `Yes, I've got three rabbits and a tortoise.' ｀你有什么宠物吗?＇｀有, 我有三只兔子和一只乌龟.＇

In US English (and commonly in tenses other than the present in British English) have is used 在美式英语中, 用have表示｀有＇（在英式英语, have表示｀有＇时一般不用于现在时态, 但常用于其他时态）:
I have an apartment in downtown Manhattan. 我在曼哈顿中心区有一套住房.
*  I haven't got a car now but I'll have one next week. 我现在没有汽车, 但是下星期就能有一辆.

Have when used in the present tense in British English is more formal than have got *have在英式英语中用于现在时态, 比用have got显得郑重:
I have no objection to your proposal. 我对你的提议没有异议.

In British English have got, indicating possession, behaves like an auxiliary verb and a pp 在英式英语中, have got表示｀有＇的意思时, 其用法如同一个助动词加一个过去分词:
`Have you got a computer?' `Yes, I have.' ｀你有计算机吗?＇｀有.＇

In US English questions and negatives are formed with do 在美式英语中, 与do连用可构成疑问式和否定式:
`Do you have a computer?' `Yes I do.' ｀你有计算机吗?＇｀我有.＇

This construction is common in British English in tenses other than the present 这种结构在英式英语中多用于除现在式以外的其他时态:
I didn't have any money so I couldn't get a newspaper. 我当时没有钱, 所以没能买报纸.

It is also increasingly found in the present tense. 这种用法现亦逐渐多见于现在时态.

/hæv; hæv/ v =>Usage 见所附用法.

* PERFORMING AN ACTION 做某动作
1 [Tn]
(a) perform (the action indicated by the following n) for a limited period （以有限的时间）从事, 进行（由後接之名词所表示的动作）:
have a swim, walk, ride, etc (Cf 参看 go for a swim, walk, ride, etc) 游泳、散步、骑马
* have a wash, rest, talk 洗一洗、歇一歇、谈一谈
* Let me have a try. 让我试一下.
* She usually has a bath in the morning. 她早上通常要洗个澡.

(b) consume (sth) by eating, drinking, smoking, etc 消费（某物）; 吃、喝或吸（烟）等:
have breakfast/lunch/dinner 吃早饭[午饭/晚饭]
* I usually have a sandwich for lunch. 我午饭时通常吃块三明治.
* We have coffee at 11. 我们11点钟喝咖啡.

* RECEIVING OR UNDERGOING 接受或经受
2 [Tn]
(a) (not used in the continuous tenses 不用于进行时态) receive (sth); experience 接受（某物）; 体验:
I had a letter from my brother this morning. 今早我收到哥哥的来信.
* She'll have an accident one day. 她总有一天要出事.
* I had a shock when I heard the news. 我听到这个消息时感到震惊.

(b) undergo (sth) 经受（某事物）:
I'm having treatment for my lumbago. 我腰痛正在治疗中.
* She's having an operation on her leg. 她的腿正在动手术.
3 [Tn] experience (sth) 经历（某事物）:
We're having a wonderful time, holiday, party. 我们玩得、假期过得、聚会举办得有意思极了.
* I've never had a worse morning than today. 我哪一天早上也不像今天早上这样倒霉.
* They seem to be having some difficulty in starting the car. 他们在启动这辆小汽车时似乎遇到了一些困难.

* PRODUCING 生产或产生
4 [Tn] give birth to (sb/sth); produce 生（孩子[小动物]）; 生产; 产生:
My wife's having a baby. 我妻子正在分娩.
* Our dog has had puppies twice already. 我们的狗已经生了两窝小狗了.
*have a good effect/result/outcome 产生良好的效果[结果/成果]
* His paintings had a strong influence on me as a student. 他的画儿对我这个学生产生了很大的影响.

* CAUSING OR ALLOWING SOMETHING TO HAPPEN 使或让某事发生
5 [Cn.i no passive 不用于被动语态] order or arrange (that sb does sth) 命令或安排（某人做某事）:
I`ll have the gardener plant some trees. 我要让园丁种些树.
* Have the driver bring the car round at 4. 让司机4点钟把汽车开来.

6
(a) (used with a n + past participle 与名词+过去分词连用) cause sth to be done 使某事物予以处理:
Why don't you have your hair cut? 你为什么不理发?
* They're going to have their house painted. 他们准备把房子粉刷一下.
* We're having our car repaired. 我们的汽车正在修理.

(b) (used with a n + past participle 与名词　过去分词连用) suffer the consequences of another person's action 承受、蒙受他人行为之後果:
He had his pocket picked, ie Something was stolen from his pocket. 他的口袋被掏了（衣袋中有东西被窃）.
* She's had her wallet taken. 她的钱包被人拿走了.
* Charles I had his head cut off. 查理一世遭斩首.
* They have had their request refused. 他们的请求遭到拒绝.
(c) [Tn, Cn.g] (used in negative sentences, esp after will not, cannot, etc 用在否定句中, 尤用于will not、cannot等之後) allow or tolerate (sth) 允许或容忍（某事物）:
I cannot have such behaviour in my house. 我不能容忍家中有这种行为.
* She won't have boys arriving late. 她不允许这些男孩子迟到.

7
(a) [Cn.g no passive 不用于被动语态] cause sb to do sth 使某人做某事:
She had her audience listening attentively. 她使听众听得入神.
* The film had us all sitting on the edges of our seats with excitement. 这部影片让我们大家激动不已.
(b) [Cn.a no passive 不用于被动语态] cause sb to be in a certain state 使某人处于某种状态:
The news had me worried. 我听了这消息十分不安.

8 [no passive 不用于被动语态: Tn.pr, Tn.p] cause (sb) to come in a specified direction as a visitor, guest, etc 邀请（某人）来访、来作客等:
We're having friends (over) for dinner. 我们请朋友们来吃饭.
* We had her up here last term to give a lecture. 我们上学期请她上这里来讲过课.

* OTHER MEANINGS 其他意义
9 [Tn] (infml 口) (a) (esp passive 尤用于被动语态) trick (sb); deceive 蒙骗（某人）; 欺骗:
I'm afraid you've been had. 看来你上当了.
(b) win an advantage over (sb); beat 胜过（某人）; 击败:
She certainly had me in that argument. 她在辩论中确实把我驳倒了.
* You had me there! 还是你行!

10[Tn] (<!> sl 讳, 俚) (esp of a man) have sexual intercoursewith (sb) （尤指男人）与（某人）性交:
Have you had her yet? 你跟她发生过性关系吗?

11 (idm 习语) have `had it (sl 俚)
(a) not be going to receive or enjoy sth 将得不到或享受不到某事物:
If he was hoping for a lift home I'm afraid he's had it. 他要是想搭乘便车回家, 我看是吹了.
(b) be going to experience sth unpleasant 将吃苦头:
When they were completely surrounded by police they realized they'd had it. 警察把他们团团围住, 他们知道要有罪受了.

have it `off/a`way (with sb) (<!> sl 讳, 俚) have sexual intercourse with sb 与某人性交:
She was having it off with a neighbour while her husband was away on business. 她在丈夫出差时跟邻居发生了性关系.

what `have you (infml 口) other things, people, etc of the same kind 诸如此类的事物、人等:
There's room in the cellar to store unused furniture and what have you. 地下室里有地方存放不用的家具之类的东西.

12 (phr v) have sb back allow (a spouse, etc from whom one is separated) to return 允许（分手的配偶等）返回:
I'll never have her back. 我决不与她复合.

have sth back receive sth that has been borrowed, stolen, etc from one 收回（被借走、偷走等之）某物:
Let me have it back soon. 早些把东西还给我.
* You can have your files back after we've checked them. 等我们检查完你的文件就退还给你.

NOTE ON USAGE 用法:
Have is used as an auxiliary verb (have1) and as two separate main verbs (have2 and have3).
*have可用作助动词（have1, have2have3.
                                                                                                                    *Except for the negative forms haven't, hasn't and hadn't, the following written and spoken forms are common to all three verbs 除否定形式haven't、hasn't、hadn't外, 这三个动词具有以下共同的书写和读音形式:
                                                                                                                     have (pres t with I, you, we, they) have（现在时态, 与I、you、we、they连用） /hEv, Ev, v; hEv, Ev, v/, strong form 强读式 / hAv; hAv/; written contractions 缩写式 I've / aIv; aIv/, you've / ju:v; juv/, we've / wi:v; wiv/, they've /TeIv; TEv/; negative 否定式 haven't / 5hAvnt; `hAvnt/. has (pres t with he, she, it) has（现在时态, 与he、she、it连用） / hEz, Ez, s, z; hEz, Ez, s, z/, trong form 强读式 /hAz; hAz/; written contractions 缩写式 he's / hi:z; hiz/, she's / Fi:z; Fiz/, it's / Its; Its/, Jack's / dVAks; dVAks/, Sam's / sAmz; sAmz/; negative 否定式 hasn't / 5hAznt; `hAznt/. had (pt) / hEd, Ed, d; hEd, Ed, d/, strong form 强读式 / hAd; hAd/; written contractions 缩写式 I'd /aId; aId/, we'd / wi:d; wid/, she'd / Fi:d; Fid/, etc; negative 否定式 hadn't / 5hAdnt; `hAdnt/. had (pp) /hAd; hAd/. When have2 refers to a regular state orhabitual feature, etc, negatives and questions are formed with do in both British and US English *have2, do连用, 构成否定式和疑问式: People don't have central heating in their houses in my country. 在我国, 一般人家里没有集中供热设备.
                                                                                                                     * Does the referee have the power to send him off the field? 裁判员有权勒令他退场吗? However, when have2 refers to a specific object, fact or feature, etc, British speakers tend to form negatives and questions without an auxiliary verb (informally they use have got), while US speakers invariably form them with do 然而当have2 , , have got）, 而美国人则一律使用do: (Brit) We haven't (got) many wine glasses. 我们的酒杯不多.
*  (US) We don't have many wine glasses. 我们的酒杯不多.
*  (Brit) Have you got a 1 coin? 你有一枚1英镑的硬币吗?
*  (US, and sometimes Brit) Do you have a 1 coin? 你有一枚1英镑的硬币吗? As regards have3, British and US speakers form negatives and questions in the same way  with do 至于have3, do）构成否定式和疑问式: She didn't have any letters last week. 她上周没有收到任何信件.
*  Did this have a good effect? 这有效吗? Note that, as a general rule, the continuous tenses can be used with have3 but not with have2. 注意: 一般说来, have3, have2. As a present tense form of the auxiliary, has is often contracted to 's
*has用作现在时态的助动词时, 常缩写为's/ s, z; s, z/, 如 She's gone to Scotland. 她到苏格兰去了. But has is seldom reduced in this way when it is a part of a main verb, except in set phrases 但has用作主要动词时, 则很少使用缩写形式, 只有一些惯用语例外, 如: He's no head for heights. 他攀高就头晕.
*  She's no right to say that. 她没有权利说那话."""


def test_have_parsing():
    """测试"have"词条解析"""
    parser = OxfordParser()
    
    print("=" * 80)
    print("【have】词条解析测试")
    print("=" * 80)
    
    # 解析
    entry = parser.parse("have", HAVE_RAW_CONTENT)
    
    if not entry:
        print("❌ 解析失败!")
        return
    
    # 显示解析结果
    print("\n📊 解析结果摘要:")
    print("-" * 80)
    
    # 音标
    print(f"\n🎵 音标 ({len(entry.pronunciations)}个):")
    for i, p in enumerate(entry.pronunciations):
        note = f" ({p.__dict__.get('note', '')})" if hasattr(p, 'note') and p.note else ""
        print(f"  [{i+1}] {p.region}: {p.ipa}{note}")
    
    # 词性统计
    pos_count = {}
    for sense in entry.senses:
        pos = sense.pos or 'unknown'
        pos_count[pos] = pos_count.get(pos, 0) + 1
    
    print(f"\n📖 词性统计:")
    for pos, count in pos_count.items():
        print(f"  {pos}: {count}个义项")
    
    # 释义列表
    print(f"\n📚 释义列表 ({len(entry.senses)}个):")
    print("-" * 80)
    
    for i, sense in enumerate(entry.senses[:20]):  # 显示前20个
        pos = sense.pos or '-'
        num = sense.sense_number or '-'
        grammar = f" [{sense.grammar_note}]" if sense.grammar_note else ""
        
        print(f"\n  [{i+1}] POS: {pos} | #{num}{grammar}")
        
        def_text = sense.definition
        if len(def_text) > 120:
            def_text = def_text[:120] + "..."
        print(f"      定义: {def_text}")
        
        if sense.examples:
            print(f"      例句: {len(sense.examples)}个")
            # 显示前2个例句
            for j, ex in enumerate(sense.examples[:2]):
                ex_text = ex.text[:70] + "..." if len(ex.text) > 70 else ex.text
                print(f"        - {ex_text}")
                if ex.translation:
                    print(f"          → {ex.translation[:60]}")
    
    if len(entry.senses) > 20:
        print(f"\n  ... 还有{len(entry.senses) - 20}个释义未显示")
    
    # 相关短语
    if entry.related_phrases:
        print(f"\n🔗 相关短语 ({len(entry.related_phrases)}个):")
        for i, phrase in enumerate(entry.related_phrases[:10]):
            print(f"  [{i+1}] {phrase.phrase} - {phrase.meaning or ''}")
    
    # 解析质量
    print(f"\n📈 解析质量: {entry.parse_quality}")
    if entry.parse_notes:
        print(f"📝 解析备注:")
        for note in entry.parse_notes:
            print(f"  - {note}")
    
    # 详细分析
    print("\n" + "=" * 80)
    print("🔍 详细分析")
    print("=" * 80)
    
    # 检查是否有助动词部分
    aux_senses = [s for s in entry.senses if s.pos == 'aux']
    if aux_senses:
        print(f"\n✅ 找到助动词部分: {len(aux_senses)}个义项")
        for sense in aux_senses:
            print(f"  - #{sense.sense_number or 'N/A'}: {sense.definition[:60]}...")
            print(f"    例句数: {len(sense.examples)}")
    else:
        print("\n❌ 未找到助动词部分 (期望至少有1个)")
    
    # 检查是否有动词部分
    verb_senses = [s for s in entry.senses if s.pos == 'v']
    if verb_senses:
        print(f"\n✅ 找到动词部分: {len(verb_senses)}个义项")
    else:
        print("\n❌ 未找到动词部分 (期望至少有10个)")
    
    # 检查子义项结构
    sub_senses = [s for s in entry.senses if s.sense_number and ('a' in s.sense_number or 'b' in s.sense_number or 'c' in s.sense_number)]
    if sub_senses:
        print(f"\n✅ 找到子义项: {len(sub_senses)}个")
        for sense in sub_senses[:5]:
            print(f"  - #{sense.sense_number}: {sense.definition[:50]}...")
    else:
        print("\n❌ 未找到子义项 (期望至少有1a, 1b等)")
    
    # 检查分类标题（不应该作为sense）
    category_titles = [s for s in entry.senses if 'POSSESSING' in s.definition or 'EXPERIENCING' in s.definition or 'SHOWING' in s.definition]
    if category_titles:
        print(f"\n⚠️  发现可能的分类标题被误识别为义项: {len(category_titles)}个")
        for sense in category_titles:
            print(f"  - #{sense.sense_number}: {sense.definition[:60]}")
    else:
        print("\n✅ 分类标题未误识别为义项")
    
    # 检查习语和短语动词
    idioms = [s for s in entry.senses if '习语' in s.definition or 'idiom' in s.definition.lower()]
    if idioms:
        print(f"\n✅ 找到习语相关义项: {len(idioms)}个")
    else:
        print("\n⚠️  未找到习语义项 (可能被识别为related_phrases)")
    
    # 检查用法说明
    usage_notes = [s for s in entry.senses if 'NOTE ON USAGE' in s.definition or '用法' in s.definition]
    if usage_notes:
        print(f"\n⚠️  用法说明被误识别为义项: {len(usage_notes)}个")
        for sense in usage_notes:
            print(f"  - {sense.definition[:60]}...")
    else:
        print("\n✅ 用法说明未误识别为义项")
    
    # 输出JSON（用于进一步分析）
    print("\n" + "=" * 80)
    print("📄 JSON输出 (保存到文件)")
    print("=" * 80)
    
    output_file = Path(__file__).parent.parent / "comprehensive_samples" / "have_parsed_result.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(entry.to_dict(), f, ensure_ascii=False, indent=2)
    
    print(f"✅ 解析结果已保存到: {output_file}")


if __name__ == '__main__':
    test_have_parsing()

