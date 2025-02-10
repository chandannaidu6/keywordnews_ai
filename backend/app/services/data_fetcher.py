import requests
import logging
from fastapi import HTTPException
from app.utils.config import get_news_api_key
from functools import lru_cache

logger = logging.getLogger(__name__)

@lru_cache(maxsize=128)
def fetch_news(keyword):
    api_key = get_news_api_key()
    url = 'https://newsapi.org/v2/everything'
    params = {
        'q': keyword,
        'apiKey': api_key,
        'language': 'en',
        'pageSize': 10  # Optional: Adjust as needed
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raises HTTPError for bad responses (4xx or 5xx)
    except requests.exceptions.HTTPError as e:
        if response.status_code == 429:
            logger.error("NewsAPI rate limit exceeded: %s", e)
            raise HTTPException(status_code=429, detail="NewsAPI rate limit exceeded. Please try again later.")
        else:
            logger.error("Error fetching news articles: %s", e)
            raise HTTPException(status_code=503, detail="NewsAPI service unavailable.")
    except requests.exceptions.RequestException as e:
        logger.error("Error fetching news articles: %s", e)
        raise HTTPException(status_code=503, detail="NewsAPI service unavailable.")

    try:
        articles = response.json().get('articles', [])
    except ValueError:
        logger.error("Invalid JSON response from NewsAPI.")
        raise HTTPException(status_code=503, detail="Invalid response from NewsAPI.")

    news_data = []

    for article in articles:
        news_info = {
            'title': article.get('title', ''),
            'content': article.get('description', ''),
            'url': article.get('url', ''),
            'source': article.get('source', {}).get('name', 'NEWSAPI')
        }
        news_data.append(news_info)

    return news_data
