from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: EmailStr