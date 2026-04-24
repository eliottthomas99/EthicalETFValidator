import os
from dotenv import load_dotenv

from ethical_validator.holdings import fetch_top_holdings
from ethical_validator.researcher import search_company_news
from ethical_validator.evaluator import evaluate_esg_risk

def main():
    print("Loading environment variables...")
    load_dotenv()
    
    ticker = "EPAB.PA"
    print(f"Fetching top 3 holdings for {ticker}...")
    try:
        holdings = fetch_top_holdings(ticker, count=3)
        print(f"Top 3 holdings found: {holdings}")
    except Exception as e:
        print(f"Error fetching holdings: {e}")
        return

    print("--- Starting ESG Risk Evaluation ---")
    for company in holdings:
        print(f"\nResearching news for: {company}")
        try:
            news = search_company_news(company)
            print(f"Found {len(news)} chars of news content.")
            
            print(f"Evaluating ESG risk for {company}...")
            score, summary = evaluate_esg_risk(company, news)
            
            print(f"Result for {company}:")
            print(f"  Score: {score}/10")
            print(f"  Summary: {summary}")
        except Exception as e:
            print(f"Error processing {company}: {e}")

if __name__ == "__main__":
    main()
