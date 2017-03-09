from base import BaseHandler
from models import *

class DeletePostHandler(BaseHandler):
    """Edit blog post handler that is used to edit blog posts."""
    def get(self, post_id):
        self.post = Post.by_id(int(post_id))

        if not self.post:
            self.redirect('/')
            return

        if not self.user:
            self.redirect('/login')
            return

        template_vars = dict(user=self.user,
                             post=self.post,
                             page_title="Delete your blog post!")

        self.render("post_delete.html", **template_vars)

    def post(self, post_id):
        self.post = Post.by_id(int(post_id))

        if not self.post:
            self.redirect('/')
            return

        if not self.user_owns_post(self.post):
            return self.redirect('/')

        self.post.key.delete()

        self.redirect('/')