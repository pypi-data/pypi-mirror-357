"""
Cache utilities - Generic caching functions that can be used across projects
"""

import hashlib
import json
from typing import Callable, Any, Optional, Union
from fastapi.encoders import jsonable_encoder
from bson.objectid import ObjectId

# Import core utilities
from ..core.data import normalize
from ..core.serialization import datetime_serializer


def generate_cache_id(params: dict) -> str:
    """
    Utility to generate a cache key hash from a dictionary.
    Creates a consistent hash based on normalized dictionary content.
    """
    normalized = normalize(params)
    encoded_data = jsonable_encoder(normalized, custom_encoder={ObjectId: str})
    serialized = json.dumps(encoded_data, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def get_or_set_cache(
    redis_client,
    cache_key: str,
    fetch_func: Callable,
    clear_cache: Union[str, bool] = False,
    ttl: Optional[int] = None,
    serializer: Optional[Callable] = None,
) -> Any:
    """
    Retrieve data from cache if available, otherwise fetch, cache, and return it.
    Optionally clear cache before fetching.
    
    Args:
        redis_client: Redis client instance
        cache_key: Key to use for caching
        fetch_func: Function to call if cache miss
        clear_cache: Pattern to clear or boolean to clear specific key
        ttl: Time to live in seconds
        serializer: Function to serialize data before caching
    """
    if clear_cache:
        invalidate_cache_keys(
            redis_client,
            clear_cache if isinstance(clear_cache, str) else cache_key
        )
    
    if redis_client.exists(cache_key):
        return json.loads(redis_client.get(cache_key))
    
    data = fetch_func()
    if serializer:
        data = serializer(data)
    
    encoded_data = jsonable_encoder(data, custom_encoder={ObjectId: str})
    redis_client.set(cache_key, json.dumps(encoded_data), ex=ttl)
    return encoded_data


def invalidate_cache_keys(redis_client, pattern: str) -> int:
    """
    Utility to invalidate cache keys matching a pattern.
    
    Args:
        redis_client: Redis client instance
        pattern: Pattern to match keys for deletion
        
    Returns:
        Number of keys deleted
    """
    cursor = 0
    batch_size = 1000
    total_deleted = 0

    while True:
        cursor, keys = redis_client.scan(cursor=cursor, match=pattern, count=batch_size)
        if keys:
            redis_client.unlink(*keys)
            total_deleted += len(keys)
        if cursor == 0:
            break

    return total_deleted 