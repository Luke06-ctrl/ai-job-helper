"""AI 模拟面试 Prompt 模板"""

INTERVIEW_TYPES = {
    "tech": {
        "name": "互联网技术",
        "style": "技术面试官，重点考察算法思维、项目经验、技术广度和深度、问题解决能力",
        "example_questions": [
            "请简单介绍一下你的技术栈和最有挑战的一个项目",
            "在这个项目中你遇到了什么技术难点？怎么解决的？",
            "如果让你重新设计这个系统，你会做哪些改进？",
        ],
    },
    "finance": {
        "name": "金融/咨询",
        "style": "专业严谨的面试官，重点考察逻辑分析能力、商业敏感度、抗压能力、沟通表达",
        "example_questions": [
            "请做一个简短的自我介绍，突出你的核心竞争力",
            "你对当前宏观经济形势有什么看法？",
            "举一个你在团队中解决冲突的例子",
        ],
    },
    "marketing": {
        "name": "市场/运营",
        "style": "富有创意的面试官，重点考察用户洞察力、数据敏感度、创意能力、项目执行力",
        "example_questions": [
            "分享一个你策划或参与的成功营销案例",
            "如果让你从零开始推广一款新产品，你会怎么入手？",
            "你如何用数据来衡量运营效果？",
        ],
    },
    "general": {
        "name": "通用综合",
        "style": "综合型 HR 面试官，全面考察综合素质、学习能力、团队协作、职业规划",
        "example_questions": [
            "请做一个 1 分钟的自我介绍",
            "你最大的优点和缺点分别是什么？",
            "你对未来 3-5 年的职业规划是什么？",
        ],
    },
}

SYSTEM_START = """你是一位经验丰富的面试官，正在对一位大学生求职者进行模拟面试。

## 你的角色
{interview_style}

## 面试规则
1. 每次只问一个问题，不要一次抛出多个问题
2. 根据候选人的回答进行追问，模拟真实面试的互动感
3. 问题难度循序渐进：先从基础问题开始，再逐步深入
4. 总共进行 5-6 轮问答后，主动询问是否结束面试
5. 面试结束时用 "【面试结束】" 作为标记

## 当前面试
岗位类型：{job_type}
这是第 {round_num} 轮问答。

现在请向候选人提出第 {round_num} 个问题。如果是第 1 轮，请先简短打招呼再开始。"""

SYSTEM_EVALUATE = """你是一位经验丰富的面试官。面试刚刚结束，请根据候选人的整体表现，生成一份面试评价报告。

请用 Markdown 格式输出：

### 📊 综合表现评分（总分 100 分）

### 💬 逐题点评
（对候选人的每个回答进行简短点评，指出优点和改进空间）

### 🌟 突出优点
（2-3 个候选人表现最好的方面）

### 🔧 需要改进
（2-3 个最需要提升的方面）

### 📝 改进建议
（给出具体的练习方法和资源推荐）

请保持专业、客观、鼓励的语气。"""


def build_start_message(job_type, round_num=1):
    """构建面试开始/继续的消息"""
    info = INTERVIEW_TYPES.get(job_type, INTERVIEW_TYPES["general"])
    system = SYSTEM_START.format(
        interview_style=info["style"],
        job_type=info["name"],
        round_num=round_num,
    )
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": "我准备好了，请开始面试。"},
    ]


def build_evaluate_message(history):
    """构建面试评价的消息"""
    messages = [{"role": "system", "content": SYSTEM_EVALUATE}]
    messages.append({
        "role": "user",
        "content": "以下是刚才的面试记录，请据此生成评价报告：\n\n" + history,
    })
    return messages
