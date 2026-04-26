# Ethical ETF Validator - Project Blueprint

## Vision
A pipeline that detects greenwashing by cross-referencing ETF holdings with real-world news and controversies.

## Current Tech Stack (Prototype)
- **Orchestration:** LangGraph (Python) - *to be implemented after basic linear proof-of-concept*
- **LLM:** `nvidia/nemotron-3-super-120b-a12b:free` (via OpenRouter)
- **Environment:** `uv`
- **Data Tools:** `yfinance` (ETF data), `tavily-python` (Web search)

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

## Known Limitations & Future Improvements
- **Data Recency:** `yfinance` holdings data can lag behind official fund reporting (e.g., justETF). 
    - *Plan:* In a future milestone, investigate scraping official fund manager documents (PDF/CSV) or using a more premium ESG data API.
- **ISIN Support:** Currently using Ticker symbols; add ISIN resolution in the future.

## Project Standards
- Surgical updates to code.
- Frequent git commits.
- All secrets (API keys) in `.env`.
