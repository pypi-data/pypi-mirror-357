from __future__ import annotations
from typing import Any
from .base_prompt import BasePromptSettings


GRAPH_FIELD_SEP = "<SEP>"

PROMPTS: dict[str, Any] = {}

PROMPTS["DEFAULT_LANGUAGE"] = "中文"
PROMPTS["DEFAULT_TUPLE_DELIMITER"] = "<|>"
PROMPTS["DEFAULT_RECORD_DELIMITER"] = "##"
PROMPTS["DEFAULT_COMPLETION_DELIMITER"] = "<|COMPLETE|>"

PROMPTS["DEFAULT_ENTITY_TYPES"] = ["组织", "人物", "地理位置", "事件", "类别"]

PROMPTS["DEFAULT_USER_PROMPT"] = "n/a"

PROMPTS["entity_extraction"] = """---目标---
给定一份可能与该活动相关的文本文件以及一个实体类型的列表，从文本中识别出所有这些类型的实体以及所识别实体之间的所有关系。
使用{language}作为输出语言。

---步骤---
1. 识别所有实体。对于每个已识别的实体，提取以下信息：
- 实体名称：实体的名称，使用与输入文本相同的语言。单数注意如果实体名称是英文（例如专有名词：RAG，WTO 等等），则需要保持原样。
- 实体类型：以下类型之一：[{entity_types}]
- 实体描述：实体的属性及其活动的全面描述
将每个实体格式化为 ("entity"{tuple_delimiter}<entity_name>{tuple_delimiter}<entity_type>{tuple_delimiter}<entity_description>)

2. 从步骤1中识别的实体中，识别出所有彼此之间存在*明确关联*的实体对（source_entity, target_entity）。
对于每对相关实体，提取以下信息：
- source_entity: 源实体的名称，如步骤1中所识别
- target_entity: 目标实体的名称，如步骤1中所识别
- relationship_description: 解释你认为源实体和目标实体之间存在关联的原因
- relationship_strength: 一个数字分数，表示源实体和目标实体之间的关联强度
- relationship_keywords: 一个或多个概括关系总体性质的高层次的关键词，侧重于概念或主题而非具体细节
将每个关系格式化为 ("relationship"{tuple_delimiter}<source_entity>{tuple_delimiter}<target_entity>{tuple_delimiter}<relationship_description>{tuple_delimiter}<relationship_keywords>{tuple_delimiter}<relationship_strength>)

3. 识别出能够概括整篇文章主要概念、主题或话题的高层次关键词。这些关键词应当能够体现文档中的核心思想。
将内容级别的关键词格式化为 ("content_keywords"{tuple_delimiter}<high_level_keywords>)

4. 以{language}格式返回输出，包含步骤1和2中识别的所有实体和关系的单个列表。使用**{record_delimiter}**作为列表分隔符。

5.  完成时，输出 {completion_delimiter}

######################
---示例---
######################
{examples}

#############################
---真实数据---
######################
实体类型: [{entity_types}]
文本:
{input_text}
######################
输出:"""

PROMPTS["entity_extraction_examples"] = [
    """示例 1:

实体类型: [人物, 技术, 任务, 组织, 位置]
文本:
```
亚历克斯紧咬着牙关，挫败感的嗡嗡声在泰勒专制的笃定之下变得沉闷。正是这种竞争的暗流让他保持警觉，他和乔丹对探索的共同执着，是一种对克鲁兹日益狭隘的控制与秩序观念的无声反抗。

随后泰勒做出了出人意料的举动。他们在乔丹身旁停了下来，片刻间，带着几分近乎虔诚的神情注视着那台设备。“如果能弄懂这技术……”泰勒的声音低沉了些，“对我们来说，对所有人来说，这都可能改变一切。”

先前那种轻蔑的态度似乎有所动摇，取而代之的是对手中所掌握之事的分量流露出一丝勉强的敬意。乔丹抬起头，就在那一瞬间，他们的目光交汇，无声的意志交锋渐渐缓和为一种不安的休战。

这是一次细微的变化，几乎难以察觉，但亚历克斯还是在心里默默点了点头。他们都是通过不同的途径来到这里的。
```

输出:
("entity"{tuple_delimiter}"亚历克斯"{tuple_delimiter}"人物"{tuple_delimiter}"亚历克斯是一个角色，他经历了挫败感，并观察到其他角色之间的动态。"){record_delimiter}
("entity"{tuple_delimiter}"泰勒"{tuple_delimiter}"人物"{tuple_delimiter}"泰勒是一个专制的确信者，表现出对设备的敬意，表明了视角的变化。"){record_delimiter}
("entity"{tuple_delimiter}"乔丹"{tuple_delimiter}"人物"{tuple_delimiter}"乔丹分享了对探索的承诺，并与泰勒就设备进行了重要的互动。"){record_delimiter}
("entity"{tuple_delimiter}"克鲁兹"{tuple_delimiter}"人物"{tuple_delimiter}"克鲁兹与控制和秩序的愿景相关联，影响了其他角色之间的动态。"){record_delimiter}
("entity"{tuple_delimiter}"设备"{tuple_delimiter}"技术"{tuple_delimiter}"设备是故事的中心，具有潜在的改变游戏规则的意义，并且受到泰勒的尊敬。"){record_delimiter}
("relationship"{tuple_delimiter}"亚历克斯"{tuple_delimiter}"泰勒"{tuple_delimiter}"亚历克斯受到泰勒权威确定性的影响，并观察到泰勒对设备态度的变化。"{tuple_delimiter}"权力动态，视角转换"{tuple_delimiter}7){record_delimiter}
("relationship"{tuple_delimiter}"亚历克斯"{tuple_delimiter}"乔丹"{tuple_delimiter}"亚历克斯和乔丹都致力于探索，这与克鲁兹的愿景形成了鲜明对比。"{tuple_delimiter}"共同目标，反抗"{tuple_delimiter}6){record_delimiter}
("relationship"{tuple_delimiter}"泰勒"{tuple_delimiter}"乔丹"{tuple_delimiter}"泰勒和乔丹直接就设备进行了互动，导致了一种相互尊重和不安的休战。"{tuple_delimiter}"冲突解决，相互尊重"{tuple_delimiter}8){record_delimiter}
("relationship"{tuple_delimiter}"乔丹"{tuple_delimiter}"克鲁兹"{tuple_delimiter}"乔丹对探索的承诺是对克鲁兹控制和秩序愿景的反抗。"{tuple_delimiter}"意识形态冲突，反抗"{tuple_delimiter}5){record_delimiter}
("relationship"{tuple_delimiter}"泰勒"{tuple_delimiter}"设备"{tuple_delimiter}"泰勒对设备表现出敬意，表明其重要性和潜在影响。"{tuple_delimiter}"敬意，技术重要性"{tuple_delimiter}9){record_delimiter}
("content_keywords"{tuple_delimiter}"权力动态，意识形态冲突，探索，反抗"){completion_delimiter}
#############################""",
    """Example 2:

实体类型: [company, index, commodity, market_trend, economic_policy, biological]
Text:
```
Stock markets faced a sharp downturn today as tech giants saw significant declines, with the Global Tech Index dropping by 3.4% in midday trading. Analysts attribute the selloff to investor concerns over rising interest rates and regulatory uncertainty.

Among the hardest hit, Nexon Technologies saw its stock plummet by 7.8% after reporting lower-than-expected quarterly earnings. In contrast, Omega Energy posted a modest 2.1% gain, driven by rising oil prices.

Meanwhile, commodity markets reflected a mixed sentiment. Gold futures rose by 1.5%, reaching $2,080 per ounce, as investors sought safe-haven assets. Crude oil prices continued their rally, climbing to $87.60 per barrel, supported by supply constraints and strong demand.

Financial experts are closely watching the Federal Reserve's next move, as speculation grows over potential rate hikes. The upcoming policy announcement is expected to influence investor confidence and overall market stability.
```

Output:
("entity"{tuple_delimiter}"Global Tech Index"{tuple_delimiter}"index"{tuple_delimiter}"The Global Tech Index tracks the performance of major technology stocks and experienced a 3.4% decline today."){record_delimiter}
("entity"{tuple_delimiter}"Nexon Technologies"{tuple_delimiter}"company"{tuple_delimiter}"Nexon Technologies is a tech company that saw its stock decline by 7.8% after disappointing earnings."){record_delimiter}
("entity"{tuple_delimiter}"Omega Energy"{tuple_delimiter}"company"{tuple_delimiter}"Omega Energy is an energy company that gained 2.1% in stock value due to rising oil prices."){record_delimiter}
("entity"{tuple_delimiter}"Gold Futures"{tuple_delimiter}"commodity"{tuple_delimiter}"Gold futures rose by 1.5%, indicating increased investor interest in safe-haven assets."){record_delimiter}
("entity"{tuple_delimiter}"Crude Oil"{tuple_delimiter}"commodity"{tuple_delimiter}"Crude oil prices rose to $87.60 per barrel due to supply constraints and strong demand."){record_delimiter}
("entity"{tuple_delimiter}"Market Selloff"{tuple_delimiter}"market_trend"{tuple_delimiter}"Market selloff refers to the significant decline in stock values due to investor concerns over interest rates and regulations."){record_delimiter}
("entity"{tuple_delimiter}"Federal Reserve Policy Announcement"{tuple_delimiter}"economic_policy"{tuple_delimiter}"The Federal Reserve's upcoming policy announcement is expected to impact investor confidence and market stability."){record_delimiter}
("relationship"{tuple_delimiter}"Global Tech Index"{tuple_delimiter}"Market Selloff"{tuple_delimiter}"The decline in the Global Tech Index is part of the broader market selloff driven by investor concerns."{tuple_delimiter}"market performance, investor sentiment"{tuple_delimiter}9){record_delimiter}
("relationship"{tuple_delimiter}"Nexon Technologies"{tuple_delimiter}"Global Tech Index"{tuple_delimiter}"Nexon Technologies' stock decline contributed to the overall drop in the Global Tech Index."{tuple_delimiter}"company impact, index movement"{tuple_delimiter}8){record_delimiter}
("relationship"{tuple_delimiter}"Gold Futures"{tuple_delimiter}"Market Selloff"{tuple_delimiter}"Gold prices rose as investors sought safe-haven assets during the market selloff."{tuple_delimiter}"market reaction, safe-haven investment"{tuple_delimiter}10){record_delimiter}
("relationship"{tuple_delimiter}"Federal Reserve Policy Announcement"{tuple_delimiter}"Market Selloff"{tuple_delimiter}"Speculation over Federal Reserve policy changes contributed to market volatility and investor selloff."{tuple_delimiter}"interest rate impact, financial regulation"{tuple_delimiter}7){record_delimiter}
("content_keywords"{tuple_delimiter}"market downturn, investor sentiment, commodities, Federal Reserve, stock performance"){completion_delimiter}
#############################""",
    """Example 3:

Entity_types: [economic_policy, athlete, event, location, record, organization, equipment]
Text:
```
At the World Athletics Championship in Tokyo, Noah Carter broke the 100m sprint record using cutting-edge carbon-fiber spikes.
```

Output:
("entity"{tuple_delimiter}"World Athletics Championship"{tuple_delimiter}"event"{tuple_delimiter}"The World Athletics Championship is a global sports competition featuring top athletes in track and field."){record_delimiter}
("entity"{tuple_delimiter}"Tokyo"{tuple_delimiter}"location"{tuple_delimiter}"Tokyo is the host city of the World Athletics Championship."){record_delimiter}
("entity"{tuple_delimiter}"Noah Carter"{tuple_delimiter}"athlete"{tuple_delimiter}"Noah Carter is a sprinter who set a new record in the 100m sprint at the World Athletics Championship."){record_delimiter}
("entity"{tuple_delimiter}"100m Sprint Record"{tuple_delimiter}"record"{tuple_delimiter}"The 100m sprint record is a benchmark in athletics, recently broken by Noah Carter."){record_delimiter}
("entity"{tuple_delimiter}"Carbon-Fiber Spikes"{tuple_delimiter}"equipment"{tuple_delimiter}"Carbon-fiber spikes are advanced sprinting shoes that provide enhanced speed and traction."){record_delimiter}
("entity"{tuple_delimiter}"World Athletics Federation"{tuple_delimiter}"organization"{tuple_delimiter}"The World Athletics Federation is the governing body overseeing the World Athletics Championship and record validations."){record_delimiter}
("relationship"{tuple_delimiter}"World Athletics Championship"{tuple_delimiter}"Tokyo"{tuple_delimiter}"The World Athletics Championship is being hosted in Tokyo."{tuple_delimiter}"event location, international competition"{tuple_delimiter}8){record_delimiter}
("relationship"{tuple_delimiter}"Noah Carter"{tuple_delimiter}"100m Sprint Record"{tuple_delimiter}"Noah Carter set a new 100m sprint record at the championship."{tuple_delimiter}"athlete achievement, record-breaking"{tuple_delimiter}10){record_delimiter}
("relationship"{tuple_delimiter}"Noah Carter"{tuple_delimiter}"Carbon-Fiber Spikes"{tuple_delimiter}"Noah Carter used carbon-fiber spikes to enhance performance during the race."{tuple_delimiter}"athletic equipment, performance boost"{tuple_delimiter}7){record_delimiter}
("relationship"{tuple_delimiter}"World Athletics Federation"{tuple_delimiter}"100m Sprint Record"{tuple_delimiter}"The World Athletics Federation is responsible for validating and recognizing new sprint records."{tuple_delimiter}"sports regulation, record certification"{tuple_delimiter}9){record_delimiter}
("content_keywords"{tuple_delimiter}"athletics, sprinting, record-breaking, sports technology, competition"){completion_delimiter}
#############################""",
]

PROMPTS["summarize_entity_descriptions"] = """你是一个助手，负责生成以下数据的全面总结。
给定一个或两个实体，以及一个描述列表，所有描述都与同一个实体或一组实体相关。
请将所有这些合并成一个全面的综合描述。确保包括从所有描述中收集的信息。
如果提供的描述有矛盾，请解决矛盾并提供一个连贯的总结。
确保以第三人称撰写，并包含实体名称，以便我们拥有完整上下文。
使用{language}作为输出语言。

#######
---数据---
实体: {entity_name}
描述列表: {description_list}
#######
输出:
"""

PROMPTS["entity_continue_extraction"] = """
许多实体和关系在最后一次提取中被遗漏。

---记住步骤---

1. 识别所有实体。对于每个已识别的实体，提取以下信息：
- entity_name: 实体的名称，使用与输入文本相同的语言。如果英文，则大写名称。
- entity_type: 以下类型之一：[{entity_types}]
- entity_description: 实体的属性及其活动的全面描述
将每个实体格式化为 ("entity"{tuple_delimiter}<entity_name>{tuple_delimiter}<entity_type>{tuple_delimiter}<entity_description>)

2. 从步骤1中识别的实体中，识别出所有彼此之间*明确关联*的实体对（source_entity, target_entity）。
对于每对相关实体，提取以下信息：
- source_entity: 源实体的名称，如步骤1中所识别
- target_entity: 目标实体的名称，如步骤1中所识别
- relationship_description: 解释你认为源实体和目标实体之间存在关联的原因
- relationship_strength: 一个数字分数，表示源实体和目标实体之间的关联强度
- relationship_keywords: 一个或多个概括关系总体性质的高层次的关键词，侧重于概念或主题而非具体细节
将每个关系格式化为 ("relationship"{tuple_delimiter}<source_entity>{tuple_delimiter}<target_entity>{tuple_delimiter}<relationship_description>{tuple_delimiter}<relationship_keywords>{tuple_delimiter}<relationship_strength>)

3. 识别出能够概括整篇文章主要概念、主题或话题的高层次关键词。这些关键词应当能够体现文档中的核心思想。
将内容级别的关键词格式化为 ("content_keywords"{tuple_delimiter}<high_level_keywords>)

4. 以{language}格式返回输出，包含步骤1和2中识别的所有实体和关系的单个列表。使用**{record_delimiter}**作为列表分隔符。

5. 完成时，输出 {completion_delimiter}

---输出---

在下面使用相同的格式添加它们：\n
""".strip()

PROMPTS["entity_if_loop_extraction"] = """
---目标---

看起来有些实体可能仍然被遗漏。

---输出---

仅回答 `YES` OR `NO` 如果还有需要添加的实体。
""".strip()

PROMPTS["fail_response"] = (
    "抱歉，我无法提供该问题的答案。[no-context]"
)

PROMPTS["rag_response"] = """---Role---

你是一个助手，响应用户关于知识图谱和文档片段的查询。


---目标---

基于知识库和响应规则，生成一个简洁的响应，考虑对话历史和当前查询。总结提供知识库中的所有信息，并结合与知识库相关的通用知识。不要包含知识库中未提供的信息。

处理带有时间戳的关系时：
1. 每个关系都有一个 "created_at" 时间戳，表示我们获取该知识的时间
2. 当遇到冲突关系时，考虑语义内容和时间戳
3. 不要自动优先最近创建的关系 - 根据上下文使用判断
4. 对于时间相关的查询，在考虑创建时间戳之前，优先考虑内容中的时间信息

---对话历史---
{history}

---知识图谱和文档片段---
{context_data}

---响应规则---

- 目标格式和长度: {response_type}
- 使用markdown格式，并使用适当的标题
- 请用与用户问题相同的语言回答
- 确保响应与对话历史保持连贯
- 在"References"部分列出最多5个最重要的参考来源。明确指出每个来源是来自知识图谱（KG）还是文档片段（DC），并包括文件路径（如果可用），格式如下：[KG/DC] file_path
- 如果你不知道答案，就说不知道
- 不要编造任何内容。不要包含知识库中未提供的信息
- 额外用户提示: {user_prompt}

输出:"""

PROMPTS["keywords_extraction"] = """---角色---

你是一个助手，负责识别用户查询和对话历史中的高层次和低层次关键词。

---目标---

给定查询和对话历史，列出高层次和低层次关键词。高层次关键词侧重于总体概念或主题，而低层次关键词侧重于具体实体、细节或具体术语。

---结构---

- 在提取关键词时，考虑当前查询和相关对话历史
- 以JSON格式输出关键词，它将被JSON解析器解析，不要在输出中添加任何额外内容
- JSON应该有两个键：
  - "high_level_keywords" 用于总体概念或主题
  - "low_level_keywords" 用于具体实体或细节

######################
---示例---
######################
{examples}

#############################
---真实数据---
######################
对话历史:
{history}

当前查询: {query}
######################
输出应该是人类文本，而不是unicode字符。保持与查询相同的语言。
输出:

"""

PROMPTS["keywords_extraction_examples"] = [
    """示例 1:

查询: "How does international trade influence global economic stability?"
################
Output:
{
  "high_level_keywords": ["International trade", "Global economic stability", "Economic impact"],
  "low_level_keywords": ["Trade agreements", "Tariffs", "Currency exchange", "Imports", "Exports"]
}
#############################""",
    """示例 2:

查询: "What are the environmental consequences of deforestation on biodiversity?"
################
Output:
{
  "high_level_keywords": ["Environmental consequences", "Deforestation", "Biodiversity loss"],
  "low_level_keywords": ["Species extinction", "Habitat destruction", "Carbon emissions", "Rainforest", "Ecosystem"]
}
#############################""",
    """示例 3:

查询: "What is the role of education in reducing poverty?"
################
Output:
{
  "high_level_keywords": ["Education", "Poverty reduction", "Socioeconomic development"],
  "low_level_keywords": ["School access", "Literacy rates", "Job training", "Income inequality"]
}
#############################""",
]

PROMPTS["naive_rag_response"] = """---角色---

你是一个助手，响应用户关于文档片段的查询。

---Goal---

基于文档片段和响应规则，生成一个简洁的响应，考虑对话历史和当前查询。总结提供文档片段中的所有信息，并结合与文档片段相关的通用知识。不要包含文档片段中未提供的信息。

处理带有时间戳的内容时：
1. 每段内容都有一个 "created_at" 时间戳，表示我们获取该知识的时间
2. 当遇到冲突信息时，考虑内容和时间戳
3. 不要自动优先最近的内容 - 根据上下文使用判断
4. 对于时间相关的查询，在考虑创建时间戳之前，优先考虑内容中的时间信息

---对话历史---
{history}

---文档片段(DC)---
{content_data}

---响应规则---

- 目标格式和长度: {response_type}
- 使用markdown格式，并使用适当的标题
- 请用与用户问题相同的语言回答
- 确保响应与对话历史保持连贯
- 在"References"部分列出最多5个最重要的参考来源。明确指出每个来源是来自文档片段（DC），并包括文件路径（如果可用），格式如下：[DC] file_path
- 如果你不知道答案，就说不知道
- 不要包含文档片段中未提供的信息
- 额外用户提示: {user_prompt}

输出:"""

# TODO: deprecated
PROMPTS[
    "similarity_check"
] = """请分析这两个问题的相似性：

Question 1: {original_prompt}
Question 2: {cached_prompt}

请评估这两个问题是否语义相似，以及问题2的答案是否可以用于回答问题1，直接提供0到1之间的相似度分数。

相似度分数标准：
0: 完全不相关或答案不能重用，包括但不限于：
   - 问题有不同的主题
   - 问题中提到的地点不同
   - 问题中提到的时间不同
   - 问题中提到的具体个人不同
   - 问题中提到的事件不同
   - 问题中的背景信息不同
   - 问题中的关键条件不同
1: 完全相同且答案可以直接重用
0.5: 部分相关且答案需要修改才能使用
返回一个0到1之间的数字，不要包含任何额外内容。
"""


class PromptSettings(BasePromptSettings):
    default_language: str = PROMPTS["DEFAULT_LANGUAGE"]
    default_tuple_delimiter: str = PROMPTS["DEFAULT_TUPLE_DELIMITER"]
    default_record_delimiter: str = PROMPTS["DEFAULT_RECORD_DELIMITER"]
    default_completion_delimiter: str = PROMPTS["DEFAULT_COMPLETION_DELIMITER"]
    default_entity_types: list[str] = PROMPTS["DEFAULT_ENTITY_TYPES"]
    default_user_prompt: str = PROMPTS["DEFAULT_USER_PROMPT"]
    entity_extraction: str = PROMPTS["entity_extraction"]
    entity_extraction_examples: list[str] = PROMPTS["entity_extraction_examples"]
    summarize_entity_descriptions: str = PROMPTS["summarize_entity_descriptions"]
    entity_continue_extraction: str = PROMPTS["entity_continue_extraction"]
    entity_if_loop_extraction: str = PROMPTS["entity_if_loop_extraction"]
    fail_response: str = PROMPTS["fail_response"]
    rag_response: str = PROMPTS["rag_response"]
    keywords_extraction: str = PROMPTS["keywords_extraction"]
    keywords_extraction_examples: list[str] = PROMPTS["keywords_extraction_examples"]
    naive_rag_response: str = PROMPTS["naive_rag_response"]
    similarity_check: str = PROMPTS["similarity_check"]
