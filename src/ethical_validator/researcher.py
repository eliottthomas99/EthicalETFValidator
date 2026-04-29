# src/ethical_validator/researcher.py
import datetime
from ddgs import DDGS

def search_company_news(company: str) -> str:
    current_year = datetime.datetime.now().year
    query = f"{company} (environmental scandal OR labor violation OR greenwashing OR lawsuit) {current_year - 1} {current_year}"
    
    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=5))
    
    if not results:
        return f"No significant news found for {company}."
    
    return "\n---\n".join([r.get("body", "") for r in results])
