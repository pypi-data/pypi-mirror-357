import pandas as pd
import numpy as np
import time
import os
import queue
from redis import Redis
from redis.cluster import RedisCluster, ClusterNode
from typing import Set, Dict
import bson
import asyncio

from datetime import datetime, timezone

from SharedData.Logger import Logger
from SharedData.Database import DATABASE_PKEYS

class CacheRedis:
    def __init__(self, database, period, source, tablename, user='master'):
        """Initialize RedisCluster connection."""
        self.database = database
        self.period = period
        self.source = source
        self.tablename = tablename
        self.user = user

        self.path = f'{user}/{database}/{period}/{source}/cache/{tablename}'
        self.data = {}                
        self.queue = asyncio.Queue()
        self._flush_task = None
        self.set_counter = np.uint64(0)
        self.pkeycolumns = DATABASE_PKEYS[database]
        self.mtime = datetime(1970,1,1, tzinfo=timezone.utc)

        if not 'REDIS_CLUSTER_NODES' in os.environ:
            raise Exception('REDIS_CLUSTER_NODES not defined')
        startup_nodes = []
        for node in os.environ['REDIS_CLUSTER_NODES'].split(','):
            startup_nodes.append(ClusterNode(node.split(':')[0], int(node.split(':')[1])))
        if len(startup_nodes)>1:
            self.redis = RedisCluster(startup_nodes=startup_nodes, decode_responses=False)
        else:
            node = startup_nodes[0]
            host, port = node.split(':')[0], int(node.split(':')[1])
            self.redis = Redis(host=host, port=port, decode_responses=False)

        if not self.header_get('cache->set_counter'):
            self.header_set('cache->set_counter', 0)

    def __getitem__(self, pkey):
        if not isinstance(pkey, str):
            raise Exception('pkey must be a string')
        if '#' in pkey:
            raise Exception('pkey cannot contain #')
        _bson = self.redis.get(self.get_hash(pkey))
        if _bson is None:
            return {}
        value = bson.BSON.decode(_bson)        
        self.data[pkey] = value
        return value
    
    def get(self, pkey):        
        return self.__getitem__(pkey)
    
    def mget(self, pkeys: list[str]) -> list[dict]:
        """
        Retrieve multiple entries from Redis in a single call.

        :param pkeys: List of primary keys (as strings)
        :return: List of decoded dicts (empty dict if missing)
        """
        redis_keys = [self.get_hash(pkey) for pkey in pkeys]
        vals = self.redis.mget(redis_keys)
        result = []
        for pkey, _bson in zip(pkeys, vals):
            if _bson is None:
                result.append({})
            else:
                value = bson.BSON.decode(_bson)
                self.data[pkey] = value
                result.append(value)
        return result

    def get_pkey(self, value):
        key_parts = [
            str(value[col])
            for col in self.pkeycolumns
            if col in ['symbol','portfolio','tag']
        ]        
        return ','.join(key_parts)

    def get_hash(self, pkey: str) -> str:
        """
        Return the full Redis key for a given pkey, using a hash tag for cluster slot affinity.
        All keys with the same path will map to the same slot.
        """
        return f"{{{self.path}}}:{pkey}"

    def __setitem__(self, pkey, new_value):
        # load the current value if it is not in the data
        if not pkey in self.data:
            cached_value = self.__getitem__(pkey)
            if cached_value:
                self.data[pkey] = cached_value
            else:
                self.data[pkey] = new_value
        # update the current value
        if not 'mtime' in new_value:
            new_value['mtime'] = datetime.now(timezone.utc)
            
        if isinstance(self.data[pkey]['mtime'], (int, np.integer)):
            self.data[pkey]['mtime'] = datetime.fromtimestamp(self.data[pkey]['mtime'] / 1e9, timezone.utc).replace(tzinfo=None)
        if isinstance(new_value['mtime'], (int, np.integer)):
            new_value['mtime'] = datetime.fromtimestamp(new_value['mtime'] / 1e9, timezone.utc).replace(tzinfo=None)

        if new_value['mtime'].replace(tzinfo=None)>=self.mtime.replace(tzinfo=None):
            self.mtime = new_value['mtime']
        if new_value['mtime'].replace(tzinfo=None)>=self.data[pkey]['mtime'].replace(tzinfo=None):
            # update the mtime            
            self.data[pkey] = self.recursive_update(self.data[pkey],new_value)                            
    
    def recursive_update(self, original, updates):
        """
        Recursively update the original dictionary with updates from the new dictionary,
        preserving unmentioned fields at each level of depth.
        """
        for key, value in updates.items():
            if isinstance(value, dict):
                # Get existing nested dictionary or use an empty dict if not present
                original_value = original.get(key, {})
                if isinstance(original_value, dict):
                    # Merge recursively
                    original[key] = self.recursive_update(original_value, value)
                else:
                    # Directly assign if original is not a dict
                    original[key] = value
            else:
                # Non-dict values are directly overwritten
                original[key] = value
        return original

    def set(self, new_value, pkey=None):
        if pkey is None:
            pkey = self.get_pkey(new_value)
        self.__setitem__(pkey, new_value)
        _bson = bson.BSON.encode(self.data[pkey])
        self.redis.set(self.get_hash(pkey), _bson)

    def header_incrby(self, field, value):
        self.redis.incrby(f"{{{self.path}}}#{field}",value)

    def header_set(self, field, value):
        self.redis.set(f"{{{self.path}}}#{field}",value)
    
    def header_get(self, field):
        return self.redis.get(f"{{{self.path}}}#{field}")

    def header_list(self):
        return self.redis.keys(f"{{{self.path}}}#*")

    async def set_async(self, new_value, pkey=None):
        """
        Asynchronously set a message in the cache and signal the queue.

        Raises:
            Exception: 
        """        
        if self._flush_task is None or self._flush_task.done():
            raise Exception("Queue consumer (flush task) is not running. Call 'await cache.start()' first.")
        if pkey is None:
            pkey = self.get_pkey(new_value)
        self.__setitem__(pkey, new_value)
        await self.queue.put(pkey)
            
    async def async_flush_loop(self, conflate_ms=100) -> None:
        """Flush the queue to Redis asynchronously."""        
        try:
            while True:
                flush_pkeys: Set[str] = set()
                symbol = await self.queue.get()
                flush_pkeys.add(symbol)
                while not self.queue.empty():
                    symbol = await self.queue.get()
                    flush_pkeys.add(symbol)
                async with self.async_pipeline() as pipe:
                    for pkey in flush_pkeys:
                        msg = self.data[pkey]
                        rhash = self.get_hash(pkey)
                        await pipe.set(rhash, msg)
                    await pipe.execute()
                self.set_counter += len(flush_pkeys)
                self.header_incrby("cache->set_counter", len(flush_pkeys))
                await asyncio.sleep(conflate_ms / 1000)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            # Optionally log the exception
            Logger.log.error(f"async_flush_loop error: {e}")
    
    async def start(self):
        """
        Start the background async_flush_loop task.
        Should be called once, from a running event loop.
        """
        if (self._flush_task is None or self._flush_task.done()):
            self._flush_task = asyncio.create_task(self.async_flush_loop())
            await asyncio.sleep(0)  # Yield control to allow the task to start

    def load(self) -> dict:
        """Load all data from Redis into the cache dictionary using mget for efficiency."""
        self.datastore = True
        pkeys = self.list_keys('*')
        self.mget(pkeys)        
        return self.data
    
    def clear(self):
        """Clear all data from Redis for this path."""
        self.redis.delete(*self.redis.scan_iter(f"{{{self.path}}}:*"))
    
    def pipeline(self):
        """Return a pipeline proxy that BSON-encodes set values."""
        return PipelineProxy(self.redis.pipeline())
    
    def async_pipeline(self):
        """Return an async pipeline proxy that BSON-encodes set values."""
        return AsyncPipelineProxy(self.redis.pipeline())
    
    def __iter__(self):
        for key in self.list_keys():
            yield key
        
    def list_keys(self, keyword: str = '*') -> list[str]:
        """List all keys matching the keyword, returning the key part after the first colon."""
        result = []
        for s in self.redis.scan_iter(f"{{{self.path}}}:{keyword}"):
            decoded = s.decode()
            if ':' in decoded:
                result.append(decoded.split(':', 1)[1])
        return result

class PipelineProxy:
    """Proxy for Redis pipeline to auto-BSON encode values on set."""
    def __init__(self, pipe):
        self._pipe = pipe

    def set(self, key, value):
        """Intercept set to BSON-encode value."""
        return self._pipe.set(key, bson.BSON.encode(value))
    
    def __getattr__(self, attr):
        # Delegate other attributes/methods to the pipeline
        return getattr(self._pipe, attr)

class AsyncPipelineProxy:
    """Proxy for async Redis pipeline to auto-BSON encode values on set."""

    def __init__(self, pipe):
        self._pipe = pipe

    def __enter__(self):
        self._pipe.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self._pipe.__exit__(exc_type, exc_val, exc_tb)

    async def __aenter__(self):
        self._pipe.__enter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return self._pipe.__exit__(exc_type, exc_val, exc_tb)
    
    async def set(self, key, value):
        """Intercept async set to BSON-encode value."""
        return self._pipe.set(key, bson.BSON.encode(value))

    async def execute(self):
        """Execute the pipeline asynchronously."""
        return self._pipe.execute()
