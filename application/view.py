#!/usr/bin/env python2
# coding=utf-8
import os
import json
import traceback
import httplib
import re
import orm
import utils
import forms
import StringIO
import Image

from jinja2 import Environment, FileSystemLoader
from tornado import web

class Base(web.RequestHandler):
    templname = ''
    Form = None


    def get_current_user(self):
        cookie = self.get_secure_cookie('user')
        if not cookie: return False
        user = json.loads(cookie)
        user = orm.Person.get_by(id=int(user['id']))
        return user

    def json_write(self, obj):
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(obj))

    def render_string(self, template_name, **kwargs):
        '''Template render by Jinja2.'''
        methods = kwargs
        methods.update(
            {
                'xsrf': self.xsrf_form_html,
                'request': self.request,
                'settings': self.settings,
                'me': self.current_user,
                'url': self.settings['site_url'],
                'static': self.static_url,
                'handler': self,
            })
        methods.update(self.ui)
        template = self.get_template(template_name)
        html = template.render(methods)
        return utils.remove_space(html)

    def get_template(self, template_name):
        '''Get jinja2 template object.'''
        env = Environment(
            loader = FileSystemLoader(self.settings['template_path']),
            auto_reload = self.settings['debug'],
            autoescape = False,
        )
        template = env.get_template(template_name)
        return template

    def get_error_html(self, status_code, **kwargs):
        code = status_code
        try:
            # add stack trace information
            message = httplib.responses[status_code]
            exception = "%s\n\n%s" % (kwargs["exception"],
                traceback.format_exc())
            template = "error.html"
            if code == 404: template = 'error_404.html'
            return self.render_string(
                template,
                code=code,
                message=message,
                exception=exception,
            )
        except Exception:
            return super(Base, self).get_error_html(status_code, **kwargs)

    def redirect(self, to=None):
        if not to:
            to = self.get_argument("next", None)
            if not to: to = '/'
        super(Base, self).redirect(to)

    def get_obj(self, Obj, obj_id=None):
        if not obj_id:
            obj = Obj.query.all()
        else:
            obj = Obj.get_by(id = int(id))
        if not obj:
            raise web.HTTPError(404)
        return obj

    def form_validate(self, form, **kwargs):
        if not form.validate():
            self.render(self.templname, form = form, **kwargs)
            return False
        return True


class Error404(Base):
    def get(self):
        raise web.HTTPError(404)


class Home(Base):
    def get(self):
        self.render('home.html')


class Sign(Base):
    def login(self, user):
        '''LogIn user to secure cookie'''
        json_str = json.dumps(
            {
                'id': user.id,
                'name': user.name,
                'email': user.email,
            }
        )
        self.set_secure_cookie("user", json_str)


class SignIn(Sign):
    Form = forms.SignIn
    templname = 'sign.in.html' #tamplate file name.
    def get(self):
        self.render(self.templname, form=self.Form())

    def post(self):
        form = self.Form(self)
        if self.form_validate(form):
            user = orm.Person.get_by(email=form.email.data)
            self.login(user)
            self.redirect()


class SignUp(Sign):
    templname = 'sign.up.html'
    Form = forms.SignUp

    def get(self):
        self.render(self.templname, form=self.Form())
    
    def post(self):
        form = self.Form(self)
        if self.form_validate(form):
            user = orm.Person(
                name=form.name.data,
                password=form.password.data,
                email=form.email.data,
            )
            orm.session.commit()
            self.login(user)
            self.redirect()


class SignOut(Sign):
    def get(self):
        self.set_secure_cookie('user', '')
        self.redirect()


class PersonPage(Base):
    def get(self, uid=None):
        if uid:
            person = get_obj(orm.Person, int(uid))
        elif self.current_user:
            person = self.current_user
        else:
            raise web.HTTPError(404)
        self.render('person.page.html', person=person)


class Settings(Base):
    Form = forms.Settings
    templname = 'settings.html'

    @web.authenticated
    def get(self):
        self.render(self.templname, form=self.Form())
    
    @web.authenticated
    def post(self):
        #Upload avatar
        files = self.request.files
        if files:
            self.avatar_uploads(files['avatar'][0])
            return
        #normal settings
        form = self.Form(self)
        if self.form_validate(form):
            new_password = form.new_password.data
            name = form.name.data
            if new_password:
                self.current_user.password = utils.string_hash(new_password)
            if name:
                self.current_user.name = name
            orm.session.commit()
            self.redirect()

    def avatar_uploads(self, avatar):
        #ToDo
        #* 支持Nginx upload module.
        #* 文件上传class。
        #* 限制每日上传次数
        if self.avatar_validate(avatar):
            self.remove_old_avatar()
            filename = self.avatar_save(avatar)
            self.current_user.avatar = filename
            orm.session.commit()
            self.redirect('/settings')
        return
    
    def avatar_validate(self, avatar):
        avatar_error = None
        max_size = 1024 * 1024 * 2 #3MB
        try:
            Image.open(StringIO.StringIO(avatar['body']))
        except IOError:
            avatar_error = u'请上传图片'
        if len(avatar['body']) > max_size:
            avatar_error = u'文件太大！最多能上传2mb的图片。'
        # todo : validation file size
        if avatar_error:
            self.render(self.templname, form = self.Form(),
                avatar_error = avatar_error)
            return False
        return True

    def remove_old_avatar(self):
        old_file = self.current_user.avatar
        if old_file:
            os.remove(self.settings['avatar_path'] + old_file)

    def avatar_save(self, avatar):
        path = self.settings['avatar_path']
        if not os.path.exists(path): os.mkdir(path)
        uid = str(self.current_user.id)
        suffix = avatar['filename'].split('.')[-1]
        filename = uid + '.' + suffix
        avatar_file = Image.open(StringIO.StringIO(avatar['body']))
        avatar_file = self.avatar_resize(avatar_file)
        avatar_file.save(path + filename, avatar_file.format)
        return filename

    def avatar_resize(self, avatar):
        height = 160
        weight = 160
        return avatar.resize((height, weight))
