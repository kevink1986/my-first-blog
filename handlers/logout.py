from base import BaseHandler


class LogoutHandler(BaseHandler):
    """Logout handler that used to logout users."""

    def get(self):
        self.logout()
        self.redirect('/')