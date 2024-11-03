import os
from dotenv import load_dotenv

load_dotenv()

def get_twitter_api_key():
    api_key = os.getenv("TWITTER_BEARER_TOKEN")
    if not api_key:
        raise ValueError("Twitter api not found")
    return api_key

def get_news_api_key():
    api_key = os.getenv("NEWSAPI_KEY")
    if not api_key:
        raise ValueError("news api not found")
    return api_key

def get_model_path():
    model_path = os.getenv("MODEL_PATH")
    if not model_path:
        raise ValueError("Model PAth not found")
    return model_path