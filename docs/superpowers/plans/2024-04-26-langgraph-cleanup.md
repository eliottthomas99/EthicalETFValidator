# LangGraph Architecture Cleanup Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Separate the unified `graph.py` file into two distinct files (`company_graph.py` and `etf_graph.py`) to improve readability and adhere to the Single Responsibility Principle. Update GEMINI.md to reflect Milestone 2 completion.

**Architecture:** Split the LangGraph implementation. `company_graph.py` handles the sub-graph blueprint for individual companies. `etf_graph.py` imports this blueprint and handles the main ETF orchestration and map-reduce logic.

**Tech Stack:** Python, LangGraph, pytest.

---

### Task 1: Extract Company Sub-Graph

**Files:**
- Create: `src/ethical_validator/company_graph.py`
- Create: `tests/test_company_graph.py`

- [ ] **Step 1: Write tests for `company_graph`**

```python
# tests/test_company_graph.py
import pytest
from ethical_validator.company_graph import research_node, evaluate_node, CompanyState

def test_research_node_success(mocker):
    mocker.patch('ethical_validator.company_graph.search_company_news', return_value="Great news!")
    state = CompanyState(company="Test Co", news="", score=0, summary="", error="")
    result = research_node(state)
    assert result == {"news": "Great news!"}

def test_research_node_error(mocker):
    mocker.patch('ethical_validator.company_graph.search_company_news', side_effect=Exception("API Error"))
    state = CompanyState(company="Test Co", news="", score=0, summary="", error="")
    result = research_node(state)
    assert result == {"error": "API Error"}
    
def test_evaluate_node_skips_on_error():
    state = CompanyState(company="Test Co", news="", score=0, summary="", error="Previous Error")
    result = evaluate_node(state)
    assert result == {}
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_company_graph.py -v`
Expected: FAIL with "ModuleNotFoundError"

- [ ] **Step 3: Implement `company_graph.py`**

```python
# src/ethical_validator/company_graph.py
from typing import TypedDict
from langgraph.graph import StateGraph, START, END

from ethical_validator.researcher import search_company_news
from ethical_validator.evaluator import evaluate_esg_risk

class CompanyState(TypedDict):
    company: str
    news: str
    score: int
    summary: str
    error: str

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

# Compile Sub-Graph Blueprint
company_builder = StateGraph(CompanyState)
company_builder.add_node("research", research_node)
company_builder.add_node("evaluate", evaluate_node)
company_builder.add_edge(START, "research")
company_builder.add_edge("research", "evaluate")
company_builder.add_edge("evaluate", END)

company_graph = company_builder.compile()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_company_graph.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/ethical_validator/company_graph.py tests/test_company_graph.py
git commit -m "refactor: extract Company Sub-Graph into dedicated module"
```

---

### Task 2: Extract ETF Main Graph

**Files:**
- Create: `src/ethical_validator/etf_graph.py`
- Create: `tests/test_etf_graph.py`

- [ ] **Step 1: Write tests for `etf_graph`**

```python
# tests/test_etf_graph.py
import pytest
from ethical_validator.etf_graph import process_company_wrapper, fetch_node, process_holdings, ETFState

def test_process_company_wrapper(mocker):
    mocker.patch('ethical_validator.etf_graph.company_graph.invoke', return_value={"company": "Test Co", "score": 5})
    result = process_company_wrapper({"company": "Test Co"})
    assert result == {"company_results": [{"company": "Test Co", "score": 5}]}

def test_fetch_node(mocker):
    mocker.patch('ethical_validator.etf_graph.fetch_top_holdings', return_value=["Co A"])
    state = ETFState(ticker="EPAB.PA", holdings=[], company_results=[], final_report="")
    assert fetch_node(state) == {"holdings": ["Co A"]}

def test_process_holdings():
    state = ETFState(ticker="EPAB.PA", holdings=["Co A", "Co B"], company_results=[], final_report="")
    sends = process_holdings(state)
    assert len(sends) == 2
    assert sends[0].node == "process_company"
    assert sends[0].arg == {"company": "Co A"}
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_etf_graph.py -v`
Expected: FAIL with "ModuleNotFoundError"

- [ ] **Step 3: Implement `etf_graph.py`**

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_etf_graph.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/ethical_validator/etf_graph.py tests/test_etf_graph.py
git commit -m "refactor: extract ETF Main Graph into dedicated module"
```

---

### Task 3: Cleanup and Update Entry Point

**Files:**
- Modify: `src/ethical_validator/main.py`
- Delete: `src/ethical_validator/graph.py`
- Delete: `tests/test_graph.py`
- Modify: `GEMINI.md`

- [ ] **Step 1: Update `main.py` imports**

```python
# src/ethical_validator/main.py
import os
from dotenv import load_dotenv
from ethical_validator.etf_graph import app

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
```

- [ ] **Step 2: Delete old unified files**

Run: `rm src/ethical_validator/graph.py tests/test_graph.py`

- [ ] **Step 3: Update `GEMINI.md`**

Replace the Milestone section in `GEMINI.md` to reflect the completion of Milestone 2:

```markdown
## Milestone 1: "Walking Skeleton" (Completed)
1. Fetch top 3 holdings for an ETF using `yfinance`.
2. Search web for recent news on those companies using `tavily-python`.
3. Rough LLM evaluation for greenwashing/ethics risk using `langchain-openai` (OpenRouter).
4. Output basic markdown report to `reports/`.

## Milestone 2: Graph Architecture (Completed)
1. Transition the linear script (`main.py`) into a LangGraph `StateGraph`.
2. Define the State schema to pass data between nodes.
3. Wire the nodes: `fetch_holdings` -> `research_companies` (parallel map/reduce) -> `analyze_ethics` -> `generate_report`.
4. Extracted Sub-Graph (`company_graph.py`) and Main Graph (`etf_graph.py`) for clarity.

## Milestone 3: Refining Data Sources & Features (Next Session)
1. Investigate alternative holding fetchers (replacing or augmenting `yfinance` for better recency).
2. Consider caching mechanisms to reduce `tavily` API costs across runs.
3. Enhance the LLM evaluation prompt and scoring mechanism.
```

- [ ] **Step 4: Run full test suite to verify everything still works**

Run: `uv run pytest -v`
Expected: ALL PASS

- [ ] **Step 5: Commit**

```bash
git add src/ethical_validator/main.py GEMINI.md
git rm src/ethical_validator/graph.py tests/test_graph.py
git commit -m "refactor: cleanup old graph files and update documentation for Milestone 2 completion"
```
