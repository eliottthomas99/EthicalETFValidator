import os
from dotenv import load_dotenv
from ethical_validator.evaluator import evaluate_esg_risk

def main():
    load_dotenv()
    company = "ASML Holding NV"
    # Some sample news based on what we just found
    sample_news = "ASML is facing a class-action lawsuit regarding misrepresentations of its business impact from export regulations to China. Plaintiffs allege the stock was artificially inflated."
    
    print(f"--- Evaluating ESG risk for {company} ---")
    try:
        score, summary = evaluate_esg_risk(company, sample_news)
        print(f"\n[SUCCESS]")
        print(f"Score: {score}/10")
        print(f"Summary: {summary}")
    except Exception as e:
        print(f"\n[FAILURE] Error: {e}")

if __name__ == "__main__":
    main()
