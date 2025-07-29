import numpy as np
import pandas as pd
import os
import time
import uuid
import threading
import bson
import lz4.frame
import asyncio
import queue

from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka import Consumer, KafkaError        
from confluent_kafka import Producer

from aiokafka import AIOKafkaProducer, AIOKafkaConsumer

from SharedData.Database import DATABASE_PKEYS
from SharedData.Logger import Logger

class StreamKafka:

    def __init__(
        self,
        database, period, source, tablename,
        user='master',
        bootstrap_servers=None,
        replication=None,
        partitions=None,
        retention_ms=None, 
        use_aiokafka=False,        
    ):
        self.user = user
        self.database = database
        self.period = period
        self.source = source
        self.tablename = tablename
        self.use_aiokafka = use_aiokafka
        self.topic = f'{user}/{database}/{period}/{source}/stream/{tablename}'.replace('/','-')

        self.mtime = None
        self.counter = np.int64(0)        

        if bootstrap_servers is None:
            bootstrap_servers = os.environ['KAFKA_BOOTSTRAP_SERVERS']
        self.bootstrap_servers = bootstrap_servers
        
        if replication is None:
            self.replication = int(os.environ['KAFKA_REPLICATION'])
        else:
            self.replication = replication
        
        if partitions is None:
            self.partitions = int(os.environ['KAFKA_PARTITIONS'])
        else:
            self.partitions = partitions

        if retention_ms is None:
            self.retention_ms = int(os.environ['KAFKA_RETENTION'])
        else:
            self.retention_ms = retention_ms

        self.lock = threading.Lock()
        self.pkeys = DATABASE_PKEYS[database]

        self._producer = None                
        self.consumer = {} # groupid: consumer

        admin = AdminClient({'bootstrap.servers': self.bootstrap_servers})
        # create topic if not exists
        if not self.topic in admin.list_topics().topics:
            new_topic = NewTopic(
                self.topic, 
                num_partitions=self.partitions, 
                replication_factor=self.replication,
                config={"retention.ms": str(self.retention_ms)} 
            )
            fs = admin.create_topics([new_topic])
            for topic, f in fs.items():
                try:
                    f.result()
                    time.sleep(2)
                    Logger.log.info(f"Topic {topic} created.")
                except Exception as e:
                    if not 'already exists' in str(e):
                        raise e
        else:
            #get number of partitions
            self.partitions = len(admin.list_topics(topic=self.topic).topics[self.topic].partitions)

    #
    # Producer sync (confluent) and async (aiokafka)
    #
    @property
    def producer(self):
        if self.use_aiokafka:
            raise RuntimeError("Use 'await get_async_producer()' in aiokafka mode.")
        with self.lock:
            if self._producer is None:                
                self._producer = Producer({'bootstrap.servers': self.bootstrap_servers})
            return self._producer

    async def get_async_producer(self):
        if not self.use_aiokafka:
            raise RuntimeError("This method is only available in aiokafka mode.")
        if self._producer is None:            
            self._producer = AIOKafkaProducer(
                bootstrap_servers=self.bootstrap_servers,                
            )            
            await self._producer.start()
        return self._producer

    #
    # Extend (produce) sync/async
    #
    def extend(self, data):
        if self.use_aiokafka:
            raise RuntimeError("Use 'await async_extend(...)' in aiokafka mode.")
        
        if isinstance(data, list):
            for msg in data:
                for pkey in self.pkeys:
                    if not pkey in msg:
                        raise Exception(f'extend(): Missing pkey {pkey} in {msg}')
                if not 'mtime' in msg:
                    msg['mtime'] = time.time_ns()
                message = lz4.frame.compress(bson.BSON.encode(msg))                
                self.producer.produce(self.topic, value=message)
        elif isinstance(data, dict):
            for pkey in self.pkeys:
                if not pkey in data:
                    raise Exception(f'extend(): Missing pkey {pkey} in {data}')
            if not 'mtime' in data:
                data['mtime'] = time.time_ns()            
            message = lz4.frame.compress(bson.BSON.encode(data))
            self.producer.produce(self.topic, value=message)
        else:
            raise Exception('extend(): Invalid data type')                
      
        # Wait up to 5 seconds
        result = self.producer.flush(timeout=5.0)
        if result > 0:
            raise Exception(f"Failed to flush {result} messages")
                
    async def async_extend(self, data):
        if not self.use_aiokafka:
            raise RuntimeError("Use 'extend()' in confluent_kafka mode.")
        
        producer = await self.get_async_producer()                            
        if isinstance(data, list):
            for msg in data:
                for pkey in self.pkeys:
                    if not pkey in msg:
                        raise Exception(f'extend(): Missing pkey {pkey} in {msg}')
                if not 'mtime' in msg:
                    msg['mtime'] = time.time_ns()
                message = lz4.frame.compress(bson.BSON.encode(msg))                
                await producer.send(self.topic, value=message)            
        elif isinstance(data, dict):
            for pkey in self.pkeys:
                if not pkey in data:
                    raise Exception(f'extend(): Missing pkey {pkey} in {data}')
            if not 'mtime' in data:
                data['mtime'] = time.time_ns()
            message = lz4.frame.compress(bson.BSON.encode(data))            
            await producer.send(self.topic, value=message)
        else:
            raise Exception('extend(): Invalid data type')
                    
    #
    # Flush/close producer
    #
    def flush(self, timeout=5.0):
        if self.use_aiokafka:
            raise RuntimeError("Use 'await async_flush()' in aiokafka mode.")
        if self._producer is not None:
            result = self._producer.flush(timeout=timeout)
            if result > 0:
                raise Exception(f"Failed to flush {result} messages")
    
    async def async_flush(self):
        if not self.use_aiokafka:
            raise RuntimeError("Use 'flush()' in non-aiokafka mode.")
        if self._producer is not None:
            await self._producer.flush()            

    #
    # Consumer sync/async
    #
    def subscribe(self, groupid=None, offset = 'latest', autocommit=True, timeout=None):
        if self.use_aiokafka:
            raise RuntimeError("Use 'await async_subscribe()' in aiokafka mode.")
        
        if groupid is None:
            groupid = str(uuid.uuid4())
                
        self.consumer[groupid] = Consumer({
                'bootstrap.servers': self.bootstrap_servers,
                'group.id': groupid,
                'auto.offset.reset': offset,
                'enable.auto.commit': autocommit
            })            
        self.consumer[groupid].subscribe([self.topic])
        # Wait for partition assignment
        if timeout is not None:
            start = time.time()
            while not self.consumer[groupid].assignment():
                if time.time() - start > timeout:
                    raise TimeoutError("Timed out waiting for partition assignment.")
                self.consumer[groupid].poll(0.1)
                time.sleep(0.1)
    
    async def async_subscribe(self, groupid=None, offset='latest', autocommit=True):
        if not self.use_aiokafka:
            raise RuntimeError("Use 'subscribe()' in confluent_kafka mode.")
        
        if groupid is None:
            groupid = str(uuid.uuid4())

        if not groupid in self.consumer:
            consumer = AIOKafkaConsumer(
                self.topic,
                bootstrap_servers=self.bootstrap_servers,
                group_id=groupid,
                auto_offset_reset=offset,
                enable_auto_commit=autocommit
            )
            await consumer.start()
            self.consumer[groupid] = consumer            
    
    #
    # Poll (consume one message) sync/async
    #
    def poll(self, groupid = None, timeout=None):
        if self.use_aiokafka:
            raise RuntimeError("Use 'async_poll()' in aiokafka mode.")
        
        if groupid is None:
            groupid = list(self.consumer.keys())[0] # use first consumer

        if timeout is None:
            msg = self.consumer[groupid].poll()
        else:
            msg = self.consumer[groupid].poll(timeout)
            
        if msg is None:
            return None
        if msg.error():            
            if msg.error().code() != KafkaError._PARTITION_EOF:
                raise Exception(f"Error: {msg.error()}")
        msgdict = bson.BSON.decode(lz4.frame.decompress(msg.value()))
        if 'mtime' in msgdict:
            if self.mtime is None or msgdict['mtime'] > self.mtime:
                self.mtime = msgdict['mtime']
        self.counter += 1
        return msgdict
    
    async def async_poll(self, groupid=None, timeout=0, max_records=None, decompress=True):
        if not self.use_aiokafka:
            raise RuntimeError("Use 'poll()' in confluent_kafka mode.")
        if groupid is None:
            if len(self.consumer) == 0:
                raise RuntimeError("You must call 'await async_subscribe()' first.")
            groupid = list(self.consumer.keys())[0] # use first consumer
        if self.consumer[groupid] is None:
            raise RuntimeError("You must call 'await async_subscribe()' first.")
                
        partitions = await self.consumer[groupid].getmany(
            timeout_ms=timeout, max_records=max_records)
        msgs = []
        for partition, messages in partitions.items():
            for msg in messages:
                if msg.value is not None:
                    if decompress:
                        msgdict = bson.BSON.decode(lz4.frame.decompress(msg.value))
                    else:
                        msgdict = msg.value
                    if 'mtime' in msgdict:
                        if self.mtime is None or msgdict['mtime'] > self.mtime:
                            self.mtime = msgdict['mtime']
                    self.counter += 1
                    msgs.append(msgdict)
        return msgs


    #
    # Retention update (sync mode only)
    #
    def set_retention(self, retention_ms):
        if self.use_aiokafka:
            raise RuntimeError("Set retention_ms only supported in sync mode (confluent_kafka).")
        from confluent_kafka.admin import AdminClient, ConfigResource
        admin = AdminClient({'bootstrap.servers': self.bootstrap_servers})
        config_resource = ConfigResource('topic', self.topic)
        new_config = {'retention.ms': str(retention_ms)}
        fs = admin.alter_configs([config_resource], new_configs=new_config)
        for resource, f in fs.items():
            try:
                f.result()
                Logger.log.debug(f"Retention period for topic {resource.name()} updated to {retention_ms} ms.")
                return True
            except Exception as e:
                Logger.log.error(f"Failed to update retention_ms period: {e}")
                return False

    #
    # Sync/async close for consumer (optional)
    #
    def close(self):
        for consumer in self.consumer:            
            consumer.close()

    async def async_close(self):
        for consumer in self.consumer:            
            await consumer.stop()

    def delete(self) -> bool:
        """
        Deletes the specified Kafka topic.
        Returns True if deleted, False if topic did not exist or an error occurred.
        """
        
        admin = AdminClient({'bootstrap.servers': self.bootstrap_servers})
        if self.topic not in admin.list_topics(timeout=10).topics:
            Logger.log.warning(f"Topic {self.topic} does not exist.")
            return False
        fs = admin.delete_topics([self.topic])
        for topic, f in fs.items():
            try:
                f.result()  # Wait for operation to finish
                Logger.log.debug(f"Topic {topic} deleted.")
                return True
            except Exception as e:
                Logger.log.error(f"Failed to delete topic {topic}: {e}")
                return False
        return False

    async def run_async_cache_and_persist_tasks(
        self,
        shdata,
        partitioning: str = 'daily',
        snapshots: list[str] | None = None
    ) -> None:
        """
        Run and await cache and persist tasks asynchronously.
        """
        if snapshots is None:
            snapshots = ['D1', 'M15', 'M1']
        tasks = await self.async_cache_and_persist_tasks(shdata, partitioning=partitioning, snapshots=snapshots)
        await asyncio.gather(*tasks)
                                            
    async def async_cache_and_persist_tasks(
        self,
        shdata,
        partitioning: str = 'daily',
        snapshots: list[str] | None = None
    ) -> list[asyncio.Task]:
        """
        Create async cache and persist tasks.
        """
        if snapshots is None:
            snapshots = ['D1', 'M15', 'M1']

        if not self.use_aiokafka:
            raise Exception('use_aiokafka must be True to use async_cache_and_persist_tasks')
        
        cache = shdata.cache(self.database, self.period, self.source, self.tablename, use_async_queue=True)
        cache_consumer_task = asyncio.create_task(self.async_cache_stream_task(cache))
        cache_flush_task = asyncio.create_task(self.async_flush_cache_task(cache))
        
        # Persist tasks
        self.persist_queue = asyncio.Queue(maxsize=50000)
        persist_consume_task = asyncio.create_task(self.async_persist_stream_task(self.persist_queue))
        persist_flush_task = asyncio.create_task(
            self.async_persist_flush_task(self.persist_queue,shdata, partitioning=partitioning, snapshots=snapshots)
        )
        return [cache_consumer_task, cache_flush_task, persist_consume_task, persist_flush_task]

    async def async_cache_stream_task(self, cache):                
        groupid = 'cache-group'
        offset = 'earliest'
        await self.async_subscribe(offset=offset, groupid=groupid)        
        while True:
            msgs = await self.async_poll(timeout=1.0, groupid=groupid)
            if not msgs:
                continue
            for msg in msgs:
                pkey = tuple(msg[pk] for pk in cache.pkeycolumns)
                cache[pkey] = msg
                cache.consumer_counter += 1
    
    async def async_flush_cache_task(self, cache):
        """
        Asynchronously consume upsert tasks from cache.queue and push the latest
        symbol data to Redis Cluster. Uses pipeline for batch efficiency.
        Prints write throughput in symbols/sec.
        """        
        while True:
            nupsert = await cache.async_flush()
            cache.counter += nupsert

    async def async_persist_stream_task(self, queue):
        groupid = 'persist-group'        
        offset = 'earliest'
        await self.async_subscribe(offset=offset, groupid=groupid)        
        while True:
            msgs = await self.async_poll(timeout=1.0, groupid=groupid)
            if not msgs:
                continue
            for msg in msgs:
                await queue.put(msg)


    async def async_persist_flush_task(self, queue, shdata, partitioning = 'daily', snapshots= ['D1','M15','M1']) -> None:
        while True:
            data = [ await queue.get() ]            
            while not queue.empty() and len(data)<1000:
                data.append(await queue.get())            

            tablename = self.tablename
            if not partitioning is None:
                if partitioning=='daily':
                    tablename = f"{self.tablename}/{data[0]['mtime'].strftime('%Y%m%d')}"    
                elif partitioning=='monthly':
                    tablename = f"{self.tablename}/{data[0]['mtime'].strftime('%Y%m')}"
                elif partitioning=='yearly':
                    tablename = f"{self.tablename}/{data[0]['mtime'].strftime('%Y')}"

            collection = shdata.collection(self.database, self.period, self.source, tablename, user=self.user)
            collection.extend(data)
    

    
# ========== USAGE PATTERNS ==========

# --- Synchronous / confluent_kafka ---
"""
stream = StreamKafka(
    database="mydb", period="1m", source="agg", tablename="prices",
    self.bootstrap_servers="localhost:9092",
    KAFKA_PARTITIONS=1,
    use_aiokafka=False
)
stream.extend({'price': 100, 'ts': time.time()})
stream.subscribe()
msg = stream.poll(timeout=1.0)
print(msg)
stream.close()
"""

# --- Asynchronous / aiokafka ---
"""
import asyncio

async def main():
    stream = StreamKafka(
        database="mydb", period="1m", source="agg", tablename="prices",
        self.bootstrap_servers="localhost:9092",
        KAFKA_PARTITIONS=1,
        use_aiokafka=True
    )
    await stream.async_extend({'price': 200, 'ts': time.time()})
    await stream.async_subscribe()
    async for msg in stream.async_poll():
        print(msg)
        break
    await stream.async_flush()
    await stream.async_close()

asyncio.run(main())
"""