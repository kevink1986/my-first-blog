from base import BaseHandler
from models import Post


class NewPostHandler(BaseHandler):
    """New blog post handler that is used to create new blog posts."""
    def get(self):
        if self.user:
            template_vars = dict(user=self.user)

            template_vars["page_title"] = "Create a new blog post!"

            self.render("post_edit.html", **template_vars)
        else:
            self.redirect('/login')

    def post(self):
        self.title = self.request.get("title")
        self.post = self.request.get("post")

        if self.title and self.post:
            p = Post.register(self.user.key,
                              self.title,
                              self.post)
            p.put()

            self.redirect("/" + str(p.key.id()))
        else:
            error = "we need both a title and some blog text!"
            self.render("post_edit.html",
                        user=self.user,
                        title=self.title,
                        blog=self.post,
                        error=error)