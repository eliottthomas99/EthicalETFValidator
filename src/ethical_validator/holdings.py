from typing import List

import requests
from bs4 import BeautifulSoup


def fetch_top_holdings(isin: str, count: int = 3) -> List[str]:
    """Fetch the top holdings for an ETF by scraping justETF.

    Args:
        isin: The fund's ISIN (e.g. ``"LU2195226068"``).
        count: Number of top holdings to return.

    Returns:
        A list of company names.
    """
    url = f"https://www.justetf.com/en/etf-profile.html?isin={isin}"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }

    try:
        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"Failed to fetch JustETF page for {isin}: {e}")

    soup = BeautifulSoup(resp.text, "lxml")
    holdings_heading = soup.find("h3", string="Top 10 Holdings")
    if holdings_heading is None:
        raise RuntimeError(
            f"Could not find 'Top 10 Holdings' section on JustETF for {isin}. "
            "The page structure may have changed or the ISIN may be invalid."
        )

    container = holdings_heading.find_parent()
    if container is None:
        raise RuntimeError(f"Could not locate holdings container on JustETF for {isin}.")

    # justETF renders each holding as a link to /en/stock-profiles/{isin}
    links = container.find_all("a", href=lambda x: x and "/stock-profiles/" in x)
    if not links:
        raise RuntimeError(f"No holdings links found on JustETF for {isin}.")

    holdings = [link.get_text(strip=True) for link in links if link.get_text(strip=True)]
    if not holdings:
        raise RuntimeError(f"Holdings list is empty after parsing JustETF page for {isin}.")

    return holdings[:count]
