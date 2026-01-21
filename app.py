#!/usr/bin/env python3
"""
Simple Flask web server to serve Ascelia Owners Chart and dynamic data.
"""
from flask import Flask, jsonify, send_from_directory, request
import requests
from flask_caching import Cache
import logging
from bs4 import BeautifulSoup
import time
from datetime import datetime
from zoneinfo import ZoneInfo  # Python 3.9+


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Stock configuration - centralized
STOCK_CONFIG = {
    "ASCELIA": {
        "id": "941919",
        "name": "Ascelia Pharma",
        "max_owners_filter": 9700,  # For advanced filter query
    },
    "EGETIS": {
        "id": "283294",
        "name": "Egetis Therapeutics",
        "max_owners_filter": 7000,  # For advanced filter query
    }
}

# Select which stock to use
CURRENT_STOCK = STOCK_CONFIG["ASCELIA"]

app = Flask(__name__, static_folder=None)
app.config['CACHE_TYPE'] = 'SimpleCache'
# 2 hours cache
app.config['CACHE_DEFAULT_TIMEOUT'] = 60 * 60 * 2
cache = Cache(app)

@app.route('/')
def index():
    """
    Serve the main chart HTML page.
    """
    return send_from_directory('.', 'chart.html')

@app.route('/api/stocks')
def api_stocks():
    """
    Return list of available stocks.
    """
    stocks = []
    for key, config in STOCK_CONFIG.items():
        stocks.append({
            "key": key,
            "id": config["id"],
            "name": config["name"]
        })
    return jsonify({"stocks": stocks, "default": "ASCELIA"})

@app.route('/api/config')
def api_config():
    """
    Return current stock configuration.
    Accepts optional 'stock' query parameter (e.g., ?stock=ASCELIA or ?stock=EGETIS)
    """
    stock_key = request.args.get('stock', 'ASCELIA').upper()

    if stock_key not in STOCK_CONFIG:
        return jsonify({"error": f"Invalid stock: {stock_key}"}), 400

    stock = STOCK_CONFIG[stock_key]
    return jsonify({
        "stockId": stock["id"],
        "stockName": stock["name"],
        "stockKey": stock_key
    })

@app.route('/data.json')
@cache.cached(query_string=True)
def data_json():
    """
    Fetch owners data from Avanza API and return as JSON.
    Accepts optional 'stock' query parameter.
    """
    stock_key = request.args.get('stock', 'ASCELIA').upper()

    if stock_key not in STOCK_CONFIG:
        return jsonify({"error": f"Invalid stock: {stock_key}"}), 400

    stock = STOCK_CONFIG[stock_key]
    url = f"https://www.avanza.se/_api/market-guide/number-of-owners/{stock['id']}"
    logger.info("GET %s" % url)
    headers = {"Accept": "application/json", "User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return jsonify({"error": f"Failed to fetch data: {response.status_code}"}), response.status_code
    return jsonify(response.json())

@app.route('/api/market-guide')
@cache.cached(query_string=True)
def api_owners():
    """
    Fetch current number of owners from Avanza API and return JSON.
    Accepts optional 'stock' query parameter.
    """
    stock_key = request.args.get('stock', 'ASCELIA').upper()

    if stock_key not in STOCK_CONFIG:
        return jsonify({"error": f"Invalid stock: {stock_key}"}), 400

    stock = STOCK_CONFIG[stock_key]
    url = f"https://www.avanza.se/_api/market-guide/stock/{stock['id']}"
    logger.info(f"GET {url}")
    headers = {"Accept": "application/json", "User-Agent": "Mozilla/5.1"}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return jsonify({"error": f"Failed to fetch data: {response.status_code}"}), response.status_code
    return jsonify(response.json())


@app.route("/api/ascelia-owner-change")
@cache.cached(query_string=True)
def get_ascelia_owner_change():
    stock_key = request.args.get('stock', 'ASCELIA').upper()

    if stock_key not in STOCK_CONFIG:
        return jsonify({"error": f"Invalid stock: {stock_key}"}), 400

    stock = STOCK_CONFIG[stock_key]
    timestamp = int(time.time() * 1000)

    url = (
        f"https://www.avanza.se/frontend/template.html/marketing/advanced-filter/advanced-filter-template?"
        f"{timestamp}&"  # ← this must come *before* everything else
        "widgets.marketCapitalInSek.filter.lower=&"
        "widgets.marketCapitalInSek.filter.upper=&"
        "widgets.marketCapitalInSek.active=true&"
        "widgets.stockLists.filter.list%5B0%5D=SE.SmallCap.SE&"
        "widgets.stockLists.active=true&"
        "widgets.numberOfOwners.filter.lower=&"
        f"widgets.numberOfOwners.filter.upper={stock['max_owners_filter']}&"
        "widgets.numberOfOwners.active=true&"
        "widgets.sectors.filter.list%5B0%5D=17&"
        "widgets.sectors.active=true&"
        "parameters.startIndex=0&parameters.maxResults=100&"
        "parameters.selectedFields%5B0%5D=SECTOR&"
        "parameters.selectedFields%5B1%5D=NBR_OF_OWNERS&"
        "parameters.selectedFields%5B2%5D=NBR_OF_OWNERS_CHANGE_ABS_DAY&"
        "parameters.selectedFields%5B3%5D=NBR_OF_OWNERS_CHANGE_ABS_WEEK&"
        "parameters.selectedFields%5B4%5D=NBR_OF_OWNERS_CHANGE_ABS_MONTH&"
        "parameters.selectedFields%5B5%5D=NBR_OF_OWNERS_CHANGE_ABS_THREE_MONTHS&"
        "parameters.selectedFields%5B6%5D=NBR_OF_OWNERS_CHANGE_ABS_THIS_YEAR"
    )

    print(url)

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
    }

    res = requests.get(url, headers=headers)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")
    row = soup.select_one("div.tableScrollContainer tr.rowId1")
    if not row:
        return jsonify({"error": "Ascelia row not found"}), 404

    cells = row.find_all("td")

    # Cells: [Sector, #Owners, 1d, 1w, 1m, 3m, YTD]
    number_of_owners = int(cells[1].get_text(strip=True).replace("\xa0", "").replace(" ", ""))
    changes = {
        # Remove non breaking space. remove normal space, then parse result to int for number
        "1d": int(cells[2].get_text(strip=True).replace("\xa0", "").replace(" ", "")),
        "1w": int(cells[3].get_text(strip=True).replace("\xa0", "").replace(" ", "")),
        "1m": int(cells[4].get_text(strip=True).replace("\xa0", "").replace(" ", "")),
        "3m": int(cells[5].get_text(strip=True).replace("\xa0", "").replace(" ", "")),
        "ytd": int(cells[6].get_text(strip=True).replace("\xa0", "").replace(" ", ""))
    }

    # Current time in ISO format, e.g., "2025-05-17 14:08"
    last_updated = datetime.now(ZoneInfo("Europe/Stockholm")).strftime("%Y-%m-%d %H:%M")

    return jsonify({
        "numberOfOwners": number_of_owners,
        "changes": changes,
        "lastUpdated": last_updated
    })


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Ascelia Owners Chart Web Server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind')
    parser.add_argument('--port', default=5000, type=int, help='Port to bind')
    args = parser.parse_args()
    app.run(host=args.host, port=args.port, debug=True)