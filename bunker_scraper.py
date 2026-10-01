import pandas as pd
import requests
from db_manager import log_daily_bunker_price

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
        
        # pandas read_html automatically finds all <table> elements
        dfs = pd.read_html(response.text)
        
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
        
        # Save to database to build our own historical trendline!
        log_daily_bunker_price(vlsfo_price, mgo_price)
        
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

def get_historical_usda_bunker_prices():
    """
    Downloads the authentic historical daily bunker fuel prices dataset 
    from the USDA Agricultural Marketing Service (AMS) Open Data Portal.
    """
    url = "https://agtransport.usda.gov/api/views/y4ft-fdwn/rows.csv?accessType=DOWNLOAD"
    try:
        # Pandas can natively download and parse a CSV directly from a URL!
        df = pd.read_csv(url)
        # Ensure the date column is properly formatted for our charts
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'])
            df = df.sort_values(by='Date')
        return df
    except Exception as e:
        print(f"Error fetching USDA dataset: {e}")
        return None

if __name__ == "__main__":
    prices = get_live_bunker_prices()
    print("Live Bunker Prices ($/mt):")
    print(f"VLSFO: ${prices['VLSFO']}")
    print(f"MGO: ${prices['MGO']}")
    
    print("\nFetching USDA Historical Data...")
    usda_df = get_historical_usda_bunker_prices()
    if usda_df is not None:
        print(f"Successfully loaded {len(usda_df)} historical records from USDA!")
        print(usda_df.head())
