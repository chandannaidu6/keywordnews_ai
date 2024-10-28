import tweepy
import requests
from app.utils.config  import get_twitter_api_key,get_news_api_key

def fetch_tweets(keyword):
    api_key = get_twitter_api_key()
    client = tweepy.Client(bearer_token=api_key)
    query = f'{keyword} -is:retweet lang:en'
    tweets = client.search_recent_tweets(query=query,max_results=10,tweet_fields=['text','id'])
    tweet_data = []

    if tweets.data:
        for tweet in tweets.data:
            tweet_info = {
                'title':'',
                'content':tweet.text,
                'url':f"https://twitter.com/i/web/status/{tweet.id}",
                'source':'Twitter'


            }
            tweet_data.append(tweet_info)

        return tweet_data
    
def fetch_news(keyword):
    api_key = get_news_api_key()
    url = {
        'https://newsapi.org/v2/everything?'
        f'q={keyword}&apiKey={api_key}'

    }
    response = requests.get(url)
    articles = response.json().get('articles',[])
    news_data = []

    for article in articles:
        news_info = {
            'title':article.get('title',''),
            'content':article.get('description',''),
            'url':article.get('url',''),
            'source':article.get('source',{}).get('name','NEWSAPI')

        }
        news_data.append(news_info)

    return news_data
