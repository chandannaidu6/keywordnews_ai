from pydantic import BaseModel
from typing import List

class Article(BaseModel):
    title:str
    summary:str
    url:str
    source:str

class SearchRequest(BaseModel):
    keyword:str

class SearchResponse(BaseModel):
    keyword:str
    articles:List[Article]

