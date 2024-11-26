from typing import Any, TypeVar
import json
from collections.abc import Callable

import redis.asyncio as redis
from redis import RedisError

from .json_encoder import CustomJSONEncoder
from .logger import logger

T = TypeVar("T", bound=Callable[..., Any])


class RedisBackend:
    def __init__(self, url: str):
        self.redis_client: redis.Redis = redis.from_url(url=url, decode_responses=True)

    async def get(self, key: str) -> Any:
        return await self.redis_client.get(key)

    async def set(self, key: str, value: Any, expire_time: int | None = None) -> None:
        if expire_time:
            await self.redis_client.setex(key, expire_time, value)
        else:
            await self.redis_client.set(key, value)

    async def delete(self, key: str) -> None:
        await self.redis_client.delete(key)

    async def close(self) -> None:
        await self.redis_client.close()


class RedisDBManager:
    def __init__(self) -> None:
        self._backend: RedisBackend | None = None

    @property
    def backend(self) -> RedisBackend:
        if self._backend is None:
            raise RuntimeError("Cache backend is not initialized.")
        return self._backend

    def init(self, backend: RedisBackend) -> None:
        self._backend = backend

    async def get(self, key: str) -> Any:
        try:
            data = await self.backend.get(key)

            if data is None:
                logger.warning("No data found for key: %s", key)
                return False

            return json.loads(data)
        except json.decoder.JSONDecodeError as e:
            logger.error("Error decoding JSON: %s", e)
            return data
        except RedisError as err:
            logger.error("Cannot get cache data: %s", str(err))
            return False

    async def set(self, key: str, value: Any, ttl: int | None = None) -> bool:
        try:
            await self.backend.set(key, json.dumps(value, cls=CustomJSONEncoder), ttl)
        except RedisError as err:
            logger.error("Cannot set cache data: %s", str(err))
            return False
        return True

    async def delete(self, key: str) -> bool:
        try:
            await self.backend.delete(key)
        except RedisError as err:
            logger.error("Cannot delete cache data: %s", str(err))
            return False
        return True

    async def close(self) -> None:
        try:
            await self.backend.close()
        except RedisError as err:
            logger.error("Cannot close cache: %s", str(err))


DbManager = RedisDBManager()
