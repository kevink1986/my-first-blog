import webapp2

from webapp2_extras import jinja2
from functions import *
from models import User


class BaseHandler(webapp2.RequestHandler):
    """Base handler with functions that are used on all pages"""
    @webapp2.cached_property
    def jinja2(self):
        # Returns a Jinja2 renderer cached in the app registry.
        return jinja2.get_jinja2(app=self.app)

    def render_str(self, template, **context):
        return self.jinja2.render_template(template, **context)

    def render(self, template, **context):
        # Renders a template and writes the result to the response.
        self.response.write(self.render_str(template, **context))

    def set_secure_cookie(self, name, s):
        cookie_val = make_secure_val(s)
        self.response.headers.add_header(
            'Set-Cookie',
            '%s=%s; path=/' % (name, cookie_val))

    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and check_secure_val(cookie_val)

    def login(self, user):
        self.set_secure_cookie('user_id', str(user.key.id()))

    def logout(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

    def user_owns_post(self, post):
        return self.user.key == post.user_key

    def user_owns_comment(self, comment):
        return self.user.key == comment.user_key

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and User.by_id(int(uid))