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

    def __init__(self, project_id: int) -> None:
        self.project_id = project_id
        self.redis_client = redis.Redis.from_url(CACHE_REDIS_URL, decode_responses=True)

    @staticmethod
    def _get_cache_key(project_id: int, node_id: str, params: dict[str, Any], inputs: dict[str, Data]) -> str:
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
        return f"cache:proj_{project_id}:{node_id}:{signature}"

    def get(self, node_id: str, params: dict[str, Any], inputs: dict[str, Data]) -> dict[str, Data] | None:
        """Get cached result for a node with given parameters and inputs. Return None if not found."""
        cache_key = CacheManager._get_cache_key(self.project_id, node_id, params, inputs)

        cached_value = self.redis_client.get(cache_key)
        if cached_value is not None:
            assert isinstance(cached_value, str)
            cache_value = json.loads(cached_value)
            result: dict[str, Data] = {}
            for key, data_dict in cache_value.items():
                result[key] = Data.from_view(DataView.from_dict(data_dict))
            return result
        return None
    
    def set(self, node_id: str, params: dict[str, Any], inputs: dict[str, Data], outputs: dict[str, Data]) -> None:
        """Set cached result for a node with given parameters and inputs."""
        cache_key = CacheManager._get_cache_key(self.project_id, node_id, params, inputs)
        cache_value: dict[str, dict[str, Any]] = {}
        for key, data in outputs.items():
            cache_value[key] = data.to_view().to_dict()
        self.redis_client.set(cache_key, json.dumps(cache_value))
        self.redis_client.expire(cache_key, CACHE_TTL_SECONDS)
