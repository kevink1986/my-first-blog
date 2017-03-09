from base import BaseHandler
from models import *


class EditCommentHandler(BaseHandler):
    """Edit blog post handler that is used to edit blog posts."""

    def get(self, post_id, comment_id):
        have_error = True
        self.comment = Comment.by_id(int(comment_id))

        if not self.comment:
            self.redirect('/')
            return

        template_vars = dict(user=self.user,
                             post_id=post_id,
                             comment=self.comment.comment,
                             page_title="Edit your blog comment!")

        if not self.user:
            template_vars["error"] = """You have to be logged in to edit
                                     blog comments"""
            template_vars["disable"] = True
        elif not self.user_owns_comment(self.comment):
            template_vars["error"] = "You can only edit you own blog comments!"
            template_vars["disable"] = True

        self.render("comment_edit.html", **template_vars)

    def post(self, post_id, comment_id):
        self.comment = self.request.get("comment")

        if not self.comment:
            self.redirect('/' + str(post_id))
            return

        if self.comment:
            c = Comment.by_id(int(comment_id))
            c.comment = self.comment

            c.put()

            self.redirect("/" + str(post_id))

        else:
            template_vars = dict(user=self.user,
                                 post_id=post_id,
                                 comment=self.comment.comment,
                                 page_title="Edit your blog comment!")

            template_vars['error'] = "we need some blog comment text!"

            self.render("comment_edit.html", **template_vars)
