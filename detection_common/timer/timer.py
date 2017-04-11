#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor

from detection_common.redis.redis_manager import RedisManager
from detection_common.requests.url_requests import UrlRequests

executors = {
    'default': ThreadPoolExecutor(10),
    'processpool': ProcessPoolExecutor(2)
}
job_defaults = {
    'coalesce': False,
    'max_instances': 1  # 任务并发数
}


class Timer:
    scheduler = None
    DEFAULT_EXPIRE = 60  # 单位：秒

    def __new__(cls, *args):
        if not hasattr(cls, '_instance'):
            cls._instance = super(Timer, cls).__new__(cls, *args)
            Timer.scheduler = BackgroundScheduler(executors=executors, job_defaults=job_defaults)
        return cls._instance

    def __init__(self):
        self.urlRequest = UrlRequests()
        self.rm = RedisManager()

    # 用于存储响应时间到redis中的定时任务
    def new_job(self, key):
        response_time = self.urlRequest.url_request()
        self.rm.hash_set(key, response_time, expire=Timer.DEFAULT_EXPIRE)

    """
        :param day_of_week :  一周内星期几, mon,tue,wed,thu,fri,sat,sun
        :param interval: 时间间隔，和time_unit配合使用
    """

    def crontab_executor(self, key,  day_of_week='mon-sat', interval=60, time_unit='second'):
        if time_unit == 'second':
            Timer.scheduler.add_job(self.new_job, 'cron', args=[key], day_of_week=day_of_week, second='*/' + str(interval))
        elif time_unit == 'min':
            Timer.scheduler.add_job(self.new_job, 'cron', args=[key], day_of_week=day_of_week, minute='*/' + str(interval))
        elif time_unit == 'hour':
            Timer.scheduler.add_job(self.new_job, 'cron', args=[key], day_of_week=day_of_week, hour='*/' + str(interval))

        Timer.scheduler.start()

    def interval_executor(self, key, interval=60, time_unit='second'):
        if time_unit == 'second':
            Timer.scheduler.add_job(self.new_job, 'interval', args=[key], seconds=interval)
        elif time_unit == 'min':
            Timer.scheduler.add_job(self.new_job, 'interval', args=[key], minutes=interval)
        elif time_unit == 'hour':
            Timer.scheduler.add_job(self.new_job, 'interval', args=[key], hours=interval)

        Timer.scheduler.start()

    @staticmethod
    def is_not_stopped():
        sched = Timer.scheduler
        return sched is not None and len(sched.get_jobs()) >= 1 and sched.running
