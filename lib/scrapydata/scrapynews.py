#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/4/6 17:20
# @Author  : Sugare
# @Site    : 30733705@qq.com
# @File    : scrapynews.py
# @Software: PyCharm

import requests
from bs4 import BeautifulSoup
from models.tables import ScrapyNewsData, MySession

session = MySession()

def getNewsData(url, store=True):
    cont = requests.get(url)
    soup = BeautifulSoup(cont.text, 'html.parser')
    news_list = soup.find_all('h3',attrs={'class':'f18 l26'}, limit=5)
    for i in news_list:
        content_url = i.a['href']
        content_title = i.a['title']
        if not store:
            print(content_url, content_title)
        else:
            data = ScrapyNewsData(url=content_url, title=content_title)
            session.add(data)
            session.commit()

if __name__ == '__main__':
    url = "http://tech.qq.com/"
    getNewsData(url)