from typing import List, Dict, Any

from fastapi import Depends, HTTPException
from starlette.requests import Request
from token_throttler import TokenBucket, TokenThrottlerAsync, TokenThrottlerException
from token_throttler.storage.redis import RedisStorageAsync
from auth.auth_models import User
from auth.base_config import unverified_user
from redis import asyncio as aioredis


def get_user_id(verified_user: User = Depends(unverified_user)) -> str:
    """
    Get user's id as string
    :return: str
    """
    return str(verified_user.id)


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
            rate_authenticated: int = 10,
            time_authenticated: int = 10,
            rate_unauthenticated: int = 3,
            time_unauthenticated: int = 20,

    ):
        """
        :param rate_authenticated: how many requests authenticated user can make
        :param time_authenticated: how much time(seconds) needs to rest if authenticated user exceeded number of allowed
         requests
        :param rate_unauthenticated: how many requests unauthenticated user can make
        :param time_unauthenticated: how much time(seconds) needs to rest if unauthenticated user exceeded number of
         allowed requests
        """

        self.rate_authenticated = rate_authenticated
        self.rate_unauthenticated = rate_unauthenticated
        self.time_authenticated = time_authenticated
        self.time_unauthenticated = time_unauthenticated
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
        self.throttler: TokenThrottlerAsync = TokenThrottlerAsync(
            1, RedisStorageAsync(redis=redis, delimiter="||"))

    async def __call__(self, request: Request, unknown_user: User = Depends(unverified_user)) -> None:
        """Limits number of user's requests whether user authenticated or not
          :returns: None"""
        try:
            throttler = self.throttler
            ip_address = request.client.host

            # Limit unauthenticated user by ip address
            if not unknown_user or not unknown_user.is_verified:

                # Check whether any buckets exist if not add new one
                if await throttler.get_all_buckets(identifier=f"{ip_address}") is None:
                    await throttler.add_from_dict(identifier=f"{ip_address}",
                                                  bucket_config=self.bucket_config_unauthenticated,
                                                  remove_old_buckets=False)
                    # await throttler.add_bucket(identifier=f"{ip_address}",
                    #                            bucket=TokenBucket(replenish_time=self.time_unauthenticated,
                    #                                               max_tokens=self.rate_unauthenticated))
                # Consume bucket if it is possible
                if not await throttler.consume(identifier=f"{ip_address}"):
                    raise HTTPException(status_code=429, detail={"message": "You've reached the limit!"})
                # await throttler.enable(identifier=f"{ip_address}")

            else:
                # Limit unauthenticated user by user_id
                user_id = get_user_id(unknown_user)

                if await throttler.get_all_buckets(identifier=f"{user_id}") is None:
                    # Check whether any buckets exist if not add new one
                    await throttler.remove_all_buckets(identifier=f"{ip_address}")
                    await throttler.add_from_dict(identifier=f"{user_id}",
                                                  bucket_config=self.bucket_config_authenticated,
                                                  remove_old_buckets=False)
                    # await throttler.add_bucket(identifier=f"{user_id}",
                    #                            bucket=TokenBucket(replenish_time=self.time_authenticated,
                    #                                               max_tokens=self.rate_authenticated))

                # Consume bucket if it is possible
                if not await throttler.consume(identifier=f"{user_id}"):
                    raise HTTPException(status_code=429, detail={"message": "You've reached the limit!"})
                # await throttler.enable(identifier=f"{user_id}")

        except TokenThrottlerException:
            raise HTTPException(status_code=429, detail="You've reached the limit!")
