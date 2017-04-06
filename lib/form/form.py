#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/3/29 8:46
# @Author  : Sugare
# @Site    : 30733705@qq.com
# @File    : form.py
# @Software: PyCharm

import re
import random

class BaseResponse:
    def __init__(self):
        self.status = False
        self.data = None
        self.summary = None
        self.message = {}

class BaseField(object):
    def __init__(self, error_dict=None, required=True):
        self.error_dict = {}
        if error_dict:
            self.error_dict.update(error_dict)

        self.required = required
        self.error = None
        self.is_valid = False
        self.value = None

    def validate(self, name, input_value):
        if not self.required:
            self.is_valid = True
            self.value = input_value
        else:
            if not input_value.strip():
                if self.error_dict.get('required', None):
                    self.error = self.error_dict['required']
                else:
                    self.error = "%s is required" % name
            else:
                ret = re.match(self.REGULAR, input_value)
                if ret:
                    self.is_valid = True
                    self.value = ret.group()            # input_value
                else:
                    if self.error_dict.get('valid', None):
                        self.error = self.error_dict['valid']
                    else:
                        self.error = "%s is invalid" % name

class UsernameField(BaseField):
    def __init__(self):
        self.REGULAR = "^[a-zA-Z0-9_@.]{4,16}$"
        super(UsernameField, self).__init__(error_dict={'valid':'用户名需大于4个字符'},required=True)

class EmailField(BaseField):
        def __init__(self):
            self.REGULAR = "^([a-zA-Z0-9_-])+@([a-zA-Z0-9_-])+(.[a-zA-Z0-9_-])+"
            self.error_dict = {}
            super(EmailField, self).__init__(error_dict=None, required=True)

class StringField(BaseField):
        def __init__(self):
            self.REGULAR = ".*"
            super(StringField, self).__init__(error_dict=None, required=True)

class CataImgField(BaseField):
    def __init__(self,error_dict=None, required=False):
        self.REGULAR = ".*"
        super(CataImgField, self).__init__(error_dict=None, required=False)

class NumField(BaseField):
        def __init__(self):
            self.REGULAR = "\d+"
            super(NumField, self).__init__(error_dict=None, required=True)

class ValidateCodeField(BaseField):
    def __init__(self):
        self.REGULAR = "^[a-zA-Z0-9]{4}$"
        super(ValidateCodeField, self).__init__(error_dict=None, required=True)

class CheckBoxField:
    def __init__(self, error_dict=None, required=False):
        self.error_dict = {}
        if error_dict:
            self.error_dict.update(error_dict)

        self.required = required
        self.error = None
        self.is_valid = False
        self.value = None

    def validate(self, name, input_value):
        if not self.required:
            self.is_valid = True
            self.value = input_value
        else:
            if not input_value:
                if self.error_dict.get('required'):
                    self.error = self.error_dict['required']
                else:
                    self.error = "%s is required" % name
            else:
                self.is_valid = True
                self.value = input_value

class FileField:
    def __init__(self, error_dict=None, required=True):
        self.REGULAR = "^(\w+/.pdf)|(\w+\.mp3)|(\w+\.py)$"
        self.error_dict = {}
        if error_dict:
            self.error_dict.update(error_dict)

        self.required = required
        self.error = None
        self.is_valid = True
        self.value = []
        self.name = None

    def validate(self, name, all_file_name_list):
        self.name = name

        if not self.required:
            self.is_valid = True
            self.value = all_file_name_list
        else:
            if not all_file_name_list:
                self.is_valid = False
                if self.error_dict.get('required', None):
                    self.error = self.error_dict['required']
                else:
                    self.error = "%s is required" % name
            else:
                for file_name in all_file_name_list:
                    ret = re.match(self.REGULAR, file_name)
                    if not ret:
                        self.is_valid = False
                        if self.error_dict.get('valid', None):
                            self.error = self.error_dict['valid']
                        else:
                            self.error = "%s is invalid" % name
                        break
                    else:
                        self.value.append(file_name)
    '''
    def save(self, request, path=None):
        file_metas = request.files.get(self.name)

        temp_list = []
        for meta in file_metas:
            file_name = meta['filename']
            new_file_name = os.path.join(path, file_name)

            if file_name and file_name in self.value:
                temp_list.append(new_file_name)
                with open(file_name, 'wb') as up:
                    up.write(meta['body'])
            self.value = temp_list
    '''

class BaseForm(object):
    def __init__(self):
        self._value_dict = {}
        self._error_dict = {}
        self._valid_status = True

    def valid(self, handler):

        for field_name, field_obj in self.__dict__.items():
            # if field_name.startswitch('_'):
            if field_name[0] == '_':
                continue

            if type(field_obj) == CheckBoxField:

                    post_value = handler.get_arguments(field_name)

            elif type(field_obj) == FileField:
                post_value = []
                file_list = handler.request.files.get(field_name, [])
                for file_item in file_list:
                    post_value.append(file_item['filename'])

            else:
                post_value = handler.get_argument(field_name, None)

            field_obj.validate(field_name, post_value)
            if field_obj.is_valid:
                self._value_dict[field_name] = field_obj.value
            else:
                self._error_dict[field_name] = field_obj.error
                self._valid_status = False
        # print(self._value_dict)
        return self._valid_status

class RegisterForm(BaseForm):
    def __init__(self):
        self.register_username = UsernameField()
        self.register_email = EmailField()
        self.register_code = ValidateCodeField()
        self.register_password = StringField()

        super(RegisterForm, self).__init__()

class CommentForm(BaseForm):
    def __init__(self):
        self.user_info_id = NumField()
        self.reply_id = NumField()
        self.article_id = NumField()
        self.content = StringField()

        super(CommentForm, self).__init__()

class LoginForm(BaseForm):
    def __init__(self):
        self.login_username = UsernameField()
        self.login_password = StringField()
        self.login_code = ValidateCodeField()
        self.login_session = CheckBoxField()


        super(LoginForm, self).__init__()

class ArticleForm(BaseForm):
    def __init__(self):

        self.title = StringField()
        self.cataimg = CataImgField()
        self.type_id = NumField()
        self.content = StringField()

        super(ArticleForm, self).__init__()

class ValidateEmailForm(BaseForm):
    def __init__(self):
        self.register_username = UsernameField()
        self.register_email = EmailField()

        super(ValidateEmailForm, self).__init__()

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

if __name__ == '__main__':
    pass