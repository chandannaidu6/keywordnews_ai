from pydantic import BaseModel, EmailStr
from typing import List, Optional

class Article(BaseModel):
    title: str
    summary: str
    url: str
    source: str

class SearchRequest(BaseModel):
    keyword: str

class SearchResponse(BaseModel):
    keyword: str
    articles: List[Article]

# Authentication models
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserLogin(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    name: Optional[str] = None
    image: Optional[str] = None

    class Config:
        from_attributes = True

class OAuthUserInput(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    image: Optional[str] = None
