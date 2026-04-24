import yfinance as yf
from typing import List

def fetch_top_holdings(ticker: str, count: int = 3) -> List[str]:
    etf = yf.Ticker(ticker)
    # yfinance holdings can be unreliable; we'll attempt to get them 
    # and fail loudly if the data structure isn't what we expect.
    try:
        # In this version of yfinance, holdings are in funds_data.top_holdings
        funds = etf.funds_data
        if funds is None:
            raise RuntimeError(f"No funds data available for {ticker}")
        holdings_data = funds.top_holdings
    except Exception as e:
        raise RuntimeError(f"Error fetching holdings for {ticker}: {e}")

    if holdings_data is None or holdings_data.empty:
        raise RuntimeError(f"Could not fetch holdings for {ticker}. yfinance returned no data.")
    
    # Extract company names from the top 'count' rows
    # In this version, the column name is 'Name'
    if 'Name' not in holdings_data.columns:
        raise RuntimeError(f"Expected 'Name' column in holdings data, but found: {holdings_data.columns}")
        
    top_holdings = holdings_data.head(count)['Name'].tolist()
    if not top_holdings:
         raise RuntimeError(f"Holdings list is empty for {ticker}.")
    return top_holdings
