# src/ethical_validator/main.py
import os
from dotenv import load_dotenv
from ethical_validator.etf_graph import app

def main():
    print("Loading environment variables...")
    load_dotenv()
    
    # ISIN for Amundi S&P Eurozone Climate Paris Aligned UCITS ETF Acc (EPAB.PA)
    isin = "LU2195226068"
    print(f"--- Starting LangGraph ESG Risk Evaluation for {isin} ---")

    initial_state = {"ticker": isin}
    
    try:
        # Invoke the compiled LangGraph
        final_state = app.invoke(initial_state)
        
        report = final_state.get("final_report", "")
        
        # Save Report
        os.makedirs("reports", exist_ok=True)
        report_filename = f"reports/{isin}_langgraph_report.md"
        with open(report_filename, "w") as f:
            f.write(report)
            
        print(f"\n[+] Full report saved to {report_filename}")
        print("\n--- Report Preview ---")
        print(report[:500] + "...\n")
        
    except Exception as e:
        print(f"Error executing graph: {e}")

if __name__ == "__main__":
    main()
