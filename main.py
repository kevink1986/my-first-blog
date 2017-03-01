import os
import re
import datetime
import jinja2
import webapp2

from google.appengine.ext import ndb

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)


def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
    return username and USER_RE.match(username)

PASS_RE = re.compile(r"^.{3,20}$")
def valid_password(password):
    return password and PASS_RE.match(password)

EMAIL_RE  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
def valid_email(email):
    return not email or EMAIL_RE.match(email)


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Blog(ndb.Model):
    """Models an individual blog entry with content and date."""
    title = ndb.StringProperty(required = True)
    blog = ndb.TextProperty(required = True)
    created = ndb.DateTimeProperty(auto_now_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)

    def render(self):
        self._render_text = self.blog.replace('\n', "<br>")
        return render_str("blog_text.html", b = self)

class User(ndb.Model):
    username = ndb.StringProperty(required = True)
    password = ndb.StringProperty(required = True)
    email = ndb.StringProperty()


class MainPage(Handler):
    def get(self):
        blogs = Blog.query().order(-Blog.created).fetch(10)
        self.render("front.html", name = "Blog", blogs = blogs)

class SignupHandler(Handler):
    def get(self):
        self.render("signup.html")

    def post(self):
        error = False
        username = self.request.get("username")
        password = self.request.get("password")
        password_check = self.request.get("password_check")
        email = self.request.get("email")

        template_vars = dict(username = username,
                      email = email)

        if not valid_username(username):
            template_vars['error_username'] = "That's not a valid username."
            error = True

        if not valid_password(password):
            template_vars['error_password'] = "That wasn't a valid password."
            error = True
        elif password != password_check:
            template_vars['error_check'] = "Your passwords didn't match."
            error = True

        if not valid_email(email):
            template_vars['error_email'] = "That's not a valid email."
            error = True

        if error:
            self.render('signup.html', **template_vars)
        else:
            u = User(username = username, password = password, email = email)
            u.put()

            self.response.set_cookie('username',
                                     username,
                                     expires=datetime.datetime.now(),
                                     path='/',
                                     domain='localhost')

            self.redirect('/?')


class NewPostHandler(Handler):
    def get(self):
        name = "New post"
        self.render("newpost.html", name = name)

    def post(self):
        title = self.request.get("title")
        blog = self.request.get("blog")

        if title and blog:
            b = Blog(title = title, blog = blog)
            b.put()

            b = Blog.query().fetch(1)[0]

            self.redirect("/" + str(b.key.id()))
        else:
            error = "we need both a title and some blog text!"
            self.render("newpost.html", title=title, blog=blog, error=error)

class BlogPostHandler(Handler):
    def get(self, blog_id):
        blog = Blog.get_by_id(int(blog_id))

        if not blog:
            self.error(404)
            return

        self.render("blog.html", blog = blog)


app = webapp2.WSGIApplication([('/?', MainPage),
                               ('/signup', SignupHandler),
                               ('login', LoginHandler),
                               ('logout', LogoutHandler),
                               ('/new', NewPostHandler),
                               ('/([0-9]+)', BlogPostHandler)
                               ],
                               debug=True)
