from fastapi import FastAPI
from app.routers import search, auth
from fastapi.middleware.cors import CORSMiddleware
import os
from app.database.database import engine
from app.database.user import Base

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

app = FastAPI(
    title="Keyword News Summarizer",
    description="Fetches and summarizes news based on key words",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search.router)
app.include_router(auth.router, prefix="/api/auth")

@app.get("/")
async def read_root():
    return {"Message": "Welcome to the Keyword News Summarizer API"}

@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

