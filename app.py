"""职途星 — AI 大学生就业助手"""

from flask import Flask, render_template, request, jsonify, Response, session
from flask_limiter import Limiter
from config import SECRET_KEY, DEBUG
from utils.deepseek import chat, chat_stream
from prompts.resume import build_messages as resume_build
from prompts.interview import (
    build_start_message,
    build_evaluate_message,
    INTERVIEW_TYPES,
)
from prompts.career import build_messages as career_build, PRESET_QUESTIONS
import json

app = Flask(__name__)
app.secret_key = SECRET_KEY


# 获取真实客户端 IP（穿透代理/负载均衡）
def get_real_ip():
    forwarded = request.headers.get("X-Forwarded-For", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.remote_addr or "127.0.0.1"


# 请求频率限制（防刷 API 额度）
limiter = Limiter(
    get_real_ip,
    app=app,
    default_limits=["30 per minute"],  # 全局默认
    storage_uri="memory://",
)


@app.errorhandler(429)
def ratelimit_error(e):
    return jsonify({"error": "请求太频繁，请稍后再试"}), 429


# ═══════════════ 页面路由 ═══════════════

@app.route("/")
def index():
    """首页"""
    return render_template("index.html")


@app.route("/resume")
def resume_page():
    """简历优化页"""
    return render_template("resume.html")


@app.route("/interview")
def interview_page():
    """AI 模拟面试页"""
    return render_template("interview.html", types=INTERVIEW_TYPES)


@app.route("/career")
def career_page():
    """职业规划问答页"""
    return render_template("career.html", presets=PRESET_QUESTIONS)


# ═══════════════ API 路由 ═══════════════

@app.route("/api/resume/analyze", methods=["POST"])
@limiter.limit("3 per minute")
def api_resume_analyze():
    """简历优化 API"""
    data = request.get_json()
    resume_text = data.get("content", "").strip()
    target_job = data.get("target_job", "").strip()

    if not resume_text:
        return jsonify({"error": "请输入简历内容"}), 400
    if len(resume_text) < 50:
        return jsonify({"error": "简历内容太短，请至少输入 50 个字"}), 400

    messages = resume_build(resume_text, target_job)
    result = chat(messages, temperature=0.6)
    return jsonify({"result": result})


@app.route("/api/interview/start", methods=["POST"])
@limiter.limit("3 per minute")
def api_interview_start():
    """面试开始 API"""
    data = request.get_json()
    job_type = data.get("job_type", "general")

    if job_type not in INTERVIEW_TYPES:
        return jsonify({"error": "无效的岗位类型"}), 400

    # 初始化会话状态
    session["interview_job"] = job_type
    session["interview_round"] = 1
    session["interview_history"] = []

    messages = build_start_message(job_type, round_num=1)
    result = chat(messages, temperature=0.8)

    # 保存 AI 的问题到历史
    session["interview_history"].append({"role": "ai", "content": result})
    session.modified = True

    return jsonify({
        "result": result,
        "round": 1,
        "job_name": INTERVIEW_TYPES[job_type]["name"],
    })


@app.route("/api/interview/answer", methods=["POST"])
@limiter.limit("10 per minute")
def api_interview_answer():
    """面试回答 API"""
    data = request.get_json()
    answer = data.get("answer", "").strip()

    job_type = session.get("interview_job", "general")
    round_num = session.get("interview_round", 1)
    history = session.get("interview_history", [])

    if not answer:
        return jsonify({"error": "请输入你的回答"}), 400

    # 保存用户回答
    history.append({"role": "user", "content": answer})

    if answer == "结束面试" or round_num >= 6:
        # 生成评价报告
        history_text = "\n".join([
            f"面试官: {h['content']}" if h["role"] == "ai"
            else f"候选人: {h['content']}"
            for h in history
        ])
        messages = build_evaluate_message(history_text)
        result = chat(messages, temperature=0.6)

        # 清理会话
        session.pop("interview_job", None)
        session.pop("interview_round", None)
        session.pop("interview_history", None)

        return jsonify({
            "result": result,
            "round": round_num,
            "finished": True,
        })

    # 继续面试
    round_num += 1
    session["interview_round"] = round_num

    # 构建上下文理解
    recent = history[-4:]  # 最近 2 轮
    context = "\n".join([
        f"{'面试官' if h['role'] == 'ai' else '候选人'}: {h['content']}"
        for h in recent
    ])

    followup_messages = [
        {
            "role": "system",
            "content": f"""你是一位经验丰富的面试官。

岗位类型：{INTERVIEW_TYPES[job_type]['name']}
当前是第 {round_num} 轮问答。

## 面试历史
{context}

请根据候选人上一轮的回答，提出第 {round_num} 个问题。规则：
1. 针对候选人回答中的细节进行追问
2. 只问一个问题
3. 如果这是第 5-6 轮，可以开始收尾，问候选人是否有问题要问你""",
        },
        {"role": "user", "content": "请提出下一个面试问题。"},
    ]

    result = chat(followup_messages, temperature=0.8)
    history.append({"role": "ai", "content": result})
    session["interview_history"] = history
    session.modified = True

    return jsonify({
        "result": result,
        "round": round_num,
        "finished": False,
    })


@app.route("/api/career/chat", methods=["POST"])
@limiter.limit("5 per minute")
def api_career_chat():
    """职业规划问答 API"""
    data = request.get_json()
    question = data.get("question", "").strip()
    history = data.get("history", [])

    if not question:
        return jsonify({"error": "请输入你的问题"}), 400

    messages = career_build(question, history)
    result = chat(messages, temperature=0.8, max_tokens=2048)
    return jsonify({"result": result})


@app.route("/api/career/chat/stream", methods=["POST"])
@limiter.limit("5 per minute")
def api_career_chat_stream():
    """职业规划问答 API（流式）"""
    data = request.get_json()
    question = data.get("question", "").strip()
    history = data.get("history", [])

    if not question:
        return jsonify({"error": "请输入你的问题"}), 400

    messages = career_build(question, history)

    def generate():
        for chunk in chat_stream(messages, temperature=0.8, max_tokens=2048):
            yield f"data: {json.dumps({'content': chunk})}\n\n"
        yield "data: [DONE]\n\n"

    return Response(generate(), mimetype="text/event-stream")


# ═══════════════ 启动入口 ═══════════════

if __name__ == "__main__":
    app.run(debug=DEBUG, host="0.0.0.0", port=5000)
