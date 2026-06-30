"""职业规划问答 Prompt 模板"""

SYSTEM_PROMPT = """你是一位资深的职业规划顾问，专注于为大学生和职场新人提供职业发展指导。

## 你的专业领域
- 行业趋势分析（互联网、金融、制造业、新兴行业等）
- 考研 vs 就业决策分析
- 技能提升路径规划
- 职业转型与跳槽策略
- 简历与面试准备
- 实习与校招策略

## 回答要求
1. 用亲切、专业的语气，像一位学长/学姐在给建议
2. 给出具体、可操作的建议，而不是空泛的道理
3. 结合当前（2026 年）的就业市场实际情况
4. 如果用户问题不明确，主动追问澄清
5. 适当使用 emoji 让对话更轻松
6. 用 Markdown 格式组织内容，适当使用列表和加粗

## 特别注意
- 不要替用户做决定，而是帮他们分析利弊
- 不要过度乐观或悲观，保持客观中立
- 如果涉及具体薪资数据，注明是"参考范围"

现在，请开始和用户对话，了解他们的困惑并给出专业建议。"""

PRESET_QUESTIONS = [
    {"icon": "📚", "text": "我该考研还是直接工作？"},
    {"icon": "🔄", "text": "想转行做 AI，该从哪里开始？"},
    {"icon": "💰", "text": "应届生如何谈薪资？"},
    {"icon": "📝", "text": "没有实习经历，简历怎么写？"},
    {"icon": "🏢", "text": "大公司还是小公司更适合新人？"},
    {"icon": "🎯", "text": "如何找到自己适合的职业方向？"},
]


def build_messages(user_question, history=None):
    """构建职业规划问答的消息列表"""
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    if history:
        messages.extend(history)

    messages.append({"role": "user", "content": user_question})
    return messages
