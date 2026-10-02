import pandas as pd
import requests
def get_live_bunker_prices():
    """
    Scrapes live global average bunker fuel prices from Ship & Bunker.
    Returns a dictionary of prices in $/mt for VLSFO and MGO.
    """
    url = "https://shipandbunker.com/prices"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        from io import StringIO
        # pandas read_html automatically finds all <table> elements
        dfs = pd.read_html(StringIO(response.text))
        
        # Ship & Bunker organizes fuel types into sequential tables on the homepage
        # Table 0: IFO380
        # Table 1: VLSFO (Very Low Sulfur Fuel Oil)
        # Table 2: MGO (Marine Gas Oil)
        
        vlsfo_df = dfs[1]
        mgo_df = dfs[2]
        
        # Find the row for "Global 20 Ports Average"
        vlsfo_row = vlsfo_df[vlsfo_df.iloc[:, 0].str.contains("Global 20", na=False)]
        mgo_row = mgo_df[mgo_df.iloc[:, 0].str.contains("Global 20", na=False)]
        
        vlsfo_price = float(vlsfo_row["Price $/mt"].values[0])
        mgo_price = float(mgo_row["Price $/mt"].values[0])
        
        from datetime import datetime, timezone
        import os
        
        csv_file = "data/daily_bunker_prices.csv"
        today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        
        new_row = pd.DataFrame([{
            "date": today,
            "vlsfo_price": vlsfo_price,
            "mgo_price": mgo_price,
            "ifo380_price": None,
            "lng_price": None,
            "methanol_price": None,
            "ammonia_price": None,
            "biofuel_price": None
        }])
        
        if os.path.exists(csv_file):
            existing_df = pd.read_csv(csv_file)
            if today not in existing_df["date"].values:
                existing_df = pd.concat([existing_df, new_row], ignore_index=True)
                existing_df.to_csv(csv_file, index=False)
        else:
            new_row.to_csv(csv_file, index=False)
        
        return {
            "VLSFO": vlsfo_price,
            "MGO": mgo_price
        }
        
    except Exception as e:
        print(f"Error fetching live bunker prices: {e}")
        print("Falling back to static average estimates...")
        # Fallback to realistic static averages if the site blocks the scraper or goes down
        return {
            "VLSFO": 650.00,  # Estimated $/mt
            "MGO": 850.00     # Estimated $/mt
        }

if __name__ == "__main__":
    prices = get_live_bunker_prices()
    print("Live Bunker Prices ($/mt):")
    print(f"VLSFO: ${prices['VLSFO']}")
    print(f"MGO: ${prices['MGO']}")
