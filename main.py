import os
import re
import datetime
import hashlib
import hmac
import random
import string
import jinja2
import webapp2

from google.appengine.ext import ndb

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

secret = "12345"

# Function that is used to render blog content
def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

# Functions that are used for data validation submitted via forms
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
    return username and USER_RE.match(username)

PASS_RE = re.compile(r"^.{3,20}$")
def valid_password(password):
    return password and PASS_RE.match(password)

EMAIL_RE  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
def valid_email(email):
    return not email or EMAIL_RE.match(email)

# Hashing values
def make_secure_val(s):
    return "%s|%s" % (s, hmac.new(secret, s).hexdigest())

def check_secure_val(h):
    h = h.split('|')
    if h[1] == hmac.new(secret, h[0]).hexdigest():
        return h[0]

def make_salt():
    return ''.join([random.choice(string.ascii_letters) for n in xrange(5)])

def make_pw_hash(username, pw, salt = None):
    if not salt:
        salt = make_salt()
    hash = hashlib.sha256(username + pw + salt).hexdigest()
    return "%s|%s" % (hash,salt)

def valid_pw(username, pw, h):
    salt = h.split('|')[1]
    return h == make_pw_hash(username, pw, salt)

# Base Handler
class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

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

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and User.by_id(int(uid))


class Blog(ndb.Model):
    """Models an individual blog entry with content and date."""
    title = ndb.StringProperty(required = True)
    blog = ndb.TextProperty(required = True)
    created = ndb.DateTimeProperty(auto_now_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)

    @classmethod
    def by_id(cls, bid):
        return cls.get_by_id(bid)

    @classmethod
    def register(cls, title, blog):
        return cls(title = title,
                    blog = blog)

    def render(self):
        self._render_text = self.blog.replace('\n', "<br>")
        return render_str("blog_text.html", b = self)

class User(ndb.Model):
    """Models an individual User entry"""
    username = ndb.StringProperty(required = True)
    pw_hash = ndb.StringProperty(required = True)
    email = ndb.StringProperty()

    @classmethod
    def by_id(cls, uid):
        return cls.get_by_id(uid)

    @classmethod
    def by_username(cls, username):
        u = cls.query(cls.username == username).get()
        return u

    @classmethod
    def register(cls, username, pw, email = None):
        pw_hash = make_pw_hash(username, pw)
        return cls(username = username,
                    pw_hash = pw_hash,
                    email = email)

    @classmethod
    def login(cls, username, pw):
        u = cls.by_username(username)
        if u and valid_pw(username, pw, u.pw_hash):
            return u

class Comment(ndb.Model):
    """Models an individual comment entry with content and date."""
    user_key = ndb.KeyProperty(kind=User)
    blog_key = ndb.KeyProperty(kind=Blog)
    comment = ndb.TextProperty(required = True)
    created = ndb.DateTimeProperty(auto_now_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)

#     def create_entity_with_parent_keys():
#     account_key = ndb.Key(Account, 'sandy@example.com')

#     # Ask Datastore to allocate an ID.
#     new_id = ndb.Model.allocate_ids(size=1, parent=account_key)[0]

#     # Datastore returns us an integer ID that we can use to create the message
#     # key
# message_key = ndb.Key('Message', new_id, parent=account_key)

#     @classmethod
#     def query_book(cls, ancestor_key):
#         return cls.query(ancestor=ancestor_key).order(-cls.date)

    @classmethod
    def register(cls, user_key, blog_key, comment):
        return cls(user_key = user_key,
                   blog_key = blog_key,
                   comment = comment)

    def render(self):
        self._render_text = self.comment.replace('\n', "<br>")
        return render_str("comment_text.html", c = self)

class MainPage(Handler):
    def get(self):
        blogs = Blog.query().order(-Blog.created).fetch(10)
        self.render("front.html", name = "Blog", blogs = blogs)

class SignupHandler(Handler):
    def get(self):
        self.render("signup.html")

    def post(self):
        error = False
        self.username = self.request.get("username")
        self.password = self.request.get("password")
        self.password_check = self.request.get("password_check")
        self.email = self.request.get("email")

        template_vars = dict(username = self.username,
                      email = self.email)

        if not valid_username(self.username):
            template_vars['error_username'] = "That's not a valid username."
            error = True
        elif User.by_username(self.username):
            template_vars['error_username'] = "This username already exists."
            error = True

        if not valid_password(self.password):
            template_vars['error_password'] = "That wasn't a valid password."
            error = True
        elif self.password != self.password_check:
            template_vars['error_check'] = "Your passwords didn't match."
            error = True

        if not valid_email(self.email):
            template_vars['error_email'] = "That's not a valid email."
            error = True

        if error:
            self.render('signup.html', **template_vars)
        else:
            u = User.register(self.username, self.password, self.email)
            u.put()

            self.login(u)
            self.redirect('/?')

class LoginHandler(Handler):
    def get(self):
        self.render('login.html')

    def post(self):
        self.username = self.request.get('username')
        self.password = self.request.get('password')

        u = User.login(self.username, self.password)
        if u:
            self.login(u)
            self.redirect('/')

class LogoutHandler(Handler):
    def get(self):
        self.logout()
        self.redirect('/')

class NewPostHandler(Handler):
    def get(self):
        name = "New post"
        if self.user:
            self.render("newpost.html", name = name)
        else:
            self.redirect('/login')

    def post(self):
        self.title = self.request.get("title")
        self.blog = self.request.get("blog")

        if self.title and self.blog:
            b = Blog.register(self.title, self.blog)
            b.put()

            self.redirect("/" + str(b.key.id()))
        else:
            error = "we need both a title and some blog text!"
            self.render("newpost.html", title=title, blog=blog, error=error)

class BlogPostHandler(Handler):
    def get(self, blog_id):
        blog = Blog.by_id(int(blog_id))

        if not blog:
            self.error(404)
            return

        comments = Comment.query(Comment.blog_key == blog.key).order(-Comment.created)

        self.render("blog.html", blog = blog, comments = comments)

    def post(self, blog_id):
        self.comment = self.request.get('comment')

        if self.comment:
            blog = Blog.by_id(int(blog_id))
            c = Comment.register(self.user.key, blog.key, self.comment)
            c.put()

            self.redirect('/' + blog_id)
        else:
            error = "Submit a comment!"
            blog = Blog.by_id(int(blog_id))
            self.render("blog.html", blog = blog, error = error)


app = webapp2.WSGIApplication([('/?', MainPage),
                               ('/signup', SignupHandler),
                               ('/login', LoginHandler),
                               ('/logout', LogoutHandler),
                               ('/new', NewPostHandler),
                               ('/([0-9]+)', BlogPostHandler)
                               ],
                               debug=True)


# # Map URLs to handlers
# routes = [
#   Route('/', handler='handlers.RootHandler'),
#   Route('/profile', handler='handlers.ProfileHandler', name='profile'),
#   Route('/preference', handler='handlers.PreferenceHandler', name='preference'),
#   Route('/event', handler='handlers.EventHandler', name='event'),

#   Route('/logout', handler='handlers.AuthHandler:logout', name='logout'),
#   Route('/auth/<provider>',
#     handler='handlers.AuthHandler:_simple_auth', name='auth_login'),
#   Route('/auth/<provider>/callback',
#     handler='handlers.AuthHandler:_auth_callback', name='auth_callback')
# ]

# app = WSGIApplication(routes, config=app_config, debug=True)
