#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import re
import subprocess
import requests
import sys


class UrlRequests:
    url_list = ['210.30.0.1', '210.30.1.114', 'http://www.dlnu.edu.cn',
                'http://lib.dlnu.edu.cn/', 'http://zhjw.dlnu.edu.cn', 'http://www.dlnu.edu.cn/its/xyq/',
                'http://mail.dlnu.edu.cn/']

    ip_pattern = "^(1\\d{2}|2[0-4]\\d|25[0-5]|[1-9]\\d|[1-9])\\." \
                 + "(1\\d{2}|2[0-4]\\d|25[0-5]|[1-9]\\d|\\d)\\." \
                 + "(1\\d{2}|2[0-4]\\d|25[0-5]|[1-9]\\d|\\d)\\." \
                 + "(1\\d{2}|2[0-4]\\d|25[0-5]|[1-9]\\d|\\d)$"

    protocol_pattern = '^(http|ftp|https).+$'
    WINDOWS_DEFAULT_ENCODE = 'gbk'

    def url_request(self):

        response_time = {}
        for url in UrlRequests.url_list:
            try:
                if re.compile(UrlRequests.ip_pattern).match(url) or \
                        not re.compile(UrlRequests.protocol_pattern).match(url):
                    os_name = os.name
                    # 根据系统平台设置 ping 命令
                    if os_name == 'nt':  # windows
                        cmd = 'ping ' + url
                    else:  # unix/linux
                        cmd = 'ping -c 4 ' + url

                    sub = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE, shell=True)

                    # 获取时间信息
                    if os_name == 'nt':
                        out = sub.communicate()[0].decode(UrlRequests.WINDOWS_DEFAULT_ENCODE)
                        text = out.replace('\r\n', '\n').replace('\r', '\n')
                        time = re.findall(r'\d+(?=ms$)', text)
                    else:
                        # unix/linux
                        out = sub.communicate()[0].decode(sys.getdefaultencoding())
                        text = out.replace('\r\n', '\n').replace('\r', '\n')
                        time = re.findall(r'(?<=\d/)[\d.]+(?=/)', text)

                    if len(time) > 0:
                        response_time[url] = str(time[0]) + "ms"
                    else:
                        response_time[url] = "error"
                else:
                    response = requests.get(url, timeout=5)
                    response.encoding = 'utf-8'
                    ms = str(round(response.elapsed.microseconds / 1000))
                    response_time[url] = ms + "ms"

            except Exception:
                response_time[url] = "error"

        return response_time

if __name__ == "__main__":
    response_time = UrlRequests().url_request()

    for key in response_time:
        print("key= " + key + " value= " + response_time[key])
