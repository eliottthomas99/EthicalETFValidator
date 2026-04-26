# LangGraph Architecture Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor the linear pipeline into a robust, parallelized LangGraph application using the Sub-Graph (Map-Reduce) pattern.

**Architecture:** Dual-Graph Strategy. A Main Graph (ETF Orchestrator) uses LangGraph's `Send` API to map over holdings and execute parallel Sub-Graphs (Company Evaluator) for research and evaluation.

**Tech Stack:** Python, LangGraph, pytest, pytest-mock.

---

### Task 1: State Definitions & Sub-Graph Nodes

**Files:**
- Create: `src/ethical_validator/graph.py`
- Create: `tests/test_graph.py`

- [ ] **Step 1: Write failing tests for sub-graph nodes**

```python
# tests/test_graph.py
from ethical_validator.graph import research_node, evaluate_node, CompanyState

def test_research_node_success(mocker):
    mocker.patch('ethical_validator.graph.search_company_news', return_value="Great news!")
    state = CompanyState(company="Test Co", news="", score=0, summary="", error="")
    result = research_node(state)
    assert result == {"news": "Great news!"}

def test_research_node_error(mocker):
    mocker.patch('ethical_validator.graph.search_company_news', side_effect=Exception("API Error"))
    state = CompanyState(company="Test Co", news="", score=0, summary="", error="")
    result = research_node(state)
    assert result == {"error": "API Error"}
    
def test_evaluate_node_skips_on_error():
    state = CompanyState(company="Test Co", news="", score=0, summary="", error="Previous Error")
    result = evaluate_node(state)
    assert result == {}
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_graph.py -v`
Expected: FAIL with "ImportError"

- [ ] **Step 3: Implement state schemas and sub-graph nodes**

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_graph.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/ethical_validator/graph.py tests/test_graph.py
git commit -m "feat: add LangGraph state schemas and sub-graph nodes"
```

---

### Task 2: Compile Sub-Graph and Wrapper

**Files:**
- Modify: `tests/test_graph.py`
- Modify: `src/ethical_validator/graph.py`

- [ ] **Step 1: Append test for wrapper to `tests/test_graph.py`**

```python
# tests/test_graph.py (append this code to the bottom of the file)
from ethical_validator.graph import process_company_wrapper

def test_process_company_wrapper(mocker):
    # Mock the compiled graph's invoke method
    mocker.patch('ethical_validator.graph.company_graph.invoke', return_value={"company": "Test Co", "score": 5})
    # The wrapper should return a dict updating the company_results list
    result = process_company_wrapper({"company": "Test Co"})
    assert result == {"company_results": [{"company": "Test Co", "score": 5}]}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_graph.py::test_process_company_wrapper -v`
Expected: FAIL

- [ ] **Step 3: Compile Sub-Graph and implement wrapper**

```python
# src/ethical_validator/graph.py (append this code to the bottom of the file)
from langgraph.graph import StateGraph, START, END

# Compile Sub-Graph
company_builder = StateGraph(CompanyState)
company_builder.add_node("research", research_node)
company_builder.add_node("evaluate", evaluate_node)
company_builder.add_edge(START, "research")
company_builder.add_edge("research", "evaluate")
company_builder.add_edge("evaluate", END)
company_graph = company_builder.compile()

def process_company_wrapper(state: CompanyState):
    """Wraps the subgraph to correctly format the output for the Main Graph's state."""
    result = company_graph.invoke(state)
    return {"company_results": [result]}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_graph.py::test_process_company_wrapper -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/ethical_validator/graph.py tests/test_graph.py
git commit -m "feat: compile company sub-graph and add state wrapper"
```

---

### Task 3: Main Graph Nodes and Compilation

**Files:**
- Modify: `tests/test_graph.py`
- Modify: `src/ethical_validator/graph.py`

- [ ] **Step 1: Append tests for Main Graph nodes to `tests/test_graph.py`**

```python
# tests/test_graph.py (append this code to the bottom of the file)
from ethical_validator.graph import fetch_node, process_holdings, ETFState

def test_fetch_node(mocker):
    mocker.patch('ethical_validator.graph.fetch_top_holdings', return_value=["Co A"])
    state = ETFState(ticker="EPAB.PA", holdings=[], company_results=[], final_report="")
    assert fetch_node(state) == {"holdings": ["Co A"]}

def test_process_holdings():
    state = ETFState(ticker="EPAB.PA", holdings=["Co A", "Co B"], company_results=[], final_report="")
    sends = process_holdings(state)
    assert len(sends) == 2
    assert sends[0].target == "process_company"
    assert sends[0].arg == {"company": "Co A"}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_graph.py::test_fetch_node tests/test_graph.py::test_process_holdings -v`
Expected: FAIL

- [ ] **Step 3: Implement Main Graph nodes and compile**

```python
# src/ethical_validator/graph.py (append this code to the bottom of the file)
from langgraph.constants import Send

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

Run: `uv run pytest tests/test_graph.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/ethical_validator/graph.py tests/test_graph.py
git commit -m "feat: compile main graph and map-reduce nodes"
```

---

### Task 4: Update Main Orchestrator

**Files:**
- Modify: `src/ethical_validator/main.py`

- [ ] **Step 1: Replace contents of `src/ethical_validator/main.py`**

```python
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
```

- [ ] **Step 2: Run verification**

Run: `uv run python src/ethical_validator/main.py`
Expected: The script should load environment variables and output the "Starting LangGraph ESG Risk Evaluation..." message, process the holdings, and generate the report.

- [ ] **Step 3: Commit**

```bash
git add src/ethical_validator/main.py
git commit -m "feat: integrate LangGraph app into main orchestrator"
```
