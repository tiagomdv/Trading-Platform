from flask import Flask, render_template, session, request, redirect, jsonify, make_response
from tempfile import mkdtemp
from flask_session import Session
from helper import login_req, buildGraphArray

import sqlite3, datetime
import math

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
@login_req
def market():    

    if request.method == "GET":

        #session["recentLog"] = 1 # Temporary TTTTTTTTTTTTTTTTTTTT

        symbols = ["TSLA", "AAPL", "AMZN", "MSFT", "FB", "BTCUSD=X", "EURUSD=X", "^TNX", "CL=F", "GC=F"]

        price = []
        ytdChange = []
        i = 0

        if session["recentLog"] == 21: # Condition to prevent Market page to reload everytime. It slows alot the flow of the website
            for each in symbols:
                i += 1
                q = yf.Ticker(each)
                if not q == None:
                    if i<=5:                        
                        ytdChange.append(round(q.info["52WeekChange"]*100, 2))                        
                        price.append(round(q.info["ask"], 2))
                        
                    else:
                        if each in ["BTCUSD=X", "GC=F"]:
                            price.append(round(q.info["open"]))
                        else:
                            price.append(round(q.info["open"], 4))
            session["recentLog"] = 0

        if not "priceMarket" in session:
            session["priceMarket"] = price
            session["ytdChange"] = ytdChange
        else:
            price = session["priceMarket"]
            ytdChange = session["ytdChange"]

    xAxis = buildGraphArray("TSLA")[0]
    yAxis = buildGraphArray("TSLA")[1]

    return render_template("market.html", yAxis=yAxis, xAxis=xAxis, price=price, ytdChange=ytdChange)


@app.route('/wallet')
@login_req
def wallet():

    
    ticker = "TSLA"


    tickData = yf.Ticker(ticker)

    tempData = tickData.history(period="5y", interval="1mo")

    tempyAxis = tempData.Close.values
    yAxis = []
    xAxis = []

    size = len(tempData.Close.values)

    for each in tempyAxis:
        yAxis.append(round(each, 2))

    for share in yAxis:
        test = share

    MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', "August", "September", "October", "November", "December"]

    date = datetime.datetime.now()
    xAxis.append(MONTHS[date.month-1])
    monN = int(date.strftime("%m"))
    year = 2020
    for i in range(size - 1):
        monN = monN - 1   
        if monN < 1: 
            monN = 12
            year -= 1
        xAxis.append(MONTHS[monN-1] + "/" + str(year - 2000))

    xAxis.reverse()    

    return render_template("wallet.html", yAxis=yAxis, xAxis=xAxis)

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
            session["recentLog"] = 1
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

@app.route("/fetchDo", methods=["GET", "POST"])
def fetchDo():

    req = request.get_json()
    temp = req.split()

    ticker = req.split()[0]
    xy = req.split()[1]

    if xy == "1":
        yAxis = buildGraphArray(ticker)[1]
        i = 0
        for n in yAxis:
            if math.isnan(n):
                yAxis[i] = 0      
            else:
                yAxis[i] = float(n)
            i += 1
        result = make_response(jsonify(yAxis))
    else:
        xAxis = buildGraphArray(ticker)[0]
        result = make_response(jsonify(xAxis))

    return result