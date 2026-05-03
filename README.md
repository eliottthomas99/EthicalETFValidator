# Ethical ETF Validator

> AI-powered ESG risk analysis for ETF holdings. Detect greenwashing before you invest.

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Render-success)](https://ethicaletfvalidator.onrender.com/)
[![Python](https://img.shields.io/badge/Python-3.12-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-1.1+-purple)](https://langchain-ai.github.io/langgraph/)

## What is this?

**Ethical ETF Validator** analyzes the top holdings of any ETF and evaluates their ESG (Environmental, Social, Governance) risk using AI-powered research.

Enter an ETF's ISIN code, and the tool will:
1. Fetch the top 3 holdings from [JustETF](https://www.justetf.com)
2. Search recent news for ESG controversies on each company
3. Use AI to evaluate greenwashing and ethical risks
4. Generate a clear risk report with scores and summaries

## Live Demo

Try it now: **[https://ethicaletfvalidator.onrender.com/](https://ethicaletfvalidator.onrender.com/)**

No installation required — just enter an ISIN and your [OpenRouter](https://openrouter.ai) API key.

## How it works

```
User enters ISIN
    ↓
Scrape top 3 holdings from JustETF
    ↓
Search DuckDuckGo for news on each company
    ↓
AI evaluates ESG risk (1-10 scale)
    ↓
Generate report with scores and summaries
```

### Architecture

- **Backend:** FastAPI + LangGraph (Python)
- **Frontend:** HTML + Tailwind CSS (vanilla JS)
- **AI Models:** Any OpenRouter model (default: Nemotron 3 Super Free)
- **Data Sources:** JustETF (holdings), DuckDuckGo (news)
- **Deployment:** Render (free tier)

## Features

- **Real-time ESG Analysis** — Analyzes ETF holdings using up-to-date news
- **AI-Powered Scoring** — Risk scores from 1 (Low) to 10 (Extreme)
- **Company Knowledge Base** — Accumulates research across multiple runs with automatic summarization
- **Model Selection** — Choose any OpenRouter AI model (including free tiers)
- **Privacy-First** — Your API key is never stored; each request is stateless
- **Mobile Responsive** — Works on desktop, tablet, and phone

## Example

Input: `LU2195226068` (Amundi S&P Eurozone Climate Paris Aligned)

Output:
```
ASML Holding NV        — Score: 3/10 (Low Risk)
SAP SE                 — Score: 4/10 (Low Risk)  
Schneider Electric SE  — Score: 5/10 (Medium Risk)
```

## Tech Stack

| Component | Technology |
|-----------|------------|
| Orchestration | LangGraph |
| Web Framework | FastAPI |
| Styling | Tailwind CSS |
| Web Scraping | BeautifulSoup4 |
| Search | DuckDuckGo (ddgs) |
| AI/LLM | OpenRouter (any model) |
| Environment | uv |
| Testing | pytest |

## Local Development

```bash
# Clone the repo
git clone https://github.com/eliottthomas99/EthicalETFValidator.git
cd EthicalETFValidator

# Install dependencies
uv sync

# Set your OpenRouter API key
echo "OPENROUTER_API_KEY=your_key_here" > .env

# Run tests
uv run pytest tests/ -v

# Start the web server
uv run uvicorn web.app:app --reload --port 8000
```

Then visit: `http://127.0.0.1:8000`

## Project Roadmap

- [x] Walking skeleton (fetch holdings, search news, LLM evaluation)
- [x] LangGraph architecture with parallel company processing
- [x] Company knowledge base with automatic summarization
- [x] Web GUI with FastAPI
- [x] Deploy to Render
- [x] Custom AI model selection
- [ ] Support for more than 3 holdings
- [ ] Portfolio-level risk aggregation
- [ ] Historical trend tracking
- [ ] Ticker-to-ISIN lookup

## Contributing

This project uses a branch-and-PR workflow for practice:

```bash
# Create a feature branch
git checkout -b feature/your-feature

# Make changes and commit
git add .
git commit -m "feat: description"

# Push and open PR
git push origin feature/your-feature
```

See `AGENTS.md` for full workflow details.

## License

MIT License — feel free to use, modify, and share.

## Acknowledgments

- [OpenRouter](https://openrouter.ai) for providing access to multiple AI models
- [JustETF](https://www.justetf.com) for ETF holding data
- [LangGraph](https://langchain-ai.github.io/langgraph/) for the graph orchestration framework

---

Built with curiosity and a desire to make finance more transparent.
