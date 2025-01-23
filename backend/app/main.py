from fastapi import FastAPI
from routers import search
from fastapi.middleware.cors import CORSMiddleware
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

app = FastAPI(
    title = "Keyword News Summarizer",
    description = "Fetches and summarizes news based on key words",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search.router)