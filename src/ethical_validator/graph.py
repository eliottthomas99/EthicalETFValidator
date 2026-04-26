# src/ethical_validator/graph.py
import operator
from typing import Annotated, List, TypedDict

from ethical_validator.holdings import fetch_top_holdings
from ethical_validator.researcher import search_company_news
from ethical_validator.evaluator import evaluate_esg_risk

class CompanyState(TypedDict):
    company: str
    news: str
    score: int
    summary: str
    error: str

class ETFState(TypedDict):
    ticker: str
    holdings: List[str]
    company_results: Annotated[List[CompanyState], operator.add]
    final_report: str

def research_node(state: CompanyState):
    try:
        news = search_company_news(state["company"])
        return {"news": news}
    except Exception as e:
        return {"error": str(e)}

def evaluate_node(state: CompanyState):
    if state.get("error"):
        return {}
    try:
        score, summary = evaluate_esg_risk(state["company"], state.get("news", ""))
        return {"score": score, "summary": summary}
    except Exception as e:
        return {"error": str(e)}
