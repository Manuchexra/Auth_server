from contextlib import asynccontextmanager
from fastapi import FastAPI
from db.session import engine
from db.base import Base
from auth.router import router as auth_router
from redis_client.redis import redis_client

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ishga tushirish
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await redis_client.connect()
    yield
    # To'xtatish
    await engine.dispose()
    await redis_client.disconnect()

app = FastAPI(title="Auth API", lifespan=lifespan)
app.include_router(auth_router)

@app.get("/")
async def root():
    return {"message": "Auth server is running"}