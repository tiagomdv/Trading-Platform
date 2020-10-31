from flask import Flask, render_template, session, request, redirect
from tempfile import mkdtemp
from flask_session import Session
import sqlite3

from helper import lookup, login_req

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
    usernames = []

    # _______________________________
    # Acess to database
    dbConnection = sqlite3.connect('finance.db') # connection
    cursor = dbConnection.cursor()

    cursor.execute("SELECT username FROM users")
    user = cursor.fetchall() # gets the output from query

    # Closes connections to database
    cursor.close()
    dbConnection.close()
    # _______________________________

    for row in user:
        usernames.append(row[0])

    return render_template("index.html", quote="TESLA", usernames=usernames)

@app.route('/market', methods=["GET", "POST"])
def market():    

    if request.method == "GET":

        symbols = ["TSLA", "AAPL", "AMZN", "MSFT", "FB", "BTCUSD", "EURUSD", "DGS10", "DGS30", "DCOILWTICO"]

        price = []
        ytdChange = []
        i = 0

        for each in symbols:
            i += 1
            q = lookup(each)
            if not q == None:
                if i<=5:
                    ytdChange.append(round(q["ytdChange"]*100, 2))
                    price.append(round(q["price"], 2))
            
    return render_template("market.html", price=price, ytdChange=ytdChange)

@app.route('/wallet')
@login_req
def wallet():
    quote = lookup("AMZN")
    return render_template("wallet.html", quote=quote)

@app.route("/login", methods=["GET", "POST"]) # LOGIN REGISTER
def login(): 

    if request.method == "GET":
        return render_template("login.html")

    if request.method == "POST": # the method POST can be used to LOGIN or to REGISTER. How the code detects is if password2 variable exists
        
        # Forget any user id
        session.clear()

        # ______________________________
        # Checks for valid username and password
        username = request.form.get("username")
        password = request.form.get("password")
        if not username:
            return render_template("login.html", logError="Invalid username!")

        if not password:
            return render_template("login.html", username=username,logError="Invalid password!")         
        # _______________________________                

        # Forget any user id
        session.clear()

        # _______________________________
        # Acess to database
        dbConnection = sqlite3.connect('finance.db') # connection
        cursor = dbConnection.cursor()

        cursor.execute("SELECT username, password FROM users WHERE username=?",(username,))
        user = cursor.fetchall() # gets the output from query

        # Closes connections to database
        cursor.close()
        dbConnection.close()
        # _______________________________

        # Checks if already exist username in database
        if len(user) > 0:
            session["user_id"] = user[0][0]
            checkPass = user[0][1]
        else:
            return render_template("login.html", logError="User does NOT exist!") 

        if not checkPass == password:
            session.clear()
            return render_template("login.html", logError="Password is INCORRECT!")              
 

        return render_template("index.html", username=username, password=password)   


@app.route("/register", methods=["GET", "POST"]) # Handles REGISTRY
def register():

    if request.method == "GET":
        return render_template("register.html")

    if request.method == "POST":   
        # ______________________________
        # Checks for valid username and password
        username = request.form.get("username")
        password = request.form.get("password")

        if not username:
            return render_template("register.html", logError="Invalid username!")

        if not password:
            return render_template("register.html", username=username, logError="Invalid password!")         
        # _______________________________

        checkPass = request.form.get("checkPass")
        if checkPass == password:                  
            # _______________________________
            # Acess to database
            dbConnection = sqlite3.connect('finance.db') # connection
            cursor = dbConnection.cursor()

            cursor.execute("SELECT username FROM users WHERE username=?",(username,))
            user = cursor.fetchall() # gets the output from query
            if user:
                return render_template("register.html", logError=username + " already exists!")
                # Closes connections to database
                cursor.close()
                dbConnection.close()

            # Inserts data into database
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            dbConnection.commit() # apply changes

            # Closes connections to database
            cursor.close()
            dbConnection.close()
            # _______________________________

            return render_template("index.html", username=username, password=password, isreg=1)
        else:
            return render_template("register.html", username=username, logError="Passwords do NOT match!")

@app.route("/logout", methods=["GET"]) # Handles LOGOUT
def logout():

    session.clear()
    return redirect("/") 
