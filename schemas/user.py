from pydantic import BaseModel , EmailStr
from uuid import UUID
from typing import Optional

class UserCreate(BaseModel):
    full_name:str
    email:EmailStr
    password:str
    role:str

class UserLogin(BaseModel):
    email:EmailStr
    password:str

class UserOut(BaseModel):
    id:UUID
    full_name:str
    email:EmailStr
    role:Optional[str] = "farmer"

class Token(BaseModel):
    refresh_token:str
    token_type:str

class TokenData(BaseModel):
    id:Optional[str] = None 