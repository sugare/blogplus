#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/4/6 15:06
# @Author  : Sugare
# @Site    : 30733705@qq.com
# @File    : redissession.py
# @Software: PyCharm

import time
from lib.others import createSessionId
from conf import config
import redis


pool = redis.ConnectionPool(host='127.0.0.1', port=6379)
r = redis.Redis(connection_pool=pool)

class RedisSession:
    session_id = "__sessionId__"
    def __init__(self, handler):
        self.handler = handler

        client_random_str = handler.get_cookie(RedisSession.session_id, None)

        if client_random_str and r.exists(client_random_str):
            self.random_str = client_random_str
        else:
            self.random_str = createSessionId()
            r.hset(self.random_str, None, None)

        expires_time = time.time() + config.SESSION_EXPIRES
        r.expire(self.random_str, config.SESSION_EXPIRES)
        handler.set_cookie(RedisSession.session_id, self.random_str, expires=expires_time)

    def __getitem__(self, key):
        result = r.hget(self.random_str, key)
        if result:
            return result.decode('utf-8')   # python3
            # return str(result, encoding='utf-8')
        else:
            return result


    def __setitem__(self, key, value):
        r.hset(self.random_str, key, value)

    def __delitem__(self, key):
        r.hdel(self.random_str, key)

if __name__ == '__main__':
    pass
