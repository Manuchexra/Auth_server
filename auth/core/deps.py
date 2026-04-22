from fastapi import Request, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError
from auth.crud import get_user_by_id
from core.security import decode_token
from db.session import get_db

# get_current_user – bu autentifikatsiya qilingan foydalanuvchini olishning standart usuli.
async def get_current_user(request: Request, db: AsyncSession = Depends(get_db)):
   
    #1. Cookie dan access_token ni olish
    token = request.cookies.get("access_token")
    
    #2. Agar cookie'da bo'lmasa Not authenticated qaytarsin
    if not token:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Not authenticated")
    
    try:
        payload = decode_token(token)
        user_id = int(payload.get("sub"))
        if user_id is None:
            raise HTTPException(status_code =401, detail = "Invalid token")
    except JWTError:
        raise HTTPException(status_code = 401, detail = "Invalid token")
    
    user = await get_user_by_id(db, user_id)
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail = "User not found or inactive")
    return user
        