import os
from datetime import datetime, timezone
from io import StringIO

import pandas as pd
import requests

URL = "https://shipandbunker.com/prices"
CSV_FILE = "data/daily_bunker_prices.csv"
CSV_COLUMNS = ["date", "vlsfo_price", "mgo_price", "ifo380_price", "lng_price",
               "methanol_price", "ammonia_price", "biofuel_price"]

# Used if the site blocks the scraper or is down ($/mt)
FALLBACK_PRICES = {"VLSFO": 650.00, "MGO": 850.00}


def scrape_prices():
    """Scrapes the Ship & Bunker 'Global 20 Ports Average' for VLSFO and MGO ($/mt)."""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    response = requests.get(URL, headers=headers, timeout=10)
    response.raise_for_status()

    # The homepage has one table per fuel: 0 = IFO380, 1 = VLSFO, 2 = MGO
    tables = pd.read_html(StringIO(response.text))

    def global_average(table):
        row = table[table.iloc[:, 0].str.contains("Global 20", na=False)]
        return float(row["Price $/mt"].values[0])

    return {"VLSFO": global_average(tables[1]), "MGO": global_average(tables[2])}


def save_prices(prices):
    """Appends today's prices to the CSV unless today is already there."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    new_row = pd.DataFrame([{
        "date": today,
        "vlsfo_price": prices["VLSFO"],
        "mgo_price": prices["MGO"],
    }], columns=CSV_COLUMNS)

    if not os.path.exists(CSV_FILE):
        new_row.to_csv(CSV_FILE, index=False)
        return

    existing = pd.read_csv(CSV_FILE)
    if today not in existing["date"].values:
        pd.concat([existing, new_row], ignore_index=True).to_csv(CSV_FILE, index=False)


def get_live_bunker_prices():
    """Returns {"VLSFO": $/mt, "MGO": $/mt}, saving today's prices to the CSV."""
    try:
        prices = scrape_prices()
        save_prices(prices)
        return prices
    except Exception as e:
        print(f"Error fetching live bunker prices: {e}")
        print("Falling back to static average estimates...")
        return dict(FALLBACK_PRICES)


if __name__ == "__main__":
    prices = get_live_bunker_prices()
    print("Live Bunker Prices ($/mt):")
    print(f"VLSFO: ${prices['VLSFO']}")
    print(f"MGO: ${prices['MGO']}")
