#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/4/6 10:05
# @Author  : Sugare
# @Site    : 30733705@qq.com
# @File    : others.py
# @Software: PyCharm
import random
import collections
import smtplib
from email.mime.text import MIMEText
from email.header import Header

# 发送邮件
def sendEmail(email_list, content, subject='科技小组--用户注册验证'):
    mail_host = "smtp.qq.com"  # 设置服务器
    mail_user = "30733705@qq.com"  # 用户名
    mail_pass = "xxzvhujurvsibiah"  # 口令,QQ邮箱是输入授权码，在qq邮箱设置 里用验证过的手机发送短信获得，不含空格

    sendmail = """
    <h3>亲爱的用户：</h3>
    <p style="text-indent:2em;">您好！</p>
    <p style="text-indent:2em;">您正在进行邮箱验证，</p>
    <p style="text-indent:2em;">请在验证码输入框中输入此次验证码：
    <strong> %s </strong> 以完成验证。</p>
    <p style="text-indent:2em;">如非本人操作，请忽略此邮件，由此给您带来的不便请谅解！</p>
    """ % content

    message = MIMEText(sendmail, 'html', 'utf-8')
    message['From'] = Header("科技小组", 'utf-8')
    message['To'] =  Header("Baby", 'utf-8')
    message['Subject'] = Header(subject, 'utf-8')


    try:
        smtpObj = smtplib.SMTP_SSL(mail_host, 465)
        smtpObj.login(mail_user,mail_pass)
        smtpObj.sendmail(mail_user, email_list, message.as_string())
        smtpObj.quit()
        print(u"邮件发送成功")
    except smtplib.SMTPException:
        print('fuck')

# 发送邮箱随机生成4位验证码
def randomCode(len=4):
    code_list = []
    for i in range(10):
        code_list.append(str(i))
    for i in range(65, 91):
        code_list.append(chr(i))
    for i in range(97, 123):
        code_list.append(chr(i))
    myslice = random.sample(code_list, len)
    verification_code = ''.join(myslice)
    return verification_code

# 用户评论缩进显示 html
TEMP = """

    <div class="item" style="margin:5px 0 0 %spx;">
        <a class="item-img" href="#">
            <img class="img-circle" style="border:1px solid;" src="/static/img/tou.jpg" alt="">
        </a>

        <div class="item-content" style="margin: -4px 0 0 10px;">
            <h4> %s : </h4>
            <h4> 评论：%s</h4>
            <p style="border-bottom: 1px solid #f3f3f3;">
                <span> %s </span>
                <a onclick="openForm(this);"> 回 复 </a>
            </p>
        </div>
        <form class="hidden" method="POST" action="/comment" user_info_id=%s reply_id=%s article_id=%s>
            <textarea name="comment" class="form-control" cols='1' rows="3" placeholder="请输入评论 限200字!"></textarea>
            <button style='margin-top:-30px;' type="button" class="btn btn-default pull-right" onclick="replyComment(this);">提交</button>
        </form>

"""

# 递归查看是否有回复
def treeSearch(d_dic, comment_obj):
    for k, v_dic in d_dic.items():
        if k[5] == comment_obj[2]:
            d_dic[k][comment_obj] = collections.OrderedDict()
            return
        else:
            treeSearch(d_dic[k], comment_obj)

# 生成评论树
def buildTree(comment_list):

    comment_dic = collections.OrderedDict()

    for comment_obj in comment_list:
        if comment_obj[2] is None:      # 1层评论
            comment_dic[comment_obj] = collections.OrderedDict()
        else:
            treeSearch(comment_dic, comment_obj)
    return comment_dic

def generateCommentHtml(sub_comment_dic, margin_left_val):
    html = ''
    for k, v_dic in sub_comment_dic.items():
        html += TEMP %(margin_left_val, k[0], k[1], k[4], k[3], k[5],k[6])
        if v_dic:
            html += generateCommentHtml(v_dic, margin_left_val)

        html += '</div>'
    html += ''
    return html

def commentTree(comment_dic):
    html = ''

    for k,v in comment_dic.items():
        html += TEMP %(0, k[0], k[1], k[4], k[3], k[5],k[6])
        html += generateCommentHtml(v, 20)
        html += "</div>"
    return html

def createSessionId():
    import hashlib
    import time
    obj = hashlib.md5()
    obj.update(bytes(str(time.time()), encoding='utf-8'))
    random_str = obj.hexdigest()
    return random_str



if __name__ == '__main__':
    pass
