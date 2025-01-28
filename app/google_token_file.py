# google_auth.py

import time
import httpx
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
from .database.models import UserOrm, TokenOrm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException
from datetime import datetime, timedelta


# Обновление access_token с использованием refresh_token
from datetime import datetime, timedelta
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy import update

async def refresh_access_token(token: TokenOrm, db: AsyncSession):
    if not token or not token.refresh_token:
        raise Exception("Refresh token is missing")
        
    try:
        print('НЕТ ОШИБКИ ПЕРВЫЙ  1')
        # Make the request to Google OAuth
        async with httpx.AsyncClient() as client:
            response = await client.post(
                'https://accounts.google.com/o/oauth2/token',
                data={
                    'grant_type': 'refresh_token',
                    'refresh_token': token.refresh_token,
                    'client_id': GOOGLE_CLIENT_ID,
                    'client_secret': GOOGLE_CLIENT_SECRET,
                }
            )
            response.raise_for_status()  # Raise exception for bad status codes
            new_token_data = response.json()

        print('НЕТ ОШИБКИ ВТОРОЙ  2')    
        # Update token in database using SQLAlchemy async pattern
        stmt = (
            update(TokenOrm)
            .where(TokenOrm.id == token.id)
            .values(
                access_token=new_token_data['access_token'],
                expires_in=new_token_data['expires_in'],
                expires_at=datetime.now() + timedelta(seconds=new_token_data['expires_in'])
            )
        )
        print('НЕТ ОШИБКИ ТРЕТИЙ  3')
        await db.execute(stmt)
        print('НЕТ ОШИБКИ ЧЕТВЕРТЫЙ  4')
        await db.commit()
        print('НЕТ ОШИБКИ ПЯТЫЙ  5')
        return new_token_data['access_token']
        
    except httpx.HTTPError as e:
        await db.rollback()
        raise Exception(f"Failed to refresh token: {str(e)}")
    except Exception as e:
        await db.rollback()
        raise Exception(f"Unexpected error while refreshing token: {str(e)}")

# Проверка истечения токена
def is_token_expired(token: TokenOrm):
    print(token.expires_at)
    return datetime.now() >= token.expires_at 

# Получение Gmail сервиса
async def get_gmail_service(user: UserOrm, db: AsyncSession):
    print('get_gmail_service')
    # Извлекаем токен OAuth из объекта пользователя
    # Выполняем асинхронный запрос для получения токена пользователя
    stmt = select(TokenOrm).where(TokenOrm.user_id == user.id)
    print('НЕТ ОШИБКИ')
    result = await db.execute(stmt)
    token = result.scalar_one_or_none()

    if not token:
        raise HTTPException(status_code=404, detail="Токен не найден.")

    print('token')
    # Проверяем, не истек ли токен, и обновляем при необходимости
    if is_token_expired(token):
        print('token has expired')
        await refresh_access_token(token, db)

        await db.refresh(token)
        await db.flush()

    print(token.access_token)
    print('НЕТ ОШИБКИ ПОСЛЕ refresh')
    # Создаем объект Credentials для работы с Gmail API
    creds = Credentials(
        token=token.access_token,
        refresh_token=token.refresh_token,
        token_uri='https://accounts.google.com/o/oauth2/token',
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        scopes=['https://www.googleapis.com/auth/gmail.send']
    )
    print('НЕТ ОШИБКИ ПОСЛЕ creds')

    return build('gmail', 'v1', credentials=creds)

# Получение GoogleSheets сервиса
async def get_sheets_service(user: UserOrm, db: AsyncSession):
    print('get sheets service')
    # Извлекаем токен OAuth из объекта пользователя
    # Выполняем асинхронный запрос для получения токена пользователя
    stmt = select(TokenOrm).where(TokenOrm.user_id == user.id)
    result = await db.execute(stmt)
    token = result.scalar_one_or_none()

    if not token:
        raise HTTPException(status_code=404, detail="Токен не найден.")

    print('token')
    # Проверяем, не истек ли токен, и обновляем при необходимости
    if is_token_expired(token):
        print('token has expired')
        await refresh_access_token(token, db)

    # Создаем объект Credentials для работы с Gmail API
    creds = Credentials(
        token=token.access_token,
        refresh_token=token.refresh_token,
        token_uri='https://accounts.google.com/o/oauth2/token',
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
    )

    return build('sheets', 'v4', credentials=creds)