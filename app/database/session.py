import sys
import os

# Добавляем корневую директорию проекта в PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from .db import engine
from contextlib import asynccontextmanager

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