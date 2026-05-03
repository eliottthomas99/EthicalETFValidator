from typing import TypedDict
from langgraph.graph import StateGraph, START, END

from ethical_validator.researcher import search_company_news
from ethical_validator.evaluator import evaluate_esg_risk
from ethical_validator.knowledge_base import add_news_items, get_accumulated_context

class CompanyState(TypedDict):
    company: str
    news: str
    accumulated_knowledge: str
    score: int
    summary: str
    error: str
    api_key: str
    model: str

def research_node(state: CompanyState):
    try:
        news_results = search_company_news(state["company"])
        if not news_results:
            return {"news": "No significant news found.", "accumulated_knowledge": "No accumulated knowledge available."}

        # Join for the immediate evaluator context
        news_text = "\n---\n".join([r.get("body", "") for r in news_results])

        # Update knowledge base with structured results
        add_news_items(state["company"], news_results, api_key=state.get("api_key", ""), model=state.get("model", "nvidia/nemotron-3-super-120b-a12b:free"))
        accumulated = get_accumulated_context(state["company"])

        return {
            "news": news_text,
            "accumulated_knowledge": accumulated
        }
    except Exception as e:
        return {"error": str(e)}

def evaluate_node(state: CompanyState):
    if state.get("error"):
        return {}
    try:
        company = state["company"]
        fresh_news = state.get("news", "")
        accumulated = state.get("accumulated_knowledge", "")
        score, summary = evaluate_esg_risk(company, fresh_news, accumulated, api_key=state.get("api_key", ""), model=state.get("model", "nvidia/nemotron-3-super-120b-a12b:free"))
        return {"score": score, "summary": summary}
    except Exception as e:
        return {"error": str(e)}

# Compile Sub-Graph Blueprint
company_builder = StateGraph(CompanyState)
company_builder.add_node("research", research_node)
company_builder.add_node("evaluate", evaluate_node)
company_builder.add_edge(START, "research")
company_builder.add_edge("research", "evaluate")
company_builder.add_edge("evaluate", END)

company_graph = company_builder.compile()
