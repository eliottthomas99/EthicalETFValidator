from ethical_validator.holdings import fetch_top_holdings

def test_fetch_top_holdings_returns_list_of_strings():
    # Using a known ETF ISIN (EPAB.PA -> Amundi S&P Eurozone Climate Paris Aligned)
    holdings = fetch_top_holdings("LU2195226068", count=3)
    assert isinstance(holdings, list)
    assert len(holdings) == 3
    assert all(isinstance(h, str) for h in holdings)
