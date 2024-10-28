from pydantic import BaseModel
from typing import List

class SearchRequest(BaseModel):
    keyword:str

class Article(BaseModel):
    title:str
    summary:str
    url:str
    source:str

class SearchResponse(BaseModel):
    keyword:str
    articles:List[Article]