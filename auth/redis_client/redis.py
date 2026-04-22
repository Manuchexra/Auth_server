import json
from typing import Optional, Any
from redis.asyncio import Redis, from_url
from core.config import config

class RedisClient:
    def __init__(self):
        self.redis: Optional[Redis] = None

    # Redisga ulanish.
    async def connect(self):
        self.redis = await from_url(
            config.REDIS_URL,
            encoding = "utf-8",
            decode_responses = True
        )

    # Redisga ulanishni yopish.
    async def disconnect(self):
        if self.redis:
            await self.redis.close()

    # Kalit - qiymat saqlash. expire: sekundlarda (Agar berilmasa, cheksiz)
    async def set(self, key:str, value: Any, expire: int = None) -> bool:
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        else:
            value = str(value)
        result = await self.redis.set(key, value, ex= expire)
        return result is True
    
    # Qiymatni olish
    async def get(self, key: str) -> Optional[str]:
        return await self.redis.get(key)
    
    # JSON qiymatni olish
    async def get_json(self, key: str) -> Optional[dict]:
        data = await self.redis.get(key)
        if data:
            return json.loads(data)
        return None
    
    # Kalitni o'chirish
    async def delete(self, key:str) -> int:
        return await self.redis.delete(key)
    
    # Kalit mavjudligini tekshirish
    async def exists(self, key:str) -> bool:
        return await self.redis.exists(key) > 0
    
    # Kalit muddatini o'zgartirish
    async def expire(self, key: str, seconds: int) -> bool:
        return await self.redis.expire(key, seconds)
    
    # Refresh token saqlash
    async def set_refresh_token(self, user_id: int, refresh_token: str, expire_days: int =7) -> bool:
        key = f"refresh_token:{user_id}"
        refresh_tokenn= f"Refresh token: {refresh_token} "
        expire_seconds = expire_days * 24 * 60 * 60
        return await self.set(key,refresh_tokenn, expire=expire_seconds)

    # Refresh tokenni olish
    async def get_refresh_token(self, user_id: int) -> Optional[str]:
        key = f"refresh_token:{user_id}"
        return await self.get(key)

    # Refresh token o'chirish (logout)
    async def delete_refresh_token(self, user_id: int) -> int:
        key = f"refresh_token:{user_id}"
        return await self.delete(key)
    

redis_client = RedisClient()