# Walking Skeleton Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a linear Python prototype that fetches ETF holdings, researches them via Tavily, and evaluates ESG risk via OpenRouter.

**Architecture:** Modular functional approach with TDD. Each component (holdings, researcher, evaluator) is implemented as a standalone function with its own tests.

**Tech Stack:** uv, yfinance, tavily-python, langchain-openai, pytest, python-dotenv.

---

### Task 1: Project Initialization & Dependency Management

**Files:**
- Create: `pyproject.toml`, `.env.example`, `src/ethical_validator/__init__.py`

- [ ] **Step 1: Initialize uv project**
Run: `uv init --lib`

- [ ] **Step 2: Add dependencies**
Run: `uv add yfinance tavily-python langchain-openai langgraph python-dotenv pytest pytest-mock`

- [ ] **Step 3: Create `.env.example`**
```text
TAVILY_API_KEY=your_tavily_key_here
OPENROUTER_API_KEY=your_openrouter_key_here
```

- [ ] **Step 4: Create package structure**
Run: `mkdir -p src/ethical_validator tests && touch src/ethical_validator/__init__.py`

- [ ] **Step 5: Commit**
```bash
git add pyproject.toml .env.example src/
git commit -m "chore: initialize uv project and directory structure"
```

---

### Task 2: ETF Holdings Fetcher (`holdings.py`)

**Files:**
- Create: `src/ethical_validator/holdings.py`
- Test: `tests/test_holdings.py`

- [ ] **Step 1: Write failing test for `fetch_top_holdings`**
```python
# tests/test_holdings.py
from ethical_validator.holdings import fetch_top_holdings

def test_fetch_top_holdings_returns_list_of_strings():
    # Using a known ETF ticker
    holdings = fetch_top_holdings("EPAB.PA", count=3)
    assert isinstance(holdings, list)
    assert len(holdings) == 3
    assert all(isinstance(h, str) for h in holdings)
```

- [ ] **Step 2: Run test to verify it fails**
Run: `pytest tests/test_holdings.py`
Expected: `ImportError` or `ModuleNotFoundError`

- [ ] **Step 3: Implement `fetch_top_holdings`**
```python
# src/ethical_validator/holdings.py
import yfinance as yf
from typing import List

def fetch_top_holdings(ticker: str, count: int = 3) -> List[str]:
    etf = yf.Ticker(ticker)
    # yfinance holdings can be unreliable; we'll attempt to get them 
    # and fail loudly if the data structure isn't what we expect.
    holdings_data = etf.get_holdings()
    if holdings_data is None or holdings_data.empty:
        raise RuntimeError(f"Could not fetch holdings for {ticker}. yfinance returned no data.")
    
    # Extract company names from the top 'count' rows
    top_holdings = holdings_data.head(count)['Holding'].tolist()
    if not top_holdings:
         raise RuntimeError(f"Holdings list is empty for {ticker}.")
    return top_holdings
```

- [ ] **Step 4: Run test to verify it passes**
Run: `pytest tests/test_holdings.py`
Expected: `PASS`

- [ ] **Step 5: Commit**
```bash
git add src/ethical_validator/holdings.py tests/test_holdings.py
git commit -m "feat: implement ETF holdings fetcher with yfinance"
```

---

### Task 3: Scandal Researcher (`researcher.py`)

**Files:**
- Create: `src/ethical_validator/researcher.py`
- Test: `tests/test_researcher.py`

- [x] **Step 1: Write failing test for `search_company_news`**
```python
# tests/test_researcher.py
from ethical_validator.researcher import search_company_news
from unittest.mock import patch

@patch("ethical_validator.researcher.TavilyClient")
def test_search_company_news_calls_tavily(mock_tavily):
    mock_tavily.return_value.search.return_value = {"results": [{"content": "Scandal found"}]}
    result = search_company_news("Test Corp")
    assert "Scandal found" in result
```

- [x] **Step 2: Run test to verify it fails**
Run: `pytest tests/test_researcher.py`
Expected: `ImportError`

- [x] **Step 3: Implement `search_company_news`**
```python
# src/ethical_validator/researcher.py
import os
from tavily import TavilyClient

def search_company_news(company: str) -> str:
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise RuntimeError("TAVILY_API_KEY not found in environment.")
    
    tavily = TavilyClient(api_key=api_key)
    query = f"{company} (environmental scandal OR labor violation OR greenwashing OR lawsuit) 2023 2024"
    response = tavily.search(query=query, search_depth="advanced")
    
    results = response.get("results", [])
    if not results:
        return f"No significant news found for {company}."
    
    return "\n---\n".join([r.get("content", "") for r in results])
```

- [x] **Step 4: Run test to verify it passes**
Run: `pytest tests/test_researcher.py`
Expected: `PASS`

- [x] **Step 5: Commit**
```bash
git add src/ethical_validator/researcher.py tests/test_researcher.py
git commit -m "feat: implement scandal researcher with Tavily"
```

---

### Task 4: ESG Evaluator (`evaluator.py`)

**Files:**
- Create: `src/ethical_validator/evaluator.py`
- Test: `tests/test_evaluator.py`

- [ ] **Step 1: Write failing test for `evaluate_esg_risk`**
```python
# tests/test_evaluator.py
from ethical_validator.evaluator import evaluate_esg_risk
from unittest.mock import patch

@patch("ethical_validator.evaluator.ChatOpenAI")
def test_evaluate_esg_risk_returns_score_and_summary(mock_chat):
    # Mocking the LLM response
    mock_chat.return_value.invoke.return_value.content = "Score: 7. Summary: Highly controversial."
    score, summary = evaluate_esg_risk("Test Corp", "Bad news here.")
    assert score == 7
    assert "Highly controversial" in summary
```

- [ ] **Step 2: Run test to verify it fails**
Run: `pytest tests/test_evaluator.py`
Expected: `ImportError`

- [ ] **Step 3: Implement `evaluate_esg_risk`**
```python
# src/ethical_validator/evaluator.py
import os
import re
from langchain_openai import ChatOpenAI

def evaluate_esg_risk(company: str, news: str) -> tuple[int, str]:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY not found in environment.")
    
    llm = ChatOpenAI(
        model="nvidia/nemotron-3-super-120b-a12b:free",
        openai_api_key=api_key,
        openai_api_base="https://openrouter.ai/api/v1"
    )
    
    prompt = f"""
    You are an expert ESG auditor. Review the following news about {company}:
    {news}
    
    Assess the risk of greenwashing or unethical practices on a scale of 1-10 (1=Low Risk, 10=Extreme Risk).
    Format your response EXACTLY as:
    Score: [Number]
    Summary: [2-sentence justification]
    """
    
    response = llm.invoke(prompt).content
    
    # Loud parsing logic
    score_match = re.search(r"Score:\s*(\d+)", response)
    summary_match = re.search(r"Summary:\s*(.*)", response, re.DOTALL)
    
    if not score_match or not summary_match:
        raise RuntimeError(f"LLM failed to follow format. Response was: {response}")
    
    return int(score_match.group(1)), summary_match.group(1).strip()
```

- [ ] **Step 4: Run test to verify it passes**
Run: `pytest tests/test_evaluator.py`
Expected: `PASS`

- [ ] **Step 5: Commit**
```bash
git add src/ethical_validator/evaluator.py tests/test_evaluator.py
git commit -m "feat: implement ESG evaluator with OpenRouter"
```

---

### Task 5: Main Orchestrator (`main.py`)

**Files:**
- Create: `src/ethical_validator/main.py`

- [ ] **Step 1: Implement the "Walking Skeleton" Orchestrator**
```python
# src/ethical_validator/main.py
from dotenv import load_dotenv
from ethical_validator.holdings import fetch_top_holdings
from ethical_validator.researcher import search_company_news
from ethical_validator.evaluator import evaluate_esg_risk

def run_skeleton():
    load_dotenv()
    ticker = "EPAB.PA"
    print(f"--- Analyzing {ticker} ---")
    
    holdings = fetch_top_holdings(ticker, count=3)
    
    for company in holdings:
        print(f"\n[+] Researching {company}...")
        news = search_company_news(company)
        score, summary = evaluate_esg_risk(company, news)
        print(f"Score: {score}/10")
        print(f"Summary: {summary}")

if __name__ == "__main__":
    run_skeleton()
```

- [ ] **Step 2: Final Verification (Manual Run)**
Run: `uv run src/ethical_validator/main.py`
Expected: A console output showing the 3 holdings and their assessments.

- [ ] **Step 3: Commit & Push**
```bash
git add src/ethical_validator/main.py
git commit -m "feat: complete walking skeleton orchestrator"
git push origin main
```
