import time
import json
import threading
from collections import defaultdict

try:
    import redis
except ImportError:
    redis = None

import asyncio

class HyperDict:

    def __init__(self, use_redis=False, redis_config=None):
        self.store = {}
        self.ttl = {}
        self.versions_map = defaultdict(list)
        self.lock = threading.Lock()
        self.use_redis = use_redis and redis is not None

        if self.use_redis:
            self.redis = redis.Redis(**(redis_config or {}))
        else:
            self.redis = None

    def _serialize_key(self, key):
        return json.dumps(list(key)) if isinstance(key, tuple) else (
            json.dumps(key, sort_keys=True) if isinstance(key, (list, dict)) else str(key)
        )

    def _try_load_json(self, k):
        try:
            val = json.loads(k)
            return tuple(val) if isinstance(val, list) else val
        except Exception:
            return k

    def _is_expired(self, key):
        return key in self.ttl and time.time() > self.ttl[key]

    def set(self, key, value, ttl=None):
        key_s = self._serialize_key(key)
        now = time.time()

        with self.lock:
            self.store[key_s] = value
            self.versions_map[key_s].append((now, value))
            if ttl:
                self.ttl[key_s] = now + ttl

        if self.use_redis:
            try:
                self.redis.set(name=key_s, value=json.dumps(value), ex=ttl)
            except Exception as e:
                print(f"[Redis Error - set] {e}")

    def get(self, key, version=None):
        key_s = self._serialize_key(key)

        if self.use_redis:
            try:
                val = self.redis.get(key_s)
                if val:
                    return json.loads(val)
            except Exception as e:
                print(f"[Redis Error - get] {e}")

        with self.lock:
            if self._is_expired(key_s):
                self.store.pop(key_s, None)
                return None

            if version is not None:
                versions = self.versions_map.get(key_s, [])
                for ts, val in reversed(versions):
                    if ts <= version:
                        return val
                return None

            return self.store.get(key_s)

    def __setitem__(self, key, value):
        self.set(key, value)

    def __getitem__(self, key):
        val = self.get(key)
        if val is None:
            raise KeyError(key)
        return val

    def __delitem__(self, key):
        self.delete(key)

    def filter(self, predicate):
        with self.lock:
            return {
                self._try_load_json(k): v
                for k, v in self.store.items()
                if not self._is_expired(k) and predicate(self._try_load_json(k), v)
            }

    def versions(self, key):
        key_s = self._serialize_key(key)
        return self.versions_map.get(key_s, [])

    def delete(self, key):
        key_s = self._serialize_key(key)
        with self.lock:
            self.store.pop(key_s, None)
            self.ttl.pop(key_s, None)
            self.versions_map.pop(key_s, None)
        if self.use_redis:
            try:
                self.redis.delete(key_s)
            except Exception as e:
                print(f"[Redis Error - delete] {e}")

    def keys(self):
        with self.lock:
            return [self._try_load_json(k) for k in self.store.keys() if not self._is_expired(k)]

    def items(self):
        with self.lock:
            return [
                (self._try_load_json(k), v)
                for k, v in self.store.items()
                if not self._is_expired(k)
            ]

    def __contains__(self, key):
        return self.get(key) is not None

    async def aset(self, key, value, ttl=None):
        return await asyncio.to_thread(self.set, key, value, ttl)

    async def aget(self, key, version=None):
        return await asyncio.to_thread(self.get, key, version)

    async def afilter(self, predicate):
        return await asyncio.to_thread(self.filter, predicate)

    def clear(self):
        with self.lock:
            self.store.clear()
            self.ttl.clear()
            self.versions_map.clear()
        if self.use_redis:
            try:
                self.redis.flushdb()
            except Exception as e:
                print(f"[Redis Error - flushdb] {e}")
