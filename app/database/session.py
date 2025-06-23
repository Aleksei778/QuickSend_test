from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from contextlib import asynccontextmanager

from .db import engine

SessionLocal = async_sessionmaker(autocommit = False, autoflush=False, bind=engine, class_=AsyncSession)

async def get_db():
    db: AsyncSession = SessionLocal()
    try:
        yield db
    finally:
        await db.close()

@asynccontextmanager
async def get_db2():
    db: AsyncSession = SessionLocal()
    try:
        yield db
    finally:
        await db.close() 