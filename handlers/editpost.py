from base import BaseHandler
from models import *


class EditPostHandler(BaseHandler):
    """Edit blog post handler that is used to edit blog posts."""

    def get(self, post_id):
        have_error = True
        self.post = Post.by_id(int(post_id))

        if not self.post:
            self.redirect('/')
            return

        if not self.user:
            self.redirect('/login')
            return

        template_vars = dict(user=self.user,
                             title=self.post.title,
                             post=self.post.post,
                             page_title="Edit your blog post!")

        if not self.user_owns_post(self.post):
            template_vars["error"] = "You can only edit you own blog posts!"
            template_vars["disable"] = True

        self.render("post_edit.html", **template_vars)

    def post(self, post_id):
        self.title = self.request.get("title")
        self.post = self.request.get("post")

        p = Post.by_id(int(post_id))

        if not p:
            self.redirect('/')
            return

        if not self.user_owns_post(p):
            return self.redirect('/')

        if self.title and self.post:
            p.title = self.title
            p.post = self.post

            p.put()

            self.redirect("/" + str(p.key.id()))
        else:
            template_vars = dict(user=self.user,
                                 title=self.title,
                                 post=self.post,
                                 page_title="Edit your blog post!")

            template_vars['error'] = "we need both a title and some blog text!"

            self.render("post_edit.html", **template_vars)
