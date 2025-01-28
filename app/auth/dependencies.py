from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from .jwt_auth import verify_token
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database.session import get_db
from database.models import UserOrm
from fastapi_cache.decorator import cache

security = HTTPBearer()

@cache(expire=3600, namespace="user_info")
async def get_user_from_db(user_id: str, user_email: str, db: AsyncSession = Depends(get_db)):
    stmt = select(UserOrm).where(
        (UserOrm.id == user_id) & (UserOrm.email == user_email)
    )
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    return user

async def get_current_user(
        credentials: HTTPBearer = Depends(security),
        db: AsyncSession = Depends(get_db)
    ):
    print(credentials)
    try:
        # Проверяем наличие credentials
        if not credentials or not credentials.credentials:
            raise HTTPException(
                status_code=401, 
                detail="Отсутствуют данные аутентификации"
            )

        # Проверяем токен и получаем payload
        payload = await verify_token(token=credentials.credentials)
        
        # Получаем информацию о пользователе из правильной структуры payload
        user_info = payload.get("user_info")

        user_id = user_info.get("id")
        user_email = user_info.get("email")

        if not user_id or not user_email:
            raise HTTPException(
                status_code=401, 
                detail="Неверные данные в токене"
            )
        
        print(user_info)

        # Получаем пользователя из базы данных
        user = await get_user_from_db(user_id, user_email, db)
        
        # Добавляем отладочную информацию
        print(f"Успешная аутентификация для пользователя {user_email}")
        
        return user

    except Exception as e:
        # Логируем ошибку для отладки
        print(f"Ошибка аутентификации: {str(e)}")
        raise HTTPException(
            status_code=401, 
            detail="Ошибка аутентификации"
        )