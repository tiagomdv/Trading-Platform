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