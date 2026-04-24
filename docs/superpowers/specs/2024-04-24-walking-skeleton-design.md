# Design Spec: Walking Skeleton (Milestone 1)

**Date:** 2024-04-24
**Status:** Draft
**Topic:** End-to-end prototype for Ethical ETF Validator

## 1. Goal
A linear Python script that fetches the top 3 holdings of a hardcoded ETF ticker, searches for news on each holding, and provides a rough ESG risk evaluation using an LLM.

## 2. Architecture
We will use a modular functional structure in `src/`.

### Components:
- `main.py`: Orchestrator. Hardcoded ticker -> calls sub-modules -> console output.
- `holdings.py`: Interface for `yfinance`.
    - `fetch_top_holdings(ticker: str, count: int) -> List[str]`
- `researcher.py`: Interface for `tavily-python`.
    - `search_company_news(company: str) -> str`
- `evaluator.py`: Interface for OpenRouter (`langchain-openai`).
    - `evaluate_esg_risk(company: str, news: str) -> RiskAssessment` (Score 1-10 + 2-sentence summary).

## 3. Data Flow
1. Start with hardcoded ticker `EPAB.PA` (Amundi S&P Eurozone Climate Paris Aligned).
2. Fetch top 3 holdings via `yfinance`.
3. For each holding:
    - Search Tavily for scandals/news.
    - Prompt LLM for a 1-10 score and justification.
4. Output a summary table to the console.

## 4. Error Handling (Loud Fails)
- No `try/except` blocks that swallow errors.
- If an API call fails, the program crashes with a stack trace.
- Validation logic will raise `ValueError` or `RuntimeError` if data is missing or malformed.

## 5. Testing Strategy
- Use `pytest` for TDD.
- Each module (`holdings`, `researcher`, `evaluator`) must have at least one unit test before implementation.
- Mocking will be introduced for API calls to ensure tests are fast and don't consume credits unnecessarily.

## 6. Tech Stack
- Python (uv)
- yfinance
- tavily-python
- langchain-openai (OpenRouter)
- pytest
