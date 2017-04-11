#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from django.conf.urls import url

import detection_service.views

urlpatterns = [
    url(r'^response_time/', detection_service.views.get_response_time),
]