from fastapi import APIRouter,HTTPException
from ..models import SearchRequest,SearchResponse
from ..services.data_fetcher import fetch_news
from ..services.ai_agent import filter_and_summarize
import logging
router = APIRouter(
    prefix='/api',
    tags=['Search']
)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.post('/search',response_model=SearchResponse)
async def search_news(request:SearchRequest):
    keyword = request.keyword
    logger.info("Received request for keyword: %s", keyword)


    try:

        logger.info("Fetching news articles...")

        news_articles = fetch_news(keyword)
        logger.info("Fetched news articles: %s", news_articles)

        combined_content = news_articles
        logger.info("Running AI summarization...")

        articles = await filter_and_summarize(combined_content)
        logger.info("Summarization complete: %s", articles)

        response = SearchResponse(
            keyword=keyword,
            articles=articles
        )
        return response
    except HTTPException as http_exc:
        raise http_exc
    
    except Exception as e:
        logger.error("Error occurred: %s", e)

        raise HTTPException(status_code = 500,detail=str(e))
