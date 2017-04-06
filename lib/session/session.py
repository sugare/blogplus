#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/3/28 9:20
# @Author  : Sugare
# @Site    : 30733705@qq.com
# @File    : session.py
# @Software: PyCharm

from conf import config
from lib.session.cachesession import CacheSession
from lib.session.memcachedsession import MemcachedSession
from lib.session.redissession import RedisSession

class SessionFactory:

    @staticmethod
    def get_session_obj(handler):
        obj = None

        if config.SESSION_TYPE == "cache":
            obj = CacheSession(handler)
        elif config.SESSION_TYPE == "memcached":
            obj = MemcachedSession(handler)
        elif config.SESSION_TYPE == "redis":
            obj = RedisSession(handler)
        return obj

if __name__ == '__main__':
    print('!')