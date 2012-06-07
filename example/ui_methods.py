#!/usr/bin/env python2.7
# coding=utf-8
import utils

def text2html(handler, text):
    '''Text to HTML.'''
    if not text: return ''
    text = utils.remove_space(text)
    html = ''
    paragraphs = text.split('\n')
    for paragraph in paragraphs:
        html += '<p>%s</p>\n' % paragraph
    return html

def avatar(handler, user, size=200):
    avatar = user.avatar
    if (not avatar) or (avatar == 'gravatar'):
        return utils.gravatar(user.email, size=200)
    return '/media/avatar/%s' % user.avatar # TODO resize.