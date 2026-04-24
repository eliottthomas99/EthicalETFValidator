from ethical_validator.holdings import fetch_top_holdings

def test_fetch_top_holdings_returns_list_of_strings():
    # Using a known ETF ticker
    holdings = fetch_top_holdings("EPAB.PA", count=3)
    assert isinstance(holdings, list)
    assert len(holdings) == 3
    assert all(isinstance(h, str) for h in holdings)
