from typing import List, Dict, Any

from fastapi import Depends, HTTPException
from starlette.requests import Request
from token_throttler import TokenThrottlerAsync, TokenThrottlerException
from token_throttler.storage.redis import RedisStorageAsync
from auth.auth_models import User
from auth.base_config import unverified_user
from redis import asyncio as aioredis

from utilties.error_code import ErrorCode


# async def monitor_server_load():
#     while True:
#         # Monitor the server's CPU and memory usage
#         cpu_usage = psutil.cpu_percent() * 10
#         cpu_usage = abs(cpu_usage - 100)
#         memory_usage = psutil.virtual_memory().percent
#         virtual_memory = psutil.virtual_memory().available
#         virtual_memory = virtual_memory / (1024 ** 3)
#         print(cpu_usage)
#         print(virtual_memory)
#         # Estimate the maximum number of requests the server can handle per second
#         max_requests_per_second = int(0.8 * (psutil.cpu_count() or 1) * cpu_usage / 100 + 0.2
#                                       * virtual_memory)
#
#         print(max_requests_per_second)
#
#         # Check the sever load every 5 seconds
#         await asyncio.sleep(5)

class BucketLimiter:
    def __init__(
            self,
            rate_authenticated: int = 3,
            time_authenticated: int = 10,
            rate_unauthenticated: int = 2,
            time_unauthenticated: int = 20,
            consuming_coefficient: int = 1,
    ):
        """
        :param rate_authenticated: how many requests authenticated user can make
        :param time_authenticated: how much time(seconds) needs to rest if authenticated user exceed number of allowed
         requests
        :param rate_unauthenticated: how many requests unauthenticated user can make
        :param time_unauthenticated: how much time(seconds) needs to rest if unauthenticated user exceed number of
         allowed requests
        :param consuming_coefficient: how many tokens does our limiter consume in every request
        """

        self.rate_authenticated = rate_authenticated
        self.rate_unauthenticated = rate_unauthenticated
        self.time_authenticated = time_authenticated
        self.time_unauthenticated = time_unauthenticated
        self.consuming_coefficient = consuming_coefficient
        self.bucket_config_authenticated: List[Dict[str, Any]] = [
            {
                "replenish_time": time_authenticated,
                "max_tokens": rate_authenticated,
            },
        ]
        self.bucket_config_unauthenticated: List[Dict[str, Any]] = [
            {
                "replenish_time": time_unauthenticated,
                "max_tokens": rate_unauthenticated,
            },
        ]

        # Add redis as data storage for our buckets
        redis = aioredis.from_url("redis://localhost:6379", max_connections=100)
        redis_storage = RedisStorageAsync(redis=redis, delimiter="||")
        self.throttler: TokenThrottlerAsync = TokenThrottlerAsync(
            1, redis_storage)

    @staticmethod
    def _get_user_id(
            user_get: User = Depends(unverified_user)
    ) -> str:
        """
        Get user's id as string
        :returns: str
        """
        return str(user_get.id)

    async def _get_dependency_index(
            self,
            request: Request
    ) -> int:
        """Get dependency index for current request"""
        dependency_index: int = 0
        for route in request.app.routes:
            if route.path == request.scope["path"] and request.method in route.methods:
                for j, dependency in enumerate(route.dependencies):
                    if self is dependency.dependency:
                        dependency_index = j
                        break

        return dependency_index

    async def _consume(
            self,
            identifier: str,
            coefficient: int = 1
    ) -> None:
        """Consuming tokens once by default if it is available and raise exception if not"""
        for count in range(coefficient):
            if not await self.throttler.consume(identifier=identifier):
                raise TokenThrottlerException

    async def _manage_buckets(self, identifier: str, bucket_config: List[Dict[str, Any]]) -> None:
        """Consume tokens as it's possible and add buckets if it wasn't added before"""
        if await self.throttler.get_all_buckets(identifier=identifier) is None:
            # Check whether any buckets exist if not add new one
            await self.throttler.add_from_dict(identifier=identifier,
                                               bucket_config=bucket_config,
                                               remove_old_buckets=False)

        # Consume tokens if it is possible with entered coefficient
        await self._consume(identifier=identifier, coefficient=self.consuming_coefficient)

    async def __call__(
            self,
            request: Request,
            unknown_user: User = Depends(unverified_user)
    ) -> None:
        """Limits number of user's requests whether user authenticated or not
          :returns: None"""
        try:
            throttler = self.throttler
            dependency_index = await self._get_dependency_index(request=request)
            ip_address = request.client.host
            print(throttler._storage.buckets.items())

            # Limit unauthenticated user by ip address
            if not unknown_user or not unknown_user.is_verified:
                identifier = f"{ip_address}:{dependency_index}"
                print(identifier)

                await self._manage_buckets(identifier=identifier, bucket_config=self.bucket_config_unauthenticated)

            else:
                # Limit unauthenticated user by user_id
                user_id = self._get_user_id(user_get=unknown_user)
                identifier = f"{user_id}:{dependency_index}"
                print(identifier)

                await self._manage_buckets(identifier=identifier, bucket_config=self.bucket_config_authenticated)

        except TokenThrottlerException:
            raise HTTPException(status_code=429, detail=ErrorCode.TOO_MANY_REQUESTS)
