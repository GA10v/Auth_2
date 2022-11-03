import aioredis

from core.config import settings

redis: aioredis.Redis = aioredis.from_url(settings.redis.url, max_connections=20, decode_responses=True)
