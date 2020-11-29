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

    userid = session["user_id"]

    cursor.execute("SELECT name, number, price, symbol, typeasset FROM stocks WHERE ID=?", (userid,) )
    temp = cursor.fetchall() # gets the output from query

    numberDict = {}
    numberDict2 = {}
    priceDict = {}
    priceDict2 = {}
    symbolDict = {}
    tempL = []
    history = []

    # Takes the query results and creates dicts with price and share number of all stock
    if len(temp) == 0:
        return

    for row in temp:
        if row[0] not in numberDict:
            numberDict[row[0]] = []
            priceDict[row[0]] = []
            if row[0] not in symbolDict:
                append_value(symbolDict, row[0], row[3])
                append_value(symbolDict, row[0], row[4])
        append_value(numberDict, row[0], row[1])
        append_value(priceDict, row[0], round(row[2]*row[1], 2))
        append_value(numberDict2, row[0], row[1])
        append_value(priceDict2, row[0], round(row[2]*row[1], 2))

    for row in numberDict:                
        # Sums price and share number of every stock
        numberDict[row] = sum(numberDict[row])
        priceDict[row] = sum(priceDict[row])

    # builds the dict to send to webpage
    for row in priceDict:        
        numShares = numberDict[row]
        if numShares == 0:
            continue

        temp_price = 0
        temp_number_pos = 0
        temp_number_neg = 0

        if type(numberDict2[row]) is int:
            temp_number_pos += numberDict2[row]
            temp_price = priceDict2[row]
        else:
            for each in numberDict2[row]:
                if each > 0:
                    temp_number_pos += each # How many shares bought
                else:
                    temp_number_neg += each # How many shares sold

            for each in priceDict2[row]:
                if each > 0:
                    temp_price += each   

        #Builds the history list with Name, Shares, W Cost, Value, $P/L and %P/L
        ticker = symbolDict[row][0]
        assetType = symbolDict[row][1]

        try:
            currentStockPrice = session["all_stock_price"][ticker]
        except:
            currentStockPrice = getStockPrice(symbolDict[row])

        average_price = temp_price / temp_number_pos
        total_cost = average_price * numShares         

        value = round((numShares * currentStockPrice), 2) 
        unit_roi = round(value - total_cost, 2)
        perc_roi = round((unit_roi / total_cost) * 100, 2)

        history.append((row, numShares, average_price, value, unit_roi, perc_roi, ticker, assetType))

    cursor.close()
    dbConnection.close()
    # ____Close access to database___
    return history, unit_roi, perc_roi


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
        tickerPrice = round(tickerInfo.info["ask"], 2)
    except:
        tickerPrice = round(tickerInfo.info["open"], 2)

    return tickerPrice

def getCashPosition():
    # ______Acess to database________
    dbConnection = sqlite3.connect('finance.db') # connection
    cursor = dbConnection.cursor()

    # Get cash position
    cursor.execute("SELECT cash FROM users WHERE username=?", (session["user_name"],))
    temp = cursor.fetchall() # gets the output from query
    cashPosition = round(temp[0][0], 2)

    # Get cash invested
    cursor.execute("SELECT sum(price*number) FROM stocks WHERE id=?", (session["user_id"],))
    temp = cursor.fetchall() # gets the output from query

    try:
        cashInvested = round(temp[0][0], 2)
    except:
        cashInvested = 0

    cursor.close()
    dbConnection.close()
    # ____Close access to database___

    return cashPosition, cashInvested

def calculate_cash():

    temp = getCashPosition()

    cash_position_first = int(temp[0] / 1000)
    cash_position_second = temp[0] - (cash_position_first * 1000)
    if cash_position_second < 10:
        cash_position_second *= 100
    if cash_position_second < 100:
        cash_position_second *= 10
    if cash_position_second == 0:
        cash_position_second = "000"
        cashPosition = [cash_position_first, cash_position_second]
    else:
        cashPosition = [cash_position_first, round(cash_position_second, 2)]

    cash_invested_first = int(temp[1] / 1000)
    cash_invested_second = temp[1] - (cash_invested_first * 1000)
    if cash_invested_second < 10:
        cash_invested_second *= 100
    if cash_invested_second < 100:
        cash_invested_second *= 10
    if cash_invested_second == 0:
        cash_invested_second = "000"
        cashInvested = [cash_invested_first, cash_invested_second]
    else:
        cashInvested = [cash_invested_first, round(cash_invested_second, 2)]
    
    cash_total_first = int((temp[0] + temp[1]) / 1000)
    cash_total_second = (temp[0] + temp[1]) - (cash_total_first * 1000)
    if cash_total_second < 10:
        cash_total_second *= 100
    if cash_total_second < 100:
        cash_total_second *= 10
    if cash_total_second == 0:
        cash_total_second = "000"
        cashTotal = [cash_total_first, cash_total_second]
    else:
        cashTotal = [cash_total_first, round(cash_total_second, 2)]  
    
    return cashPosition, cashInvested, cashTotal
