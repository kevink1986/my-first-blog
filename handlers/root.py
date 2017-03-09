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