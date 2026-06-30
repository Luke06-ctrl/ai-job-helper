"""DeepSeek API 调用封装"""

import base64
from openai import OpenAI
from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL

client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url=DEEPSEEK_BASE_URL,
)


def chat(messages, temperature=0.7, max_tokens=4096):
    """通用对话接口"""
    try:
        response = client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"[错误] API 调用失败: {str(e)}"


def chat_stream(messages, temperature=0.7, max_tokens=4096):
    """流式对话接口，返回生成器"""
    try:
        response = client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )
        for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    except Exception as e:
        yield f"[错误] API 调用失败: {str(e)}"


def ocr_image(image_base64, mime_type="image/png"):
    """使用 DeepSeek 多模态能力识别图片中的文字（OCR）"""
    try:
        response = client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "你是一个专业的 OCR 文字识别工具。请精确识别并提取图片中的所有文字内容，保持原有的段落结构和换行。只输出识别到的文字，不要添加任何解释。",
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{image_base64}"
                            },
                        },
                        {
                            "type": "text",
                            "text": "请提取这张图片中的所有文字。",
                        },
                    ],
                },
            ],
            temperature=0.1,
            max_tokens=4096,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"[OCR错误] {str(e)}"
