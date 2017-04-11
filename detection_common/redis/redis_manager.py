#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import redis
from redis import ConnectionPool


class RedisManager(object):
    HOST = '127.0.0.1'
    PORT = 6379
    DB = '1'
    MAX_CONNECTION = 20
    connection_pool = None

    def __new__(cls, *args):
        if not hasattr(cls, '_instance'):
            cls._instance = super(RedisManager, cls).__new__(cls, *args)
            RedisManager.connection_pool = ConnectionPool(host=RedisManager.HOST,
                                                          port=RedisManager.PORT,
                                                          db=RedisManager.DB)
        return cls._instance

    def __init__(self):
        self.rm = redis.Redis(connection_pool=RedisManager.connection_pool, max_connections=RedisManager.MAX_CONNECTION)

    def get_rm(self):
        return self.rm

    def hash_set(self, key_name, dic_value, expire=None):
        if isinstance(dic_value, dict) and len(dic_value) > 0 and key_name:
            for key in dic_value.keys():
                self.rm.hset(key_name, key, dic_value[key])

            if expire:
                self.rm.expire(key_name, int(expire))



