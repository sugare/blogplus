#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/4/6 15:04
# @Author  : Sugare
# @Site    : 30733705@qq.com
# @File    : memcachedsession.py
# @Software: PyCharm

import time
import json
import memcache
from lib.others import createSessionId
from conf import config


conn = memcache.Client(['192.168.2.130:11211'],debug=True, cache_cas=True)

class MemcachedSession:
    session_id = "__sessionId__"
    def __init__(self, handler):
        self.handler = handler

        client_random_str = handler.get_cookie(MemcachedSession.session_id, None)

        if client_random_str and conn.get(client_random_str):
            self.random_str = client_random_str
        else:
            self.random_str = createSessionId()
            conn.set(self.random_str, {}, config.SESSION_EXPIRES)

        conn.set(self.random_str, conn.get(self.random_str), config.SESSION_EXPIRES)
        expires_time = time.time() + config.SESSION_EXPIRES

        handler.set_cookie(MemcachedSession.session_id, self.random_str, expires=expires_time)

    def __getitem__(self, key):
        ret = conn.get(self.random_str)
        ret_dict = json.loads(ret)
        result = ret_dict.get(key, None)
        return result

    def __setitem__(self, key, value):
        ret = conn.get(self.random_str)
        ret_dict = json.loads(ret)
        ret_dict[key] = value
        conn.set(self.random_str, json.dumps(ret_dict), config.SESSION_EXPIRES)

    def __delitem__(self, key):
        ret = conn.get(self.random_str)
        ret_dict = json.loads(ret)
        del ret_dict[key]
        conn.set(self.random_str, json.dumps(ret_dict), config.SESSION_EXPIRES)
if __name__ == '__main__':
    pass