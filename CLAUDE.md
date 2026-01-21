# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Flask web application that tracks and visualizes stock ownership data for Swedish pharmaceutical companies (Ascelia Pharma and Egetis) from Avanza, a Swedish online broker. The app displays historical ownership trends and current statistics.

## Development Setup

```bash
# Create and activate virtual environment
virtualenv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the development server
python app.py

# Run with custom host/port
python app.py --host 0.0.0.0 --port 5000
```

The application will be available at http://localhost:5000

## Architecture

### Main Application (app.py)

The core Flask application with these primary routes:

1. **GET /** - Serves chart.html, the main visualization page
2. **GET /api/config** - Returns current stock configuration (id and name)
3. **GET /data.json** - Fetches historical ownership data from Avanza API (cached for 2 hours)
4. **GET /api/market-guide** - Fetches current market data for the configured stock (cached for 2 hours)
5. **GET /api/ascelia-owner-change** - Scrapes Avanza's advanced filter page to get detailed ownership change statistics (1d, 1w, 1m, 3m, ytd) (cached for 2 hours)

### Stock Configuration

Stock settings are centralized in `app.py` using the `STOCK_CONFIG` dictionary. To switch between stocks, simply change the `CURRENT_STOCK` variable:

```python
# In app.py
STOCK_CONFIG = {
    "ASCELIA": {
        "id": "941919",
        "name": "Ascelia Pharma",
        "max_owners_filter": 9700,
    },
    "EGETIS": {
        "id": "283294",
        "name": "Egetis Therapeutics",
        "max_owners_filter": 7000,
    }
}

# Select which stock to use
CURRENT_STOCK = STOCK_CONFIG["ASCELIA"]  # or STOCK_CONFIG["EGETIS"]
```

The frontend automatically fetches the current stock name from `/api/config` and updates all titles dynamically.

### Caching

Flask-Caching is configured with SimpleCache backend. All API routes use a 2-hour cache (`CACHE_DEFAULT_TIMEOUT = 60 * 60 * 2`) to reduce load on Avanza's servers and improve response times.

### Frontend (chart.html)

- Uses Highcharts for interactive time-series visualization
- Fetches data from both `/data.json` (historical) and `/api/market-guide` (current day) to display complete ownership history
- Uses Ant Design 4 for the info card showing current ownership statistics
- Fully responsive, fills viewport height
- Includes Google Analytics tracking
- Displays ownership changes using data from `/api/ascelia-owner-change`
- Shows last updated timestamp in Swedish time (Europe/Stockholm timezone)

### Standalone Analysis Scripts

- **ascelia.py** - Fetches and plots Ascelia ownership data from 2024 onwards
- **egetis.py** - Fetches and plots Egetis ownership data from December 2024
- **main_one.py** - Plots all historical data from data.json without date filtering
- **main_all_dates.py** - Plots 2024 data with forward-fill for missing dates

These scripts use matplotlib for visualization and are independent of the Flask app.

## Deployment

### Docker

```bash
docker build -t ascelia-owners .
docker run -p 5000:5000 ascelia-owners
```

The Dockerfile uses Python 3.11-slim and runs Gunicorn with 2 workers.

### Fly.io

```bash
# Initial deployment
flyctl launch --name ascelia-owners --region iad --dockerfile Dockerfile

# Subsequent deployments
flyctl deploy

# Open in browser
flyctl open
```

The app will be deployed to https://ascelia-owners.fly.dev

## API Requirements

All requests to Avanza API must include a User-Agent header to avoid 403 errors:

```python
headers = {"User-Agent": "Mozilla/5.0"}
```

The `/api/ascelia-owner-change` endpoint scrapes HTML and requires parsing with BeautifulSoup. It looks for a table row with class `rowId1` containing ownership statistics.

## Data Format

Avanza API returns ownership data as:
```json
{
  "ownersPoints": [
    {"timestamp": 1234567890000, "numberOfOwners": 9500},
    ...
  ]
}
```

Timestamps are in milliseconds since Unix epoch.
