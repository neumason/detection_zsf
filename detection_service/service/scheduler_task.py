#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from detection_common.timer.timer import Timer


class SchedulerTask:
    def __init__(self):
        self.timer = Timer()

    def interface_crawler(self, key):
        if not Timer.is_not_stopped():
            self.timer.crontab_executor(key)


