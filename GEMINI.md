# Ethical ETF Validator - Project Blueprint

## Vision
A pipeline that detects greenwashing by cross-referencing ETF holdings with real-world news and controversies.

## Current Tech Stack (Prototype)
- **Orchestration:** LangGraph (Python) - *to be implemented after basic linear proof-of-concept*
- **LLM:** `nvidia/nemotron-3-super-120b-a12b:free` (via OpenRouter)
- **Environment:** `uv`
- **Data Tools:** `yfinance` (ETF data), `tavily-python` (Web search)

## Milestone 1: "Walking Skeleton" (Today)
1. Fetch top 3 holdings for an ETF.
2. Search web for recent news on those companies.
3. Rough LLM evaluation for greenwashing/ethics risk.
4. Output basic report to console.

## Project Standards
- Surgical updates to code.
- Frequent git commits.
- All secrets (API keys) in `.env`.
