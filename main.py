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


EMAIL_RE = re.compile(r'^[\S]+@[\S]+\.[\S]+$')


def valid_email(email):
    return not email or EMAIL_RE.match(email)


# Functions that are used to make and check secure values
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
    return "%s|%s" % (hash, salt)


def valid_pw(username, pw, h):
    salt = h.split('|')[1]
    return h == make_pw_hash(username, pw, salt)


class Handler(webapp2.RequestHandler):
    """Base handler with functions that are used on all pages"""
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


class Blog(ndb.Model):
    """Models an individual blog entry with content and date."""
    user_key = ndb.KeyProperty(kind=User)
    title = ndb.StringProperty(required = True)
    blog = ndb.TextProperty(required = True)
    created = ndb.DateTimeProperty(auto_now_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)

    @classmethod
    def by_id(cls, bid):
        return cls.get_by_id(bid)

    @classmethod
    def register(cls, user_key, title, blog):
        return cls(user_key = user_key,
                   title = title,
                   blog = blog)

    def render(self):
        self._render_text = self.blog.replace('\n', "<br>")
        return render_str("blog_text.html", b = self)


class Comment(ndb.Model):
    """Models an individual comment entry with content and date."""
    user_key = ndb.KeyProperty(kind=User)
    blog_key = ndb.KeyProperty(kind=Blog)
    comment = ndb.TextProperty(required = True)
    created = ndb.DateTimeProperty(auto_now_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)

    @classmethod
    def register(cls, user_key, blog_key, comment):
        return cls(user_key = user_key,
                   blog_key = blog_key,
                   comment = comment)

    def render(self):
        self._render_text = self.comment.replace('\n', "<br>")
        return render_str("comment_text.html", c = self)


class Rate(ndb.Model):
    """Models an individual rate entry for a single blog post."""
    user_key = ndb.KeyProperty(kind=User)
    blog_key = ndb.KeyProperty(kind=Blog)
    rate = ndb.StringProperty(required = True)

    @classmethod
    def get_rates(cls, blog_key):
        up = cls.query(cls.blog_key == blog_key, cls.rate == "up").count()
        down = cls.query(cls.blog_key == blog_key, cls.rate == "down").count()
        return up, down

    @classmethod
    def register(cls, user_key, blog_key, rate):
        return cls(user_key = user_key,
                   blog_key = blog_key,
                   rate = rate)


class RootHandler(Handler):
    """Root handler that renders the the home page with 10 blog posts."""
    def render_front(self, error = None):
        blogs = Blog.query().order(-Blog.created).fetch(10)

        for b in blogs:
            b.up_rates, b.down_rates = Rate.get_rates(b.key)

        self.render("front.html",
                    user = self.user,
                    blogs = blogs,
                    error = error)

    def get(self):
        self.render_front()

    def post(self):
        have_error = False
        self.up_rate = self.request.get('up_rate')
        self.down_rate = self.request.get('down_rate')

        if self.up_rate:
            rate = "up"
            blog_id = self.up_rate
        elif self.down_rate:
            rate = "down"
            blog_id = self.down_rate

        self.blog = Blog.by_id(int(blog_id))

        if not self.user:
            error = "You have to be logged in to rate blogs"
            have_error = True
        elif self.user.key == self.blog.user_key:
            error = "You cannot rate your own blogs"
            have_error = True

        if have_error:
            self.render_front(error = error)
        else:
            r = Rate.register(self.user.key,
                              self.blog.key,
                              rate)
            r.put()

            self.redirect('/')


class SignupHandler(Handler):
    """Sign up handler that is used to signup users."""
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
            u = User.register(self.username,
                              self.password,
                              self.email)
            u.put()

            self.login(u)
            self.redirect('/?')


class LoginHandler(Handler):
    """Login handler that is used to login users."""
    def get(self):
        self.render('login.html')

    def post(self):
        self.username = self.request.get('username')
        self.password = self.request.get('password')

        u = User.login(self.username, self.password)
        if u:
            self.login(u)
            self.redirect('/')
        else:
            template_vars = dict(username = self.username)

            template_vars['error'] = ("This is not a valid username and",
                                      " password combination!")

            self.render("login.html", **template_vars)


class LogoutHandler(Handler):
    """Logout handler that used to logout users."""
    def get(self):
        self.logout()
        self.redirect('/')


class NewPostHandler(Handler):
    """New blog post handler that is used to create new blog posts."""
    def get(self):
        if self.user:
            template_vars = dict(user = self.user)

            template_vars["page_title"] = "Create a new blog post!"

            self.render("newpost.html", **template_vars)
        else:
            self.redirect('/login')

    def post(self):
        self.blog_id = self.request.get("q")
        self.title = self.request.get("title")
        self.blog = self.request.get("blog")

        if self.title and self.blog:
            if self.blog_id:
                b = Blog.by_id(int(self.blog_id))
                b.title = self.title
                b.blog = self.blog
            else:
                b = Blog.register(self.user.key,
                                  self.title,
                                  self.blog)

            b.put()

            self.redirect("/" + str(b.key.id()))
        else:
            error = "we need both a title and some blog text!"
            self.render("newpost.html",
                        user = self.user,
                        title = self.title,
                        blog = self.blog,
                        error=error)


class BlogPostHandler(Handler):
    """Blog handler that is used to render blog posts and
    to add blog comments"""
    def render_blog(self,
                    blog_id,
                    error = None,
                    error_comment = None):
        self.blog = Blog.by_id(int(blog_id))

        if not self.blog:
            self.error(404)
            return

        comments = Comment.query(Comment.blog_key == self.blog.key).order(Comment.created)

        self.blog.up_rates, self.blog.down_rates = Rate.get_rates(self.blog.key)

        template_vars = dict(user = self.user,
                             blog = self.blog,
                             comments = comments,
                             error = error,
                             error_comment = error_comment)

        self.render("blog.html", **template_vars)

    def get(self, blog_id):
        self.render_blog(blog_id)

    def post(self, blog_id):
        have_error = False
        self.up_rate = self.request.get('up_rate')
        self.down_rate = self.request.get('down_rate')
        self.comment = self.request.get('comment')

        self.blog = Blog.by_id(int(blog_id))

        template_vars = dict(blog_id = blog_id)

        if self.up_rate or self.down_rate:
            if not self.user:
                template_vars["error"] = """You have to be logged in
                                         to rate blogs"""
                have_error = True
            elif self.user.key == self.blog.user_key:
                template_vars["error"] = """You cannot rate your own
                                          blogs"""
                have_error = True

            if have_error:
                self.render("blog.html", **template_vars)
                return
            else:
                if self.up_rate:
                    rate = "up"
                else:
                    rate = "down"

                r = Rate.register(self.user.key,
                                  self.blog.key,
                                  rate)
                r.put()

                self.redirect('/' + blog_id)
                return

        if self.comment:
            if not self.user:
                template_vars['error'] = """You have to be logged in to
                                         create comments!"""
                have_error = True

            if have_error:
                self.render_blog(**template_vars)
            else:
                c = Comment.register(self.user.key,
                                     self.blog.key,
                                     self.comment)
                c.put()

                self.redirect('/' + blog_id)
        else:
            template_vars["error_comment"] = "Submit a comment!"
            self.render_blog(**template_vars)


class EditPostHandler(Handler):
    """Edit blog post handler that is used to edit blog posts."""
    def get(self):
        have_error = True
        self.blog_id = self.request.get('b')

        self.blog = Blog.by_id(int(self.blog_id))

        if not self.blog:
            self.error(404)
            return

        template_vars = dict(user = self.user,
                             title = self.blog.title,
                             blog = self.blog.blog,
                             page_title = "Edit your blog post!")

        if not self.user:
            template_vars["error"] = """You have to be logged in to edit
                                     blog posts"""
            template_vars["disable"] = True
        elif self.user.key != self.blog.user_key:
            template_vars["error"] = "You can only edit you own blog posts!"
            template_vars["disable"] = True

        self.render("newpost.html", **template_vars)

    def post(self):
        self.blog_id = self.request.get("b")
        self.title = self.request.get("title")
        self.blog = self.request.get("blog")

        if self.title and self.blog:
            if self.blog_id:
                b = Blog.by_id(int(self.blog_id))
                b.title = self.title
                b.blog = self.blog
            else:
                self.redirect('/')

            b.put()

            self.redirect("/" + str(b.key.id()))
        else:
            template_vars = dict(user = self.user,
                                 title = self.title,
                                 blog = self.blog,
                                 page_title = "Edit your blog post!")

            template_vars['error'] = "we need both a title and some blog text!"

            self.render("newpost.html", **template_vars)


# Map URLs to handlers
routes = [
    webapp2.Route('/', handler=RootHandler, name = 'root'),
    webapp2.Route('/signup', handler=SignupHandler, name = 'signup'),
    webapp2.Route('/login', handler=LoginHandler, name = 'login'),
    webapp2.Route('/logout', handler=LogoutHandler, name = 'logout'),
    webapp2.Route('/new', handler=NewPostHandler, name = 'new_blog'),
    webapp2.Route('/<blog_id:\d+>', handler=BlogPostHandler, name = 'blog'),
    webapp2.Route('/edit', handler=EditPostHandler, name = 'edit_blog')
]

app = webapp2.WSGIApplication(routes, debug=True)
