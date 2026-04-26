# src/ethical_validator/etf_graph.py
import operator
from typing import Annotated, List, TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.types import Send

from ethical_validator.holdings import fetch_top_holdings
from ethical_validator.company_graph import CompanyState, company_graph

class ETFState(TypedDict):
    ticker: str
    holdings: List[str]
    company_results: Annotated[List[CompanyState], operator.add]
    final_report: str

def process_company_wrapper(state: CompanyState):
    """Wraps the subgraph to correctly format the output for the Main Graph's state."""
    result = company_graph.invoke(state)
    return {"company_results": [result]}

def fetch_node(state: ETFState):
    holdings = fetch_top_holdings(state["ticker"], count=3)
    return {"holdings": holdings}

def process_holdings(state: ETFState):
    # LangGraph map-reduce pattern using Send
    return [Send("process_company", {"company": holding}) for holding in state.get("holdings", [])]

def report_node(state: ETFState):
    ticker = state["ticker"]
    results = state.get("company_results", [])
    
    report_lines = [
        f"# ESG Risk Report: {ticker}",
        f"**Holdings Evaluated:** {', '.join(state.get('holdings', []))}",
        "---"
    ]
    
    for result in results:
        company = result.get("company", "Unknown")
        if result.get("error"):
            report_lines.extend([f"## {company}", f"**Error:** {result['error']}", ""])
        else:
            score = result.get("score", "N/A")
            summary = result.get("summary", "N/A")
            news_snippet = result.get("news", "")[:500]
            report_lines.extend([
                f"## {company}",
                f"**Risk Score:** {score}/10",
                f"**Summary:** {summary}",
                f"**Key News Snippet:**\n> {news_snippet}...",
                ""
            ])
            
    final_report = "\n".join(report_lines)
    return {"final_report": final_report}

# Compile Main Graph
etf_builder = StateGraph(ETFState)
etf_builder.add_node("fetch", fetch_node)
etf_builder.add_node("process_company", process_company_wrapper)
etf_builder.add_node("report", report_node)

etf_builder.add_edge(START, "fetch")
etf_builder.add_conditional_edges("fetch", process_holdings, ["process_company"])
etf_builder.add_edge("process_company", "report")
etf_builder.add_edge("report", END)

app = etf_builder.compile()
