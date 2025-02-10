from pydantic import BaseModel,EmailStr
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

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password:str

class UserLogin(UserBase):
    password:str

class UserResponse(UserBase):
    id:int

    class Config:
        orm_mode = True