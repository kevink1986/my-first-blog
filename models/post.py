from google.appengine.ext import ndb
from user import User


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

    # @property
    # def comments(self):
    #     return Comment.query(
    #         Comment.post_key == self.key).order(
    #         Comment.created)
