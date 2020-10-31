import requests, sqlite3
import urllib.parse

from functools import wraps
from flask import request, redirect, render_template, session

def lookup(symbol):
    """Look up quote for symbol."""
    api_key = "private key"
    symNot = ["BTCUSD", "EURUSD", "DGS10", "DGS30", "DCOILWTICO"]

    # Contact API if CRYPTO
    if symbol=="BTCUSD":
        try:
            response = requests.get(f"https://cloud-sse.iexapis.com/stable/crypto/{urllib.parse.quote_plus(symbol)}/price?token={api_key}")
            response.raise_for_status()
        except requests.RequestException:
            return None
            
    # Contact API if CURRENCY
    if symbol=="EURUSD":
        try:
            response = requests.get(f"https://cloud-sse.iexapis.com/stable/fx/latest?symbols={urllib.parse.quote_plus(symbol)}&token={api_key}")
            response.raise_for_status()
        except requests.RequestException:
            return None    
               
    # Contact API if Bonds
    if symbol=="DGS10" or symbol=="DGS30":
        try:
            response = requests.get(f"https://cloud-sse.iexapis.com/stable//time-series/treasury/symbols={urllib.parse.quote_plus(symbol)}&token={api_key}")
            response.raise_for_status()
        except requests.RequestException:
            return None
    
    # Contact API if Oil
    if symbol=="DCOILWTICO":
        try:
            response = requests.get(f"https://cloud-sse.iexapis.com/stable//time-series/energy/symbols={urllib.parse.quote_plus(symbol)}&token={api_key}")
            response.raise_for_status()
        except requests.RequestException:
            return None
            
    if not symbol in symNot:
        # Contact API if Stocks
        try:
            response = requests.get(f"https://cloud-sse.iexapis.com/stable/stock/{urllib.parse.quote_plus(symbol)}/quote?token={api_key}")
            response.raise_for_status()
        except requests.RequestException:
            return None

    # Parse response
    try:
        quote = response.json()

        if symbol=="BTCUSD": # If CRYPTO
            return {
                "price": float(quote["price"])
            }

        if symbol=="EURUSD": # If Currency
            return {
                "price": float(quote["rate"])
            } 
        
        if symbol=="DGS10" or symbol=="DGS30": # If Bonds
            return {
                "price": float(quote["value"])
            } 
        
        if symbol=="DCOILWTICO": # If Oil
            return {
                "price": float(quote["value"])
            } 

        if not symbol in symNot: # If Stocks
            return {
                "name": quote["companyName"],
                "price": float(quote["latestPrice"]),
                "symbol": quote["symbol"],
                "ytdChange": float(quote["ytdChange"])
            }

    except (KeyError, TypeError, ValueError):
        return None

def login_req(f):

    @wraps(f)
    def wrapper(*args, **kwargs):
        if session.get("user_id") is None:
            return render_template("login.html", logError="LOGIN required!")
        return f(*args, **kwargs)
    return wrapper