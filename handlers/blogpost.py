from base import BaseHandler
from models import *

class BlogPostHandler(BaseHandler):
    """Blog handler that is used to render blog posts and
    to add blog comments"""

    def render_blog(self,
                    post_id,
                    error=None,
                    error_comment=None):
        self.post = Post.by_id(int(post_id))
        self.error = self.request.get('error')

        if not self.post:
            self.redirect('/')
            return

        comments = Comment.query(
            Comment.post_key == self.post.key).order(
            Comment.created)

        self.post.up_rates, self.post.down_rates = Rate.get_rates(
            self.post.key)

        template_vars = dict(user=self.user,
                             post=self.post,
                             comments=comments,
                             error=error,
                             error_comment=error_comment)

        if self.error == "error_user":
            template_vars["error"] = """You have to be logged in
                                     to rate posts!"""
        elif self.error == "error_owner":
            template_vars["error"] = """You cannot rate your own
                                     posts!"""

        self.render("blogpost.html", **template_vars)

    def get(self, post_id):
        self.render_blog(post_id)

    def post(self, post_id):
        have_error = False
        self.comment = self.request.get('comment')

        self.post = Post.by_id(int(post_id))

        if not self.post:
            self.redirect('/')
            return

        template_vars = dict(post_id=post_id)

        if not self.user:
            template_vars['error'] = """You have to be logged in to
                                     create comments!"""
            have_error = True

        if not self.comment:
            template_vars["error_comment"] = "Submit a comment!"
            have_error = True

        if have_error:
            self.render_blog(**template_vars)
        else:
            c = Comment.register(self.user.key,
                                 self.post.key,
                                 self.comment)
            c.put()

            self.redirect('/' + post_id)