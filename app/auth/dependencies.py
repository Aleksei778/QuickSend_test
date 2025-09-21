from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from fastapi_cache.decorator import cache
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from database.session import get_db
from database.models import UserOrm
from auth.jwt_auth import verify_token

security = HTTPBearer()


@cache(expire=3600, namespace="user_info")
async def get_user_from_db(
    user_id: str, user_email: str, db: AsyncSession = Depends(get_db)
):
    stmt = select(UserOrm).where(
        (UserOrm.id == user_id) & (UserOrm.email == user_email)
    )
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


async def get_current_user(
    credentials: HTTPBearer = Depends(security), db: AsyncSession = Depends(get_db)
):
    try:
        if not credentials or not credentials.credentials:
            raise HTTPException(status_code=401, detail="No credentials provided")

        payload = await verify_token(token=credentials.credentials)
        user_info = payload.get("user_info")
        user_id = user_info.get("id")
        user_email = user_info.get("email")

        if not user_id or not user_email:
            raise HTTPException(
                status_code=401, detail="No authentication information provided"
            )

        print(user_info)

        user = await get_user_from_db(user_id, user_email, db)

        return user

    except Exception as e:
        raise HTTPException(status_code=401, detail="Auth error")
