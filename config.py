import os
from pathlib import Path
from dotenv import load_dotenv

# 确保加载项目根目录的 .env
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

# DeepSeek API 配置
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "your-api-key-here")
DEEPSEEK_BASE_URL = "https://api.deepseek.com"

# 模型选择
DEEPSEEK_MODEL = "deepseek-chat"

# Flask 配置
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
DEBUG = os.getenv("FLASK_DEBUG", "true").lower() == "true"
