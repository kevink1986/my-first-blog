from base import BaseHandler
from models import User


class LoginHandler(BaseHandler):
    """Login handler that is used to login users."""

    def get(self):
        self.render('login.html')

    def post(self):
        self.username = self.request.get('username')
        self.password = self.request.get('password')

        u = User.login(self.username, self.password)
        if u:
            self.login(u)
            self.redirect('/')
        else:
            template_vars = dict(username=self.username)

            template_vars['error'] = "This is not a valid username and password combination!"

            self.render("login.html", **template_vars)