import re
import datetime
import hashlib
import hmac
import random
import string


secret = "12345"


# Functions that are used for data validation submitted via forms
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")


def valid_username(username):
    return username and USER_RE.match(username)


PASS_RE = re.compile(r"^.{3,20}$")


def valid_password(password):
    return password and PASS_RE.match(password)


EMAIL_RE = re.compile(r'^[\S]+@[\S]+\.[\S]+$')


def valid_email(email):
    return not email or EMAIL_RE.match(email)


# Functions that are used to make and check secure values
def make_secure_val(s):
    return "%s|%s" % (s, hmac.new(secret, s).hexdigest())


def check_secure_val(h):
    h = h.split('|')
    if h[1] == hmac.new(secret, h[0]).hexdigest():
        return h[0]


def make_salt():
    return ''.join([random.choice(string.ascii_letters) for n in xrange(5)])


def make_pw_hash(username, pw, salt=None):
    if not salt:
        salt = make_salt()
    hash = hashlib.sha256(username + pw + salt).hexdigest()
    return "%s|%s" % (hash, salt)


def valid_pw(username, pw, h):
    salt = h.split('|')[1]
    return h == make_pw_hash(username, pw, salt)
