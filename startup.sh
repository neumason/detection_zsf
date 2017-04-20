#!/bin/bash

host=$1
if [ ! -n "$host" ];then
   echo “please input ip and port separated by :”
else
   python /usr/local/pyapp/detection/manage.py runserver $host &
   /usr/local/redis-3.2.8/src/redis-server &
fi
