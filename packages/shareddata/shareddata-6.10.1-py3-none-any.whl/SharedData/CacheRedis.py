import pandas as pd
import numpy as np
import time
import os
import queue
from redis.cluster import RedisCluster, ClusterNode
from typing import Set, Dict
import bson
import asyncio

from SharedData.Database import DATABASE_PKEYS

class CacheRedis:
    def __init__(self, database, period, source, tablename, user='master', use_async_queue: bool = False):
        """Initialize RedisCluster connection."""
        self.database = database
        self.period = period
        self.source = source
        self.tablename = tablename
        self.user = user

        self.path = f'{user}/{database}/{period}/{source}/cache/{tablename}'
        self.data = {}        
        self.use_async_queue = use_async_queue
        self.queue = asyncio.Queue() if use_async_queue else queue.Queue()
        self.counter = np.int64(0)
        self.consumer_counter = np.int64(0)
        self.pkeycolumns = DATABASE_PKEYS[database]

        if not 'REDIS_CLUSTER_NODES' in os.environ:
            raise Exception('REDIS_CLUSTER_NODES not defined')
        startup_nodes = []
        for node in os.environ['REDIS_CLUSTER_NODES'].split(','):
            startup_nodes.append(ClusterNode(node.split(':')[0], int(node.split(':')[1])))        
        self.redis = RedisCluster(startup_nodes=startup_nodes, decode_responses=False)

    def __getitem__(self, pkey):        
        if isinstance(pkey, str):
            if len(self.pkeycolumns) > 1:
                raise ValueError(f'Primary key must be a tuple of length {len(self.pkeycolumns)}')            
        _bson = self.redis.get(self.get_hash(pkey))
        if _bson is None:
            return {}
        value = bson.BSON.decode(_bson)        
        self.data[pkey] = value
        return value
    
    def get(self, pkey):        
        return self.__getitem__(pkey)
    
    def __setitem__(self, pkey, value):
        # check if all primary keys are in the pkey
        if isinstance(pkey, tuple):
            if len(pkey) != len(self.pkeycolumns):
                raise ValueError(f'Primary key must be a tuple of length {len(self.pkeycolumns)}')
        elif isinstance(pkey, str):
            if len(self.pkeycolumns) > 1:
                raise ValueError(f'Primary key must be a tuple for multi-key tables')
        # load the current value if it is not in the data
        if not pkey in self.data:
            self.data[pkey] = self.__getitem__(pkey)
            if self.data[pkey] == {}:
                self.data[pkey] = value
                if self.use_async_queue:
                    # Non-blocking, in async context user should await this
                    asyncio.create_task(self.queue.put(pkey))
                else:
                    self.queue.put(pkey)
                return                
        
        if not 'mtime' in value:
            value['mtime'] = time.time_ns()

        if value['mtime']>=self.data[pkey]['mtime']:
            # update the current value
            self.data[pkey].update(value)
            # signal that the value has been updated
            if self.use_async_queue:
                asyncio.create_task(self.queue.put(pkey))
            else:
                self.queue.put(pkey)
        
    def set(self, value):        
        pkey = tuple(value[pk] for pk in self.pkeycolumns)
        self.__setitem__(pkey, value)
        _bson = bson.BSON.encode(self.data[pkey])
        self.redis.set(self.get_hash(pkey), _bson)
        
    def flush(self, block=False, timeout=None):
        """Flush the queue to Redis."""
        flush_pkeys: Set[str] = set()
        if self.queue.empty():
            return 0
        symbol = self.queue.get(block=block, timeout=timeout)
        flush_pkeys.add(symbol)
        while not self.queue.empty():
            symbol = self.queue.get(block=block, timeout=timeout)
            flush_pkeys.add(symbol)
        
        with self.pipeline() as pipe:
            for pkey in flush_pkeys:
                msg = self.data[pkey]
                rhash = self.get_hash(pkey)
                pipe.set(rhash, msg)
            pipe.execute()
        
        return len(flush_pkeys)    
    
    async def async_flush(self) -> int:
        """Flush the queue to Redis asynchronously."""
        if not self.use_async_queue:
            raise ValueError('use_async_queue must be True to use async_flush')
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

        return len(flush_pkeys)
    
    async def run_stream_cache_tasks(self, stream, offset='latest', groupid=None) -> None:
        """
        Helper to launch both async_consume_stream_task and async_flush_task and wait for them.
        Simplifies consumer loop to a one-liner.
        """
        worker_task = asyncio.create_task(self.async_consume_stream_task(stream, offset=offset, groupid=groupid))
        consumer_task = asyncio.create_task(self.async_flush_task())
        await asyncio.gather(worker_task, consumer_task)

    async def async_consume_stream_task(self, stream, offset='latest', groupid=None):
        if groupid is None:
            groupid = self.path
        await stream.async_subscribe(offset=offset, groupid=groupid)
        # last_count = 0
        # last_print = time.time()
        while True:
            msgs = await stream.async_poll(timeout=1.0, groupid=groupid)  
            
            # if time.time() - last_print > 5:
            #     msgs_per_sec = (stream.counter - last_count) / (time.time() - last_print)
            #     last_count = stream.counter
            #     last_print = time.time()
            #     now = pd.Timestamp.utcnow()
            #     print(f'{pd.Timestamp(stream.mtime, unit="ns")},{now}, Messages processed: {stream.counter}, {msgs_per_sec:.2f} msgs/sec', flush=True)
          
            if not msgs:
                continue
            for msg in msgs:
                pkey = tuple(msg[pk] for pk in self.pkeycolumns)
                self[pkey] = msg
                self.consumer_counter += 1

    async def async_flush_task(self):
        """
        Asynchronously consume upsert tasks from cache.queue and push the latest
        symbol data to Redis Cluster. Uses pipeline for batch efficiency.
        Prints write throughput in symbols/sec.
        """        
        while True:
            nupsert = await self.async_flush()
            self.counter += nupsert

    def load(self):
        """Load all data from Redis into a dictionary."""    
        self.datastore = True    
        for key in self.redis.scan_iter(f"{self.path}:*"):
            pkeys = key.decode('utf-8').split(':')[-1].split(',')
            if len(pkeys) == len(self.pkeycolumns):                
                if len(pkeys) == 1:
                    self.data[pkeys[0]] = self.__getitem__(pkeys[0])
                else:
                    self.data[tuple(pkeys)] = self.__getitem__(tuple(pkeys))
            else:
                self.redis.delete(key)
        return self.data
    
    def clear(self):
        """Clear all data from Redis for this path."""
        self.redis.delete(*self.redis.scan_iter(f"{self.path}:*"))
    
    def pipeline(self):
        """Return a pipeline proxy that BSON-encodes set values."""
        return PipelineProxy(self.redis.pipeline())
    
    def async_pipeline(self):
        """Return an async pipeline proxy that BSON-encodes set values."""
        return AsyncPipelineProxy(self.redis.pipeline())
    
    def get_hash(self, pkey):
        if isinstance(pkey, tuple):
            pkey = ','.join(pkey)
        return f"{self.path}:{pkey}"

    def __iter__(self):
        for key in self.list_keys():
            yield key
        
    def list_keys(self):
        return [s.decode().split(':')[1] for s in list(self.redis.scan_iter(f"{self.path}:*"))]        

    

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
