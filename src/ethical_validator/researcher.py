# src/ethical_validator/researcher.py
import datetime
from ddgs import DDGS

def search_company_news(company: str) -> list[dict[str, str]]:
    """
    Search DuckDuckGo for recent news about a company.
    Returns a list of result dicts with 'href' and 'body' keys.
    """
    current_year = datetime.datetime.now().year
    query = f"{company} (environmental scandal OR labor violation OR greenwashing OR lawsuit) {current_year - 1} {current_year}"
    
    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=5))
    
    if not results:
        return []
    
    return [
        {
            "href": r.get("href", ""),
            "body": r.get("body", "")
        }
        for r in results
    ]
