from fastapi import FastAPI
from .routers import search

app = FastAPI(
    title = "Keyword News Summarizer",
    description = "Fetches and summarizes news based on key words",
    version="1.0.0"
)

app.include_router(search.router)