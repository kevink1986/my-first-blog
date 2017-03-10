from base import BaseHandler
from models import *


class RatePostHandler(BaseHandler):
    """Blog handler that is used to render blog posts and
    to add blog comments"""

    def get(self, direction, post_id):
        have_error = False
        self.post = Post.by_id(int(post_id))

        if not self.user:
            self.redirect('/login')
            return

        if not self.post:
            self.redirect('/')
            return

        if self.user_owns_post(self.post):
            error = "error_owner"
            have_error = True
        elif Rate.get_rate_by_user(self.user, self.post) > 0:
            error = "already_rated"
            have_error = True

        if have_error:
            # self.redirect('/' + post_id)
            self.redirect('/%s?error=%s' % (post_id, error))
            return

        r = Rate.register(self.user.key,
                          self.post.key,
                          direction)
        r.put()

        self.redirect('/' + post_id)
