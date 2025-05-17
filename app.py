#!/usr/bin/env python3
"""
Simple Flask web server to serve Ascelia Owners Chart and dynamic data.
"""
from flask import Flask, jsonify, send_from_directory
import requests
from flask_caching import Cache

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
    print("GET %s" % url)
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return jsonify({"error": f"Failed to fetch data: {response.status_code}"}), response.status_code
    return jsonify(response.json())

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Ascelia Owners Chart Web Server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind')
    parser.add_argument('--port', default=5000, type=int, help='Port to bind')
    args = parser.parse_args()
    app.run(host=args.host, port=args.port, debug=True)