from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from sqlalchemy.future import select
from fastapi import HTTPException
from datetime import datetime, timedelta
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update

from config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
from database.models import UserOrm, TokenOrm

# Обновление access_token с использованием refresh_token
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

def is_token_expired(token: TokenOrm):
    return datetime.now() >= token.expires_at 

async def get_gmail_service(user: UserOrm, db: AsyncSession):
    stmt = select(TokenOrm).where(TokenOrm.user_id == user.id)
    result = await db.execute(stmt)
    token = result.scalar_one_or_none()

    if not token:
        raise HTTPException(
            status_code=404,
            detail="Token has not found"
        )

    if is_token_expired(token):
        await refresh_access_token(token, db)

        await db.refresh(token)
        await db.flush()

    creds = Credentials(
        token=token.access_token,
        refresh_token=token.refresh_token,
        token_uri='https://accounts.google.com/o/oauth2/token',
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        scopes=['https://www.googleapis.com/auth/gmail.send']
    )

    return build('gmail', 'v1', credentials=creds)

async def get_sheets_service(user: UserOrm, db: AsyncSession):
    stmt = select(TokenOrm).where(TokenOrm.user_id == user.id)
    result = await db.execute(stmt)
    token = result.scalar_one_or_none()

    if not token:
        raise HTTPException(status_code=404, detail="Токен не найден.")

    if is_token_expired(token):
        print('token has expired')
        await refresh_access_token(token, db)

    creds = Credentials(
        token=token.access_token,
        refresh_token=token.refresh_token,
        token_uri='https://accounts.google.com/o/oauth2/token',
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
    )

    return build('sheets', 'v4', credentials=creds)