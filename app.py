from flask import Flask, render_template, session, request
from tempfile import mkdtemp
from flask_session import Session

from helper import lookup

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route('/')
def hello_world():
    quote = lookup("TSLA")
    return render_template("index.html", quote=quote)

@app.route('/market')
def market_func():
    quote = lookup("AAPL")
    return render_template("market.html", quote=quote)

@app.route('/wallet')
def wallet():
    quote = lookup("AMZN")
    return render_template("wallet.html", quote=quote)

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        if username == "":
            msg = "username."
            return render_template("login.html", username=username, msg=msg)
        
        password = request.form.get("password")
        if password == "":
            msg = "password."
            return render_template("login.html", username=username, password=password, msg=msg)

        
        return render_template("login.html", username=username, password=password)

    msg = "information."
    type = request.args.get("type")
    
    if type == "register":  
        return render_template("login.html", isreg=1)

    #if type == "registerAcc":
        #TODO
    
    return render_template("login.html", msg=msg)