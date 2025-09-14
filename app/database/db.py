from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import DeclarativeBase

from config import DB_PORT, DB_HOST, DB_NAME, DB_PASS, DB_USER

SQLALCHEMY_DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}?async_fallback=True"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL
)

class Base(DeclarativeBase):
    pass

async def create_tables():
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

async def delete_tables():
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)

