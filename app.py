#!/usr/bin/env python3
"""
Simple Flask web server to serve Ascelia Owners Chart and dynamic data.
"""
from flask import Flask, jsonify, send_from_directory
import requests
from flask_caching import Cache
import logging
from bs4 import BeautifulSoup
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder=None)
app.config['CACHE_TYPE'] = 'SimpleCache'
# 6 hours cache
app.config['CACHE_DEFAULT_TIMEOUT'] = 60 * 60 * 60 * 6
cache = Cache(app)

@app.route('/')
def index():
    """
    Serve the main chart HTML page.
    """
    return send_from_directory('.', 'chart.html')

@app.route('/data.json')
@cache.cached(timeout=3600)
def data_json():
    """
    Fetch owners data from Avanza API and return as JSON.
    """
    url = "https://www.avanza.se/_api/market-guide/number-of-owners/941919"
    logger.info("GET %s" % url)
    headers = {"Accept": "application/json", "User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return jsonify({"error": f"Failed to fetch data: {response.status_code}"}), response.status_code
    return jsonify(response.json())

@app.route('/api/market-guide')
@cache.cached(timeout=3600)
def api_owners():
    """
    Fetch current number of owners from Avanza API and return JSON.
    """
    url = "https://www.avanza.se/_api/market-guide/stock/941919"
    logger.info(f"GET {url}")
    headers = {"Accept": "application/json", "User-Agent": "Mozilla/5.1"}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return jsonify({"error": f"Failed to fetch data: {response.status_code}"}), response.status_code
    return jsonify(response.json())


@app.route("/api/ascelia-owner-change")
def get_ascelia_owner_change():
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
        "widgets.numberOfOwners.filter.upper=9700&"
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

    return jsonify({
        "numberOfOwners": number_of_owners,
        "changes": changes
    })


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Ascelia Owners Chart Web Server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind')
    parser.add_argument('--port', default=5001, type=int, help='Port to bind')
    args = parser.parse_args()
    app.run(host=args.host, port=args.port, debug=True)