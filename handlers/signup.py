from base import BaseHandler
from functions import *
from models import User


class SignupHandler(BaseHandler):
    """Sign up handler that is used to signup users."""
    def get(self):
        self.render("signup.html")

    def post(self):
        error = False
        self.username = self.request.get("username")
        self.password = self.request.get("password")
        self.password_check = self.request.get("password_check")
        self.email = self.request.get("email")

        template_vars = dict(username=self.username,
                             email=self.email)

        if not valid_username(self.username):
            template_vars['error_username'] = "That's not a valid username."
            error = True
        elif User.by_username(self.username):
            template_vars['error_username'] = "This username already exists."
            error = True

        if not valid_password(self.password):
            template_vars['error_password'] = "That wasn't a valid password."
            error = True
        elif self.password != self.password_check:
            template_vars['error_check'] = "Your passwords didn't match."
            error = True

        if not valid_email(self.email):
            template_vars['error_email'] = "That's not a valid email."
            error = True

        if error:
            self.render('signup.html', **template_vars)
        else:
            u = User.register(self.username,
                              self.password,
                              self.email)
            u.put()

            self.login(u)
            self.redirect('/?')