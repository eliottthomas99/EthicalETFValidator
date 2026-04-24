import os
from dotenv import load_dotenv
from ethical_validator.researcher import search_company_news

def main():
    load_dotenv()
    company = "ASML Holding NV"
    print(f"--- Searching news for {company} ---")
    try:
        news = search_company_news(company)
        print("\n[SUCCESS] News found:")
        print(news[:500] + "...") # Print first 500 chars
    except Exception as e:
        print(f"\n[FAILURE] Error: {e}")

if __name__ == "__main__":
    main()
