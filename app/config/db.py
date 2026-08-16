import os
from collections.abc import AsyncGenerator
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine
)
from sqlalchemy.orm import DeclarativeBase

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
)

print(DATABASE_URL)

engine = create_async_engine(
    DATABASE_URL,
    echo= True,
)

AsyncSessionLocal = async_sessionmaker(
    class_=AsyncSession,
    bind=engine,
    expire_on_commit=False,
    autoflush=False,
)

class Base(DeclarativeBase):
    pass

async def get_db() -> AsyncGenerator[AsyncSession, None]:

    async with AsyncSessionLocal() as session:
        try:
            yield session

        except Exception as e:
            await session.rollback()
            raise