import uuid
import redis
import json
import pickle
from functools import wraps

class RedisHashSerializer:
    def __init__(self, pool):
        self.pool = pool

    def hset_json(self, hash_name, key, value):
        """使用JSON序列化存储"""
        serialized = json.dumps(value, ensure_ascii=False)
        with redis.Redis(connection_pool=self.pool) as r:
          res = r.hset(hash_name, key, serialized)
        return res

    def hget_json(self, hash_name, key):
        """获取并JSON反序列化"""
        with redis.Redis(connection_pool=self.pool) as r:
          data = r.hget(hash_name, key)
        return json.loads(data.decode('utf-8')) if data else None

    def hset_pickle(self, hash_name, key, value):
        """使用Pickle序列化存储"""

        serialized = pickle.dumps(value)
        with redis.Redis(connection_pool=self.pool) as r:
            res = r.hset(hash_name, key, serialized)
        return res

    def hget_pickle(self, hash_name, key):
        """获取并Pickle反序列化"""
        with redis.Redis(connection_pool=self.pool) as r:
          data = r.hget(hash_name, key)
        return pickle.loads(data) if data else None
    
    def hget_pickle_all(self, hash_name):
        with redis.Redis(connection_pool=self.pool) as r:
          data = r.hgetall(hash_name)
        return data

    def set_pickle(self, key, value, timeout: int = 3600):
        serialized = pickle.dumps(value)
        with redis.Redis(connection_pool=self.pool) as r:
            res = r.set(key, serialized)
            if timeout:
                r.expire(key, timeout)

    def get_pickle(self, key):
        with redis.Redis(connection_pool=self.pool) as r:
          data = r.get(key)
        return pickle.loads(data) if data else None

class RedisCache:
    pool : None
    serializer = None
    def __init__(self,config):
       self.pool = redis.ConnectionPool(
            host = config['host'] ,
            port = config['port'] ,
            db = config['db'] ,
            password = config['password'] ,
            max_connections = config['max_connections'],
            socket_timeout=config['socket_timeout'],        # 套接字操作超时（秒）
            socket_connect_timeout=config['socket_connect_timeout'], # 连接建立超时（秒）
            retry_on_timeout=config['retry_on_timeout'], )
       self.serializer = RedisHashSerializer(self.pool)

    def generate_id(self, *args, **kwargs):
        return 'bossai-'+str(uuid.uuid4())

    def set(self, id, field, value):
        self.serializer.hset_pickle(id, field, value)

    def get(self, id, field):
        return self.serializer.hget_pickle(id,field)

    def setExpire(self, key, expire):
        with redis.Redis(connection_pool = self.pool) as r:
          r.expire(key, expire)

    def set_obj(self,key,value,timeout: int = 3600):
        self.serializer.set_pickle(key,value,timeout)

    def get_obj(self,key):
        return self.serializer.get_pickle(key)

    def get_all(self, key) -> list:
        return self.serializer.hget_pickle_all(key)

    def delete(self, id):
        with redis.Redis(connection_pool = self.pool) as r:
          r.delete(id)
