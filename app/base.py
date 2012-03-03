#!/usr/bin/env python2 
# coding=utf-8 
import json
import utils
import forms

from tornado import web
from model import getitem, Person
from jinja2 import Environment, FileSystemLoader

class BaseHandler(web.RequestHandler):
    def __init__(self, *args):
        super(BaseHandler, self).__init__(*args)
        name = str(self.__class__.__name__) # Class name.
        self.name = name


class FormHandler(BaseHandler):
    forms = {}

    def __init__(self, *args):
        super(FormHandler, self).__init__(*args)
        # default form.
        try:
            self.forms[self.name] = eval('forms.' + self.name)
        except AttributeError:
            pass

    def form_loader(self, key = None):
        '''Return instance of form.'''
        if not key:
            key = self.name
        form = self.forms[self.name]
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
        else:
            return True


class TemplateHandler(FormHandler):
    templname = ''

    def __init__(self, *args):
        super(TemplateHandler, self).__init__(*args)
        # default template.
        self.templname = self.name + '.html'

    def render(self, formobj_dict = None, **kwargs):
        # Auto load form.
        formdict = {}
        for key in self.forms:
            formdict[key] = self.forms[key]() # Instance of form.
        if formobj_dict:
            formdict.update(formobj_dict) # merger.
        super(TemplateHandler, self).render(self.templname, forms = formdict,
            **kwargs)

    def get_error_html(self, status_code, **kwargs):
        if status_code == 404:
            return self.render_string('errors/404.html', **kwargs)
        elif status_code == 500:
            return self.render_string('errors/500.html', **kwargs)
        else:
            self.write('Sorry, server error.')
        return


class JinjaHandler(TemplateHandler):
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


class Base(JinjaHandler):
    def json_write(self, obj):
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(obj))

    def redirect(self, path = None):
        if not path:
            path = self.get_argument("next", None)
            if not path:
                path = '/'
        super(Base, self).redirect(path)

    def get_current_user(self):
        cookie = self.get_secure_cookie('user')
        if not cookie:
            return False
        user_json = json.loads(cookie)
        user = getitem(Person, user_json['id'], show_error = False)
        if not user:
            return False
        return user
