from fastapi import APIRouter,HTTPException
from app.models import SearchRequest,SearchResponse
from app.services.data_fetcher import fetch_tweets,fetch_news
from app.services.ai_agent import filter_and_summarize

router = APIRouter(
    prefix='/api',
    tags=['Search']
)

@router.post('/search',response_model=SearchResponse)
async def search_news(request:SearchRequest):
    keyword = request.keyword

    try:
        tweets = fetch_tweets(keyword)
        news_articles = fetch_news(keyword)

        combined_content = tweets+news_articles

        articles = filter_and_summarize(combined_content)

        response = SearchResponse(
            keyword=keyword,
            articles=articles
        )
        return response
    
    except Exception as e:
        raise HTTPException(status_code = 500,detail=str(e))
