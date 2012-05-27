#!/usr/bin/env python2
# coding=utf-8
'''
WTForm with tornado.
'''
import wtforms

from wtforms import TextField
from wtforms import IntegerField as _IntegerField
from wtforms import DecimalField as _DecimalField
from wtforms import DateField as _DateField
from wtforms.widgets import Input

class FormDict(dict):
    '''Tornado handler arguments to MultiDict, wtforms required.'''
    def __init__(self, handler):
        self.handler = handler

    def __iter__(self):
        return iter(self.handler.request.arguments)

    def __len__(self):
        return len(self.handler.request.arguments)

    def __contains__(self, name):
        return (name in self.handler.request.arguments)

    def getlist(self, name):
        return self.handler.get_arguments(name, strip=False)


class Form(wtforms.Form):
    '''
    Base form class
    '''
    def __init__(self, handler = None, **kwargs):
        formdata = None
        if handler:
            formdata = FormDict(handler)
            self.current_user = handler.current_user
            self.files = handler.request.files
        super(Form, self).__init__(formdata = formdata, **kwargs)


#some html5 field
#form https://github.com/rduplain/flask-wtf/
class DateInput(Input):
    """
    Creates `<input type=date>` widget
    """
    input_type = "date"


class NumberInput(Input):
    """
    Creates `<input type=number>` widget
    """
    input_type="number"


class RangeInput(Input):
    """
    Creates `<input type=range>` widget
    """
    input_type="range"


class URLInput(Input):
    """
    Creates `<input type=url>` widget
    """
    input_type = "url"


class EmailInput(Input):
    """
    Creates `<input type=email>` widget
    """

    input_type = "email"


class SearchInput(Input):
    """
    Creates `<input type=search>` widget
    """

    input_type = "search"

class TelInput(Input):
    """
    Creates `<input type=tel>` widget
    """

    input_type = "tel"


class SearchField(TextField):
    """
    **TextField** using **SearchInput** by default
    """
    widget = SearchInput()


class DateField(_DateField):
    """
    **DateField** using **DateInput** by default
    """
 
    widget = DateInput()


class URLField(TextField):
    """
    **TextField** using **URLInput** by default
    """
 
    widget = URLInput()
    

class EmailField(TextField):
    """
    **TextField** using **EmailInput** by default
    """
 
    widget = EmailInput()

class TelField(TextField):
    """
    **TextField** using **TelInput** by default
    """

    widget = TelInput()


class IntegerField(_IntegerField):
    """
    **IntegerField** using **NumberInput** by default
    """

    widget = NumberInput()


class DecimalField(_DecimalField):
    """
    **DecimalField** using **NumberInput** by default
    """

    widget = NumberInput()


class IntegerRangeField(_IntegerField):
    """
    **IntegerField** using **RangeInput** by default
    """

    widget = RangeInput()


class DecimalRangeField(_DecimalField):
    """
    **DecimalField** using **RangeInput** by default
    """

    widget = RangeInput()