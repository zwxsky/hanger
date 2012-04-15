#!/usr/bin/env python2 
# coding=utf-8 
import json
import forms
import utils
import model

from model import getuser
from tornado import web
from jinja2 import Environment, FileSystemLoader

class Base(web.RequestHandler):
    forms = {}
    templname = ''

    def __init__(self, *args, **kwargs):
        super(Base, self).__init__(*args, **kwargs)
        name = str(self.__class__.__name__) # Class name.
        self.name = name

        # default form.
        try:
            self.forms[self.name] = eval('forms.' + self.name)
        except AttributeError:
            pass

        # default template.
        self.templname = self.name + '.html'

    def on_finish(self):
        model.session.commit()
        model.session.close()

    def form_loader(self, key = None):
        '''Return instance of form.'''
        if not key:
            key = self.name
        form = self.forms[key]
        return form(self)

    def form_add(self, form_name):
        '''Add form to self.forms. '''
        self.forms[form_name] = eval('forms.' + form_name)

    def form_validate(self, form, key = None, **kwargs):
        '''Automated handle of Forms validate.'''
        if not key:
            key = self.name # default form key.
        if not form.validate():
            self.render({key: form}, **kwargs)
            return False
        return True

    def render(self, formobj_dict = None, **kwargs):
        # Auto load form.
        formdict = {}
        for key in self.forms:
            formdict[key] = self.forms[key]() # Instance of form.
        if formobj_dict:
            formdict.update(formobj_dict) # merger.
        super(Base, self).render(self.templname, forms = formdict,
            **kwargs)

    def get_error_html(self, status_code, **kwargs):
        if status_code == 404:
            return self.render_string('errors/404.html', **kwargs)
        elif status_code == 500:
            return self.render_string('errors/500.html', **kwargs)
        self.write('Sorry, server error.')

    def render_string(self, template_name, **kwargs):
        '''Template render by Jinja2.'''
        default = {
            'xsrf': self.xsrf_form_html,
            'request': self.request,
            'settings': self.settings,
            'me': self.current_user,
            'static': self.static_url,
            'handler': self,
        }
        kwargs.update(default)
        kwargs.update(self.ui) # Enabled tornado UI methods.
        template = self.get_template(template_name)
        html = template.render(**kwargs) #Render template.
        html = utils.remove_space(html) #remove space in line head and end.
        return html 

    def get_template(self, template_name):
        '''Get jinja2 template object.'''
        env = Environment(
            # load template in file system.
            loader = FileSystemLoader(self.settings['template_path']), 
            auto_reload = self.settings['debug'], #auto reload
            autoescape = False, # auto escape
        )
        template = env.get_template(template_name)
        return template

    def json_write(self, obj):
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(obj))

    def redirect(self, url = None, *args):
        if url == None:
            url = self.get_argument("next", None)
        if url == None:
            url = '/'
        super(Base, self).redirect(url, *args)

    def get_current_user(self):
        cookie = self.get_secure_cookie('user')
        if cookie:
            user_json = json.loads(cookie)
            user = getuser(user_json['id'])
            if user:
                return user
        return False


class Error404(Base):
    '''If url not belonging to any handler, raise 404error.'''
    def get(self):
        raise web.HTTPError(404)

    def post(self):
        raise web.HTTPError(404)
