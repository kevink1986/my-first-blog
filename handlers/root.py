from base import BaseHandler
from models import *


class RootHandler(BaseHandler):
    """Root handler that renders the the home page with 10 blog posts."""

    def render_front(self, error=None):
        posts = Post.query().order(-Post.created).fetch(10)

        for p in posts:
            p.up_rates, p.down_rates = Rate.get_rates(p.key)

        self.render("front.html",
                    user=self.user,
                    posts=posts,
                    error=error)

    def get(self):
        self.render_front()

    def post(self):
        have_error = False
        self.up_rate = self.request.get('up_rate')
        self.down_rate = self.request.get('down_rate')

        if self.up_rate:
            rate = "up"
            post_id = self.up_rate
        elif self.down_rate:
            rate = "down"
            post_id = self.down_rate

        self.post = Post.by_id(int(post_id))

        if not self.user:
            error = "You have to be logged in to rate blogs"
            have_error = True
        elif self.user.key == self.post.user_key:
            error = "You cannot rate your own blogs"
            have_error = True

        if have_error:
            self.render_front(error=error)
        else:
            r = Rate.register(self.user.key,
                              self.post.key,
                              rate)
            r.put()

            self.redirect('/')