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


class Post(ndb.Model):
    """Models an individual blog entry with content and date."""
    user_key = ndb.KeyProperty(kind=User)
    title = ndb.StringProperty(required=True)
    post = ndb.TextProperty(required=True)
    created = ndb.DateTimeProperty(auto_now_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)

    @classmethod
    def by_id(cls, bid):
        return cls.get_by_id(bid)

    @classmethod
    def register(cls, user_key, title, post):
        return cls(user_key=user_key,
                   title=title,
                   post=post)

    @property
    def comments(self):
        return Comment.query(
            Comment.post_key == self.key).order(
            Comment.created)


class Comment(ndb.Model):
    """Models an individual comment entry with content and date."""
    user_key = ndb.KeyProperty(kind=User)
    post_key = ndb.KeyProperty(kind=Post)
    comment = ndb.TextProperty(required=True)
    created = ndb.DateTimeProperty(auto_now_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)

    @classmethod
    def by_id(cls, cid):
        return cls.get_by_id(cid)

    @classmethod
    def register(cls, user_key, post_key, comment):
        return cls(user_key=user_key,
                   post_key=post_key,
                   comment=comment)


class Rate(ndb.Model):
    """Models an individual rate entry for a single blog post."""
    user_key = ndb.KeyProperty(kind=User)
    post_key = ndb.KeyProperty(kind=Post)
    rate = ndb.StringProperty(required=True)

    @classmethod
    def get_rates(cls, post_key):
        up = cls.query(cls.post_key == post_key, cls.rate == "up").count()
        down = cls.query(cls.post_key == post_key, cls.rate == "down").count()
        return up, down

    @classmethod
    def get_rate_by_user(cls, user, post):
        return cls.query(cls.user_key == user.key,
            cls.post_key == post.key).count()

    @classmethod
    def register(cls, user_key, post_key, rate):
        return cls(user_key=user_key,
                   post_key=post_key,
                   rate=rate)