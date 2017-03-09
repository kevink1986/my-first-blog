from google.appengine.ext import ndb
from user import User
from post import Post


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
    def register(cls, user_key, post_key, rate):
        return cls(user_key=user_key,
                   post_key=post_key,
                   rate=rate)
