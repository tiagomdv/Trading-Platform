from flask import Flask, render_template, session, request, redirect, jsonify, make_response
from tempfile import mkdtemp
from flask_session import Session
from helper import login_req, buildGraphArray, getStockHistory, getStockPrice, getCashPosition

import sqlite3, datetime
import math
import yfinance as yf

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
    # ______Acess to database________
    dbConnection = sqlite3.connect('finance.db') # connection
    cursor = dbConnection.cursor()

    cursor.execute("SELECT username FROM users")
    user = cursor.fetchall() # gets the output from query

    cursor.close()
    dbConnection.close()
    # ____Close access to database___

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
                    if i<=5: # From the symbols list, only the first 5 have 52WeekChange attributes                       
                        ytdChange.append(round(q.info["52WeekChange"]*100, 2))                        
                        price.append(round(q.info["ask"], 2))
                        
                    else: 
                        if each in ["BTCUSD=X", "GC=F"]:
                            price.append(round(q.info["open"]))
                        else:
                            price.append(round(q.info["open"], 4))
            session["recentLog"] = 0

        if not "priceMarket" in session: # If list does not exist, create
            session["priceMarket"] = price
            session["ytdChange"] = ytdChange
        else:
            price = session["priceMarket"]
            ytdChange = session["ytdChange"]

    return render_template("market.html", price=price, ytdChange=ytdChange)


@app.route('/wallet', methods=["GET"])
@login_req
def wallet():
    history = getStockHistory()

    temp = getCashPosition()
    cashPosition = int(temp[0]/1000)
    cashInvested = int(temp[1]/1000)
    cashTotal = round(cashPosition + cashInvested, 0)

    return render_template("wallet.html", history=history, cashTotal=cashTotal, cashInvested=cashInvested, cashPosition=cashPosition, username=session["user_id"])

@app.route('/account', methods=["GET", "POST"])
@login_req
def account():

    if request.method == "GET":
        # ______Acess to database________
        dbConnection = sqlite3.connect('finance.db') # connection
        cursor = dbConnection.cursor()

        # Get id 
        cursor.execute("SELECT id FROM users WHERE username=?", (session["user_id"],))
        temp = cursor.fetchall()
        userid = temp[0][0]

        # Get user data
        cursor.execute("SELECT firstname, lastname, age, city FROM users WHERE ID=?", (userid,))
        userdata = cursor.fetchall()

        # Get history data
        cursor.execute("SELECT date, name, number, price, symbol FROM stocks WHERE ID=?", (userid,))
        history = cursor.fetchall()

        # Get expenses data
        cursor.execute("SELECT type, sum(cost), date FROM expenses WHERE user_id=? GROUP BY type", (userid,))
        expenses = cursor.fetchall()

        cursor.close()
        dbConnection.close()
        # ____Close access to database___
    
    
    if request.method == "POST":
        firstname = request.form.get("firstname")
        lastname = request.form.get("lastname")
        password = request.form.get("password")
        city = request.form.get("city")
        age = request.form.get("age")
        initialcash = request.form.get("initialcash")

        # ______Acess to database________
        dbConnection = sqlite3.connect('finance.db') # connection
        cursor = dbConnection.cursor()

        # Get id 
        cursor.execute("SELECT id FROM users WHERE username=?", (session["user_id"],))
        temp = cursor.fetchall()
        userid = temp[0][0]

        # Updates cash position
        if initialcash is not None:
            if float(initialcash) > 0:     
                # Update user info
                cursor.execute("UPDATE users SET cash=?, cashset=1 WHERE ID=?", (initialcash, userid))
                session["cash_set"] = 1
        else:
            if password:
                # Update user info with password
                cursor.execute("UPDATE users SET firstname=?, lastname=?, city=?, age=?, password=? WHERE ID=?", (firstname, lastname, city, age, password, userid))
            else:
                # Update user info without password
                cursor.execute("UPDATE users SET firstname=?, lastname=?, city=?, age=? WHERE ID=?", (firstname, lastname, city, age, userid))

        # Get history data
        cursor.execute("SELECT date, name, number, price, symbol FROM stocks WHERE ID=?", (userid,))
        history = cursor.fetchall()

        # Get expenses data
        cursor.execute("SELECT type, sum(cost), date FROM expenses WHERE user_id=? GROUP BY type", (userid,))
        expenses = cursor.fetchall()
      
        # Get user data
        cursor.execute("SELECT firstname, lastname, age, city FROM users WHERE ID=?", (userid,))
        userdata = cursor.fetchall()

        dbConnection.commit() # apply changes
        cursor.close()
        dbConnection.close()
        # ____Close access to database___  

    return render_template("account.html", expenses=expenses, history=history,userdata=userdata, cashSet=session["cash_set"])

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

        # ______Acess to database________
        dbConnection = sqlite3.connect('finance.db') # connection
        cursor = dbConnection.cursor()

        cursor.execute("SELECT username, password, cashset FROM users WHERE username=?",(username,))
        user = cursor.fetchall() # gets the output from query
        cashset = user[0][2]

        # Checks if already exist username in database
        if len(user) > 0:
            session["user_id"] = user[0][0]
            session["recentLog"] = 1
            session["cash_set"] = cashset
            checkPass = user[0][1]
        else:
            return render_template("login.html", logError="User does NOT exist!") 

        if not checkPass == password:
            session.clear()
            return render_template("login.html", logError="Password is INCORRECT!")  
        
        cursor.close()
        dbConnection.close()
        # ____Close access to database___          
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

            # ______Acess to database________
            dbConnection = sqlite3.connect('finance.db') # connection
            cursor = dbConnection.cursor()

            cursor.execute("SELECT username FROM users WHERE username=?",(username,))
            user = cursor.fetchall() # gets the output from query
            if user:
                # Closes connections to database
                cursor.close()
                dbConnection.close()
                return render_template("register.html", logError=username + " already exists!")

            # Inserts data into database
            cursor.execute("INSERT INTO users (username, password, cash, cashset) VALUES (?, ?, ?, ?)", (username, password, 0, 0))
            
            dbConnection.commit() # apply changes
            cursor.close()
            dbConnection.close()
            # ____Close access to database___
            return render_template("index.html", username=username, password=password, isreg=1)
        else:
            return render_template("register.html", username=username, logError="Passwords do NOT match!")

@app.route("/logout", methods=["GET"]) # Handles LOGOUT
def logout():

    session.clear()
    return redirect("/") 

@app.route("/getHistoricalData", methods=["POST"])
def getHistoricalData():

    ticker = request.get_json()

    tickerData = buildGraphArray(ticker)

    yAxis = tickerData[1]
    xAxis = tickerData[0]

    i = 0
    for n in yAxis:
            if math.isnan(n):
                yAxis[i] = yAxis[i-1]      
            else:
                yAxis[i] = float(n)
            i += 1

    result = make_response(jsonify({"xAxis": xAxis, "yAxis": yAxis}))

    return result


@app.route("/getPrice", methods=["GET", "POST"])
def getPrice():


    ticker = request.get_json()


    if not ticker == None:
  
        tickerData = yf.Ticker(ticker)

        # Get quote price
        try:
            price = tickerData.info["ask"]
            if price == 0:
                price = tickerData.info["open"]
        except:
            try:
                price = tickerData.info["open"]
            except:
                ticker = "quote-error"
                return make_response(jsonify(ticker))

        # Get quote name
        try:
            companyName = tickerData.info["longName"]
        except:
            companyName = tickerData.info["shortName"]      

        fifty2WL = tickerData.info["fiftyTwoWeekLow"]
        fifty2WH = tickerData.info["fiftyTwoWeekHigh"]

        # Get quote 52 week change
        try:
            fifty2WC = round(tickerData.info["52WeekChange"], 2)*100
        except:
            fifty2WC = round((fifty2WH / fifty2WL) - 1, 2) * 100

        # Get quote name
        try:
            trailingPE = round(tickerData.info["trailingPE"], 2)
        except:
            trailingPE = "Error"

        quoteType = tickerData.info["quoteType"]
        
        result = make_response(jsonify({"price": price, "companyName": companyName, "fifty2WC": fifty2WC, "fifty2WL": fifty2WL, "fifty2WH": fifty2WH, "trailingPE": trailingPE, "quoteType": quoteType}))
    else:
        result = make_response(jsonify({"price": "error", "companyName": "error", "fifty2WC": "error", "fifty2WL": "error", "fifty2WH": "error", "trailingPE": "error", "quoteTYPE": "error"}))

    return result


@app.route("/buy", methods=["POST"])
def buyStock():
    # ______Acess to database________
    dbConnection = sqlite3.connect('finance.db') # connection
    cursor = dbConnection.cursor()

    # Get buying info from submitted form
    temp = request.form.get("tickerName")
    temp = temp.split("/")
    price = temp[0]
    companyName = temp[1]
    ticker = request.form.get("tickerSymbol")
    shares = request.form.get("numberShares")
    assetType = request.form.get("assetType")

    # Get cash position
    cursor.execute("SELECT cash FROM users WHERE username=?", (session["user_id"],))
    temp = cursor.fetchall() # gets the output from query
    cashCurrent = temp[0][0]

    # Get id 
    cursor.execute("SELECT id FROM users WHERE username=?", (session["user_id"],))
    temp = cursor.fetchall()
    userid = temp[0][0]

    # Register the BUY order
    cursor.execute("INSERT INTO stocks (date, symbol, number, name, ID, price, typeasset) VALUES (date(), ?, ?, ?, ?, ?, ?)", (ticker, shares, companyName, userid, price, assetType))
    
    cashSpent = float(price) * int(shares)
    cashUpdate = cashCurrent - cashSpent

    # Updates cash position
    cursor.execute("UPDATE users SET cash=? WHERE id=?", (cashUpdate, userid))

    # ____Applies changes________
    dbConnection.commit()

    # ____Close access to database___
    cursor.close()
    dbConnection.close()   

    temp = getCashPosition()
    cashPosition = temp[0]
    cashInvested = temp[1]
    cashTotal = cashPosition + cashInvested

    history = getStockHistory()

    return render_template("wallet.html", history=history, ticker=ticker, shares=shares, isBuy=1, cashPosition=cashPosition, cashInvested=cashInvested, cashTotal=cashTotal)

@app.route("/updateDB", methods=["POST"])
def updateDB():   

    data = request.get_json()

    # ______Acess to database________
    dbConnection = sqlite3.connect('finance.db') # connection
    cursor = dbConnection.cursor()

    # Get id 
    cursor.execute("SELECT id FROM users WHERE username=?", (session["user_id"],))
    temp = cursor.fetchall()
    userid = temp[0][0]    

    # Updates expenses database
    cursor.execute("INSERT INTO expenses (type, expense, cost, date, user_id) VALUES (?, ?, ?, date(), ?)", (data[1], data[2], data[3], userid ))    

    # ____Applies changes________
    dbConnection.commit()
    # ____Close access to database___
    cursor.close()
    dbConnection.close()   
    return None

@app.route("/getDataDB", methods=["GET"])
def getDataDB():

    # ______Acess to database________
    dbConnection = sqlite3.connect('finance.db') # connection
    cursor = dbConnection.cursor()

    # Get id 
    cursor.execute("SELECT id FROM users WHERE username=?", (session["user_id"],))
    temp = cursor.fetchall()
    userid = temp[0][0]    

    # Get expenses data
    cursor.execute("SELECT type, sum(cost) FROM expenses WHERE user_id=? GROUP BY type", (userid,))
    expenses = cursor.fetchall() 

    # ____Close access to database___
    cursor.close()
    dbConnection.close() 

    result = make_response(jsonify(expenses)) 

    return result
