# src/ethical_validator/researcher.py
import os
import datetime
from tavily import TavilyClient

def search_company_news(company: str) -> str:
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise RuntimeError("TAVILY_API_KEY not found in environment.")
    
    tavily = TavilyClient(api_key=api_key)
    
    # Use dynamic recent years to keep news relevant
    current_year = datetime.datetime.now().year
    query = f"{company} (environmental scandal OR labor violation OR greenwashing OR lawsuit) {current_year - 1} {current_year}"
    response = tavily.search(query=query, search_depth="advanced")
    
    results = response.get("results", [])
    if not results:
        return f"No significant news found for {company}."
    
    return "\n---\n".join([r.get("content", "") for r in results])
