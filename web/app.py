import os
import traceback

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from ethical_validator.etf_graph import app as etf_app

app = FastAPI()

class AnalyzeRequest(BaseModel):
    isin: str
    api_key: str
    model: str = "nvidia/nemotron-3-super-120b-a12b:free"

@app.post("/api/analyze")
def analyze(request: AnalyzeRequest):
    try:
        initial_state = {
            "ticker": request.isin,
            "api_key": request.api_key,
            "model": request.model
        }
        final_state = etf_app.invoke(initial_state)

        # Strip api_key from company_results before returning
        company_results = final_state.get("company_results", [])
        safe_results = []
        for result in company_results:
            safe_result = {k: v for k, v in result.items() if k != "api_key"}
            safe_results.append(safe_result)

        return {
            "isin": request.isin,
            "holdings": final_state.get("holdings", []),
            "company_results": safe_results,
            "report": final_state.get("final_report", "")
        }
    except Exception as e:
        return {
            "error": str(e),
            "detail": traceback.format_exc()
        }

@app.get("/api/health")
def health_check():
    return {"status": "ok"}

# Get the directory where this file is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.mount("/", StaticFiles(directory=os.path.join(BASE_DIR, "static"), html=True), name="static")
