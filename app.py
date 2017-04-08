#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/3/28 8:33
# @Author  : Sugare
# @Site    : 30733705@qq.com
# @File    : app.py
# @Software: PyCharm


# system
import io
import os.path
import json
import hashlib

# tornado
import tornado.ioloop
import tornado.web
import tornado.httpserver
import tornado.options
import tornado.escape

# sqlalchemy
from sqlalchemy import and_, or_

# lib
from models.tables import UserInfo, Articles, Comment, MySession, Type, ScrapyNewsData, Scrapy51Data
from lib.others import sendEmail, buildTree, commentTree, randomCode
from lib.session.session import SessionFactory
from lib.form.form import BaseResponse, LoginForm, ValidateEmailForm, ArticleForm, RegisterForm, CommentForm
from lib.checkcode.checkcode import createValidateCode

from tornado.options import define, options
define("port", default=8888, help="run on the given port", type=int)


class Application(tornado.web.Application):
    def __init__(self):
        # url
        handlers = [
            (r'/?', IndexHandler),
            (r'/sendcode', SendCodeHandler),
            (r'/register', RegisterHandler),
            (r'/comment', CommentHandler),
            (r'/articles/?(.*)', ArticleHandler),
            (r'/publish/(.*)/(.*)', PublishHandler),
            (r'/home/?(.*)', HomeHandler),
            (r'/editor/?(.*)', EditorHandler),
            (r'/fileload', FileHandler),
            (r'/login', LoginHandler),
            (r'/logout', LogoutHandler),
            (r'/check_code', CheckCodeHandler),
            (r'/.*', ErrorHandler),

        ]
        settings = dict(
            static_path=os.path.join(os.path.dirname(__file__), 'static'),
            template_path=os.path.join(os.path.dirname(__file__), 'template'),
            # xsrf_cookies=True,
            login_url="/",
            # debug=True,
        )
        super(Application, self).__init__(handlers, **settings)

# BaseHandler
class BaseHandler(tornado.web.RequestHandler):
    def initialize(self):
        self.session = SessionFactory.get_session_obj(self)
        self.conn = MySession()

    # 用户验证装饰器
    def get_current_user(self):
        if not self.session['is_login']:
            rep = BaseResponse()
            rep.summary = 'auth failed'
            return None
        else:
            conn = MySession()
            user = self.session['login_username']
            u = conn.query(UserInfo).filter(UserInfo.username == user).first()
            return u

# 主页面显示
class IndexHandler(BaseHandler):
    def get(self):
        type_list = self.conn.query(Type).all()
        scrapy_51_data = self.conn.query(Scrapy51Data).order_by(Scrapy51Data.nid.desc())[0:5]
        scrapy_news_data = self.conn.query(ScrapyNewsData).order_by(ScrapyNewsData.nid.desc())[0:5]
        self.render('index.html',type_list=type_list, scrapy_51_data=scrapy_51_data, scrapy_news_data=scrapy_news_data)

class ErrorHandler(BaseHandler):
    def get(self):
        self.write_error(404)

# 发布文章
class PublishHandler(BaseHandler):
    def get(self,status='not',nid=None):
        art = self.conn.query(Articles).filter(Articles.nid == int(nid)).first()

        if status == 'n':
            art.status = 1
            self.conn.add(art)
            self.conn.commit()
            try:
                self.redirect('/articles/%s' % nid)
            except:
                self.write_error(403)
        else:
            art.status = 0
            self.conn.add(art)
            self.conn.commit()
            try:
                self.redirect('/home/%s' % self.get_current_user().username)
            except:
                self.write_error(403)

# 用户家目录
class HomeHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, user=None):

        userinfo = self.conn.query(UserInfo).filter(UserInfo.username == user).first()
        if user == self.get_current_user().username:
            # userinfo = self.conn.query(UserInfo).filter(UserInfo.username==user).first()
            self.render('home.html', userinfo = userinfo)
        else:
            self.write_error(403)

# 新建、编辑页面
class EditorHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, nid=None):

        user_obj = self.get_current_user()
        if user_obj.status == 1:
            type_list = self.conn.query(Type).all()
            cata_img = os.path.join(os.path.dirname(__file__), 'static', 'cataimg')
            img_list = os.listdir(cata_img)  # 列出文件夹下所有的目录与文件

            art_list = []
            for i in user_obj.art:
                art_list.append(i.nid)

            if nid:
                if int(nid) in art_list:
                    article = self.conn.query(Articles).filter(Articles.nid == int(nid)).first()
                else:
                    self.write_error(403)
            else:
                article = ''
            self.render('editor.html', art=article, img_list=img_list, type_list=type_list)
        else:
            self.write_error(403)
    @tornado.web.authenticated
    def post(self, nid=None):
        form = ArticleForm()

        if form.valid(self):
            if nid:
                update_art = self.conn.query(Articles).filter(Articles.nid == int(nid)).first()
                update_art.title = form._value_dict['title']
                update_art.content = form._value_dict['content']
                update_art.type_id = int(form._value_dict['type_id'])
                update_art.cataimg = form._value_dict['cataimg']
                self.conn.add(update_art)

            else:
                art = Articles(title=form._value_dict['title'],
                           content=form._value_dict['content'],
                           type_id=int(form._value_dict['type_id']),
                           user_info_id=self.get_current_user().nid,
                           cataimg = form._value_dict['cataimg'])

                self.conn.add(art)
        self.conn.commit()

        self.redirect('/home/%s' % (self.get_current_user().username))

# 文件上传，图片
class FileHandler(BaseHandler):
    def post(self, *args, **kwargs):
        file_metas = self.request.files['myFileName']

        for meta in file_metas:
            file_name = meta['filename']
            with open(os.path.join('static', 'img', file_name), 'wb') as up:
                up.write(meta['body'])

        self.set_header('ContentType', 'text/html')
        self.set_header('Charset', 'utf-8')
        imgUrl = '/static/img/%s' % file_name
        self.write(imgUrl)

# 邮箱发送验证码
class SendCodeHandler(BaseHandler):
    def post(self):
        rep = BaseResponse()
        form = ValidateEmailForm()

        if form.valid(self):
            validateEmail = self.conn.query(UserInfo).filter(or_(UserInfo.email == form._value_dict['register_email'],
                                                            UserInfo.username == form._value_dict['register_username'])).first()
            if not validateEmail:
                rep.status = True
                register_email = form._value_dict['register_email']
                code = randomCode()
                rep.data = code
                self.session['RegisterCode'] = code
                sendEmail([register_email,], code)
            else:
                rep.message['register_error'] = '该邮箱或用户名已经被注册过！'
        else:
            rep.message = form._error_dict

        self.write(json.dumps(rep.__dict__))

# 用户注册
class RegisterHandler(BaseHandler):
    def post(self):
        rep = BaseResponse()
        form = RegisterForm()

        if form.valid(self):
            try:
                if form._value_dict['register_code'].upper() == self.session['RegisterCode'].upper():
                    rep.status = True
                    self.session['is_login'] = True

                    self.session['login_username'] = form._value_dict['register_username']

                    password_r = form._value_dict['register_password'].encode()
                    userinfo = UserInfo(username=form._value_dict['register_username'],
                                        password=hashlib.md5(password_r).hexdigest(),
                                        email=form._value_dict['register_email'])

                    self.conn.add(userinfo)
                    self.conn.commit()
                else:
                    rep.message['register_code'] ='验证码错误，啵啵！'
            except:
                rep.message['timeout'] = '验证超时，请重新验证！'

        else:
            rep.message = form._error_dict

        self.write(json.dumps(rep.__dict__))

# 用户登录
class LoginHandler(BaseHandler):
    def post(self):
        rep = BaseResponse()
        form = LoginForm()

        if form.valid(self):
            password_r = form._value_dict['login_password'].encode()

            r = self.conn.query(UserInfo).filter(and_(or_(UserInfo.email == form._value_dict['login_username'], UserInfo.username == form._value_dict['login_username']),
                                                 UserInfo.password == hashlib.md5(password_r).hexdigest())).first()
            if form._value_dict['login_code'].upper() == self.session['CheckCode'].upper():

                if r and r.status != 2:
                    rep.status = True
                    self.session['is_login'] = True
                    self.session['login_username'] = r.username
                else:
                    if not self.conn.query(UserInfo).filter(UserInfo.username == form._value_dict['login_username']).first():
                        rep.message['login_username'] = '您输入的用户名有误!'
                    elif not self.conn.query(UserInfo).filter(UserInfo.password == hashlib.md5(password_r).hexdigest()).first():
                        rep.message['login_password'] = '您输入的密码有误!'
                    elif r.status == 2:
                        rep.message['warning'] = '您的账号已被封，如要解封，请联系管理员！'
                    else:
                        rep.message['login_username'] = '您输入的用户名有误!'
                        rep.message['login_password'] = '您输入的密码有误!'

            else:
                rep.message['login_code'] = '验证码错误，啵啵！'
        else:
            rep.message = form._error_dict
        self.write(json.dumps(rep.__dict__))

# 用户退出
class LogoutHandler(BaseHandler):
    def get(self, *args, **kwargs):
        del self.session['is_login']
        del self.session['login_username']
        self.redirect('/')

# 文章显示
class ArticleHandler(BaseHandler):
    def get(self, aid=None):
        if aid:
            art_id = int(aid)
            last_pag = self.conn.query(Articles).order_by(Articles.nid.desc()).limit(1).first()
            article = self.conn.query(Articles).filter(Articles.nid == art_id).first()
            comment = self.conn.query(Comment).filter(Comment.article_id == art_id).all()
            comment_list = []
            for i in comment:
                 if self.get_current_user():
                     user_info_id = self.get_current_user().nid
                 else:
                     user_info_id = 0
                 a = (i.user.username, i.content, i.reply_id, str(user_info_id), i.ctime, i.nid, i.article_id)
                 comment_list.append(a)
            c = buildTree(comment_list)
            self.render('article.html', article=article, te = commentTree(c), last_pag=last_pag)
        else:
            self.write_error(403)

# 用户评论
class CommentHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self, *args, **kwargs):
        rep = BaseResponse()
        form = CommentForm()

        if form.valid(self):
            rep.status = True
            if int(form._value_dict['reply_id']) == 0:
                form._value_dict['reply_id'] = None
            else:
                form._value_dict['reply_id'] = int(form._value_dict['reply_id'])

            comm = Comment(user_info_id=int(form._value_dict['user_info_id']),
                           reply_id=form._value_dict['reply_id'],
                           content=form._value_dict['content'],
                           article_id=int(form._value_dict['article_id']))
            self.conn.add(comm)
            self.conn.commit()

        else:
            rep.message = form._error_dict

        self.write(json.dumps(rep.__dict__))

# 图片验证码
class CheckCodeHandler(BaseHandler):
    def get(self):
        mstream = io.BytesIO()
        img, code = createValidateCode()
        img.save(mstream, "gif")
        print(code)
        self.session['CheckCode'] = code
        self.write(mstream.getvalue())

def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()

if __name__ == "__main__":
    main()
