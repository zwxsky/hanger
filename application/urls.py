#!/usr/bin/env python2
# coding=utf-8
from view import Home, SignIn, SignUp, SignOut

handlers = [
    (r'/?', Home),
    (r'/sign/in/?', SignIn),
    (r'/sign/up/?', SignUp),
    (r'/sign/out/?', SignOut),
]
