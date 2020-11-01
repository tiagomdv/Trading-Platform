import requests, sqlite3
import urllib.parse

from functools import wraps
from flask import request, redirect, render_template, session

def login_req(f):

    @wraps(f)
    def wrapper(*args, **kwargs):
        if session.get("user_id") is None:
            return render_template("login.html", logError="LOGIN required!")
        return f(*args, **kwargs)
    return wrapper