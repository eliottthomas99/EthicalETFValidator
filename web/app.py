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

@app.post("/api/analyze")
def analyze(request: AnalyzeRequest):
    try:
        initial_state = {
            "ticker": request.isin,
            "api_key": request.api_key
        }
        final_state = etf_app.invoke(initial_state)

        return {
            "isin": request.isin,
            "holdings": final_state.get("holdings", []),
            "company_results": final_state.get("company_results", []),
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
