from google.appengine.ext import ndb
from functions import *


class User(ndb.Model):
    """Models an individual User entry"""
    username = ndb.StringProperty(required=True)
    pw_hash = ndb.StringProperty(required=True)
    email = ndb.StringProperty()

    @classmethod
    def by_id(cls, uid):
        return cls.get_by_id(uid)

    @classmethod
    def by_username(cls, username):
        u = cls.query(cls.username == username).get()
        return u

    @classmethod
    def register(cls, username, pw, email=None):
        pw_hash = make_pw_hash(username, pw)
        return cls(username=username,
                   pw_hash=pw_hash,
                   email=email)

    @classmethod
    def login(cls, username, pw):
        u = cls.by_username(username)
        if u and valid_pw(username, pw, u.pw_hash):
            return u
