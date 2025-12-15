import pickle
from typing import Any

import redis
from loguru import logger

from server.config import CACHE_REDIS_URL, CACHE_TTL_SECONDS, USE_CACHE
from server.lib.utils import safe_hash
from server.models.data import Data
from server.models.file import File


class CacheManager:
    """
    The unified library for managing caches for intermediate results of nodes.
    Can be used by nodes or to accelerate the data processing.
    If you want to get a full view of the cache of a project, please use the SnapshotManager.
    """

    def __init__(self) -> None:
        self.redis_client = redis.Redis.from_url(
            CACHE_REDIS_URL, decode_responses=False
        )

    @staticmethod
    def _get_cache_key(node_type: str, params: dict[str, Any], inputs: dict[str, Data]) -> str:
        """Generate a unique cache key based on node ID, parameters, and inputs."""
        # 1. hash params
        param_hash = safe_hash(params)
        # 2. hash inputs
        input_hash = safe_hash(inputs)
        # 3. combine all
        signature = safe_hash(param_hash + input_hash)
        return f"cache:{node_type}:{signature}"

    def _add_cache_hit_num(self) -> None:
        """Increment the cache hit counter for the project."""
        hit_key = "cache_stat:hit"
        self.redis_client.incr(hit_key)
        total_key = "cache_stat:total"
        self.redis_client.incr(total_key)
        # print to log every 10 requests
        total = self.redis_client.get(total_key)
        hit = self.redis_client.get(hit_key)
        if total is not None and hit is not None:
            assert isinstance(total, bytes) and isinstance(hit, bytes)
            if int(total) % 10 == 0:
                hit_rate = int(hit) / int(total)
                logger.info(f"cache_stat:hit_rate: {hit_rate:.2%}")

    def _add_cache_miss_num(self) -> None:
        """Increment the cache miss counter for the project."""
        total_key = "cache_stat:total"
        self.redis_client.incr(total_key)
        # print to log every 10 requests
        hit_key = "cache_stat:hit"
        total = self.redis_client.get(total_key)
        hit = self.redis_client.get(hit_key)
        if total is not None and hit is not None:
            assert isinstance(total, bytes) and isinstance(hit, bytes)
            if int(total) % 10 == 0:
                hit_rate = int(hit) / int(total)
                logger.info(f"[cache] hit_rate: {hit_rate:.2%}")
        

    def get(self, node_type: str, params: dict[str, Any], inputs: dict[str, Data]) -> tuple[dict[str, Data], float] | None:
        """Get cached result for a node with given parameters and inputs. Return None if not found."""
        if not USE_CACHE:
            return None
        cache_key = CacheManager._get_cache_key(node_type, params, inputs)
        cached_value = self.redis_client.get(cache_key)
        if cached_value is not None:
            self._add_cache_hit_num()
            try:
                # Use pickle to deserialize efficiently
                assert isinstance(cached_value, bytes)
                cache_data = pickle.loads(cached_value)
                outputs, running_time = cache_data
                return outputs, running_time
            except Exception as e:
                logger.warning(f"Failed to load cache for {cache_key}: {e}")
                return None

        self._add_cache_miss_num()
        return None

    def set(self, node_type: str, params: dict[str, Any], inputs: dict[str, Data], outputs: dict[str, Data], running_time: float) -> None:
        """Set cached result for a node with given parameters and inputs."""
        if not USE_CACHE:
            return

        # Check if any output is a File, if so, skip caching
        for key, data in outputs.items():
            if isinstance(data.payload, File):
                # do not cache the file content in memory
                return

        cache_key = CacheManager._get_cache_key(node_type, params, inputs)

        # Directly pickle the outputs (dict[str, Data])
        # Data objects and Pandas DataFrames are picklable and much faster than JSON conversion
        cache_value = (outputs, running_time)
        try:
            self.redis_client.set(cache_key, pickle.dumps(cache_value))
            self.redis_client.expire(cache_key, CACHE_TTL_SECONDS)
        except Exception as e:
            logger.warning(f"Failed to set cache for {cache_key}: {e}")
