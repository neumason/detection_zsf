#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import threading
import time

from detection_common.redis.redis_manager import RedisManager


# 单位：秒
DEFAULT_EXPIRE = 60 * 60 * 24


class RateLimiter:
    def __init__(self, permits_per_second=1, max_permits=10):
        self.rm = RedisManager().get_rm()
        self.lastAddTime = None
        self.tokenRemainingCounter = None
        # bucket所保留的最大令牌数
        self.maxPermits = max_permits
        self.permitsPerSecond = permits_per_second

    def access_control(self, user_ip):
        # 根据user_ip生成新键，这样可以随着配置动态消除之前配置影响
        key = self._generate_key(user_ip)
        bucket_dict = self.rm.hgetall(key)
        lock = threading.RLock()
        with lock:
            if bucket_dict and len(bucket_dict) > 0:
                self.lastAddTime = int(bucket_dict[b'lastAddTime'])
                self.tokenRemainingCounter = int(bucket_dict[b'tokenRemainingCounter'])
                cur_time = round(time.time())

                interval = cur_time - self.lastAddTime
                current_tokens_remain = self.tokenRemainingCounter
                # 根据间隔时间算出所生成令牌数
                granted_tokens = int(interval * self.permitsPerSecond)
                if granted_tokens >= 1:
                    current_tokens_remain = min(granted_tokens + self.tokenRemainingCounter, self.maxPermits)

                self.lastAddTime = cur_time
                if current_tokens_remain > 0:
                    self.tokenRemainingCounter = current_tokens_remain - 1
                    self._save_to_hash(key)
                    return True
                elif current_tokens_remain == 0:
                    self.tokenRemainingCounter = 0
                    self._save_to_hash(key)
                return False
            elif not bucket_dict:
                self.tokenRemainingCounter = self.maxPermits - 1
                self.lastAddTime = round(time.time())
                self._save_to_hash(key)
                return True
            return False

    def _save_to_hash(self, key):
        with self.rm.pipeline() as pipe:
            pipe.hmset(key, {'tokenRemainingCounter': self.tokenRemainingCounter,
                             'lastAddTime': self.lastAddTime})
            pipe.expire(key, DEFAULT_EXPIRE)
            pipe.execute()

    def _generate_key(self, user_ip):
        return "rate_limit:" + str(self.maxPermits) + ":" + str(self.permitsPerSecond) + ":" + user_ip
