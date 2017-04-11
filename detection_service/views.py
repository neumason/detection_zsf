from django.http import HttpResponse


import json
import re

# Create your views here.
from detection_common.redis.rate_limiter import RateLimiter
from detection_common.redis.redis_manager import RedisManager
from detection_common.requests.url_requests import UrlRequests
from detection_service.service.scheduler_task import SchedulerTask


def get_response_time(request):
    store_key = 'host_response_time'
    if 'HTTP_X_FORWARDED_FOR' in request.META:
        ip = request.META['HTTP_X_FORWARDED_FOR']
        ip = ip.split(",")[0]
    else:
        ip = request.META['REMOTE_ADDR']

    ip_pattern = "^(1\\d{2}|2[0-4]\\d|25[0-5]|[1-9]\\d|[1-9])\\." \
        + "(1\\d{2}|2[0-4]\\d|25[0-5]|[1-9]\\d|\\d)\\." \
        + "(1\\d{2}|2[0-4]\\d|25[0-5]|[1-9]\\d|\\d)\\." \
        + "(1\\d{2}|2[0-4]\\d|25[0-5]|[1-9]\\d|\\d)$"
    ip_pattern = re.compile(ip_pattern)
    # 启动后台定时抓取url任务, 已启动不再重复开启
    SchedulerTask().interface_crawler(store_key)

    # 对用户查询频率进行限定
    rate_limiter = RateLimiter()
    response_time = {}
    if ip_pattern.match(ip) and rate_limiter.access_control(ip):
        rm = RedisManager()
        temp = rm.get_rm().hgetall(store_key)
        for key in temp.keys():
            response_time[key.decode('utf-8')] = temp[key].decode('utf-8')
        if len(response_time) == 0:
            response_time = UrlRequests().url_request()
            rm.hash_set(store_key, response_time, expire=60)
    else:
        return HttpResponse(status=403)

    return HttpResponse(json.dumps(response_time))


