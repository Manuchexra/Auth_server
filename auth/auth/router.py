from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta
from auth import crud, schemas
from core.security import create_access_token, verify_password, decode_token
from core.config import config
from db.session import get_db
from redis_client.redis import redis_client
from core.deps import get_current_user
from auth.model import User
from utils.email import send_verify_email
from core.security import decode_token
from jose import JWTError


router = APIRouter(prefix="/auth", tags = ["authentication"])

#refresh token uchun kalit
def get_refresh_token_key(user_id: int) -> str:
    return f"refresh_token: {user_id}"

#cookie larga tokenlarni o'rnatish
def set_auth_cookie(response: Response, access_token: str, refresh_token: str):
    #qisqa muddat
    response.set_cookie(
        key = "access_token",
        value = access_token,
        httponly=True,
        secure=False, # developmentda False, productionda True (https)
        samesite= "lax",
        max_age= config.ACCESS_TOKEN_EXPIRE_MINUTES* 60,
        path = "/"
    )

    #uzoq muddat
    response.set_cookie(
        key = "refresh_token",
        value= refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=config.REFRESH_TOKEN_EXPIRE_DAYS*24*60*60,
        path= "/auth/refresh" #faqat refresh endpointiga yuboriladi
    )

def clear_auth_cookie(response: Response):
    response.delete_cookie("access_token",path = "/")
    response.delete_cookie("refresh_token", path = "/auth/refresh")


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=schemas.UserRead)
async def register(user_data: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    #email mavjudligini tekshirish
    existing_user = await crud.get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered")
    
    # Foydalanuvchini yaratish
    user = await crud.create_user(db, user_data)

    #Email tasdiqlash tokenni yaratish
    verify_token = create_access_token(
        subject=str(user.id),
        expires_delta= timedelta(days=1)
    )
    await send_verify_email(user.email, verify_token)
    return user

@router.post("/login", summary="Login")
async def login(response: Response, login_data: schemas.UserLogin, db: AsyncSession = Depends(get_db)):
    user = await crud.get_user_by_email(db, login_data.email)
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "Incorrect email or password")
    if not user.is_verified:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "Email not verified")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "Account disabled")
    
    access_token = create_access_token(subject= str(user.id))
    refresh_token = create_access_token(
        subject=str(user.id),
        expires_delta= timedelta(days = config.REFRESH_TOKEN_EXPIRE_DAYS)
    )
    #refresh tokenni redisga saqlaymiz
    print(f"DEBUG: user.id = {user.id}")
    print(f"DEBUG: refresh_token : {refresh_token[:50]}...")
    results = await redis_client.set_refresh_token(user.id, refresh_token, expire_days=config.REFRESH_TOKEN_EXPIRE_DAYS)
    print(results)
    #Cookie larga joylash
    set_auth_cookie(response, access_token, refresh_token)

    return {"message": "Login successful"}

@router.post("/logout")
async def logout(
    response: Response,
    request:Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    #Redisdan tokenni o'chirish
    await redis_client.delete_refresh_token(current_user.id)
    #Cookie larni tozalash
    clear_auth_cookie(response)
    return {"message": "logout successul"}


@router.post("/refresh")
async def refresh_access_token(
    response: Response,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    #refresh tokenni cookie dan olish
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail = "Refresh token missing")
    
    #tokenni dekod qilish
    try:
        payload = decode_token(refresh_token)
        user_id = int(payload.get("sub"))
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    #Redis da saqlangan refresh token bilan solishtirish
    stored_token = await redis_client.get_refresh_token(user_id)
    if not stored_token or stored_token != refresh_token:
        raise HTTPException(status_code=401, detail = "Refresh token invalid or expired")
    
    #Yangi access token yaratish
    new_access_token = create_access_token(subject=str(user_id))

    #Cookie ni yangilash (faqat access token)
    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=config.ACCESS_TOKEN_EXPIRE_MINUTES*60,
        path = "/"
    )
    return {"message": "Access token refreshed"}

@router.get("/me", response_model=schemas.UserRead)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/verify-email")
async def verify_email(
    token: str,
    db: AsyncSession = Depends(get_db),
):
    try:
        payload = decode_token(token)
        user_id = int(payload.get("sub"))
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    
    user = await crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.is_verified:
        raise HTTPException(status_code=400, detail="Email already verified")
    
    user = await crud.verify_user_email(db, user)
    user = await crud.activate_user(db, user)
    return {"message": "Email verified successfully"}

@app.delete("/delete_user")
async def delete_user(
    response: Response,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 1. Redisdan refresh tokenni o‘chirish
    await redis_client.delete_refresh_token(current_user.id)
    
    # 2. Cookie‘larni tozalash
    clear_auth_cookie(response)   # clear_auth_cookies funksiyasi router.py da mavjud
    
    # 3. Foydalanuvchini bazadan o‘chirish (agar kerak bo‘lsa)
    await db.delete(current_user)
    await db.commit()
    
    return {"message": "User and tokens deleted successfully"}