import os
import datetime
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
    
    # Initialize report
    report_lines = [
        f"# ESG Risk Report: {ticker}",
        f"**Date:** {datetime.datetime.now().strftime('%Y-%m-%d')}",
        f"**Holdings Evaluated:** {', '.join(holdings)}",
        "---"
    ]

    for company in holdings:
        print(f"\nResearching news for: {company}")
        try:
            news = search_company_news(company)
            print(f"Found {len(news)} chars of news content.")
            # Print a snippet so the user can see what was found
            print(f"Snippet: {news[:200]}...")
            
            print(f"Evaluating ESG risk for {company}...")
            score, summary = evaluate_esg_risk(company, news)
            
            print(f"Result for {company}:")
            print(f"  Score: {score}/10")
            print(f"  Summary: {summary}")
            
            # Add to report
            report_lines.extend([
                f"## {company}",
                f"**Risk Score:** {score}/10",
                f"**Summary:** {summary}",
                f"**Key News Snippet:**\n> {news[:500]}...",
                ""
            ])
            
        except Exception as e:
            print(f"Error processing {company}: {e}")
            report_lines.extend([f"## {company}", f"**Error:** {e}", ""])

    # Save Report
    os.makedirs("reports", exist_ok=True)
    report_filename = f"reports/{ticker}_report.md"
    with open(report_filename, "w") as f:
        f.write("\n".join(report_lines))
    print(f"\n[+] Full report saved to {report_filename}")

if __name__ == "__main__":
    main()
