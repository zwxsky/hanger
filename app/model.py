#!/usr/bin/env python2
# coding=utf-8
import datetime

from app import db
from utils import escape, string_hash
from sqlalchemy import Column, Integer, String, DateTime

session = db.session

class Person(db.Model):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    password = Column(String)
    avatar = Column(String)
    bio = Column(String)
    created = Column(DateTime)

    def __init__(self, name, email, password):
        self.name = escape(name)
        self.email = escape(email)
        self.password = string_hash(password, salt = self.email)
        self.created = datetime.datetime.now()

    def __repr__(self):
        return "<Person ('%s', '%s')>" % (self.id, self.name)

    def hash_password(self, password):
        return string_hash(password, salt = self.email)

    def change_password(self, password):
        self.password = self.hash_password(password)

    def change_name(self, name):
        self.name = escape(name)

    def change_bio(self, bio):
        self.bio = escape(bio)


def getuser(uid = None, email = None, name = None):
    query = session.query(Person)
    if uid:
        return query.filter_by(id = int(uid)).first()
    elif email:
        return query.filter_by(email = email).first()
    elif name:
        return query.filter_by(name = name).first()
    return None