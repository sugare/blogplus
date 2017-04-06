#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/3/28 8:47
# @Author  : Sugare
# @Site    : 30733705@qq.com
# @File    : tables.py
# @Software: PyCharm

from sqlalchemy import func, create_engine, Index, UniqueConstraint, and_, or_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, DateTime, TEXT
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.dialects.mysql import LONGTEXT
import datetime


# connect to the database
engine = create_engine('mysql+pymysql://root:123456@127.0.0.1:3306/song?charset=utf8', pool_size=100)

# Base class
Base = declarative_base()

# 用户信息
class UserInfo(Base):
    __tablename__ = 'userinfo'

    nid = Column(Integer, primary_key=True)
    username = Column(String(32))
    password = Column(String(32))
    email = Column(String(32))
    ctime = Column(DateTime, default=datetime.datetime.now())

    status = Column(Integer, default=0)

    __table_args__ = (
        Index('ix_user_pwd', 'username', 'password'),
        Index('ix_email_pwd', 'email', 'password'),
    )

# 文章类型
class Type(Base):
    __tablename__ = 'type'

    nid = Column(Integer, primary_key=True)
    name = Column(String(32))

a = Type(name='单片机')
b = Type(name='嵌入式')
c = Type(name='运维')
d = Type(name='开发')
e = Type(name='云计算')
f = Type(name='前辈心得')

# 文章信息
class Articles(Base):
    __tablename__ = 'articles'

    nid = Column(Integer, primary_key=True)
    user_info_id = Column(Integer, ForeignKey('userinfo.nid'))
    ctime = Column(DateTime, default=datetime.datetime.now())
    title = Column(String(32))
    status = Column(Integer, default=0)         # 0 保存，1发布，
    content = Column(LONGTEXT)
    type_id = Column(Integer, ForeignKey('type.nid'))
    cataimg = Column(String(32), default='linux.jpg')

    user = relationship('UserInfo', backref='art')
    com = relationship('Comment', backref='art')
    type = relationship('Type', backref='art')

# 用户点赞
class Favor(Base):
    __tablename__ = 'favor'

    nid = Column(Integer, primary_key=True)
    user_info_id = Column(Integer, ForeignKey('userinfo.nid'))
    article_id = Column(Integer, ForeignKey('articles.nid'))
    ctime = Column(DateTime, default=datetime.datetime.now())

    __table_args = (
        UniqueConstraint('user_info_id', 'article_id', name='uix_uid_nid'),
    )

# 评论表
class Comment(Base):
    __tablename__ = 'comment'

    nid = Column(Integer, primary_key=True, autoincrement=True)
    user_info_id = Column(Integer, ForeignKey('userinfo.nid'))
    article_id = Column(Integer, ForeignKey('articles.nid'))
    reply_id = Column(Integer, ForeignKey('comment.nid'), nullable=True, default=None)
    # up = Column(Integer, default=0)
    # down = Column(Integer, default=0)
    ctime = Column(DateTime, default=datetime.datetime.now())
    content = Column(String(150))

    user = relationship('UserInfo', backref='com')


class Scrapy51Data(Base):
    __tablename__ = 'scrapy51data'

    nid = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String(100))
    title = Column(String(100))

class ScrapyNewsData(Base):
    __tablename__ = 'scrapynewsdata'

    nid = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String(100))
    title = Column(String(100))

MySession = sessionmaker(bind=engine)
conn = MySession()

if __name__ == '__main__':
    Base.metadata.create_all(engine)
