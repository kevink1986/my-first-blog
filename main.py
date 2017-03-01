import os
import jinja2
import webapp2

from google.appengine.ext import ndb

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)


def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

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

class MainPage(Handler):
    def get(self):
        blogs = Blog.query().order(-Blog.created).fetch(10)
        self.render("front.html", name = "Blog", blogs = blogs)

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
                               ('/new', NewPostHandler),
                               ('/([0-9]+)', BlogPostHandler)
                               ],
                               debug=True)
