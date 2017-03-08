from base import BaseHandler
from models import *

class DeleteCommentHandler(BaseHandler):
    """Edit blog post handler that is used to edit blog posts."""
    def get(self, post_id, comment_id):
        self.comment = Comment.by_id(int(comment_id))

        if not self.comment:
            self.redirect('/' + str(post_id))
            return

        template_vars = dict(user=self.user,
                             post_id=post_id,
                             comment=self.comment,
                             page_title="Delete your blog comment!")

        self.render("comment_delete.html", **template_vars)

    def post(self, post_id, comment_id):
        c = Comment.by_id(int(comment_id))

        if not self.user_owns_comment(c):
            return self.redirect('/')

        c.key.delete()

        self.redirect('/' + str(post_id))