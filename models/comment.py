from google.appengine.ext import ndb
from user import User
from post import Post

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