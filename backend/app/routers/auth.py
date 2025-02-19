from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database.database import async_session
from app.models import UserCreate, UserLogin, UserResponse, OAuthUserInput
from app.database.user import User
from passlib.context import CryptContext
from typing import AsyncGenerator
import secrets

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(user: UserCreate, db: AsyncSession = Depends(get_db)):
    query = select(User).where(User.email == user.email)
    result = await db.execute(query)
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )
    hashed_password = pwd_context.hash(user.password)
    new_user = User(email=user.email, hashed_password=hashed_password)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

@router.post("/signin", response_model=UserResponse)
async def signin(user: UserLogin, db: AsyncSession = Depends(get_db)):
    query = select(User).where(User.email == user.email)
    result = await db.execute(query)
    existing_user = result.scalars().first()
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid credentials"
        )
    if not pwd_context.verify(user.password, existing_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid credentials"
        )
    return existing_user

@router.post("/oauth-signin", response_model=UserResponse)
async def oauth_signin(oauth_data: OAuthUserInput, db: AsyncSession = Depends(get_db)):
    query = select(User).where(User.email == oauth_data.email)
    result = await db.execute(query)
    existing_user = result.scalars().first()
    if existing_user:
        return existing_user

    # Create a new user with a dummy password.
    dummy_password = secrets.token_urlsafe(16)
    hashed_dummy_password = pwd_context.hash(dummy_password)
    new_user = User(
        email=oauth_data.email,
        hashed_password=hashed_dummy_password,
        name=oauth_data.name,
        image=oauth_data.image,
    )
    db.add(new_user)
    try:
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating OAuth user: {e}"
        )
    await db.refresh(new_user)
    return new_user