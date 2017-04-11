#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import threading
import time

from detection_common.redis.redis_manager import RedisManager


intervalInMills = 10000

# bucket所保留的最大令牌数
globalLimit = 10
# 设置相应的token生成频率(x/mills)
intervalPerPermit = intervalInMills * 1.0 / globalLimit
# 单位：秒
DEFAULT_EXPIRE = 60 * 60 * 24


class RateLimiter:
    def __init__(self):
        self.rm = RedisManager().get_rm()
        self.lastAddTime = None
        self.tokenRemainingCounter = None

    def access_control(self, user_ip):
        # 根据user_ip生成新键，这样可以随着配置动态消除之前配置影响
        key = RateLimiter._generate_key(user_ip)
        bucket_dict = self.rm.hgetall(key)
        lock = threading.RLock()
        with lock:
            if bucket_dict and len(bucket_dict) > 0:
                self.lastAddTime = int(bucket_dict[b'lastAddTime'])
                self.tokenRemainingCounter = int(bucket_dict[b'tokenRemainingCounter'])
                cur_time_in_mills = round(time.time() * 1000)

                interval = cur_time_in_mills - self.lastAddTime
                current_tokens_remain = self.tokenRemainingCounter
                # 根据间隔时间算出所生成令牌数
                granted_tokens = interval / intervalPerPermit
                if granted_tokens >= 1:
                    current_tokens_remain = min(granted_tokens + self.tokenRemainingCounter, globalLimit)

                self.lastAddTime = cur_time_in_mills
                if current_tokens_remain > 0:
                    self.tokenRemainingCounter = current_tokens_remain - 1
                    self._save_to_hash(key)
                    return True
                elif current_tokens_remain == 0:
                    self.tokenRemainingCounter = 0
                    self._save_to_hash(key)
                return False
            else:
                self.tokenRemainingCounter = globalLimit - 1
                self.lastAddTime = round(time.time() * 1000)
                self._save_to_hash(key)
                return True

    def _save_to_hash(self, key):
        with self.rm.pipeline() as pipe:
            pipe.hmset(key, {'tokenRemainingCounter': self.tokenRemainingCounter,
                             'lastAddTime': self.lastAddTime})
            pipe.expire(key, DEFAULT_EXPIRE)
            pipe.execute()

    @staticmethod
    def _generate_key(user_ip):
        return "rate_limit:" + str(intervalInMills) + ":" + str(globalLimit) + ":" + user_ip
