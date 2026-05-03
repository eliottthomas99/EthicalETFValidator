import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI()

class AnalyzeRequest(BaseModel):
    isin: str
    api_key: str

@app.post("/api/analyze")
def analyze(request: AnalyzeRequest):
    # TODO: Wire to actual pipeline
    return {
        "isin": request.isin,
        "message": "Hello from Ethical ETF Validator!",
        "status": "Pipeline not yet wired — this is a test response"
    }

@app.get("/api/health")
def health_check():
    return {"status": "ok"}

# Get the directory where this file is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.mount("/", StaticFiles(directory=os.path.join(BASE_DIR, "static"), html=True), name="static")
