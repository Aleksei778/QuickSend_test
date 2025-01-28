from datetime import timedelta, datetime
from jose import jwt, JWTError
from config import (
    JWT_ACCESS_SECRET_FOR_AUTH, 
    JWT_ALGORITHM, 
    JWT_REFRESH_SECRET_FOR_AUTH
)
from fastapi import HTTPException
from typing import Optional, Dict, Any
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from sqlalchemy.future import select
from database.models import UserOrm
from database.db_manager import DBManager
from database.session import get_db

# Коснтанты для токенов
ACCESS_TOKEN_EXPIRES_MINUTES = 60
REFRESH_TOKEN_EXPIRES_DAYS = 60

class TokenError(Exception):
    pass

class JWTHandler:
    def __init__(self):
        self.access_secret = JWT_ACCESS_SECRET_FOR_AUTH
        self.refresh_secret = JWT_REFRESH_SECRET_FOR_AUTH
        self.algorithm = JWT_ALGORITHM

    async def create_access_token(self, data: Dict[str, Any]) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRES_MINUTES)
        to_encode.update({
            "exp": expire, 
            "type": "access"
        })
        
        try:
            encoded_jwt = jwt.encode(
                to_encode,
                self.access_secret,
                algorithm=self.algorithm
            )
            return encoded_jwt
        except Exception as e:
            raise TokenError(f"Error creating access token: {str(e)}")

    async def create_refresh_token(self, data: Dict[str, Any]) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRES_MINUTES)
        to_encode.update({
            "exp": expire, 
            "type": "refresh"
        })
        
        try:
            encoded_jwt = jwt.encode(
                to_encode,
                self.refresh_secret,
                algorithm=self.algorithm
            )
            return encoded_jwt
        except Exception as e:
            raise TokenError(f"Error creating refresh token: {str(e)}")

    async def verify_token(
        self,
        token: str,
        token_type: str = "access"
    ) -> Dict[str, Any]:
        try:
            print("PAYLOAD")
            print("token", token)
            secret = (
                self.access_secret
                if token_type == "access"
                else self.refresh_secret
            )
            print(secret)

            payload = jwt.decode(
                token,
                secret,
                algorithms=[self.algorithm]
            )
            print(payload)
            # Проверяем тип токена
            if payload.get("type") != token_type:
                print("not type")
                raise TokenError("Invalid token type")
        
            # Проверям срок действия
            exp = payload.get("exp")
            if not exp or datetime.fromtimestamp(exp) < datetime.utcnow():
                raise TokenError("Token has expired")
            
            return payload
        except JWTError as jwt_e:
            print("JWTERROR")
            credentials_exception = HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Could not validate credentials: {str(jwt_e)}",
                headers={"WWW-Authenticate": "Bearer"},
            )
            raise credentials_exception
        except TokenError as token_e:
            credentials_exception = HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(token_e),
                headers={"WWW-Authenticate": "Bearer"},
            )
            raise credentials_exception
        
    async def refresh_token(
        self,
        refresh_token: str,
        db: AsyncSession
    ) -> Dict[str, str]:
        try:
            db_manager = DBManager(session=db)
            print(refresh_token)

            # Проверяем refresh токен
            payload = await self.verify_token(refresh_token, "refresh")
            print("verify")
            print(payload)
            # Получаем данные пользователя
            user_data = payload.get("user_info")
            if not user_data:
                print("not user data")
                raise TokenError("Invalid token data")
            print(user_data)

            # Проверяем пользователя в БД
            user = await db_manager.get_user_by_email(user_data['email'])
            print(user.id)
            
            if not user:
                print("not user")
                raise TokenError("User not found")
            
            user_id = user.id
            user_name = user.first_name + " " + user.last_name
            user_email = user.email

            # Создаем новую информацию для токенов
            active_sub = await db_manager.get_active_sub(user_id=user_id)

            active_sub_dict = {"plan": "No active sub"}

            if active_sub:
                active_sub_dict["plan"] = active_sub.plan

            new_data = {
                "user_info": {
                    "id": user_id,
                    "name": user_name,
                    "email": user_email,
                },
                "subscription_info": {
                    **active_sub_dict
                }
            }

            # Создаем новую пару токенов
            new_access_token = await self.create_access_token(new_data)
            new_refresh_token = await self.create_refresh_token(new_data)
            token_type = "bearer"
            print("")
            return {
                "access_token": new_access_token,
                "refresh_token": new_refresh_token,
                "token_type": token_type
            }
        
        except (TokenError) as e:
            print(str(e))
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e),
                headers={"WWW-Authenticate": "Bearer"},
            )
        except Exception as e:
            print(str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error refreshing token: {str(e)}"
            )


# Создаем экземпляр обработчика JWT
jwt_handler = JWTHandler()

# Экспортируем функции для удобства использования
async def create_access_token(data: Dict[str, Any]) -> str:
    return await jwt_handler.create_access_token(data)

async def create_refresh_token(data: Dict[str, Any]) -> str:
    return await jwt_handler.create_refresh_token(data)

async def verify_token(token: str, token_type: str = "access") -> Dict[str, Any]:
    return await jwt_handler.verify_token(token, token_type)

async def refresh_jwt_token(refresh_token: str, db: AsyncSession) -> Dict[str, str]:
    return await jwt_handler.refresh_token(refresh_token, db)