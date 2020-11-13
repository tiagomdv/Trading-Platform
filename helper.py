import requests, sqlite3, datetime
import urllib.parse

import yfinance as yf
from functools import wraps
from flask import request, redirect, render_template, session, jsonify

def login_req(f):

    @wraps(f)
    def wrapper(*args, **kwargs):
        if session.get("user_id") is None:
            return render_template("login.html", logError="LOGIN required!")
        return f(*args, **kwargs)
    return wrapper

def buildGraphArray(ticker):
    # ------------- Gets the data to feed the graph ---------------

    tickData = yf.Ticker(ticker) # connects to yahoo api

    # Temp variables with incorrect data structure
    tempData = tickData.history(period="5y", interval="1mo")
    tempyAxis = tempData.Close.values

    # Array necessary to build the xAxis
    MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', "August", "September", "October", "November", "December"]

    date = datetime.datetime.now()    
    
    monN = int(date.strftime("%m")) # Gets the actual month  
    size = len(tempData.Close.values)

    # Variables where correct structured data will be stored
    yAxis = []
    xAxis = []

    # --- Building the correct structured arrays ---

    for each in tempyAxis: # Build the yAxis
        yAxis.append(round(each, 2))

    xAxis.append(MONTHS[date.month-1])  # Builds the xAxis
    for i in range(size - 1):
        monN = monN - 1        
        if monN < 1: monN = 12
        xAxis.append(MONTHS[monN-1])

    xAxis.reverse() # Necessary because the xAxis array was built backwards

    return xAxis, yAxis

def getStockHistory():           
    # ______Acess to database________
    dbConnection = sqlite3.connect('finance.db') # connection
    cursor = dbConnection.cursor()

    cursor.execute("SELECT ID from users WHERE username=?", (session["user_id"],))
    temp = cursor.fetchall()
    userid = temp[0][0]

    cursor.execute("SELECT name, number, price, symbol FROM stocks WHERE ID=?", (userid,) )
    temp = cursor.fetchall() # gets the output from query

    numberDict = {}
    priceDict = {}
    symbolDict = {}
    tempL = []
    history = []

    # Takes the query results and creates dicts with price and share number of all stock
    for row in temp:
        if row[0] not in numberDict:
            numberDict[row[0]] = []
            priceDict[row[0]] = []
            if row[0] not in symbolDict:
                append_value(symbolDict, row[0], row[3])
        append_value(numberDict, row[0], row[1])
        append_value(priceDict, row[0], row[2]*row[1])


    # Sums every element from each stock
    for row in numberDict:
        numberDict[row] = sum(numberDict[row])

    # Sums every element from each stock
    for row in priceDict:
        priceDict[row] = sum(priceDict[row])

        #Builds the history list with Name, Shares, W Cost, Value, $P/L and %P/L
        totalCost = round(priceDict[row], 2)
        numShares = numberDict[row]
        WeightedCost = round(totalCost / numShares, 2)
        #currentStockPrice = getStockPrice(symbolDict[row])
        currentStockPrice = 5000 # GET current stock price
        Value = numShares * round(currentStockPrice, 2) 
        unitPL = round(Value - totalCost, 2)
        percPL = round((unitPL / totalCost) * 100, 2)

        history.append((row, numShares, WeightedCost, Value, unitPL, percPL, symbolDict[row]))

    cursor.close()
    dbConnection.close()
    # ____Close access to database___
    return history


# _______________ from thispointer.com _______________________
def append_value(dict_obj, key, value):
    # Check if key exist in dict or not
    if key in dict_obj:
        # Key exist in dict.
        # Check if type of value of key is list or not
        if not isinstance(dict_obj[key], list):
            # If type is not list then make it list
            dict_obj[key] = [dict_obj[key]]
        # Append the value in list
        dict_obj[key].append(value)
    else:
        # As key is not in dict,
        # so, add key-value pair
        dict_obj[key] = value

def getStockPrice(ticker):    
    tickerInfo = yf.Ticker(ticker[0])
    try:
        tickerPrice = round(tickerInfo.info["open"], 2)
    except:
        tickerPrice = round(tickerInfo.info["ask"], 2)

    return tickerPrice

def getCashPosition():
    # ______Acess to database________
    dbConnection = sqlite3.connect('finance.db') # connection
    cursor = dbConnection.cursor()

    # Get cash position
    cursor.execute("SELECT cash FROM users WHERE username=?", (session["user_id"],))
    temp = cursor.fetchall() # gets the output from query
    cashPosition = round(temp[0][0], 2)

    # Get cash invested
    cursor.execute("SELECT sum(price*number) FROM stocks WHERE id=6")
    temp = cursor.fetchall() # gets the output from query
    cashInvested = round(temp[0][0], 2)

    cursor.close()
    dbConnection.close()
    # ____Close access to database___

    return cashPosition, cashInvested