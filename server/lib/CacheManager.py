import redis
import os
from typing import Any
from server.models.data import Data, DataView
import hashlib
import json

CACHE_REDIS_URL = os.getenv("REDIS_URL", "") + "/2"
CACHE_TTL_SECONDS  = 60 * 60 # 1 hour

class CacheManager:
    """
    The unified library for managing caches for intermediate results of nodes.
    Can be used by nodes or to accelerate the data processing.
    If you want to get a full view of the cache of a project, please use the SnapshotManager.
    """

    def __init__(self) -> None:
        self.redis_client = redis.Redis.from_url(CACHE_REDIS_URL, decode_responses=True)

    @staticmethod
    def _get_cache_key(node_type: str, params: dict[str, Any], inputs: dict[str, Data]) -> str:
        """Generate a unique cache key based on node ID, parameters, and inputs."""
        # 1. hash params
        param_str = json.dumps(params, sort_keys=True)
        param_hash = hashlib.sha256(param_str.encode()).hexdigest()
        # 2. hash inputs
        input_hashes = []
        for port, data in sorted(inputs.items()):
            data_str = json.dumps(data.to_view().to_dict(), sort_keys=True)
            data_hash = hashlib.sha256(data_str.encode()).hexdigest()
            input_hashes.append(f"{port}:{data_hash}")
        input_hash = hashlib.sha256("||".join(input_hashes).encode()).hexdigest()
        # 3. combine all
        signature = hashlib.sha256(param_hash.encode() + input_hash.encode()).hexdigest()
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
            assert isinstance(total, str) and isinstance(hit, str)
            if int(total) % 10 == 0:
                hit_rate = int(hit) / int(total)
                print(f"cache_stat:hit_rate: {hit_rate:.2%}")

    def _add_cache_miss_num(self) -> None:
        """Increment the cache miss counter for the project."""
        miss_key = "cache_stat:miss"
        self.redis_client.incr(miss_key)
        total_key = "cache_stat:total"
        self.redis_client.incr(total_key)
        # print to log every 10 requests
        hit_key = "cache_stat:hit"
        total = self.redis_client.get(total_key)
        hit = self.redis_client.get(hit_key)
        if total is not None and hit is not None:
            assert isinstance(total, str) and isinstance(hit, str)
            if int(total) % 10 == 0:
                hit_rate = int(hit) / int(total)
                print(f"[cache] hit_rate: {hit_rate:.2%}")
        

    def get(self, node_type: str, params: dict[str, Any], inputs: dict[str, Data]) -> tuple[dict[str, Data], float] | None:
        """Get cached result for a node with given parameters and inputs. Return None if not found."""
        cache_key = CacheManager._get_cache_key(node_type, params, inputs)
        cached_value = self.redis_client.get(cache_key)
        if cached_value is not None:
            self._add_cache_hit_num()
            assert isinstance(cached_value, str)
            cache_data = json.loads(cached_value)
            outputs_dict = cache_data[0]
            running_time = cache_data[1]
            result: dict[str, Data] = {}
            for key, data_dict in outputs_dict.items():
                result[key] = Data.from_view(DataView.from_dict(data_dict))
            return result, running_time

        self._add_cache_miss_num()
        return None

    def set(self, node_type: str, params: dict[str, Any], inputs: dict[str, Data], outputs: dict[str, Data], running_time: float) -> None:
        """Set cached result for a node with given parameters and inputs."""
        cache_key = CacheManager._get_cache_key(node_type, params, inputs)
        outputs_dict = {}
        for key, data in outputs.items():
            outputs_dict[key] = data.to_view().to_dict()
        cache_value = [outputs_dict, running_time]
        self.redis_client.set(cache_key, json.dumps(cache_value))
        self.redis_client.expire(cache_key, CACHE_TTL_SECONDS)
