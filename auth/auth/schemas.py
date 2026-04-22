from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    
class UserRead(BaseModel):
    id: int
    email: EmailStr
    is_active: bool
    is_verified: bool
    
    model_config = {
        "from_attributes": True
    }

class Token(BaseModel):
    access_token: str
    token_type: str