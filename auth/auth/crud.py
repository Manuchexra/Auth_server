from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from auth.model import User
from auth.schemas import UserCreate
from core.security import get_password_hash

async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()

async def get_user_by_id(db: AsyncSession, user_id: int) -> User:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()

async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        email = user_data.email,
        hashed_password = hashed_password,
        is_active = False
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def activate_user(db: AsyncSession, user: User) -> User:
    user.is_active = True
    await db.commit()
    await db.refresh(user)
    return user

async def update_user_password(db: AsyncSession, user: User, new_password: str) ->User:
    user.hashed_password = get_password_hash(new_password)
    await db.commit()
    await db.refresh(user)
    return user

async def verify_user_email(db: AsyncSession, user: User) -> User:
    user.is_verified = True
    await db.commit()
    await db.refresh(user)
    return user

