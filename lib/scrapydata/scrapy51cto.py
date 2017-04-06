#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/4/6 14:58
# @Author  : Sugare
# @Site    : 30733705@qq.com
# @File    : scrapy51cto.py
# @Software: PyCharm

import requests
import json
import re
from models.tables import Scrapy51Data, MySession

session = MySession()

def getData(url, store=True):
    cont = requests.get(url).content
    rex = re.compile(r'\w+[(]{1}(.*)[)]{1}')
    content = rex.findall(str(cont, encoding='gbk'))[0]
    con = json.loads(content)
    for i in range(1, len(con[0])):
        content_url = con[0][i]['url']
        content_title = con[0][i]['title']
        if not store:
            print(content_url, content_title)
        else:
            data = Scrapy51Data(url=content_url, title=content_title)
            session.add(data)
            session.commit()

if __name__ == '__main__':
    url = "http://other.51cto.com/php/get_category_new_articles_list.php?callback=jsonp1491455063080&page=1&type_id=523"
    getData(url)