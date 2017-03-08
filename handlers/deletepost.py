from base import BaseHandler
from models import *

class DeletePostHandler(BaseHandler):
    """Edit blog post handler that is used to edit blog posts."""
    def get(self, post_id):
        self.post = Post.by_id(int(post_id))

        if not self.post:
            self.redirect('/')
            return

        template_vars = dict(user=self.user,
                             post=self.post,
                             page_title="Delete your blog post!")

        self.render("post_delete.html", **template_vars)

    def post(self, post_id):
        p = Post.by_id(int(post_id))

        if not self.user_owns_post(p):
            return self.redirect('/')

        p.key.delete()

        self.redirect('/')