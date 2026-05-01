# Ethical ETF Validator - Project Blueprint

> **Note for AI agents:** This file replaces the old `GEMINI.md`. If you're using the Gemini CLI, point it here instead.

## Vision
A pipeline that detects greenwashing by cross-referencing ETF holdings with real-world news and controversies.

## Current Tech Stack (Prototype)
- **Orchestration:** LangGraph (Python)
- **LLM:** `nvidia/nemotron-3-super-120b-a12b:free` (via OpenRouter)
- **Environment:** `uv`
- **Data Tools:** `justetf.com` scraping (ETF holdings via ISIN), `ddgs` (DuckDuckGo web search)

## Milestone 1: "Walking Skeleton" (Completed)
1. Fetch top 3 holdings for an ETF.
2. Search web for recent news on those companies.
3. Rough LLM evaluation for greenwashing/ethics risk using `langchain-openai` (OpenRouter).
4. Output basic markdown report to `reports/`.

> **Updates since initial implementation:**
> - Replaced `yfinance` with **JustETF scraper** (`holdings.py`) — no API key needed, better recency for European ETFs.
> - Replaced `tavily-python` with **DuckDuckGo search** (`ddgs`) — removed paid API dependency.
> - Input is now the fund's **ISIN** (e.g. `LU2195226068`) rather than a ticker symbol.

## Milestone 2: Graph Architecture (Completed)
1. Transition the linear script (`main.py`) into a LangGraph `StateGraph`.
2. Define the State schema to pass data between nodes.
3. Wire the nodes: `fetch_holdings` -> `research_companies` (parallel map/reduce) -> `analyze_ethics` -> `generate_report`.
4. Extracted Sub-Graph (`company_graph.py`) and Main Graph (`etf_graph.py`) for clarity.

## Milestone 3: Refining Data Sources & Features (In Progress)
1. ~~Investigate alternative holding fetchers (replacing or augmenting `yfinance` for better recency).~~ ✅ **Done** — JustETF scraper implemented.
2. Consider caching mechanisms to reduce `ddgs` / API costs across runs.
3. Enhance the LLM evaluation prompt and scoring mechanism.

## Known Limitations & Future Improvements
- **Scraping fragility:** JustETF layout changes could break `holdings.py`. A fallback strategy or API-based source would improve resilience.
- **Caching:** No caching layer yet — every run re-fetches holdings and re-searches news.
- **ISIN-only input:** Currently requires the user to provide the ISIN. A ticker-to-ISIN lookup would be a nice UX improvement.

## Project Standards
- Surgical updates to code.
- Frequent git commits.
- All secrets (API keys) in `.env`.
