# src/ethical_validator/main.py
import os
from dotenv import load_dotenv
from ethical_validator.graph import app

def main():
    print("Loading environment variables...")
    load_dotenv()
    
    ticker = "EPAB.PA"
    print(f"--- Starting LangGraph ESG Risk Evaluation for {ticker} ---")
    
    initial_state = {"ticker": ticker}
    
    try:
        # Invoke the compiled LangGraph
        final_state = app.invoke(initial_state)
        
        report = final_state.get("final_report", "")
        
        # Save Report
        os.makedirs("reports", exist_ok=True)
        report_filename = f"reports/{ticker}_langgraph_report.md"
        with open(report_filename, "w") as f:
            f.write(report)
            
        print(f"\n[+] Full report saved to {report_filename}")
        print("\n--- Report Preview ---")
        print(report[:500] + "...\n")
        
    except Exception as e:
        print(f"Error executing graph: {e}")

if __name__ == "__main__":
    main()
