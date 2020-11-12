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

    cursor.execute("SELECT name, number, price FROM stocks WHERE ID=?", (userid,) )
    temp = cursor.fetchall() # gets the output from query

    numberDict = {}
    priceDict = {}
    tempL = []
    history = []

    for row in temp:
        if row[0] not in numberDict:
            numberDict[row[0]] = []
            priceDict[row[0]] = []
        append_value(numberDict, row[0], row[1])
        append_value(priceDict, row[0], row[2])

    for row in numberDict:
        tempL = numberDict[row]
        numberDict[row] = sum(tempL)

    for row in priceDict:
        tempL = priceDict[row]
        priceDict[row] = sum(tempL)
        append_value(numberDict, row, priceDict[row])

    # Trying to get all the info needed in history list
    # Trying to build a list which each row has all the info related to one company

    
    for row in temp:
        history.append(row)



    cursor.close()
    dbConnection.close()
    # ____Close access to database___
    return history

    #Name	# Shares	Weighted Cost	Value	$Gain/Loss	%Gain/Loss  

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